# Proposal B 對抗式 Review Prompt

你是專業的軟體架構師與 code reviewer。你需要對以下 Proposal B 衝突分析報告進行對抗式 review。

## 審查目標

Proposal B 的衝突分析報告，包含：
- 上游 pipeline 結構
- 3 個高風險衝突（需要 maintainer 確認）
- 4 個中風險衝突
- 3 個低風險衝突
- 實作前置條件檢查清單

## 對抗式 Review 要求

請用繁體中文對這份報告進行對抗式 review，重點：

### 1. 邏輯一致性
- 衝突 A（MMR 衝突）：報告說「B-2 在 MMR 之後，neighbors 會受限於 MMR survivors」，但有沒有可能是 B-2 的 neighbor lookup 是對每個 recall result 獨立的資料庫查詢，而非對 MMR 輸出做查詢？如果是前者，MMR 完全不影響 B-2 的 neighbor 數量？
- 衝突 B（vector-only）：報告推薦方案 A（只實作 hybrid path），但有沒有可能是錯誤的建議？如果 hybrid path 才是主流路徑，這樣的建議是否過度保守？

### 2. 假設驗證
- 報告中哪些假設可能是錯誤的？
- 哪些「可以自己決定」的問題，其實並不能自己決定？

### 3. 遺漏的衝突
- 還有哪些衝突是報告沒有提到的？
- 與 #8111e26（expiry filter）、#452（auto-supersede）、#453（temporal-awareness）的互動，是否有其他被忽略的？

### 4. 實作可行性
- 衝突 D（expiry_filter）中建議的 `excludeInactive: true` 真的有幫助嗎？如果 B-2 在 MMR 之後，expiry_filter 早就執行完了，`excludeInactive` 參數在這個階段是否有意義？
- B-1 的 `invalidated_at` filter 建議：store.bm25Search() 是否有 `excludeInactive` 選項？如果沒有，這個建議是否可執行？

### 5. 衝突 C（權力問題）
- 這個問題真的是「阻塞」嗎？還是其實有 workaround？（例如：下一個 PR 只提給 rwmjhb，不提給 AliceLJY）

### 6. Pipeline 細節
- `hybridRetrieval()` 中，步驟 2 的 `Promise.all` 同時跑 vectorSearch 和 bm25Search，但 B-2 的 neighbor lookup 應該在哪個階段執行？如果在 `fuseResults()` 之後，bm25Search 的結果是否已經被用到？
- BM25 neighbor lookup 和 BM25 search 是同一個東西嗎？有沒有搞混？

## 輸出格式

請用繁體中文輸出，格式：

```
# 對抗式 Review 結果

## 假設驗證
（列出報告中可能錯誤的假設）

## 邏輯一致性問題
（列出邏輯不一致的地方）

## 遺漏的衝突
（列出報告沒提到的問題）

## 實作可行性問題
（列出建議不可執行的點）

## 降級建議
（哪些 🔴 可以降級？哪些 🟡 可以自己決定？）

## 最終優先級清單
（重新評估所有衝突的優先級）
```

請盡量尖銳，不要客氣。這是為了幫 James 節省時間，不是為了安慰他。
