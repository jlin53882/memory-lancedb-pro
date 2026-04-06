# memory-lancedb-pro 代碼分析報告：Context 正規化與噪音過濾

**分析日期：** 2026-04-02  
**目標模組：** `src/auto-capture-cleanup.ts`、`src/noise-filter.ts`、`src/noise-prototypes.ts`、`src/session-compressor.ts`  
**補充分析：** `src/smart-extractor.ts` 中的 `stripEnvelopeMetadata`

---

## 一、`normalizeAutoCaptureText` — 處理流程分析

### 1.1 核心設計：`stripAutoCaptureInjectedPrefix`

此函式專門處理 **auto-capture 階段由 OpenClaw 注入的元資料前綴**，只對 `role === "user"` 的訊息生效。處理順序如下：

```typescript
export function stripAutoCaptureInjectedPrefix(role: string, text: string): string {
  // 步驟 1：移除 <relevant-memories> XML 標籤區塊
  normalized.replace(/<relevant-memories>\s*[\s\S]*?<\/relevant-memories>\s*/gi, "")

  // 步驟 2：移除 [UNTRUSTED DATA]...[END UNTRUSTED DATA] 區塊
  normalized.replace(/\[UNTRUSTED DATA[^\n]*\][\s\S]*?\[END UNTRUSTED DATA\]\s*/gi, "")

  // 步驟 3：移除 Session Reset 前綴（如 "/new" 或 "/reset" 觸發的系統訊息）
  normalized = stripAutoCaptureSessionResetPrefix(normalized)

  // 步驟 4：移除 labeled metadata 區塊（最多執行 6 次直到收斂）
  normalized = stripLeadingInboundMetadata(normalized)

  // 步驟 5：移除 Discord/Telegram addressing prefix（@mention）
  normalized = stripAutoCaptureAddressingPrefix(normalized)

  // 步驟 6：再次執行步驟 4（防止 addressing prefix 揭露 metadata）
  normalized = stripLeadingInboundMetadata(normalized)

  // 步驟 7：規範化連續換行
  normalized.replace(/\n{3,}/g, "\n\n")
}
```

### 1.2 Channel Metadata 格式處理矩陣

| 格式類型 | 處理方式 | 範例 |
|---------|---------|------|
| `Conversation info (untrusted metadata):` + JSON code block | `AUTO_CAPTURE_INBOUND_META_BLOCK_RE` 正規表達式 | Feishu/Discord 頻道訊息夾帶的 JSON |
| `Sender (untrusted metadata):` + JSON | 同上（共用同一 regex） | 發送者 ID、名稱 |
| `Thread starter (untrusted, for context):` | 同上 | 論串起始訊息 |
| `Replied message (untrusted, for context):` | 同上 | 回覆引用 |
| `Forwarded message context (untrusted metadata):` | 同上 | 轉發訊息上下文 |
| `System: [timestamp] Channel[account] ...` | `AUTO_CAPTURE_SYSTEM_EVENT_LINE_RE` | 平台系統行 |
| `<@USER_ID>` / `@username` addressing | `AUTO_CAPTURE_ADDRESSING_PREFIX_RE` | Discord/Telegram @mention |
| `<relevant-memories>...</relevant-memories>` | Regex 直接移除 | auto-recall 注入的記憶內容 |
| `[UNTRUSTED DATA]...[END UNTRUSTED DATA]` | Regex 直接移除 | untrusted data 區塊 |

### 1.3 收斂機制（防止過度處理）

`stripLeadingInboundMetadata` 採用**最多 6 次迭代**直到文字不再改變為止。這是為了處理以下邊界情況：

- 多個 metadata 區塊連續出現時，單次 replace 無法一次移除乾淨
- Addressing prefix 移除後可能揭露隱藏的第二層 metadata
- 每次迭代後執行 `\n{3,}` → `\n\n` 規範化，防止空行堆積

**注意：** 最終輸出的 `stripAutoCaptureInjectedPrefix` 對 `role !== "user"` 直接返回 `text.trim()`，這意味著**assistant 角色的訊息完全不會被這個正規化流程處理**。

---

## 二、Envelope Leak 分析（#394/#446 關聯）

### 2.1 兩層 Metadata Stripping 架構

本系統存在**兩套獨立的 envelope/metadata 移除機制**，位於不同處理階段：

```
自動擷取階段（auto-capture）:
  normalizeAutoCaptureText() → 只處理 role=user 的注入前綴
      └─→ 移除 <relevant-memories>、UNTRUSTED DATA、metadata sentinels

智慧萃取階段（smart-extractor）:
  stripEnvelopeMetadata() → 處理**對話文字**中的平台 channel envelope
      └─→ 移除 "System: [timestamp] Channel[account]..." 行
      └─→ 移除 labeled metadata + JSON code blocks
      └─→ 移除同時含 message_id + sender_id 的獨立 JSON blocks
```

### 2.2 `stripEnvelopeMetadata` 實作細節（`smart-extractor.ts:72`）

```typescript
export function stripEnvelopeMetadata(text: string): string {
  // 1. 移除 "System: [YYYY-MM-DD HH:MM:SS GMT+N] Channel[account] ..." 行
  cleaned = text.replace(/^System:\s*\[[\d\-: +GMT]+\]\s+\S+\[.*?\].*$/gm, "")

  // 2. 移除 labeled metadata sections + JSON code blocks
  cleaned = cleaned.replace(
    /(?:Conversation info|Sender|Replied message)\s*\(untrusted[^)]*\):\s*```json\s*\{[\s\S]*?\}\s*```/g, ""
  )

  // 3. 移除同時含 message_id + sender_id 的 JSON blocks（獨立存在時）
  cleaned = cleaned.replace(
    /```json\s*\{[^}]*"message_id"\s*:[^}]*"sender_id"\s*:[^}]*\}\s*```/g, ""
  )

  // 4. 規範化空白行
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n")
  return cleaned.trim()
}
```

### 2.3 測試覆蓋的 Channel 類型

`strip-envelope-metadata.test.mjs` 驗證了以下場景：

| 測試案例 | Channel 類型 | 驗證重點 |
|---------|-------------|---------|
| Feishu DM envelope | Feishu | 完整 metadata 剝離，只留用戶內容 |
| Telegram envelope | Telegram | System: 行格式與 Feishu 不同 |
| Mixed content | 混和 | metadata 剝離但對話內容保留 |
| 僅含 metadata 無用戶內容 | 邊界 | 回傳空字串 |
| 多個 System: 行（多輪對話） | 通用 | 每行都被正確移除 |
| 非 envelope 的 JSON（含 message_id 但無 sender_id）| 邊界 | **不被移除**（regex 需要兩者同時存在）|

### 2.4 現有過濾是否足夠？潛在 Gap 分析

**已覆蓋：**
- ✅ Feishu/Telegram/Discord 的 System: 行（時間戳 + 頻道 + 訊息 ID）
- ✅ 6 種 labeled metadata sentinel blocks（含 JSON）
- ✅ auto-capture 注入的 `<relevant-memories>` 和 UNTRUSTED DATA 標籤

**潛在 Gap：**

1. **Discord thread 特有的 metadata 格式未單獨測試**
   - `thread-starter` / `thread-reply` 格式可能與現有 sentinel 不完全匹配
   - 測試用例中沒有 Discord thread 格式的明確驗證

2. **role=assistant 的 envelope 泄漏**
   - `normalizeAutoCaptureText` 只處理 `role === "user"` 的訊息
   - 如果 assistant 訊息夾帶了 channel envelope（例如 plugin 在 assistant 回覆中夾帶元資料），這些不會被處理

3. **`message_id + sender_id` 的 JSON block 移除門檻過高**
   - 如果 JSON 只含 `message_id`（不含 `sender_id`），regex 不會移除
   - 某些 channel 可能只注入 `message_id`，造成殘留

4. **無 `auto-capture-cleanup` 的單元測試**
   - `auto-capture-cleanup.ts` 沒有對應的 `.test.ts` 檔案
   - `recall-text-cleanup.test.mjs` 測試的是 `tools.ts` 的 `memory_recall` 鉤子，不是 `normalizeAutoCaptureText` 本身

---

## 三、Embedding-based Noise Prototype 分析

### 3.1 架構總覽

`NoisePrototypeBank` 類別提供**語言無關的噪音檢測**，以 cosine similarity 比對輸入向量與已知的噪音原型。

```
初始化：
  BUILTIN_NOISE_TEXTS (14 個多語言原型)
      → embedder.embed() 產生向量
      → 快取於 this.vectors

運行時：
  isNoise(textVector, threshold=0.82)
      → 與所有原型計算 cosine similarity
      → 任一 ≥ threshold → 回傳 true

反饋學習（LLM 回傳 0 記憶時）：
  learn(textVector)
      → 去重（DEDUP_THRESHOLD=0.95）
      → 加入 bank
      → 達到上限時驅逐最舊的學習原型（保留 built-in）
```

### 3.2 關鍵 Threshold 分析

| Threshold | 數值 | 用途 |
|-----------|------|------|
| `DEFAULT_THRESHOLD` | **0.82** | 判斷是否為噪音（isNoise 的相似度門檻）|
| `DEDUP_THRESHOLD` | **0.95** | 新原型與現有原型的去重門檻 |
| 退化偵測閾值 | **0.98** | 偵測 embedding 模型是否失去區分能力 |

**0.82 的選擇理由：**
- 足够高（避免將正常對話誤判為噪音）
- 足够低（捕捉跨語言的語義相似噪音，如"你还记得吗"和"Do you remember"語義相同但字面差異大）

**退化偵測機制（Degeneracy Check）：**
```typescript
if (this.vectors.length >= 2) {
  const sim = cosine(this.vectors[0], this.vectors[1])
  if (sim > 0.98) {
    // 兩隨機噪音原型的相似度 > 0.98 → 模型不具區分力
    // 停用整個 noise bank（避免全部輸入都被誤判為噪音）
    this._initialized = false
    this.vectors = []
  }
}
```

### 3.3 Built-in 原型分類

| 類別 | 數量 | 範例 |
|------|------|------|
| Recall queries（召回查詢）| 7 | "Do you remember what I told you?" / "你还记得我喜欢什么吗" |
| Agent denials（拒絕回覆）| 3 | "I don't have any information about that" / "我没有相关的记忆" |
| Greetings/boilerplate | 4 | "Hello, how are you doing today?" / "新的一天开始了" |

### 3.4 與 Regex 噪音過濾的互補關係

```
regex 噪音過濾（noise-filter.ts）          embedding 噪音過濾（noise-prototypes.ts）
       │                                          │
       ▼                                          ▼
  快速、確定性                    慢（需要 embedder）、統計性
  可解釋性強                      語言無關、捕捉語義相似性
  維護成本高（需持續更新 pattern）    自動學習新噪音原型
       │                                          │
       └────────── 兩者並行使用，互為備援 ──────────┘
```

---

## 四、Session Compression 觸發條件與演算法

### 4.1 觸發條件

```
compressTexts(texts, maxChars) 在以下情況執行：
  ✅ 當 texts.length === 0 → 立即返回空結果
  ✅ 當 allChars <= maxChars → 返回所有文字（不壓縮）
  ❌ 當 allChars > maxChars → 執行完整壓縮演算法
```

**特徵：** 純基於字元數 budget，**不是**基於訊息數量或時間。這意味著：
- 一個很長的 tool call 可以單獨觸發壓縮
- 多個短訊息加起來超過 budget 也會觸發

### 4.2 評分演算法（`scoreText`）

```
評分維度（由高到低）：

1.0  tool_call      — 含 tool_use / tool_result / function_call / memory_* 等關鍵字
0.95 correction     — 含 "actually", "instead", "wrong", "不对", "应该是" 等
0.85 decision       — 含 "confirmed", "approved", "decided", "决定", "確認" 等
0.70 substantive   — 長度 > 80（全英文）/ > 30（含 CJK）的實質內容
0.50 short_question — 含 ? 或中文問號但長度不足
0.40 short_statement — 其他短內容（既非問題也非確認）
0.10 acknowledgment — "ok", "好的", "嗯", "收到", "👍" 等
0.0  empty          — 空字串或純空白
```

**CJK 長度閾值調整：**
- 英文：`substantiveMinLength = 80`
- 中文/日文/韓文：`substantiveMinLength = 30`
- 理由：CJK 字符承載 2-3 倍資訊密度，等同 30 字的 CJK 約等於 80 字的英文

### 4.3 壓縮演算法流程

```
compressTexts(texts, maxChars):
  │
  ├── Step 1：評分所有 texts
  │
  ├── Step 2：若 allChars <= maxChars → 直接返回（不做壓縮）
  │
  ├── Step 3：初始化 selectedIndices = {0, last}（固定保留首尾）
  │
  ├── Step 4：識別 paired texts
  │            tool_call 在 index i → 自動將 i+1 視為配對夥伴
  │
  ├── Step 5：貪心選擇（greedy）
  │            按 score 降序處理 candidates
  │            每選一個 candidate，嘗試一併加入其配對夥伴
  │
  └── Step 6：all-low-score fallback
               若所有 score < minScoreToKeep（預設 0.3）
               且 selectedIndices.size < minTexts（預設 3）
               → 從尾端加入最近 N 筆
```

### 4.4 Paired Texts 保護機制

Tool call 和其結果總是被當作一個單位保留。這避免以下問題：
```
❌ 錯誤：只保留 "tool_use: memory_store"，但預算用盡
       → 萃取的 LLM 無法看到 tool result

✅ 正確：tool_call + tool_result 一起保留或一起丟棄
```

### 4.5 `estimateConversationValue` — 對話價值估算

此函式用於 **Adaptive Throttling**（Feature 7），在萃取前估算對話價值：

| 信號 | 分數 | 說明 |
|------|------|------|
| 有 memory intent（"remember", "记住"）| +0.5 | 這類對話**絕不**被低價值閘門跳過 |
| 有 tool call | +0.4 | 表示有實際操作 |
| 有 correction 或 decision | +0.3 | 強烈的學習信號 |
| 實質內容 > 200 字 | +0.2 | 內容量充足 |
| 多輪對話（>6 texts）| +0.1 | 互動豐富 |

**最高上限：1.0**

---

## 五、Regex 噪音過濾（noise-filter.ts）深度分析

### 5.1 過濾類別

| 類別 | 預設 | Pattern 數量 | 範例 |
|------|------|-------------|------|
| Agent denials | ✅ 過濾 | 8 個 | `I don't have any information` / `no relevant memories found` |
| Meta-questions | ✅ 過濾 | 10+ 個 | `Do you remember?` / `还记得吗` / `如果不知道只回复 none` |
| Session boilerplate | ✅ 過濾 | 5 個 | `^fresh session` / `^HEARTBEAT` / `hello` |
| Diagnostic artifacts | ✅ 過濾 | 3 個 | `query->no explicit solution` |

### 5.2 中文明噪音 Pattern 特色

**Meta-question 的中文 pattern 非常完整：**
- 直接翻譯型：`还记​​得` / `记不记得` / `还记得...吗`
- 指令型：`如果你知道.+只回复` / `如果不知道.+只回复\s*none`
- 混合型：`只回复精确代号` / `只回复\s*none`

這些 pattern 對應一種已知的 prompt injection 手法：用戶透過「如果知道 X 就回覆 Y，否則只回覆 Z」來強迫模型輸出特定格式的干擾資料。

### 5.3 `isNoise` 邏輯

```typescript
export function isNoise(text: string, options: NoiseFilterOptions = {}): boolean {
  if (trimmed.length < 5) return true          // 長度過短 → 直接視為噪音
  if (DENIAL_PATTERNS.some(...)) return true  // 任一 denial pattern 匹配 → 噪音
  if (META_QUESTION_PATTERNS.some(...)) return true  // 任一 meta-question → 噪音
  if (BOILERPLATE_PATTERNS.some(...)) return true     // 任一 boilerplate → 噪音
  if (DIAGNOSTIC_ARTIFACT_PATTERNS.some(...)) return true  // 診斷 artifact → 噪音
  return false
}
```

---

## 六、整合架構圖

```
自動擷取的訊息（role=user）
        │
        ▼
┌─────────────────────────────────┐
│  normalizeAutoCaptureText()     │  ← 只處理 role=user
│  1. <relevant-memories> 移除    │
│  2. UNTRUSTED DATA 區塊移除      │
│  3. Session reset prefix 移除   │
│  4. Metadata sentinels 移除     │
│  5. @mention addressing 移除    │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  session-compressor             │  ← 評分 + 預算裁剪
│  - scoreText() 評估每段價值      │
│  - compressTexts() 裁剪到 maxChars│
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  isNoise() + isNoise() (vector) │  ← Regex + Embedding 二重過濾
│  - Regex: denial/meta/boilerplate│
│  - Embedding: 語義相似度比對     │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  stripEnvelopeMetadata()        │  ← 平台 channel envelope 移除
│  (smart-extractor.ts)           │  ← 萃取 LLM 看到乾淨文字
└─────────────────────────────────┘
        │
        ▼
    萃取 LLM（smart extractor）
```

---

## 七、建議與發現

### 7.1 已確認的優點

1. **多層次 defense in depth**：regex + embedding + envelope stripping 三層互補
2. **CJK 友好**：自動偵測 CJK 字符並調整長度閾值（30 vs 80）
3. **收斂機制**：metadata 移除使用 6 次迭代直到穩定
4. **退化偵測**：embedding noise bank 有機制偵測並停用不具區分力的模型
5. **配對保護**：tool call + result 永遠被視為一個單位

### 7.2 待確認事項

1. **無 `auto-capture-cleanup.ts` 單元測試** — 建議補充，防止未來重構破壞
2. **role=assistant 的 envelope 處理** — 需確認是否真的不存在此場景
3. **Discord thread 特有格式** — 需更多測試案例覆蓋
4. **#394/#446 具體背景** — 本次分析未在程式碼或對話歷史中找到這兩個 issue 編號的具體內容

### 7.3 關鍵 Threshold 速查表

| Threshold | 數值 | 模組 |
|-----------|------|------|
| Cosine similarity（噪音判斷）| 0.82 | `noise-prototypes.ts` |
| Cosine similarity（去重）| 0.95 | `noise-prototypes.ts` |
| Cosine similarity（退化偵測）| 0.98 | `noise-prototypes.ts` |
| 評分門檻（壓縮保留）| 0.3 | `session-compressor.ts` |
| CJK 實質內容最低長度 | 30 字 | `session-compressor.ts` |
| 英文實質內容最低長度 | 80 字 | `session-compressor.ts` |
| 最大學習原型數 | 200 | `noise-prototypes.ts` |
