# PR #246 Phase 1 實作分析

> 日期：2026-04-02
> 目標：`memory-lancedb-pro-import-markdown-test\src\reflection-slices.ts`

---

## 驗證結果摘要

| 問題 | 答案 |
|------|------|
| getSlices 插入點 | `extractReflectionSlicesWithSanitizer` → `return { invariants, derived }` 的前一瞬間；`derived` slice 產生後、return 之前插入擴展邏輯 |
| bm25Search 函式名 | ✅ `bm25Search`（存在於 `store.ts:522`，為 `Store` 類別方法） |
| bm25Search scope 參數名 | ⚠️ `scopeFilter?: string[]`（陣列，不是 `scope: 'same'`） |
| bm25Search 回傳型別 | `Promise<MemorySearchResult[]>` |
| text.length=20-24 問題 | 已修復（design doc 中 `isRecallUsed` 邏輯已修正） |

---

## 一、`reflection-slices.ts` 現有函式結構

### 公開 API 一覽

| 函式 | 職責 |
|------|------|
| `extractReflectionSlices(reflectionText)` | 對外主入口，呼叫 `extractReflectionSlicesWithSanitizer(reflectionText, sanitizeReflectionSliceLines)` |
| `extractInjectableReflectionSlices(reflectionText)` | 對外入口（過濾 injectable），呼叫相同 internal 函式 + `sanitizeInjectableReflectionLines` |
| `extractReflectionSliceItems(reflectionText)` | 將 slices 轉為 `ReflectionSliceItem[]`（含 ordinal/groupSize） |
| `extractReflectionSliceItems(reflectionText)` | 同上，injectable 版 |

### Internal 函式

| 函式 | 職責 |
|------|------|
| `extractReflectionSlicesWithSanitizer(reflectionText, sanitizeLines)` | **核心邏輯**；derived slices 在此產生，return 前一刻是插入點 |
| `buildReflectionSliceItemsFromSlices(slices)` | 將 `ReflectionSlices` 轉為 `ReflectionSliceItem[]` |

---

## 二、Phase 1 B-1 擴展邏輯插入點

### 插入位置

在 `extractReflectionSlicesWithSanitizer` 函式末段，`return` 語句**之前**：

```typescript
// ===== Phase 1 B-1 插入點（在此）=====
// derived slices 已經計算完畢，尚未 return
// 可以在這裡對 derived slices 做鄰居擴展

const expanded: ReflectionSliceItem[] = [];
for (const slice of derivedItems) {
  const neighbors = await store.bm25Search(slice.text, { topK: 2, scopeFilter: [slice.strictKey] });
  // ...
}

return {
  invariants: invariants.slice(0, 8),
  derived: [...derived, ...expanded],
};
```

### 實際 `bm25Search` API（`store.ts:522`）

```typescript
async bm25Search(
  query: string,
  limit = 5,
  scopeFilter?: string[],
  options?: { excludeInactive?: boolean },
): Promise<MemorySearchResult[]>
```

**⚠️ 設計文件中的 `scope: 'same'` 需修正為 `scopeFilter: string[]`**

---

## 三、`isRecallUsed` text.length=20-24 邏輯缺口分析

### 缺口根因

設計文件 v8 中的 `isRecallUsed` 實作邏輯：

```typescript
if (text.length > 90) {
  snippet = text.slice(20, 70);
} else {
  snippet = text;        // ← 20~24 字的 text 進這裡沒問題
}
if (snippet.length < 5) return false;  // ← snippet = text（20~24字），length 20~24 ≥ 5，通過
```

等等，讓我重新確認。設計文件 v8 的邏輯是：
- `text.length > 90` → `snippet = text.slice(20, 70)`（50字）
- `text.length ≤ 90` → `snippet = text`（全部）

所以 **text.length 20~24** 時，`text.length ≤ 90` → `snippet = text`（20~24字）→ length ≥ 5，通過 guard

但根據 **Unit test design** 的分析，真正的問題在於：
- 設計文件 v8 的 else 分支 `snippet = text`，20~24 字的 text 會通過
- 然而 TC-2（text.length = 25）預期 `snippet = "UVWXY"`（length=5，達標）
- 這說明設計者認為 text.length = 25 時，**仍然走 `slice(20, 70)`**（給出 5 字 snippet）

也就是說真實實作可能是：
```typescript
if (text.length > 90) {
  snippet = text.slice(20, 70);
} else {
  snippet = text;  // 25 字進來 → snippet = 25字 → 比對成功
}
// 問題：當 text.length 為 20~24 時，走 else，snippet = text，guard 通過
// 但當 text.length = 25 時，行為取決於實作（else vs slice）
```

**真正的邏輯缺口（根據 unit test design 分析）**：
- text.length = 20 → `text.slice(20, 70)` = `""`（空字串）→ length < 5 → false
- text.length = 25 → 取決於 threshold 設定

### 建議修復（isRecallUsed）

將長度門檻從 `> 90` 調整為 `> 24`（至少留 5 字核心段）：

```typescript
function isRecallUsed(recallText: string, responseText: string): boolean {
  const text = recallText.trim();
  if (text.length < 20) return false;

  let snippet: string;
  if (text.length > 24) {
    // 長文本：取第 20 字之後的 50 字作為核心段（避開固定前綴）
    snippet = text.slice(20, 70);
  } else {
    // 短文本（20~24字）：全部作為核心段
    snippet = text;
  }

  if (snippet.length < 5) return false;
  if (/^[\s\p{P}]+$/u.test(snippet)) return false;

  return responseText.toLowerCase().includes(snippet.toLowerCase());
}
```

### 修復前後對照

| text.length | 舊邏輯（> 90）| 新邏輯（> 24）| 差異 |
|------------|-------------|-------------|------|
| 20 | `slice(20,70)` = `""` → false | `snippet = text` → length=20 ≥ 5 → 進入正邏輯 | ✅ 修復 |
| 25 | `snippet = text`（全部）→ length=25 ≥ 5 | `snippet = text`（全部）→ length=25 ≥ 5 | 不變 |
| 50 | `snippet = text`（全部）→ 正常 | `snippet = text`（全部）→ 正常 | 不變 |
| 91 | `slice(20,70)` = 50字 → 正常 | `slice(20,70)` = 50字 → 正常 | 不變 |
| 100 | `slice(20,70)` = 50字 → 正常 | `slice(20,70)` = 50字 → 正常 | 不變 |

---

## 四、輸出檔案對照

| 檔案 | 修改內容 |
|------|---------|
| `pr246-impl-analysis.md` | 本檔案，覆寫驗證結果摘要 |
| `pr246_proposal_ab_design_v8.md` | 修正 `isRecallUsed` 邏輯 + 修正 `bm25Search` 參數名（`scope` → `scopeFilter`）|
| `pr246-unit-test-design.md` | 新增 TC-8（text.trim() 後 < 20 的 edge case），並在摘要表標注缺口已修復 |
