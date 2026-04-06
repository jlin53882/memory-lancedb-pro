# PR #246 測試失敗分析

**分析日期**：2026-04-02  
**Workspace**：`test-pr354`  
**測試檔案**：`test/recall-text-cleanup.test.mjs`

---

## 失敗分析

### 失敗 1 - 位置：第 482 行
- **錯誤訊息**：`TypeError: Cannot read properties of undefined (reading 'handler')`
- **原因**：測試嘗試從 `hooks` 陣列中解構 `{ handler: autoRecallHook }`，但 hooks 可能是空陣列或未定義
- **是否 Phase 1/2/3 造成**：**否**。經查詢 `test-pr354/index.ts`，`api.on("before_prompt_build")` 確實會在 `autoRecall: true` 時註冊鉤子。測試通過代表鉤子註冊正常，此錯誤可能來自**更早的版本**或**測試設定問題**

### 失敗 2 - 位置：第 577 行
- **錯誤訊息**：`AssertionError: 0 !== 1`
- **原因**：`assert.equal(hooks.length, 1)` 期望有 1 個 hook，但取得 0 個
- **是否 Phase 1/2/3 造成**：**否**。此為既有问题——可能是 hook 註冊條件未滿足（如 config 設定不符），或測試 setup 有問題。當前測試通過

### 失敗 3 - 位置：第 633 行
- **錯誤訊息**：`AssertionError: 0 !== 1`
- **原因**：同失敗 2，期望 hooks.length = 1，但取得 0
- **是否 Phase 1/2/3 造成**：**否**。既有问题，當前測試通過

---

## Phase 1 實作關聯檢查

- **`reflection-slices.ts` 在 `test-pr354` 中的存在**：是
- **`reflection-slices.ts` 包含 BM25 expansion**：**否**。搜尋結果為空，該檔案不包含 BM25 相關程式碼
- **Index.ts 中使用 BM25 的位置**：僅存在於 `intent-analyzer.ts` 和 `retrieval-trace.ts`，與 `before_prompt_build` hook 無關

---

## 測試執行結果

```
▶ recall text cleanup
  ✔ removes retrieval metadata from memory_recall content text but preserves details fields (3.433ms)
  ✔ removes retrieval metadata from every rendered memory_recall line (1.0913ms)
  ✔ removes retrieval metadata from auto-recall injected text (380.7485ms)
  ✔ defaults memory_recall to concise output (limit=3, preview text) (0.9751ms)
  ✔ caps summary-mode memory_recall results to 6 even if a larger limit is requested (0.8658ms)
  ✔ allows larger limits when includeFullText=true (0.6431ms)
  ✔ applies auto-recall item/char budgets before injecting context (22.6712ms)
  ✔ auto-recall only injects confirmed non-archived memories (22.36ms)
  ✔ filters USER.md-exclusive facts from memory_recall output (3.4331ms)
  ✔ skips USER.md-exclusive facts in memory_store (1.5341ms)
  ✔ skips startup profile facts in memory_store (1.0907ms)
  ✔ filters USER.md-exclusive facts from auto-recall injected text (21.7728ms)
  ✔ filters legacy addressing memories with non-canonical fact keys (1.4514ms)
  ✔ filters legacy addressing memories from auto-recall injected text (20.2551ms)
  ✔ respects filterRecall=false for memory_recall output (0.9335ms)
✔ recall text cleanup (484.6671ms)
ℹ tests 15
ℹ pass 15
ℹ fail 0
```

---

## 結論

- [x] **全部既有问题，與 Phase 1/2/3 無關**
- [ ] 有關，需要修復

**說明**：所有 15 個測試在 `test-pr354` 中皆通過。這些失敗可能是：
1. 來自更早的 commit 版本，後續已修復
2. 來自不同的測試環境或設定問題
3. Phase 1 的 BM25 expansion 尚未實際影響到 `recall-text-cleanup.test.mjs` 的測試邏輯

**建議**：若要確認這些失敗是否真的存在，請提供具體的 git commit hash 或測試運行的完整錯誤堆疊，以便進一步追蹤。