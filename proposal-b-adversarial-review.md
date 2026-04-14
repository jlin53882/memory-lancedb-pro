# 對抗式 Review 結果

## 假設驗證

**假設 1（最大漏洞）**：報告將「BM25 neighbor lookup」和「BM25 search」當成同一個東西
- 這是報告最嚴重的概念混淆。`runBM25Search()`（步驟 2）是給用戶Query找相關doc的搜尋引擎；B-2 的 neighbor lookup 是對每個 recall result 做 secondary lookup。兩者輸入/輸出/目的完全不同。報告說「B-2 在步驟 2 的 `Promise.all` 中」是完全錯誤的——BM25 neighbor lookup 是步驟 2 的輸出的**消費者**，不是步驟 2 的一部分。

**假設 2**：衝突 A 的三個方案都基於「neighbor lookup 是對 MMR 輸出做查詢」
- 報告自己都承認「如果是對每個 recall result 做獨立的資料庫查詢，則 MMR 完全不影響」，但立刻又說需要 maintainer 確認。實際上這個假設完全可以自己決定——**B-2 neighbor lookup 的輸入就是每個 recall result 本身**，這是功能需求，不是架構約束。如果 AliceLJY 的意思是要對 MMR 輸出再做一次 BM25 search，那是她的設計有問題，不需要跟著她的錯誤走。

**假設 3**：「B-1 與 B-2 完全獨立」——**這個結論是錯誤的**
- 報告自己說「AliceLJY 先說 B-1 是 B-2 的驗證場，後來又說先做 B-2」。但如果 B-2 用 BM25 找 neighbors，而 B-1 是 BM25-only path，那 B-1 就是唯一驗證 BM25 neighbor lookup 行為的地方。說兩者完全獨立是自我安慰——**B-1 是 B-2 的 smoke test**，不可能完全獨立。

---

## 邏輯一致性問題

**問題 1（致命）**：衝突 D 的 `excludeInactive: true` 建議在邏輯上已經失效
- expiry_filter 在步驟 5，MMR 在步驟 13。B-2 如果在 MMR 之後，expiry_filter 早就執行完了。這個建議的問題在於：**它暗示在 MMR 之後有辦法補救 expired entries 的問題，但實際上 MMR 之後沒有任何 filter 可以改變一個 entry 是否 expired**。真正需要問的問題是：B-2 的 neighbor lookup 本身（無論在 MMR 之前還是之後）是否應該有獨立的 expired check？

**問題 2（致命）**：衝突 B 推薦方案 A（只做 hybrid）可能是錯誤的結論
- 報告推薦「只實作 hybrid path」，理由是「符合 scope 精簡原則」。但如果 `vectorOnlyRetrieval()` 和 `bm25OnlyRetrieval()` 是真實存在的使用情境，只做 hybrid 就等於讓這兩個功能退化成 beta feature。如果 B-2 的 neighbor lookup 用 vector search 而非 BM25，vector-only path 完全可以實作 B-2。**「scope 精簡」不是理由，功能完整性才是**。

**問題 3**：衝突 G 兩種說法（AliceLJY vs jlin53882）被當成「可以在 PR 中解決」的問題
- 這不是可以在 PR 中自己決定的問題。這是兩種完全不同的設計方向：在 MMR 之前插入意味著 neighbors 來自完整候選集；在 MMR 之後插入意味著 neighbors 只來自最終精選集。**沒有 maintainer 確認，兩個方案都不能選**。

---

## 遺漏的衝突

**衝突 1（重要）**：Schema 版本與向後相容
- B-2 如果新增 `neighborEnrichment` config flag 和任何新的 return 欄位（report 說 neighbors 不出現在 return 陣列，但 EnrichmentConfig schema 本身是否乾淨？），這些是否需要 schema migration？還有 `hybridRetrieval()` 的 return type 是否改變？任何 consumer 如果依賴目前的 return type，會不會 break？

**衝突 2（重要）**：Neighbors 的重複計分問題
- 如果 B-2 neighbors 被附加到 recall results 作為 context，這些 neighbors 本身會不會在下一輪（用戶下一個 query）被當成獨立的 recall results 被召回？這會造成 neighbors 的 neighbors 的 neighbors... 無限擴展。**沒有 dedup logic 的 neighbor enrichment 就是 memory leak**。

**衝突 3（中等）**：BM25F 權重與 neighbor 語境
- BM25 的 `BM25F` field weights（title, body, tags, url）在 neighbor enrichment 中是否要繼承？如果 neighbor 是從不同於 user query 的 context 被召回，BM25F 的權重設定可能不適用於 neighbor lookup。

**衝突 4（中等）**：與 #453 temporal-awareness 的實際互動——**報告說「可能不重要」是過度樂觀**
- 如果 neighbor 是 dynamic memory（`temporalType: "dynamic"`），decay 速度是 static 的 3x。但 B-2 neighbors 如果是被 MMR 刪掉的相似 item，它們很可能有**相同或相似的 tags/importance**，所以它們的 decay 行為應該相似。但如果 neighbor 是來自於完全不同的 query context，decay 行為可能差異很大。這個問題**需要實際測試**才能確認是否重要。

---

## 實作可行性問題

**問題 1（不可執行）**：B-1 的 `invalidated_at` filter 建議
- 報告說「在 B-1 的 neighbor lookup 中確認 store.bm25Search() 是否有 `invalidated_at` filter。如果沒有，需要在查詢後自己做過濾。」但 report **從未確認過 store.bm25Search() 的 API**。這不是「在 PR 中確認」的問題——如果 store.bm25Search() 根本沒有提供過濾 invalidated entries 的選項，這個功能就無法以建議的方式實作。**需要在上游 PR 提出 API enhancement request**，而不是假設 API 支援。

**問題 2（不可執行）**：衝突 D 的 `excludeInactive` 建議同樣問題
- 同上，store.bm25Search()/vectorSearch() 是否支援 `excludeInactive` 選項從未被確認。如果不支援，整個「在 neighbor lookup 階段過濾 expired entries」的建議就是紙上談兵。

**問題 3（不可執行）**：衝突 C 的 workaround 可能是無效的
- 報告說「下一個 PR 只提給 rwmjhb」。但如果這個 repo 的 PR 審查政策要求**所有 maintainers 的 approval** 才能 merge，那提給 rwmjhb 不提給 AliceLJY 不會繞過問題，只會讓 PR 一直卡在「awaiting review from AliceLJY」的狀態。**這個 workaround 需要確認 repo 的 merge policy**。

---

## 降級建議

**🔴 可以降級為 🟡：衝突 C（權力問題）**
- 如果 repo 允許單一 maintainer merge，則下一個 PR 只提給 rwmjhb 是有效的 workaround。不需要等待「共識機制」的回覆。**但這需要第一個 PR merge 的事實來驗證**。如果第一個 PR 是 rwmjhb 親自 merge 的，權力問題自動消失。

**🔴 可以降級為 🟢：衝突 B 的 vector-only 部分**
- 如果 B-2 的 neighbor lookup 用 vector search（而非 BM25），vector-only path 完全可以實作 B-2，不需要討論「只做 hybrid」。**這是 Q6 的答案決定的，不需要 maintainer 主動確認**。

**🟡 可以降級為 🟢：衝突 F（temporal-awareness）**
- 報告自己都說「可能不重要」，但還是列為中風險。實際上 B-2 neighbors 的 decay 行為只需要跟隨 neighbors 自身的 `temporalType` 欄位，不需要任何特殊處理。如果 neighbors 的 temporalType 欄位是正確設定的（這是上游 B-1 的責任），則不需要在 B-2 中做任何假影。

**🟡 可以降級為 🟢：衝突 G（pipeline 插入點的兩種說法）**
- 如果確認 B-2 的 neighbor lookup 是對每個 recall result 獨立的資料庫查詢（這是功能需求，不是架構問題），則插入點在 MMR 之前或之後都不影響 neighbors 的範圍——因為 MMR 根本管不到獨立的資料庫查詢。此時 AliceLJY 和 jlin53882 的爭論是**假議題**。

---

## 最終優先級清單

| 優先級 | 衝突 | 理由 |
|--------|------|------|
| **🔴 P0** | **衝突 1（Schema 版本）** | 從未被報告提及，可能是最阻塞的問題 |
| **🔴 P0** | **衝突 2（Neighborhood 重複計分）** | 功能性 bug，不解決的話 neighbor enrichment 會造成 memory leak |
| **🔴 P0** | **Q6（neighbor lookup 用 BM25 還是 vector）** | 決定 vector-only path 是否能實作 |
| **🔴 P1** | **衝突 A（MMR）** | 如果 neighbor lookup 是獨立 DB 查詢，則不是問題；需要確認 |
| **🔴 P1** | **衝突 C（權力）** | 取決於 repo merge policy |
| **🟡 P2** | **衝突 D/E（expiry/auto-supersede）** | 取決於 store API 是否支援過濾選項 |
| **🟡 P2** | **衝突 G（插入點爭議）** | 如果 neighbor lookup 是獨立查詢，爭議消失 |
| **🟢 P3** | **衝突 F（temporal-awareness）** | 只要 temporalType 欄位正確，不需要特殊處理 |
| **🟢 P3** | **衝突 H/I/J** | 低風險，無需 blocking |

---

**總結**：這份報告最大的問題是**把太多精力放在「誰說了算」的政治問題上，而忽略了真正的技術阻塞點**。真正需要馬上確認的不是 AliceLJY 或 rwmjhb 的態度，而是：
1. store.bm25Search()/vectorSearch() 的實際 API（是否有 excludeInactive 和 invalidated_at 過濾選項）
2. B-2 的 neighbor lookup 是否是對每個 recall result 獨立的資料庫查詢（這是功能需求，不需要 maintainer 許可）
3. Neighborhood 重複計分的 dedup logic

**政治問題可以等工作繼續推進後自動解決；技術問題不解決就會浪費大量開發時間。**