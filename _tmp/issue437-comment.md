## 處理方式

### 分析過程

收到 Issue #437 後，先完整閱讀了相關程式碼：

1. **`index.ts`**（auto-recall hook）— 已有 `<relevant-memories>` envelope，直接在組裝 `prependContext` 的位置加入 `<mode:${recallMode}>` 行
2. **`src/tools.ts`**（memory_recall tool）— 原本沒有 envelope，直接輸出 bullet list
3. **`test/recall-text-cleanup.test.mjs`** — 分析 `extractRenderedMemoryRecallLines()` 的 filter 邏輯，確認 `/^\d+\.\s\[/` 只會通過數字開頭的行，所以在文字區塊前面加任何 metadata 行都不會破壞現有測試

### 為什麼要這樣作

**問題根源**：T5 測試原本斷言輸出包含「Summary mode」indicator，但這個 indicator **從未實作過**——它只存在於測試訊息字串裡。這是設計缺口，不是迴歸。

**兩處都要改**的原因：
- **auto-recall** 回傳 `prependContext`（已有 envelope），需要加 mode 讓 consumer 知道這批記憶是 summary / full / adaptive
- **memory_recall tool** 回傳 `content[0].text`（沒有 envelope），也需要加 mode，否則 T5 無法真正驗證

**選擇 `<relevant-memories>` envelope 內**的原因：
- 符合現有 `<UNTRUSTED DATA>` / `<END UNTRUSTED DATA>` 的 XML-like tag 風格
- `extractRenderedMemoryRecallLines()` 的 filter 會自動忽略它，不破壞現有測試的 line count assertion
- Consumer 可用 `includes("<mode:summary>")` 偵測模式

### 實際修改

| 檔案 | 修改內容 |
|------|---------|
| `index.ts` | `<relevant-memories>` 與 `[UNTRUSTED DATA` 中間加入 `<mode:${recallMode}>` |
| `src/tools.ts` | 輸出包在 `<relevant-memories><mode:X>...</relevant-memories>`，`details` 加 `recallMode` 欄位 |
| `test/recall-text-cleanup.test.mjs` | 3 個測試加 `assert.match(..., /<mode:...>/)` 驗證 mode 存在 |

### 測試結果
所有 18 個測試通過

PR: https://github.com/CortexReach/memory-lancedb-pro/pull/478