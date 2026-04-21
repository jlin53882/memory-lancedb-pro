# LEARNINGS.md — 每次對話的學習筆記

---

## 2026-04-21（Lock Stale Threshold 調查與 PR #678 整理）

### ❌ 做不好的事

#### 1. PR #678 墊高時摻入大量不相關的 commit
**問題**：`origin/fix/issue-675-676-regex-bulk-store` 包含了 10 個檔案變更，其中大部分來自墊高時的歷史累積（bulkStore feature、CI fix 等），不是 #675/#676 本身。

**根因**：
- 沒有先確認 PR #678 的 scope 邊界（diff --stat）
- 墊高時貪快，把所有來源的 commit 都放進同一個分支
- 沒有定期 rebase 清理，只增量往上疊

**預防 Rule**：
```
Rule: 墊高前先確認目標 PR 的 actual scope（git diff upstream/master..PR_HEAD --stat）
Rule: 墊高的 commit 應定期 rebase 整理，只保留 PR 必要的變更
Rule: 送出前用 git diff --stat 確認所有變更都與 PR 目的相關
```

#### 2. 對 bulkStore 實作有錯誤假設
**問題**：一開始說「bulkStore 內部是 store.store() loop」，所以 TC-6 担心 1000 entry 會觸發 stale threshold。後來實際看 source code 才發現是單次 `table.add(fullEntries)` batch write。

**根因**：沒有先讀 source code 就凭假设下结论。

**預防 Rule**：
```
Rule: 對程式碼行為有假設時，先讀 source code 確認，再做推論
Rule: 測試設計前，先確認被測試方法的 actual implementation
```

#### 3. 墊高分支來回切換導致狀態混淆
**問題**：今天來回切換了 `pr674_enhanced`、`fix/issue-675-676-regex-bulk-store-v2`、`upstream/master` 等多個分支，最後 James 問「你現在本地上面的是哪個」需要重新確認。

**根因**：沒有在每次切換後更新 active_state。

**預防 Rule**：
```
Rule: 分支切換後，立即更新 active_state_discord.md 記錄當前狀態
Rule: 不在多個分支之間來回跳躍；完成一個任務再切換
```

#### 4. PowerShell heredoc `<<` 語法在 append 模式失敗
**問題**：用 `cat >> file.mjs << 'ENDOFTEST'` 追加內容時，PowerShell 把 `<<` 視為 input redirection operator 而非 heredoc，導致語法錯誤。

**解法**：改用 Python script 寫入檔案。

**預防 Rule**：
```
Rule: 向現有檔案追加內容時，統一用 Python script，避免 PowerShell heredoc 語法問題
Rule: `python script.py` 比 `cat << EOF` 更穩定可靠
```

---

### ✅ 做得好的事

#### 1. 用 diff --stat 確認 PR scope
**做法**：在做任何操作前，先執行 `git diff upstream/master..pr678-upstream --stat`，清楚看到 10 個檔案變更。再針對每個 commit 做 `--stat` 分析，最後確認只有 4 個檔案是 #675/#676 必要的。

**可複用規則**：
```
Rule: 整理 PR 分支前，先用 git diff --stat 確認 actual scope
Rule: 每個 commit 都用 --stat 看影響範圍，確認沒有混入無關變更
```

#### 2. 成功用 cherry-pick 精準重建分支
**做法**：確認只有 2 個必要 commit（`5bd63a3` test、`ca41a73` fix）後，用 `cherry-pick` 從乾淨的 upstream/master 重建乾淨的 PR 分支。

**結果**：從 10 個檔案（607 行刪除）降到 4 個檔案（12 行刪除），精準乾淨。

**可複用規則**：
```
Rule: 整理混乱的分支時，用 cherry-pick 選擇性取用需要的 commit
Rule: 重建分支 = reset 到 upstream/master + cherry-pick 必要 commit
```

#### 3. TC-6 極限測試成功重現 ELOCKED 錯誤
**做法**：寫了 `bulkStore(1000)` 測試，結果：
- `bulkStore(1000)` = **41ms** ✅
- `50xstore.store()` = **ELOCKED** ❌

**價值**：直接用單元測試重現了真實的 `Unable to update lock` 錯誤，James 可以看到明確的 before/after 對比。

**可複用規則**：
```
Rule: 遇到 runtime error 時，設計單元測試重現該錯誤
Rule: 極限測試（N=1000）能清楚展示「為何 bulkStore 比 N×store.store() 安全」
```

#### 4. 在 PR #678 留言說明 lock stale threshold 根因
**做法**：發現 `gh api --body-file` 在 PowerShell 不支援，改用 Python urllib 成功送 comment。

**可複用規則**：
```
Rule: gh api 送 body 失敗時，改用 Python urllib 直接 call GitHub API
Rule: `--input` 而非 `--body-file` 是 gh api 的正確參數
```

#### 5. PR #678 測試覆蓋範圍完整
**結果**：13 個測試，覆蓋：
- TC-1: lock 設定驗證
- TC-2: bulkStore 正確性
- TC-3: 並行 store.store() 行為
- TC-4: lock lifecycle
- TC-5: N vs bulkStore 速度對比（88x 差異）
- TC-6: 1000 entry 極限測試（ELOCKED 重現）

---

### 🔍 維護者相關觀察

#### 1. 維護者對 PR scope 的嚴格要求
**觀察**：James 要求 PR #678 只能包含 #675/#676 相關內容，不能混入墊高時的其他 commit。這反映了 maintainer 對 PR 範圍純淨度的期待。

**教訓**：墊高時就應該乾淨分開，每個 PR 的墊高 commit 不應混入其他來源的變更。

#### 2. Issue #670 vs Issue #675/#676 的區別
**觀察**：
- Issue #670：`Unable to update lock within the stale threshold`（ENOENT from realpath 是錯誤路標）
- Issue #675/#676：regex fallback + handleSupersede 的 N×lock 問題（真正的根因）

James 一開始以為 Issue #670 和 #675/#676 是同一個，後來確認是分開的。

#### 3. PR #678 merge 的合適性
**觀察**：James 選擇把 `lock-stale-threshold.test.mjs` 補進 PR #678（而非獨立成另一個 PR），因為這個測試直接證明 PR #678 的 fix 能解決問題。

**原則**：測試檔案是否放進某個 PR，取決於它是否直接證明該 PR 的 fix 有效性。

---

### 📐 可重複使用的規則（蒸餾）

| # | 規則 | 觸發時機 |
|---|------|----------|
| R1 | 墊高前先確認 PR scope（`git diff --stat`） | 任何 PR 墊高 |
| R2 | 墊高的 commit 應定期 rebase 整理 | 墊高分支累積多時 |
| R3 | 對程式碼行為有假設時，先讀 source code 確認 | 任何實作推論前 |
| R4 | 分支切換後更新 active_state | 每次分支切換 |
| R5 | 追加檔案內容統一用 Python script | 檔案 append 操作 |
| R6 | 整理混亂分支 = reset + cherry-pick | 分支需要清理時 |
| R7 | 遇到 runtime error 設計單元測試重現 | error 調查 |
| R8 | gh api 失敗時用 Python urllib 繞過 | gh api 不支援時 |
| R9 | 測試檔案放哪個 PR：看是否直接證明該 PR fix 有效 | 測試檔 PR 歸屬 |
| R10 | Issue #670（ENOENT）≠ Issue #675/676（lock contention）| 問題歸屬混淆時 |

---

### 📋 這次 Session 的重要技術發現

#### 發現 1：`bulkStore` 是真正的一次性 batch write
```
src/store.ts:
  return this.runWithFileLock(async () => {
    await this.table!.add(fullEntries);  // ← 單次 LanceDB batch
  });
```
不是 loop，是真正的單次 batch write。

#### 發現 2：stale threshold 觸發的完整邏輯鏈
```
正常情境（N=2~5）：regex fallback → bulkStore → 1×lock → 7ms << 10s ✅
極端情境（N=1000）：bulkStore(1000) → 1×lock → 41ms << 10s ✅
並行情境（50×store.store()）：50×lock → ELOCKED ❌
```

#### 發現 3：PR #678 的完整修復範圍
| 檔案 | 修復內容 | Issue |
|------|----------|-------|
| `index.ts` | regex fallback N×`store.store()` → `bulkStore()` | #675 |
| `src/smart-extractor.ts` | handleSupersede bypass → `createEntries.push()` | #676 |

#### 發現 4：TC-5 的速度數據
```
3×store.store() = 615ms  vs  1×bulkStore(3) = 7ms
速度差異：88 倍
Lock 差異：3 次 vs 1 次
```
