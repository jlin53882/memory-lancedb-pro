# PR #678 檢討報告 — Issue #675 #676 regex/bulkStore 修復

> 日期：2026-04-21
> PR：fix/issue-675-676-regex-bulk-store
> 結果：28/28 測試 PASS，已推送修復

---

## 🔴 做不好的地方（需要改進）

### 1. Commit `306c1d8` 意外覆蓋了 `invalidateEntries` 修復

**發生了什麼：**
- 上游 PR #669 重構了 `smart-extractor.ts`（引入 `createEntries[]` batch 機制）
- 我的 commit `2d53249` / `b87f858` 在舊版 smart-extractor.ts 基礎上加了 `invalidateEntries[]`
- `306c1d8`（"test: register new test files in CI manifest"）rebase 或 merge 時，以 upstream 版本的 smart-extractor.ts 為準，**把原本包含 `invalidateEntries` 的 112 行修復覆蓋掉了**
- 根本原因：不知道 upstream 已經重構了同一支檔案

**預防規則：**
> **R1｜對「只改 test/manifest」的 commit 保持警覺**
> 當一個 commit 的 message 只提到「test/manifest」，但 stat 顯示改了 `src/*.ts`，要懷疑有東西被覆蓋
> 必須在 commit 前對 stat 顯示的每一個 src 變更做 `git diff --stat` 交叉檢查

> **R2｜Rebase 前確認 upstream 是否有相同檔案的變更**
> 指令：`gh api repos/{owner}/{repo}/commits/{sha} --jq '.files[].filename'`
> 如果 upstream 改了同一個檔案，rebase 前要先看 diff

> **R3｜Rebase/merge 後立刻跑相關測試**
> 不能假設「只改 test/manifest」就沒問題

**這次怎麼發現的：**
跑測試時發現 `supersede-existing-found-bulk.test.mjs` 的 TC-1（SUPERSEDE batch mode）和 TC-4（`invalidateEntries` 內容）失敗

---

### 2. 用 `Promise.all()` 測試並發 `store.store()` 時，ELOCKED 造成 test framework failure

**發生了什麼：**
- TC-6 想用 `Promise.all(entries.map(e => store.store(e)))` 來並發 50 個 store call
- 50 個 call 同時搶 lock，觸發 `ELOCKED` 錯誤
- Node.js test runner 把未處理的 Promise rejection 當成 test failure
- 測試意圖是「測量 timing 並斷言」，但 error 直接讓整個 test 失敗

**預防規則：**
> **R4｜涉及 lock file 的並發測試，error 必須在內部 catch**
> 如果你要測量 timing，就不能讓 error 傳播出去
> 正確做法：`try { ... } catch (e) { if (e.code === 'ELOCKED') { elocked = true } else throw e }`

**修復方式：** 改成 sequential `for...of` 迴圈

---

### 3. Commit message 沒說清楚為什麼 upstream 的測試會 fail

**發生了什麼：**
一開始沒有立即確認 upstream CI 失敗的原因，就先回報「可能是 upstream 問題」
後來確認了：`smart-extractor-branches.mjs:497` 是 upstream PR #669 自己忘記更新測試

**預防規則：**
> **R5｜上報 upstream 問題前，先用 `git log --oneline upstream/master --stat` 確認**
> 不能只靠「測試在 upstream 也 fail」就斷定是 upstream 問題
> 必須找到 upstream 的 commit 確認是誰改的、什麼時候改的

---

## 🟡 維護者提出的 3 個 concerns（需要正面回應）

### Concern 1：handleSupersede batch mode 沒有 invalidate 舊 entry

**維護者說：** 
> 當 batch mode 有現有記錄時，`handleSupersede` 直接 call `store.store()`，繞過了 `createEntries[]` batch，根本沒有 invalidate 舊 entry

**我的回應：**
- 加了 `invalidateEntries[]` 陣列
- `bulkStore(createEntries)` 完成後，iterated `invalidateEntries[]`，每個 call `store.update()`
- `superseded_by` 在 batch mode 故意省略（新 entry ID 未知），用 `supersedes: matchId` 作為 authoritative dedup signal

**學到的：**
> **R6｜「繞過 batch」是嚴重的設計問題**
> 任何新增的 batch 機制，都要檢查所有路徑是否有繞路

---

### Concern 2：測試是 local mock simulation，不是真實整合測試

**維護者說：**
> 用 jiti import 真實程式碼來測，不要用 local mock

**我的回應：**
- 重構 `supersede-existing-found-bulk.test.mjs`：用 `jiti` import 真實 `SmartExtractor`
- 重構 `regex-fallback-bulk-store.test.mjs`：用 `jiti` import 真實 `MemoryStore`
- 重構 `lock-stale-threshold.test.mjs`：用 real `MemoryStore` 測 actual lock timing

**學到的：**
> **R7｜新測試預設要用 jiti import 真實程式碼**
> 只有當需要隔離、控制時間、或無法用真實元件時才用 mock
> Mock 也要確保實作了被測程式碼會呼叫的所有 method（`bulkStore()` 就是被漏掉的）

---

### Concern 3：Scope-filter 測試 mock 缺少 `bulkStore()`

**維護者說：**
> `test/smart-extractor-scope-filter.test.mjs` 的 MockStore 沒有實作 `bulkStore()`

**我的回應：**
加了 `async bulkStore() { return []; }`

**學到的：**
> **R8｜更新現有測試時，要檢查 mock 是否還完整**
> 當被測程式碼加了新 method call，要同步更新 mock

---

## 🟢 做得好的地方（可以重複使用）

### 1. 找到了 upstream CI failure 的根本原因

- `smart-extractor-branches.mjs:497` — upstream PR #669 重構後忘記更新測試
- `import-markdown.test.mjs` — upstream manifest 設定不一致
- 有完整 git log 證據，不是推測

### 2. PR description 更新完整

- 列出 3 個新測試檔案
- 說明每個測試驗證什麼
- 標明測試方法（jiti import 真實程式碼 vs mock）

### 3. 測試覆蓋了 `supersedes` 欄位

- TC-4 驗證了新 entry 的 `supersedes === existingRecord.id`
- TC-5 驗證了 non-temporal category fallback 到 CREATE

### 4. Timing 數據有說服力

- 3×`store.store()` = 600ms+，1×`bulkStore(3)` = 7ms（88×差異）
- 50×`store.store()` = 390ms，1×`bulkStore(50)` = 6ms
- 數據來自真實 MemoryStore，不是 mock

### 5. 錯誤處理有 design note

- `invalidateEntries` loop 的 per-update try-catch
- 記錄了 LanceDB 不支援 atomic bulk update 的限制

---

## 📋 衍生規則清單（下次可重用）

| # | 規則 | 觸發時機 |
|---|------|---------|
| R1 | 對「只改 test/manifest」的 commit 警覺 | stat 顯示 src 檔案被改 |
| R2 | Rebase 前確認 upstream 相同檔案變更 | 任何 rebase 前 |
| R3 | Rebase/merge 後立刻跑相關測試 | rebase/merge 完成後 |
| R4 | Lock file 並發測試，error 內部 catch | 測試涉及 `ELOCKED` |
| R5 | 上報 upstream 問題前先 git log 確認 | 聲稱某 fail 是 upstream 造成 |
| R6 | Batch 機制上線後檢查所有繞路徑 | 新 batch 機制實作完成 |
| R7 | 新測試預設用 jiti import 真實程式碼 | 寫新測試時 |
| R8 | 更新現有測試時檢查 mock 完整性 | 修改被測程式碼後 |

---

## 📊 這次 PR 的實際工作時序

1. 收到維護者 @app3apps review 回饋
2. 確認 upstream CI failure 根本原因（搞錯了一次，後來確認）
3. 重構 3 個測試檔案為 jiti import 真實程式碼
4. 修復 `invalidateEntries` 設計問題
5. PR description 更新（被 James 要求重寫一次）
6. 發現 `306c1d8` 意外覆蓋 `invalidateEntries`，緊急還原
7. 修復 `scope-filter` MockStore 缺少 `bulkStore()`
8. 修復 `lock-stale-threshold` Promise.all ELOCKED 問題
9. 28/28 PASS ✅，force push 完成

**耗時：主要花在「找到 `306c1d8` 破壞了什麼」上面**
