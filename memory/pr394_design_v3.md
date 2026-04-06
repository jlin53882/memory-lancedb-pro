# Issue #394 / #446 — Envelope Metadata Leak 設計方案 v3

> ⚠️ **重要更新 2026-04-02**：經分析 #444 PR，確認 `stripEnvelopeMetadata()` 尚未存在（由 #444 即將新增）。本設計調整為 Phase 2 方案，須等 #444 merge 後再實作。
> 日期：2026-04-02
> 狀態：✅ 經源碼交叉驗證

---

## ⚠️ 重要修正（相較於 v2）

本版根據 `memory-lancedb-pro` 源碼驗證，**更正以下 v2 的錯誤描述**：

| v2 錯誤描述 | 實際情況 |
|---|---|
| `stripEnvelopeMetadata()` 存在於 `smart-extractor.ts` | ❌ **不存在**，從未實作 |
| `auto-capture-cleanup.ts` 獨立模組 | ❌ **不存在** |
| `normalizeAutoCaptureText()` 位置不確定 | ✅ **存在**於 `index.ts:806` |
| `stripLeadingInboundMetadata()` 在獨立檔案 | ✅ 在 `index.ts:684` |

---

## 一、現有程式碼驗證結果

### `index.ts` 現有 envelope 處理（已驗證）

**`AUTO_CAPTURE_INBOUND_META_SENTINELS`（index.ts:663）**
```typescript
const AUTO_CAPTURE_INBOUND_META_SENTINELS = [
  "Conversation info (untrusted metadata):",
  "Sender (untrusted metadata):",
  "Thread starter (untrusted, for context):",
  "Replied message (untrusted, for context):",
  "Forwarded message context (untrusted metadata):",
  "Chat history since last reply (untrusted, for context):",
];
```

**🔴 缺口：`System: [...]` 和 `<<<EXTERNAL_UNTRUSTED_CONTENT` 完全不在清單內**

**`stripLeadingInboundMetadata()`（index.ts:684）**
- 只strip出現在**行首**的 sentinel block（`sentinel + ```json block`）
- 若 sentinel 後不是 ` ```json`，則 return original text（不放過，但也不乾淨）

**`stripAutoCaptureInjectedPrefix()`（index.ts:789）**
- 移除 `<relevant-memories>...</relevant-memories>`
- 移除 `[UNTRUSTED DATA...]...[END UNTRUSTED DATA]`
- 呼叫 `stripLeadingInboundMetadata()`
- 呼叫 `stripAutoCaptureAddressingPrefix()`

**`normalizeAutoCaptureText()`（index.ts:806）**
```typescript
function normalizeAutoCaptureText(role: unknown, text: string): string | null {
  if (typeof role !== "string") return null;
  const normalized = stripAutoCaptureInjectedPrefix(role, text);
  if (!normalized) return null;
  if (shouldSkipReflectionMessage(role, normalized)) return null;
  return normalized;  // ← ❌ 沒有二次 envelope 殘留檢查
}
```

### `smart-extractor.ts`（已驗證：無 envelope 邏輯）
- 純 LLM pipeline，無 regex stripping
- 不負責 envelope 過濾

### `noise-filter.ts`（已驗證：無 envelope patterns）
- 4 類 patterns：denial、meta-question、boilerplate、diagnostic artifact
- **Envelope patterns：零**

### `tools.ts` memory_store（已驗證）
- 呼叫 `isNoise()` 擋 greeting/boilerplate/meta-question
- **Envelope 過濾：無**

---

## 二、文字流向圖（已驗證）

```
原始 user message text（含 envelope）
  │
  ▼
normalizeAutoCaptureText(role, text)      ← index.ts:806
  ├─ stripAutoCaptureInjectedPrefix()
  │    ├─ 移除 <relevant-memories> block
  │    ├─ 移除 [UNTRUSTED DATA...] block
  │    ├─ stripLeadingInboundMetadata()   ← 只處理6個sentinel，缺 System: / <<<
  │    └─ stripAutoCaptureAddressingPrefix()
  ├─ shouldSkipReflectionMessage()
  └─ 返回 normalized（若非空）
       │
       ▼
  [送至 smart-extractor 的 LLM extraction]
       │
       ▼
  extractAndPersist() → processCandidate() → store()  ← 已被汙染
```

---

## 三、推薦實作方案（基於驗證的事實）

### Step 1（最小破壞性，立即見效）

**擴充 `AUTO_CAPTURE_INBOUND_META_SENTINELS`**（index.ts:663）

新增 2 個最常見的漏網格式：

```typescript
const AUTO_CAPTURE_INBOUND_META_SENTINELS = [
  // 現有 6 個...
  "Conversation info (untrusted metadata):",
  "Sender (untrusted metadata):",
  "Thread starter (untrusted, for context):",
  "Replied message (untrusted, for context):",
  "Forwarded message context (untrusted metadata):",
  "Chat history since last reply (untrusted, for context):",
  // ✅ 新增
  "System: [",          // ← 截取 "System: [" 作為前綴匹配（contains檢查）
  "<<<EXTERNAL_UNTRUSTED_CONTENT",  // ← 同上
] as const;
```

**注意**：`isAutoCaptureInboundMetaSentinelLine()` 做的是 `=== trimmed` 比對（完全相等），所以要同步修改該函數，或者改用 `includes` 比對。

建議改法：
```typescript
function isAutoCaptureInboundMetaSentinelLine(line: string): boolean {
  const trimmed = line.trim();
  return AUTO_CAPTURE_INBOUND_META_SENTINELS.some((sentinel) =>
    trimmed === sentinel || trimmed.startsWith(sentinel)
  );
}
```

### Step 2（在 normalizeAutoCaptureText 之後加二次檢查）

在 `normalizeAutoCaptureText()` 回傳前，加入殘留 envelope 檢查：

```typescript
function normalizeAutoCaptureText(role: unknown, text: string): string | null {
  if (typeof role !== "string") return null;
  const normalized = stripAutoCaptureInjectedPrefix(role, text);
  if (!normalized) return null;
  if (shouldSkipReflectionMessage(role, normalized)) return null;

  // ✅ 新增：二次 envelope 殘留檢查（不回溯，只檢查normalized結果）
  const residualEnvelope = /^System:\s*\[/im.test(normalized)
    || /^\s*<<<EXTERNAL_UNTRUSTED_CONTENT/im.test(normalized)
    || /^\s*Conversation info\s*\(untrusted metadata\)/im.test(normalized)
    || /^\s*Sender\s*\(untrusted metadata\)/im.test(normalized);

  if (residualEnvelope) {
    _autoCaptureDebugLog(`memory-lancedb-pro: residual envelope detected, skipping`);
    return null;
  }

  return normalized;
}
```

### Step 3（新增 ENVELOPE_NOISE_PATTERNS 到 noise-filter.ts）

```typescript
const ENVELOPE_NOISE_PATTERNS: RegExp[] = [
  /^System:\s*\[/im,
  /^Conversation info\s*\(untrusted metadata\)/im,
  /^Sender\s*\(untrusted metadata\)/im,
  /^<<<EXTERNAL_UNTRUSTED_CONTENT/im,
  /^<<<END EXTERNAL_UNTRUSTED_CONTENT>>/im,
  /^Thread starter\s*\(untrusted, for context\)/im,
  /^Replied message\s*\(untrusted, for context\)/im,
  /^Forwarded message context\s*\(untrusted metadata\)/im,
  /^Chat history since last reply\s*\(untrusted, for context\)/im,
  /^\[Queued messages while agent was busy\]/im,
];
```

在 `isNoise()` 中整合：
```typescript
export function isNoise(text: string, options?: NoiseFilterOptions): boolean {
  // 現有檢查...

  // ✅ Envelope 檢查
  if (options?.includeEnvelope !== false) {
    if (ENVELOPE_NOISE_PATTERNS.some(p => p.test(text))) return true;
  }

  return false;
}
```

### Step 4（memory_store tool 加入 envelope 檢查）

在 `tools.ts` 的 `memory_store` handler 中，isNoise 檢查之後追加：

```typescript
// envelope 殘留檢查
const ENVELOPE_CHECK = /^System:\s*\[/im.test(text)
  || /^\s*<<<EXTERNAL_UNTRUSTED_CONTENT/im.test(text)
  || /^\s*Conversation info\s*\(untrusted metadata\)/im.test(text)
  || /^\s*Sender\s*\(untrusted metadata\)/im.test(text);

if (ENVELOPE_CHECK) {
  return {
    content: [{ type: "text", text: `Skipped: text contains system/metadata envelope artifacts` }],
    details: { action: "envelope_filtered", text: text.slice(0, 60) },
  };
}
```

---

## 四、實作順序建議

| 順序 | 內容 | 風險 |
|------|------|------|
| 1 | Step 1 — 擴充 `AUTO_CAPTURE_INBOUND_META_SENTINELS` | 低（增加匹配範圍，不影響現有邏輯） |
| 2 | Step 3 — noise-filter.ts 新增 ENVELOPE_NOISE_PATTERNS | 低（只新增 patterns，不改行為） |
| 3 | Step 2 — `normalizeAutoCaptureText()` 殘留檢查 | 中（null return 可能影響某些edge case，需測試） |
| 4 | Step 4 — memory_store envelope 檢查 | 低（只針對明確的 envelope 格式） |

---

## 五、邊界測試案例（必測）

| # | 輸入 | 預期行為 | 風險 |
|---|------|----------|------|
| 1 | `"I prefer dark mode"` | ✅ 正常儲存 | CRITICAL：誤擋等於使用者偏好消失 |
| 2 | `"我喜歡用 Tailwind"` | ✅ 正常儲存 | CRITICAL：中文正常訊息 |
| 3 | `"System: [2026-04-02] Hello"` 行首 | ❌ 過濾 | — |
| 4 | `"Hello system: tab key"` 行中 system: | ✅ 正常儲存 | CRITICAL：行中非envelope |
| 5 | `"```json\n{\"key\":\"value\"}\n```"` | ✅ 正常儲存 | MAJOR：程式碼block |
| 6 | `"<<<EXTERNAL_UNTRUSTED_CONTENT...END"` | ❌ 過濾 | — |
| 7 | `"Conversation info (untrusted): ..."` | ❌ 過濾 | — |
| 8 | `"Sender (untrusted metadata): ..."` | ❌ 過濾 | — |

---

## 六、v2 錯誤假設排除清單

以下 v2 提到的做法，經源碼驗證後**無需實作或不可能**：

| v2 提議 | 驗證結論 |
|---|---|
| 修改 `smart-extractor.ts` 的 `stripEnvelopeMetadata()` | ❌ 函數不存在 |
| 修改 `auto-capture-cleanup.ts` | ❌ 檔案不存在 |
| 依賴 Layer 3 pre-extraction envelope check | ❌ 該層不存在，需從頭建立 |

---

## 七、待確認問題（仍需作者回應）

1. `isAutoCaptureInboundMetaSentinelLine()` 的完全相等比對是否改為 `startsWith`？
2. `System:` 只用 `"System: ["` 前綴匹配，是否足夠？（行首 `System:` 後面可能是正常訊息）

---

## 八、假設驗證清單（設計交付前必填）

| 假設 | 狀態 | 驗證方式 |
|------|------|----------|
| `System: [...]` 是最大漏網原因 | ✅ 已確認 | index.ts:663 清單中確實沒有 |
| `<<<EXTERNAL` 從未被偵測 | ✅ 已確認 | 搜尋整個 src 目錄無結果 |
| `normalizeAutoCaptureText` 是進入 LLM 前最後一關 | ✅ 已確認 | index.ts flow 追蹤 |
| noise-filter.ts 的 ENVELOPE patterns 是新增而非修改 | ✅ 已確認 | 現有4類無 envelope |

---

> **檔案位置**：實作頻道 `memory/pr394_design_v3.md`
> **驗證日期**：2026-04-02
> **驗證方式**：直接讀取 `C:\Users\admin\AppData\Roaming\npm\node_modules\memory-lancedb-pro\src\` 下所有相關檔案
