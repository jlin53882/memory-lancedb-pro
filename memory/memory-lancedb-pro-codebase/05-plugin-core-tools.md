# memory-lancedb-pro：Plugin 主體、工具 API 與 Embedder 深度分析

> 分析目標：C:\Users\admin\.openclaw\memory-lancedb-pro
> 分析日期：2026-04-02
> 主要來源：index.ts、tools.ts、embedder.ts

---

## 一、Plugin 啟動初始化流程（init 順序）

### 1.1 `register()` — 單次執行保障

`index.ts` 中的 `register()` 方法有 **idempotent guard**：

```typescript
let _initialized = false;
// ...
if (_initialized) {
  api.logger.debug("register() called again — skipping re-init (idempotent)");
  return;
}
_initialized = true;
```

這確保 `register()` 被多次呼叫時只執行一次初始化，避免重複訂閱 hook。

---

### 1.2 初始化順序（直線式）

| 順序 | 元件 | 說明 |
|------|------|------|
| 1 | `parsePluginConfig()` | 解析 pluginConfig，驗證 `embedding.apiKey` 必填 |
| 2 | `validateStoragePath()` | 預檢查 storage path（symlink 解析、mkdir、write check）；警告而非阻斷 |
| 3 | `getVectorDimensions()` | 根據 model 名稱查表取得維度，若未知則拋錯 |
| 4 | `MemoryStore` | 新建實例，傳入 `dbPath` 與 `vectorDim` |
| 5 | `createEmbedder()` | 建立 Embedder 實例（見第四章）|
| 6 | `createDecayEngine()` | 建立 decay engine，帶有默認 decay 參數 |
| 7 | `createTierManager()` | 建立 tier 等級管理器（core/working/peripheral）|
| 8 | `createRetriever()` | 建立 retriever，依賴 store + embedder + retrieval config |
| 9 | `createScopeManager()` | 建立 scope 管理器，載入 scope 定義 |
| 10 | Clawteam scope 擴展 | 解析 `CLAWTEAM_MEMORY_SCOPE` 環境變數 |
| 11 | `createMigrator()` | 建立 migrator（支援 schema 遷移）|
| 12 | `SmartExtractor`（可選）| LLM-powered 萃取器，需額外 API key |
| 13 | `NoisePrototypeBank` | 基於 embedding 的噪音原型銀行（async init）|
| 14 | `registerAllMemoryTools()` | 註冊所有 Agent 工具（見第二章）|
| 15 | `registerCli()` | 註冊 `memory-pro` CLI 命令 |
| 16 | Hook 訂閱 | 根據 config 啟動 auto-recall、auto-capture、reflection 等 hooks |
| 17 | `api.registerService()` | 註冊啟動/停止鉤子 |

### 1.3 Service start — 非阻塞設計

`registerService().start()` 採用 **fire-and-forget** 模式：

```typescript
setTimeout(() => void runStartupChecks(), 0);  // 立即返回
setTimeout(() => void runBackup(), 60_000);     // 1 分鐘後備份
backupTimer = setInterval(() => void runBackup(), BACKUP_INTERVAL_MS);
```

**重要原則**：**嚴禁阻塞 gateway 啟動**。Embedding API 或 retrieval 測試若有網路延遲，會以 8 秒 timeout 上限控速，不會卡住 HTTP port binding。

---

## 二、Lifecycle Hooks 實作邏輯

Plugin 實作了非常完整的 lifecycle hook 矩陣，以下逐一解析。

---

### 2.1 `message_received`

**觸發時機**：每收到一個新 message 時

**用途**：
- 建立 `conversationKey`（channelId + conversationId）作為 auto-capture 的 text queue key
- 將 normalized 文字推入 `autoCapturePendingIngressTexts` Map（最多保留 6 筆）
- 記錄 debug 日誌（包含 preview、content length）

**程式碼位置**：`index.ts` `api.on("message_received", ...)`

```typescript
api.on("message_received", (event: any, ctx: any) => {
  const conversationKey = buildAutoCaptureConversationKeyFromIngress(ctx.channelId, ctx.conversationId);
  const normalized = normalizeAutoCaptureText("user", event.content, shouldSkipReflectionMessage);
  if (conversationKey && normalized) {
    const queue = autoCapturePendingIngressTexts.get(conversationKey) || [];
    queue.push(normalized);
    autoCapturePendingIngressTexts.set(conversationKey, queue.slice(-6));
  }
});
```

---

### 2.2 `before_message_write`

**觸發時機**：在 message 寫入 session 之前

**用途**：只處理 `role === "user"` 的 message，記錄 debug 資訊（不主動修改內容）。

---

### 2.3 `before_prompt_build`（最重要的鉤子）

**觸發時機**：在 prompt 構建前、Agent 執行前

**優先級**：`priority: 10`（低於其他 hooks）

這個 hook 實作了兩套子系統：

#### 2.3.1 Auto-Recall（inject relevant memories）

觸發條件：`config.autoRecall === true && recallMode !== "off"`

**流程**：

```
shouldSkipRetrieval(gatingText, minLength) → 跳過短訊息/問候語
  ↓
resolveScopeFilter(scopeManager, agentId) → 取得該 agent 可存取的 scopes
  ↓
retrieveWithRetry({ query, limit, scopeFilter }) → 向量+關鍵字混合檢索
  ↓
filterUserMdExclusiveRecallResults() → 過濾屬於 USER.md 的記憶
  ↓
applyCategoryBoost(intent) → adaptive 模式下套用意圖分類 boost
  ↓
governance filter（state/importance/suppressed）
  ↓
budget allocation（maxItems × maxChars）
  ↓
inject: <relevant-memories>...</relevant-memories>
```

**Governance 過濾**：
- `state !== "confirmed"` → 排除（除非已手動 promote）
- `memory_layer === "archive" || "reflection"` → 排除
- `suppressed_until_turn > currentTurn` → 排除（bad recall 抑制）

**Redundancy 過濾**（可選）：
- 同一 session 內，同一 memory 在 `minRepeated` 個 turn 內不會重複 inject
- `recallHistory` Map 追蹤每個 session 的 inject 歷史

**Timeout 保護**：
```typescript
const result = await Promise.race([
  recallWork(),
  new Promise((resolve) => {
    timeoutId = setTimeout(() => {
      api.logger.warn("auto-recall timed out after Xms; skipping");
      resolve(undefined);
    }, AUTO_RECALL_TIMEOUT_MS);
  }),
]);
```

#### 2.3.2 Memory Reflection — Inheritance Injection

**觸發條件**：`sessionStrategy === "memoryReflection"` 且 `injectMode === "inheritance-only"` 或 `"inheritance+derived"`

**優先級**：`priority: 12`（高於 auto-recall 的 10）

**行為**：從 LanceDB 查詢 `category === "reflection"` 的 entries，加載 agent-owned 的 slices（invariants + derived），inject 為 `<inherited-rules>...</inherited-rules>` 區塊。

#### 2.3.3 Memory Reflection — Derived Focus Injection

**觸發條件**：`injectMode === "inheritance+derived"`

**優先級**：`priority: 15`

inject `<derived-focus>...</derived-focus>` 區塊，包含最近 derived deltas。

#### 2.3.4 Memory Reflection — Error Signal Reminder

inject `<error-detected>...</error-detected>` 區塊，通知 agent 最近的 tool error signals。

---

### 2.4 `after_tool_call`

**觸發條件**：`sessionStrategy === "memoryReflection"`

**優先級**：`priority: 15`

**行為**：掃描 tool call 的 error 與 output，偵測錯誤信號（`[error]`、stacktrace、`command not found` 等），以 SHA256 簽名去重後存入 `reflectionErrorStateBySession`。

**去重機制**：
```typescript
if (dedupeEnabled && state.signatureSet.has(signal.signatureHash)) return;
// signature = normalizeErrorSignature(text) → 移除 path、hex、數字等差異
// signatureHash = sha256(signature).slice(0, 16)
```

---

### 2.5 `agent_end`（Auto-Capture 主體）

**觸發條件**：`config.autoCapture !== false`

**設計**：**Fire-and-forget** — hook 本體立即返回，實際工作在 background Promise 執行：

```typescript
const backgroundRun = (async () => { /* ... */ })();
agentEndAutoCaptureHook.__lastRun = backgroundRun;
void backgroundRun;
```

**Pipeline 流程**：

```
提取 event.messages 中的 user/assistant text blocks
  ↓
normalizeAutoCaptureText() → 清理、去除 injected blocks
  ↓
Feature 7: extractionRateLimiter.isRateLimited() → 限流檢查
  ↓
Feature 7: skipLowValue（可選）→ estimateConversationValue() < 0.2 → 跳過
  ↓
Feature 1: sessionCompression（可選）→ compressTexts() → drop 低分文本
  ↓
SmartExtractor.extractAndPersist()（若啟用）→ LLM 萃取
  ↓
若失敗 → Regex fallback: shouldCapture() + detectCategory()
  ↓
去重檢查（vectorSearch similarity > 0.90 → 跳過）
  ↓
store.store() + mdMirror dual-write
```

**Auto-capture 寫入的 metadata 預設值**：
```typescript
{
  source: "auto-capture",
  state: "confirmed",        // 直接 confirmed 可被 immediate recall
  memory_layer: "working",
  injected_count: 0,
  bad_recall_count: 0,
  suppressed_until_turn: 0,
}
```

---

### 2.6 `session_end`

**觸發時機**：Session 結束時

**行為**：
- 清除 `recallHistory`、`turnCounter`、`lastRawUserMessage`（按 sessionId）
- 清除 `autoCapturePendingIngressTexts`、`autoCaptureRecentTexts`
- 清除 `reflectionErrorStateBySession`（按 sessionKey）
- 清除 `reflectionDerivedBySession`

**目的**：防止長駐 process 中的 Map 無限增長。

---

### 2.7 `gateway_start`

**觸發時機**：Gateway 啟動時

**行為**：若有 `memoryCompaction.enabled`，在 startup 時執行 auto-compaction（帶 cooldown 檢查）。

---

### 2.8 `before_reset` / `command:new` / `command:reset`

用於 session strategy 的三種模式：

| 模式 | Hook | 行為 |
|------|------|------|
| `memoryReflection` | `command:new` + `command:reset` | 觸發 `runMemoryReflection()` → 生成 reflection 日誌 |
| `systemSessionMemory` | `before_reset` | 儲存 session summary 到 LanceDB |
| `none` | — | 不做任何事 |

---

### 2.9 `agent:bootstrap`

**觸發條件**：`selfImprovement?.enabled !== false`

**行為**：在 agent bootstrap 時注入 `SELF_IMPROVEMENT_REMINDER.md` 虛擬檔案。

---

## 三、Tool 的 Input Schema 定義

### 3.1 Schema 框架

所有工具使用 **`@sinclair/typebox`** 的 `Type.Object()` 定義 schema，這是一種**靜態型別 + 运行时驗證**雙用的方案。

Helper 函式用於列舉型別：

```typescript
function stringEnum<T extends readonly [string, ...string[]]>(values: T) {
  return Type.Unsafe<T[number]>({
    type: "string",
    enum: [...values],
  });
}
```

所有工具的 category 欄位統一使用：
```typescript
const MEMORY_CATEGORIES = [
  "preference", "fact", "decision", "entity", "reflection", "other",
] as const;
```

### 3.2 各工具 Schema 一覽

| Tool | 必填參數 | 可選參數 |
|------|---------|---------|
| `memory_recall` | `query: string` | `limit`, `includeFullText`, `maxCharsPerItem`, `scope`, `category` |
| `memory_store` | `text: string` | `importance`（預設 0.7）, `category`（預設 "other"）, `scope` |
| `memory_forget` | — | `query`, `memoryId`, `scope`（至少需一個 selector）|
| `memory_update` | `memoryId: string` | `text`, `importance`, `category`（至少需一個更新欄位）|
| `memory_stats` | — | `scope` |
| `memory_debug` | `query: string` | `limit`, `scope` |
| `memory_list` | — | `limit`（預設 10）, `scope`, `category`, `offset`（預設 0）|
| `memory_promote` | — | `memoryId`, `query`, `scope`, `state`（pending/confirmed/archived）, `layer`（durable/working/reflection/archive）|
| `memory_archive` | — | `memoryId`, `query`, `scope`, `reason`（預設 "manual_archive"）|
| `memory_compact` | — | `scope`, `dryRun`（預設 true）, `limit`（預設 200）|
| `memory_explain_rank` | `query: string` | `limit`（預設 5）, `scope` |
| `self_improvement_log` | `type`（learning/error）, `summary: string` | `details`, `suggestedAction`, `category`, `area`, `priority` |
| `self_improvement_extract_skill` | `learningId`, `skillName` | `sourceFile`, `outputDir` |
| `self_improvement_review` | — | —（無參數）|

### 3.3 Zod Validation

**直接使用 TypeScript type + TypeBox，無 Zod 依賴。**

驗證主要靠：
- TypeBox schema 自動約束類型
- 工具函式中手動 `clampInt()`、`clamp01()` 做數值範圍限制
- 工具內部的參數解構時賦予預設值（如 `limit = 3`）

---

## 四、Tool 執行時的 Runtime Context 解析

### 4.1 `resolveToolContext()` — Runtime Agent ID 解析

每個 tool 的工廠函式接受 `toolCtx`，用於解析 runtime agent ID：

```typescript
function resolveToolContext(base: ToolContext, runtimeCtx: unknown): ToolContext {
  return {
    ...base,
    agentId: resolveRuntimeAgentId(base.agentId, runtimeCtx),
  };
}
```

**解析順序**：
1. `runtimeCtx.agentId`（明確傳入）
2. `parseAgentIdFromSessionKey(runtimeCtx.sessionKey)`
3. `base.agentId`（靜態設定）
4. 預設值 `"main"`

### 4.2 Scope 過濾

每個 tool 都呼叫 `resolveScopeFilter(scopeManager, agentId)` 來確認該 agent 可存取的 scopes。

---

## 五、Embedder 多 Provider 支援架構

### 5.1 Provider 偵測邏輯

`embedder.ts` 透過 `detectEmbeddingProviderProfile()` 自動偵測 provider：

```typescript
function detectEmbeddingProviderProfile(baseURL, model): EmbeddingProviderProfile {
  if (/api\.openai\.com/i.test(base)) return "openai";
  if (/\.openai\.azure\.com/i.test(base)) return "azure-openai";
  if (/api\.jina\.ai/i.test(base) || /^jina-/i.test(model)) return "jina";
  if (/api\.voyageai\.com/i.test(base) || /^voyage\b/i.test(model)) return "voyage-compatible";
  return "generic-openai-compatible";
}
```

### 5.2 各 Provider 的 Capability 差異

| Provider | `encoding_format` | `normalized` | `taskField` | `dimensionsField` |
|----------|------------------|-------------|------------|-----------------|
| OpenAI | ✅（float）| ❌ | null | `dimensions` |
| Jina | ✅ | ✅ | `task` | `dimensions` |
| Voyage | ❌ | ❌ | `input_type`（翻譯 map）| `output_dimension` |
| Generic | ✅ | ❌ | null | `dimensions` |

**Task Value Map（Voyage 專用翻譯）**：
```typescript
taskValueMap: {
  "retrieval.query": "query",
  "retrieval.passage": "document",
}
```

### 5.3 LRU Cache

```typescript
class EmbeddingCache {
  private cache = new Map<string, CacheEntry>(); // key = SHA256(text + task)
  constructor(maxSize = 256, ttlMinutes = 30)
  get(text, task?) → number[] | undefined
  set(text, task?, vector) → void
  get stats() → { size, hits, misses, hitRate }
}
```

Cache key：`SHA256("${task || ''}:${text}").slice(0, 24)`

### 5.4 Multi-Key Round-Robin

```typescript
private clients: OpenAI[];  // 每個 API key 一個 client
private _clientIndex: number = 0;

private nextClient(): OpenAI {
  const client = this.clients[this._clientIndex % this.clients.length];
  this._clientIndex = (this._clientIndex + 1) % this.clients.length;
  return client;
}
```

Rate-limit 發生時自動更換 key：
```typescript
if (this.isRateLimitError(error) && attempt < maxAttempts - 1) {
  continue; // rotate to next key
}
```

### 5.5 Ollama 特殊處理

Ollama 的 HTTP server 不正確處理 AbortController，導致長連接無法中斷。因此 Ollama 使用**原生 fetch** 而非 OpenAI SDK：

```typescript
private async embedWithNativeFetch(payload: any, signal?: AbortSignal): Promise<any> {
  const endpoint = this._baseURL.replace(/\/$/, "") + "/embeddings";
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
    body: JSON.stringify(payload),
    signal,
  });
}
```

### 5.6 Auto-Chunking

當收到"context length exceeded"錯誤時，自動觸發 `smartChunk()` 將文件分段、各别 embed、最後取平均：

```typescript
if (isContextError && this._autoChunk) {
  const chunkResult = smartChunk(text, this.model);
  const chunkEmbeddings = await Promise.all(
    chunkResult.chunks.map(chunk => this.embedSingle(chunk, task, depth + 1, signal))
  );
  // Average pooling
  const avgEmbedding = chunkEmbeddings.reduce((sum, e) => {
    for (let i = 0; i < e.length; i++) sum[i] += e[i];
    return sum;
  }, new Array(this.dimensions).fill(0))
    .map(v => v / chunkEmbeddings.length);
}
```

**FR-03 保護**：若 `smartChunk` 只產生一個 chunk 且大小接近原文的 90%，視為無效，使用 `STRICT_REDUCTION_FACTOR = 0.5` 強制截斷以確保進度。

### 5.7 Task-Aware API

```typescript
embedQuery(text)    → task = _taskQuery（預設 undefined）
embedPassage(text)   → task = _taskPassage（預設 undefined）
embedBatchQuery/batchPassage → 批次版本
```

### 5.8 Timeout 保護

所有單次 embedding 皆有 10 秒 global timeout：
```typescript
private withTimeout<T>(promiseFactory, externalSignal?) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), EMBED_TIMEOUT_MS); // 10000
  // merge external + internal abort signals
}
```

---

## 六、錯誤處理與 Fail-Open 設計

Plugin 大量採用 **fail-open** 策略，避免驗證/去重/萃取的失敗阻斷核心功能：

| 情境 | 策略 |
|------|------|
| Dupe pre-check 失敗 | 繼續 store，不阻斷寫入 |
| Auto-capture 萃取失敗 | fallback 到 regex capture |
| Tier maintenance 失敗 | 僅 warn，不影響 recall |
| Noise bank init 失敗 | 降級但繼續啟動 |
| Reflection generation 全部失敗 | 寫入 fallback text + triage entry |

---

## 七、Tool Registration 結構

```typescript
export function registerAllMemoryTools(api, context, options) {
  // Core（始終啟用）
  registerMemoryRecallTool(api, context);
  registerMemoryStoreTool(api, context);
  registerMemoryForgetTool(api, context);
  registerMemoryUpdateTool(api, context);

  // Management（可選）
  if (options.enableManagementTools) {
    registerMemoryStatsTool(api, context);
    registerMemoryDebugTool(api, context);
    registerMemoryListTool(api, context);
    registerMemoryPromoteTool(api, context);
    registerMemoryArchiveTool(api, context);
    registerMemoryCompactTool(api, context);
    registerMemoryExplainRankTool(api, context);
  }

  // Self-improvement（預設啟用）
  registerSelfImprovementLogTool(api, context);
  if (options.enableManagementTools) {
    registerSelfImprovementExtractSkillTool(api, context);
    registerSelfImprovementReviewTool(api, context);
  }
}
```

每個工具的 execute 函式結構一致：
1. 解構參數 + 賦予預設值
2. Scope 存取檢查
3. 業務邏輯
4. Try-catch 包裝，回傳 `{ content, details }` 或 error 格式

---

## 八、關鍵設計特點摘要

| 特點 | 實作位置 |
|------|---------|
| Idempotent register | `index.ts` `_initialized` guard |
| Non-blocking startup | `registerService().start()` fire-and-forget |
| Fire-and-forget hooks | `agent_end` auto-capture |
| Multi-key round-robin | `embedder.ts` `nextClient()` |
| Ollama native fetch | `embedder.ts` `embedWithNativeFetch()` |
| Auto-chunking | `embedder.ts` `embedSingle()` context error handling |
| LRU embedding cache | `embedder.ts` `EmbeddingCache` |
| Governance-aware recall | `before_prompt_build` filters |
| Redundancy dedup | `recallHistory` Map per session |
| Error signal dedup | SHA256 signature-based `signatureSet` |
| Fail-open everywhere | try-catch with continue |
| TypeBox schema | `tools.ts` 所有工具 |
| Scope isolation | `scopeManager` + `resolveScopeFilter` |
| Dual-write mirror | `mdMirror` + `store.store()` |
| Compaction cooldown | `.compaction-state.json` timestamp check |
