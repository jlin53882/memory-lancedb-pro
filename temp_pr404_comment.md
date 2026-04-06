## CI 分析：此 PR 的 FTS 修正與 CI 失敗無關

### CI 失敗的真正原因

本次 CI 失敗的是 `cli-smoke` job 中的 `plugin-manifest-regression.test.mjs` 測試，錯誤位於第 155 行：

```
AssertionError [ERR_ASSERTION]: sessionMemory should stay disabled by default
+ actual - expected
+ [AsyncFunction: appendSelfImprovementNote]
- undefined
```

這是 upstream `master` 分支的 **selfImprovement regression bug**，與本 PR 修改的 `src/store.ts` FTS index 建立邏輯完全無關。

### 觸發原因

測試 config 為 `{ autoRecall: false, embedding: {...} }`（無 selfImprovement block）。

Upstream master 最近有兩個 commit 造成 regression：

| Commit | 內容 |
|--------|------|
| `fix: default selfImprovement.enabled to true when config block omitted...` | 將 selfImprovement.enabled 預設值改為 true，但實作有 bug |
| `fix: use native fetch for Ollama embedding...` | 同時也造成 CI 失敗 |

當 selfImprovement.enabled 預設為 true 時，`appendSelfImprovementNote` 被錯誤地當作 `command:new` hook 註冊，導致 assertion `api.hooks["command:new"] === undefined` 失敗。

### upstream master 的 CI 狀態

master 分支本身的 CI 也處於 failed 狀態（最近兩次 push 都是 failed），確認這是既有問題，不是本 PR 引入的。

### 本 PR 的變更確認

- **變更檔案**：`src/store.ts`（1 行）
- **變更內容**：`Index.fts()` → `Index.fts({ withPosition: true })`
- **目的**：修復 phrase query 所需的 position 資料
- **驗證**：在 `test-pr354` 隔離環境中 30 次迭代、150 個測試 case，100% 成功
- **與 CI 失敗的關聯性**：無（隔離且最小變更）

### 建議

等待 upstream maintainer 修復 master 的 selfImprovement regression 後，本 PR 即可合併。
