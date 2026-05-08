# Strategy A 實作設計：memory-lancedb-pro 支援 OpenClaw memory-core

> **文件狀態：** v0.2 — Claude 對抗審查後修訂
> **策略：** Strategy A — 完整三階段 Dreaming Engine 實作
> **目標：** 讓 memory-lancedb-pro 成為 OpenClaw 的 official memory-core backend
> **範圍：** 涵蓋 PR #672（完整實作）、PR #650（runtime registration）、Issue #705/#707/#727

---

## 0. 對抗審查後修訂記錄（v0.2）

| 日期 | 審查者 | 發現問題 | 處理方式 |
|------|--------|----------|----------|
| 2026-05-05 | Claude Code（M2.7）| cron 實作 bug：`cronIntervalMs = 60_000` 完全忽略使用者 cron 設定，且 `cronstrue` 不是 scheduling 庫 | 修正為 `CRON_CHECK_INTERVAL_MS = 60_000` + 說明需搭配 `engine.run()` 內部防重複機制；移除 `parseCron` import；註明需要 `node-cron` 或 `cron-parser` 庫 |
| 2026-05-05 | 工具驗證 | `collectExactScope` 不在 master（只在 PR #672）| 文件已說明「從 PR #672 移植」，無需修改，確認設計方向正確 |
| 2026-05-05 | 工具驗證 | `contracts.tools` 14 個名稱已與實際程式碼核對：grep `src/tools.ts` 確認完全一致 | D5 等同通過，文件加註驗證狀態 |
| 2026-05-05 | Claude Code（M2.7）| PR #672 的測試從未通過 CI | 維持 Strategy A，新增「Phase 3 必須先通過 `npm test` 才能 merge」的強制條件 |

---

## 1. 現況分析

### 1.1 封閉的 PR 摘要

| PR | 標題 | 狀態 | 核心內容 | 主要 Blockers |
|----|------|------|----------|---------------|
| **#672** | `feat: dreaming engine with scope isolation` | CLOSED（inactivity） | 三階段 Dreaming Engine（Light/Deep/REM）+ AccessTracker 修復 + `collectExactScope()` | 4 輪 review 未通過；`dreamingTimer` scope bug；測試 suite failures |
| **#650** | `fix: register active runtime and allow dreaming config` | CLOSED（CHANGES_REQUESTED → inactivity） | `registerMemoryCapability()` + `configSchema.dreaming` 區塊 | `registerMemoryCapability` 為 unconditional call，舊版 OpenClaw 會 crash |

### 1.2 相關 Issue 整理

| Issue | 標題 | 關聯性 | 狀態 |
|-------|------|--------|------|
| **#705** | lancedb-pro + OpenClaw 夢境兼容 | 指向 openclaw/#71882（status scan bug） | Open |
| **#707** | agent_end hook 被靜默阻擋 | `allowConversationAccess` 缺失 | PR #727 已修復 manifest |
| **#727** | Hook 權限修復 | 在 plugin manifest 加 `hooks.allowConversationAccess: true` | 已合併 |
| **#577** | Dreaming 策略分析 | 三策略分析（完整/橋接/提示） | 資訊階段 |

### 1.3 五層要件現況

| 層次 | 要件 | 目前狀態 | 備註 |
|------|------|----------|------|
| **L1** | `hooks.allowConversationAccess: true` | ✅ PR #727 已修補 | plugin manifest 宣告 |
| **L1** | `contracts.tools` 宣告（14 tool names） | ❌ 缺少 | OpenClaw 5.2+ 需要 |
| **L1** | `configSchema.dreaming` 區塊 | ⚠️ PR #650 有但未進 master | 需要 feature detection |
| **L2** | `registerMemoryCapability()` + feature detection | ❌ PR #650 有但缺 feature detection | 需要加 `typeof api.registerMemoryCapability === 'function'` guard |
| **L3** | Cron scheduler 驅動 dreaming engine | ❌ PR #672 有但未進 master | 需要完整的 cron 整合 |
| **L4** | OpenClaw 正確讀取 registered runtime status | ❌ #71882 closed unstable | 上游問題，plugin 端無能為力 |
| **L5** | 三階段 Dreaming Engine | ❌ PR #672 有但未進 master | 需要 AccessTracker 修復 |

---

## 2. OpenClaw memory-core Hook 需求分析

### 2.1 需要 `allowConversationAccess` 的 Hooks

根據 OpenClaw plugin architecture，以下 hooks 需要 `allowConversationAccess: true` 才能正常運作：

| Hook | 目前是否使用 | 用途 |
|------|------------|------|
| `agent_end` | ✅ 已使用 | auto-capture 分析對話並寫入 LanceDB |
| `llm_input` | ❌ 未使用 | memory-core 可能需要攔截 LLM 輸入 |
| `llm_output` | ❌ 未使用 | memory-core 可能需要攔截 LLM 輸出 |
| `before_agent_finalize` | ❌ 未使用 | 可能用於最終記憶體 commit |

### 2.2 驗證方式

根據 PR #727 的驗證結果：

> 「在 `openclaw.plugin.json` 加 `hooks.allowConversationAccess: true` 解決 Issue #707」
> Plugin manifest 的 `hooks.allowConversationAccess` 會被 OpenClaw 在 load 時自動授予權限，不需要使用者另外修改 `openclaw.json`。

### 2.3 contracts.tools 宣告（OpenClaw 5.2+）

Plugin 目前暴露 14 個 tools，需要在 `openclaw.plugin.json` 的 `contracts.tools` 宣告：

```json
"contracts": {
  "tools": [
    "memory_archive",
    "memory_compact",
    "memory_debug",
    "memory_explain_rank",
    "memory_forget",
    "memory_list",
    "memory_promote",
    "memory_recall",
    "memory_stats",
    "memory_store",
    "memory_update",
    "self_improvement_extract_skill",
    "self_improvement_log",
    "self_improvement_review"
  ]
}
```

---

## 3. Strategy A 完整實作架構

### 3.1 架構總覽

```
┌─────────────────────────────────────────────────────────────────────┐
│                    memory-lancedb-pro                                │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────────┐                  │
│  │ openclaw.plugin  │    │     index.ts          │                  │
│  │  .json           │    │                       │                  │
│  │                  │    │  - registerMemoryCap   │                  │
│  │  - hooks.*       │    │  - DreamingScheduler  │                  │
│  │  - contracts     │    │  - AccessTracker      │                  │
│  │  - dreaming.*    │    │  - CronRunner         │                  │
│  └──────────────────┘    └──────────┬───────────┘                  │
│                                     │                               │
│                    ┌────────────────┴───────────────┐               │
│                    │     src/dreaming-engine.ts    │               │
│                    │                                │               │
│                    │  Light Sleep → Decay + Tier   │               │
│                    │  Deep Sleep  → Promote to Core │               │
│                    │  REM         → Pattern → Refl  │               │
│                    └────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Layer 1：Plugin Manifest 更新（`openclaw.plugin.json`）

#### 3.2.1 新增 `hooks` 區塊

```json
{
  "id": "memory-lancedb-pro",
  "name": "Memory (LanceDB Pro)",
  "hooks": {
    "allowConversationAccess": true
  },
  "contracts": {
    "tools": [
      "memory_archive",
      "memory_compact",
      "memory_debug",
      "memory_explain_rank",
      "memory_forget",
      "memory_list",
      "memory_promote",
      "memory_recall",
      "memory_stats",
      "memory_store",
      "memory_update",
      "self_improvement_extract_skill",
      "self_improvement_log",
      "self_improvement_review"
    ]
  },
  "configSchema": {
    "properties": {
      "dreaming": {
        "type": "object",
        "additionalProperties": false,
        "description": "Dreaming: periodic memory consolidation and promotion from short-term to long-term storage",
        "properties": {
          "enabled": {
            "type": "boolean",
            "default": false,
            "description": "Enable dreaming memory consolidation cycles"
          },
          "cron": {
            "type": "string",
            "default": "0 3 * * *",
            "description": "Cron expression for dreaming schedule (minute hour day month weekday). Uses server local timezone."
          },
          "verboseLogging": {
            "type": "boolean",
            "default": false,
            "description": "Enable verbose logging for dreaming cycles"
          },
          "phases": {
            "type": "object",
            "additionalProperties": false,
            "description": "Per-phase tuning parameters",
            "properties": {
              "light": {
                "type": "object",
                "properties": {
                  "lookbackDays": { "type": "integer", "default": 3, "minimum": 1 },
                  "limit": { "type": "integer", "default": 100, "minimum": 1 }
                }
              },
              "deep": {
                "type": "object",
                "properties": {
                  "limit": { "type": "integer", "default": 50, "minimum": 1 },
                  "minScore": { "type": "number", "default": 0.6, "minimum": 0, "maximum": 1 },
                  "minRecallCount": { "type": "integer", "default": 2, "minimum": 0 },
                  "recencyHalfLifeDays": { "type": "integer", "default": 30, "minimum": 1 }
                }
              },
              "rem": {
                "type": "object",
                "properties": {
                  "lookbackDays": { "type": "integer", "default": 7, "minimum": 1 },
                  "limit": { "type": "integer", "default": 80, "minimum": 1 },
                  "minPatternStrength": { "type": "number", "default": 0.7, "minimum": 0, "maximum": 1 }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

#### 3.2.2 UI Hints（`uiHints.dreaming.*`）

```json
"dreaming.enabled": {
  "label": "Dreaming Engine",
  "help": "Enable periodic memory consolidation: decay scoring, tier promotion, and pattern-based reflection generation."
},
"dreaming.cron": {
  "label": "Dreaming Schedule",
  "help": "Cron expression for dreaming cycles. Default: 0 3 * * * (daily at 3 AM server time).",
  "advanced": true
}
```

---

### 3.3 Layer 2：Runtime Registration（`index.ts`）

#### 3.3.1 `registerMemoryCapability` 呼叫（Feature Detection）

```typescript
// 在 plugin start() 中，初始化 store 和 retriever 後執行

// Feature detection：檢查 OpenClaw 版本是否支援 registerMemoryCapability
if (typeof api.registerMemoryCapability === 'function') {
  api.registerMemoryCapability({
    runtime: {
      name: "memory-lancedb-pro",
      version: "1.1.0",
      capabilities: ["search", "read", "status", "probe"],
    },
    search: async (query: string, options?: { scope?: string; limit?: number }) => {
      const results = await retriever.retrieve(query, {
        scope: options?.scope,
        maxResults: options?.limit ?? 5,
        now: Date.now(),
      });
      return {
        memories: results.map(r => ({
          id: r.entry.id,
          text: r.entry.text,
          scope: r.entry.scope,
          importance: r.entry.importance,
          score: r.score,
        })),
      };
    },
    readFile: async (memoryId: string) => {
      const entry = await store.get(memoryId);
      if (!entry) throw new Error(`Memory ${memoryId} not found`);
      return {
        id: entry.id,
        text: entry.text,
        metadata: entry.metadata ? JSON.parse(entry.metadata) : {},
      };
    },
    status: async () => {
      const stats = await store.stats();
      return {
        ok: true,
        totalMemories: stats.totalMemories,
        tierCounts: stats.tierCounts,
        lastUpdated: Date.now(),
      };
    },
    probeVectorAvailability: async () => {
      try {
        await embedder.embed("probe");
        return { available: true };
      } catch {
        return { available: false };
      }
    },
  });
  api.logger.info("memory-lancedb-pro: registered as OpenClaw memory runtime");
} else {
  api.logger.debug("memory-lancedb-pro: registerMemoryCapability not available in this OpenClaw version");
}
```

#### 3.3.2 Dreaming Scheduler 初始化

```typescript
// 在 start() 中，plugin 初始化完成後執行

import { createDreamingEngine, mergeDreamingConfig } from "./src/dreaming-engine.js";

// 讀取 dreaming config（合併預設值 + 使用者設定）
const dreamingConfig = mergeDreamingConfig(config.dreaming as Record<string, unknown> | undefined);

if (dreamingConfig.enabled) {
  const engine = createDreamingEngine({
    store,
    embedder: {
      embed: (text: string) => embedder.embedPassage(text),
    },
    fallbackDimensions: config.embedding?.dimensions ?? 1536,
    decayEngine: createDecayEngine(config.decay ?? {}),
    tierManager: createTierManager(config.tier ?? {}),
    config: dreamingConfig,
    log: (msg: string) => api.logger.info(`[dreaming] ${msg}`),
    debugLog: (msg: string) => api.logger.debug(`[dreaming] ${msg}`),
    workspaceDir: resolveWorkspaceDirFromContext(undefined),
  });

  // ── Cron Scheduling ──────────────────────────────────────────────
  // cronstrue 只能把 cron 表達式轉成人類可讀字串，無法用於排程調度
  // 需要另外安裝 cron-parser（node-cron / @node-cron/parser）來計算下次執行時間
  //
  // 建議實作方式（採用 node-cron）：
  //   import nodeCron from "node-cron";
  //   nodeCron.schedule(dreamingConfig.cron, checkDreaming, { scheduled: true });
  //
  // 或自己計算下次執行時間 + setTimeout：
  //   import { parseCronExpression } from "cron-parser";
  //   const next = parseCronExpression(dreamingConfig.cron, { currentDate: new Date() });
  //   const delayMs = next.getTime() - Date.now();
  //   setTimeout(checkDreaming, delayMs);
  //
  // ⚠️ 注意：若 serverless 環境不支援 setInterval（cold start 後計時器可能失效），
  // 應該提供手動 trigger tool（memory_dreaming_run）讓外部 cron job 呼叫。

  // 每分鐘檢查一次是否需要執行（粗粒度，適用 serverless）
  // 真正執行與否由 engine.run() 內部的 lastRunTimestamp 防重複機制控制
  const CRON_CHECK_INTERVAL_MS = 60_000;

  const checkDreaming = async () => {
    // engine.run() 內部檢查：若上次執行距今未超過 cron interval，不重複執行
    const scopes = scopeManager.getAllScopes();
    for (const scope of scopes) {
      try {
        await engine.run(scope);
      } catch (err) {
        api.logger.error(`[dreaming] scope ${scope} failed: ${String(err)}`);
      }
    }
  };

  // 用 closure 管理生命週期，避免 PR #672 的 dreamingTimer scope bug
  // （不直接把 timer 掛在 object 上，而是用 WeakMap 或 module-level var）
  const dreamingTimer = setInterval(checkDreaming, CRON_CHECK_INTERVAL_MS);

  // 在 plugin shutdown 時清理（模組級 cleanup callback）
  // 注意：需要修復 PR #672 中 dreamingTimer scope bug
  // 用 closure 或 WeakMap 而非直接在 object 上設定

  api.logger.info(`memory-lancedb-pro: dreaming engine enabled (cron=${dreamingConfig.cron})`);
}
```

---

### 3.4 Layer 3：AccessTracker 修復（`index.ts`）

**問題：** `AccessTracker` 在 PR #672 中從未 instantiate，導致 `access_count = 0`，tier promotion 系統形同虛設。

**修復：** 在 retriever 每次 `retrieve()` 呼叫後，更新 access metadata：

```typescript
// 在 retriever 模組中，每次 recall 回傳結果時更新 access
// 位置：src/retriever.ts 或 index.ts 的 retrieve wrapper

import { parseAccessMetadata, buildUpdatedMetadata } from "./src/access-tracker.js";

// 在 auto-recall 結果寫入 access metadata
const updatedMetadata = buildUpdatedMetadata(
  existingMetadata,
  { accessCount: currentCount + 1, lastAccessedAt: Date.now() }
);
await store.patchMetadata(memoryId, {
  access_count: currentCount + 1,
  last_accessed_at: Date.now(),
});
```

---

### 3.5 Layer 4：`collectExactScope()` 新增函式（`src/scope-helpers.ts`）

**問題：** `store.list([scope])` 包含 `OR scope IS NULL` 邏輯，導致 null-scope rows 填滿分頁，target-scope rows 餓死。

**修復：** 從 PR #672 移植 `collectExactScope()` 輔助函式：

```typescript
// src/scope-helpers.ts

import type { MemoryStore, MemoryEntry } from "./store.js";

/**
 * Paginate through store.list() results, collecting only exact-scope rows.
 * This prevents starvation when null-scope rows fill the bounded page before
 * target-scope rows appear in the sorted result set.
 */
export async function collectExactScope(
  store: MemoryStore,
  scope: string,
  needed: number,
  pageSize: number,
  debugLog: (msg: string) => void,
): Promise<MemoryEntry[]> {
  const collected: MemoryEntry[] = [];
  let offset = 0;
  let emptyPages = 0;
  const MAX_EMPTY_PAGES = 3;

  while (collected.length < needed) {
    const page = await store.list([scope], undefined, pageSize, offset);
    if (page.length === 0) break;

    let newMatches = 0;
    for (const entry of page) {
      if (entry.scope === scope) {
        collected.push(entry);
        newMatches++;
      }
    }

    if (newMatches === 0) {
      emptyPages++;
      if (emptyPages >= MAX_EMPTY_PAGES) {
        debugLog(`paginate [${scope}]: stopping after ${MAX_EMPTY_PAGES} consecutive pages with no exact-scope matches`);
        break;
      }
    } else {
      emptyPages = 0;
    }

    if (page.length < pageSize) break;
    offset += pageSize;
  }

  debugLog(`paginate [${scope}]: collected ${collected.length} exact-scope entries (needed ${needed})`);
  return collected;
}
```

---

### 3.6 Layer 5：三階段 Dreaming Engine（`src/dreaming-engine.ts`）

**完整程式碼來自 PR #672**，以下為關鍵設計說明：

#### 3.6.1 模組結構

```typescript
// src/dreaming-engine.ts

import type { MemoryStore, MemoryEntry } from "./store.js";
import type { TierTransition, TierableMemory } from "./tier-manager.js";
import type { DecayScore, DecayableMemory } from "./decay-engine.js";
import type { MemoryTier } from "./memory-categories.js";
import { parseSmartMetadata } from "./smart-metadata.js";

// ── Config ─────────────────────────────────────────────────────────

export interface DreamingConfig {
  enabled: boolean;
  cron: string;
  verboseLogging: boolean;
  phases: {
    light: { lookbackDays: number; limit: number };
    deep: { limit: number; minScore: number; minRecallCount: number; recencyHalfLifeDays: number };
    rem: { lookbackDays: number; limit: number; minPatternStrength: number };
  };
}

// ── Factory ────────────────────────────────────────────────────────

export function createDreamingEngine(params: DreamingEngineParams): DreamingEngine {
  return { async run(scope) { ... } };
}
```

#### 3.6.2 三階段實作邏輯

| Phase | 輸入 | 處理邏輯 | 輸出 |
|-------|------|----------|------|
| **Light Sleep** | 近 N 天 memories（`lookbackDays`）| 解析 smart metadata → 計算 decay score → 執行 tier transition |  tier 變更記錄 |
| **Deep Sleep** | Working tier memories | decay scoring + recency boost → 滿足 threshold 者 promote to Core | promote 數量 |
| **REM** | 近 N 天 memories（`lookbackDays`）| 類別頻率分析 + 高重要性類別檢測 → 產生 reflection memory | pattern 清單 + 新增 reflection 數量 |

#### 3.6.3 兩個關鍵 Invariants（MR1 / MR2）

| 代號 | 內容 | 目的 |
|------|------|------|
| **MR1** | 所有 phases filter by scope（每個 phase 都用 `collectExactScope`）| 預防 null-scope starvation |
| **MR2** | dreaming reflections 帶 `metadata.source = "dreaming-engine"` tag | 防止 re-processing loop |

---

## 4. Plugin Config 類型更新

在 `index.ts` 中新增 `DreamingConfig` 類型：

```typescript
interface DreamingPhaseConfig {
  lookbackDays?: number;
  limit?: number;
  minScore?: number;
  minRecallCount?: number;
  recencyHalfLifeDays?: number;
  minPatternStrength?: number;
}

interface DreamingPluginConfig {
  enabled?: boolean;
  cron?: string;
  verboseLogging?: boolean;
  phases?: {
    light?: DreamingPhaseConfig;
    deep?: DreamingPhaseConfig;
    rem?: DreamingPhaseConfig;
  };
}

// 擴展 PluginConfig
interface PluginConfig {
  // ... 現有欄位 ...
  dreaming?: DreamingPluginConfig;
}
```

---

## 5. 檔案異動對照表

| 檔案 | 變更類型 | 內容摘要 |
|------|----------|----------|
| `openclaw.plugin.json` | 修改 | + `hooks.allowConversationAccess: true` + `contracts.tools`（14 tools）+ `configSchema.dreaming` 區塊 + `uiHints.dreaming.*` |
| `src/scope-helpers.ts` | **新增** | `collectExactScope()` 分頁 helper（來自 PR #672）|
| `src/dreaming-engine.ts` | **新增** | 完整三階段 Dreaming Engine（488 lines，來自 PR #672）|
| `src/dreaming-engine.test.ts` | **新增** | 單元測試（564 lines，來自 PR #672）|
| `index.ts` | 修改 | + `registerMemoryCapability()`（feature detection）+ dreaming scheduler 初始化 + AccessTracker instantiation + `DreamingPluginConfig` 類型 |

---

## 6. 風險分析

### 6.1 High Risk

| 風險 | 說明 | 緩解 |
|------|------|------|
| **registerMemoryCapability feature detection 不足** | 不同 OpenClaw 版本可能有不同 API surface | 嚴格用 `typeof` 檢查，只呼叫確認存在的 method |
| **Dreaming cron 在 serverless 環境失效** | `setInterval` 在 serverless cold start 可能失效 | 支援由外部 cron job 觸發（透過 tool call `memory_dreaming_run`） |
| **REM phase 產生無效 reflection** | pattern detection 準確度依賴 `minPatternStrength` | 提供合理的預設值（0.7）+ ui hint 警告 |

### 6.2 Medium Risk

| 風險 | 說明 | 緩解 |
|------|------|------|
| **Deep Sleep promote 造成 importance inflation** | 每次 promote 提升 20% importance，可能超過 1.0 | `Math.min(1.0, entry.importance * 1.2)` 上限 cap |
| **`collectExactScope` pageSize 設定** | 固定 `limit * 2` 可能導致過多記憶體使用 | 限制單次查詢最多 200 筆 |
| **測試 suite failures（PR #672 的未解問題）** | PR #672 的測試從未通過 CI | 新 PR 必須先通過 `npm test`，單元測試隔離驗證 |

### 6.3 Low Risk

| 風險 | 說明 | 緩解 |
|------|------|------|
| **LLM embedding failure 導致 REM reflection 失敗** | `embedder.embed()` 可能因網路問題失敗 | try/catch 包住，failure 不阻斷整體 dreaming cycle |
| **scopeManager.getAllScopes() 仍返回靜態 scopes** | PR #672 修復了 `getAllScopes()`，但 master 沒有 | 需要確認 scopeManager 的實作是否已涵蓋動態 agent scopes |

---

## 7. 測試計畫

### 7.1 單元測試

| 測試檔 | 覆蓋範圍 |
|--------|----------|
| `src/dreaming-engine.test.ts`（新增）| Light/Deep/REM 三階段核心邏輯、`collectExactScope`、MR1/MR2 invariants |
| `src/scope-helpers.test.ts`（新增）| `collectExactScope` 邊界條件（空結果、null-scope、pagination） |
| `index.ts`（現有修改）| feature detection 分支、`mergeDreamingConfig` 合并邏輯 |

### 7.2 整合測試

| 測試 | 驗證目標 |
|------|----------|
| `test/openclaw-host-functional.mjs` | OpenClaw gateway 能正確 load plugin + 執行 hooks |
| `npm test` | 全 suite 通過（包括 `test/dreaming-engine.test.ts`）|

### 7.3 回歸測試

按照 `docs/openclaw-integration-playbook.md` Section 8 的 Regression Matrix 執行。

---

## 8. 實作順序建議

```
Phase 1：Manifest + AccessTracker（風險最低，立刻可做）
  └─ openclaw.plugin.json: hooks + contracts.tools + dreaming schema
  └─ index.ts: AccessTracker instantiation
  └─ 新增 src/scope-helpers.ts

Phase 2：Runtime Registration（已有參考，難度中等）
  └─ index.ts: registerMemoryCapability with feature detection

Phase 3：Dreaming Engine（最高風險，需要最多測試）
  └─ 新增 src/dreaming-engine.ts（完整移植 PR #672）
  └─ 新增 test/dreaming-engine.test.ts
  └─ index.ts: DreamingScheduler wiring
  └─ 確認 npm test 全suite 通過後才能 merge
```

---

## 9. 依賴 OpenClaw 上游的事項

| 項目 | 說明 | 目前狀態 |
|------|------|----------|
| **#71882（Status scan bug）| OpenClaw 的 status scan 在問 registered runtime 前就返回 null | PR #71882 closed (unstable)，未 merged |
| **OpenClaw 5.2+ `contracts.tools`** | 確認 14 tool names 的 contracts 格式 | ✅ 已驗證：grep `src/tools.ts` 確認 14 個名稱與實際程式碼一致 |
| **`llm_input`/`llm_output` hooks** | 可能需要這些 hooks 支援完整的 memory-core 功能 | 待確認 |
| **Cron scheduling 庫** | `cronstrue` 只能用來顯示人類可讀 cron，無法用於排程 | 需額外安裝 `node-cron` 或 `cron-parser` |

---

## 10. 新增專案依賴

```json
{
  "dependencies": {
    "node-cron": "^3.0.0"
  }
}
```

或使用：

```json
{
  "dependencies": {
    "cron-parser": "^4.9.0"
  }
}
```

---

## 11. 預估工作量

| 階段 | 檔案 | 新增行數 | 修改行數 |
|------|------|----------|----------|
| Phase 1 | `openclaw.plugin.json` | +120 | ~0 |
| Phase 1 | `src/scope-helpers.ts`（新）| ~80 | 0 |
| Phase 1 | `index.ts`（AccessTracker）| 0 | ~30 |
| Phase 2 | `index.ts`（registerMemoryCapability）| 0 | ~60 |
| Phase 3 | `src/dreaming-engine.ts`（新）| ~490 | 0 |
| Phase 3 | `test/dreaming-engine.test.ts`（新）| ~560 | 0 |
| Phase 3 | `index.ts`（scheduler wiring）| 0 | ~50 |
| **總計** | | **~1250** | **~140** |

---

*文件版本：v0.2 | 經 Claude 對抗審查（M2.7）| 待：James 確認 → 進入實作*
