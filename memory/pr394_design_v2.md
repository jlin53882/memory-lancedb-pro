# Issue #394 / #446 — Envelope Metadata Leak 設計方案

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒

---

## 一、問題背景

`stripLeadingInboundMetadata()` 無法完整過濾 channel/system envelope 文字，導致以下文字被寫入 LanceDB 造成記憶污染：

- `System: [timestamp] Channel[account] DM...`
- `Conversation info (untrusted metadata): ...`
- `Sender (untrusted metadata): ...`
- `<<<EXTERNAL_UNTRUSTED_CONTENT...`

**根本原因**：三層防線皆不完整
1. `noise-filter.ts` — 完全缺少 envelope patterns
2. `auto-capture-cleanup.ts` — Regex 只匹配 `System: Exec completed/failed`，漏掉多數格式
3. `smart-extractor.ts` 的 `stripEnvelopeMetadata()` — Regex 脆弱，格式變異即失效
4. `memory_store` tool — 完全沒有 envelope 過濾

---

## 二、現有程式碼分析結論

### 現有 stripEnvelopeMetadata() 的 Regex 盲點

從 `smart-extractor.ts` 分析，現有 Step 1 只匹配：
```
/^System:\s*\[[\d\-: +GMT]+\]\s+\S+\[.*?\].*$/gm
```

這要求精確格式：`System: [timestamp] ChannelName[account] ...`

**漏網格式**：
- `System: [2026-04-02 12:00 GMT+8] Feishu[default] DM | ou_xxx`
- 格式略有不同的任何 System 行
- 無 code block 包裝的 envelope

### 借鑒 Claude Code 的設計

Claude Code 的 `normalizeAutoCaptureText`（類似）採用：
- 明確的 sentinel 列表（不走 regex 寬鬆匹配）
- 結構化解析（而非字串替換）
- 多層過濾（不依賴單一 regex）

---

## 三、方案比較

### 方案 A：三層 Defense in Depth（原提案）

| 層 | 做法 | Pros | Cons |
|----|------|------|------|
| Layer 1 | `noise-filter.ts` 新增 `ENVELOPE_NOISE_PATTERNS` | 低風險、不影響既有流程 | 只是額外保護，主要防線不在這 |
| Layer 2 | `normalizeAutoCaptureText()` 加強 strip 後殘留檢查 | 直接堵源頭 | 可能影響正常 strip 邏輯 |
| Layer 3 | `smart-extractor.ts` 的 `stripEnvelopeMetadata()` 強化 | 最後安全閥 | 脆弱的 regex 仍是隱憂 |
| Layer 4 | `memory_store` tool 加入 envelope 檢查 | 完整覆蓋 | 需避免誤殺正常 JSON 內容 |

**總評**：架構正確，但實作細節需更保守。

### 方案 B：結構化 Parser（推薦）

不走 regex 匹配，改用結構化解析：

```typescript
// 1. 先用現有 stripLeadingInboundMetadata() 移除已知的 sentinel blocks
// 2. 殘留文字中若有以下關鍵字，回傳 null（不放過）：
//    - "System:" 出現在行首
//    - "Conversation info" 或 "Sender" + "(untrusted metadata)"
//    - "<<<EXTERNAL_UNTRUSTED_CONTENT"
// 3. 用 case-insensitive + 可變空白（\s+）匹配

const ENVELOPE_SENTINELS = [
  /^System:\s*/im,
  /^Conversation info\s*\(/im,
  /^Sender\s*\(/im,
  /^<<<EXTERNAL_UNTRUSTED_CONTENT/im,
];

function hasEnvelopeSentinel(text: string): boolean {
  return ENVELOPE_SENTINELS.some(p => p.test(text));
}
```

| Pros | Cons |
|------|------|
| 結構化解析比 regex 更可靠 | 需修改現有 strip 邏輯 |
| 可覆蓋所有變異格式 | 需要完整測試案例 |
| 不影響正常 strip 流程 | - |

### 方案 C：雙軌寫入過濾（memory_store 最保守做法）

針對 `memory_store` tool，採用「先標記、再過濾」：

```typescript
// memory_store 寫入前：
function sanitizeMemoryInput(text: string): string {
  // 只移除明確的 envelope block，不碰其他內容
  return text
    .replace(/<<<EXTERNAL_UNTRUSTED_CONTENT[\s\S]*?END EXTERNAL_UNTRUSTED_CONTENT>>>/gi, '')
    .trim();
}
```

| Pros | Cons |
|------|------|
| 最小破壞性：只移除明確的 envelope block | 邊界 case 仍需定義 |
| 不影響 auto-capture 流程 | 複雜格式可能漏網 |

---

## 四、最終推薦方案

**採用「方案 B + C 結合」：**

### Step 1：強化 Layer 2（normalizeAutoCaptureText）

在 `auto-capture-cleanup.ts` 的 `normalizeAutoCaptureText` 最後加入殘留檢查：

```typescript
// stripLeadingInboundMetadata() 之後
const stripped = stripLeadingInboundMetadata(text);
if (!stripped) return null;

// 新增：殘留檢查
const stillHasEnvelope = /^System:\s*/im.test(stripped)
  || /^Conversation info\s*\(/im.test(stripped)
  || /^Sender\s*\(/im.test(stripped)
  || /^<<<EXTERNAL_UNTRUSTED_CONTENT/im.test(stripped);

if (stillHasEnvelope) {
  return null; // 放棄這條，不寫入污染資料
}
```

### Step 2：memory_store 的 envelope 過濾（方案 C）

在 `memory_store` tool 輸入處理加入：

```typescript
function sanitizeStoreInput(text: string): string {
  return text
    .replace(/<<<EXTERNAL_UNTRUSTED_CONTENT[\s\S]*?END EXTERNAL_UNTRUSTED_CONTENT>>>/gi, '')
    .replace(/^System:\s*\[[^\]]*\]\s*/gim, '')
    .trim();
}
```

### Step 3：smart-extractor 的 envelope check（Layer 3 強化）

在 `stripEnvelopeMetadata()` 中加入更寬鬆的 fallback：

```typescript
// Step 4：Fallback — 如果還有疑似 envelope，直接抽出行首到第一個空行的範圍
for (const line of text.split('\n')) {
  if (/^(System|Conversation info|Sender|<<<EXTERNAL)/i.test(line.trim())) {
    // 移除這一行到下一個空行之間的內容
  }
}
```

---

## 五、實作順序建議

| 順序 | 內容 | 理由 |
|------|------|------|
| 1 | Step 1 殘留檢查 | 最簡單、風險最低、立即見效 |
| 2 | Step 2 memory_store 過濾 | 保護直接寫入徑路 |
| 3 | Step 3 extractor 強化 | 最後安全閥 |

**不需要一次做完**，每個 step 都可以獨立測試和部署。

---

## 六、需作者確認的問題

1. 殘留檢查回傳 `null` 會不會造成正常訊息被意外放過？（需設定 minTextLength guard）
2. Feishu 格式的 `System:` 具體長什麼樣子？（需要真實樣本）
3. `memory_store` 的 sanitize 是否只移除 envelope block，不改變其他內容？

---

## 七、測試邊界案例

```typescript
// 必測的邊界 case：
const cases = [
  // 正常內容
  "System: [2026-04-02] This is a normal message", // 不應被視為 envelope
  "I like using system: tab for indentation", // 小寫 system 非行首
  // 污染內容
  "System: [2026-04-02 12:00 GMT+8] Channel[account] DM | ou_xxx",
  "Conversation info (untrusted metadata):\n```json\n{...}\n```",
  "<<<EXTERNAL_UNTRUSTED_CONTENT id=\"xxx\">>>\n...\n<<<END>>>",
  // JSON 正常內容
  "Here is my config: ```json\n{\"key\": \"value\"}\n```", // 不應被移除
];
```
