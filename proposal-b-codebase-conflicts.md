# Proposal B 與上游最新程式碼衝突分析

> 分析日期：2026-04-09
> 分析者：AI 程式修改助手
> 資料來源：proposal-b-analysis.md、proposal-b-issue-details.md、上游 `memory-lancedb-pro-master/src/retriever.ts`（hybridRetrieval 約 898-1050 行的 pipeline）

---

## 上游 Pipeline 精確順序（hybridRetrieval）

經實測確認，上游 `hybridRetrieval()` 的執行順序為：

```
1.  embedQuery() + buildBM25Query()
2.  Promise.all([runVectorSearch(), runBM25Search()])
3.  fuseResults()                        ← RRF fusion
4.  filter: score >= minScore
5.  filter: !isMemoryExpired()           ← Issue #453 將 expiry filter 移至此（rerank/scoring 之前）
6.  rerankResults()                      ← 若 rerank !== "none"
7.  applyRecencyBoost()
8.  applyImportanceWeight()
9.  applyLengthNormalization()
10. filter: score >= hardMinScore
11. applyDecayBoost() 或 applyTimeDecay()
12. filterNoise()
13. applyMMRDiversity()
14. slice(0, limit)
15. return
```

`vectorOnlyRetrieval()` 和 `bm25OnlyRetrieval()` 架構類似，**亦有獨立的 expiry filter**，位於搜尋結果之後、scoring/boost 之前（與 hybridRetrieval 的步驟 5 位置相同）。

---

## 衝突 1：expiry filter 位置導致 B-2 neighbors 可能無法被找到

### 描述

Issue #453（commit #8111e26，2026-04-05）將 expiry filter 移到 scoring pipeline **之前**（"before rerank/scoring"）。這是上游已合併的變更。

AliceLJY 在 Issue #538 Comment 1（Q2 回答）中說 B-2 應在 **MMR 之後**插入。但若 B-2 在 MMR 之後執行，則：

- B-2 的 neighbors 是透過 `vectorSearch(text, topK=2, scope=same)` 對每個 recall result 做資料庫查詢
- 這些 neighbors 是獨立的 store 查詢結果，並非來自 fusion pipeline
- **但**問題在於：如果某個 recall result 自己本身就是 expired，會在步驟 5 被過濾掉，導致 B-2 根本找不到它的 neighbors（因為 B-2 是對每個「還活著的」recall result 做 neighbor lookup）
- 若 B-2 的實作是「對整個 fusion 结果集做 neighbors lookup」，expired entries 會在步驟 5 被移除，B-2 無法對它們擴展

### 嚴重程度

🟡 **中風險**

### 分析

B-2 的 neighbor lookup 是一次獨立的 `vectorSearch()` 呼叫，對象是每個 recall result（而非整個 fusion 候選池）。因此 expiry filter 只影響「哪些 recall results 有機會被 B-2 擴展」，而非「B-2 找 neighbors 時過濾掉 expired entries」。

**關鍵問題**：如果 B-2 設計為「對每個在 fusion 中存活的 recall result 做 neighbor lookup」，則 expired entries 在步驟 5 就已被移除，B-2 對它們無能為力。這符合預期——expired memories 本就不該被召回。

**但若 B-2 設計為「對 fusion 前的完整候選池做 neighbor lookup」**，則 expired neighbors 會在步驟 5 被移除，B-2 找不到它們——這是 AliceLJY 的設計所沒有考慮到的問題。

### 建議

在 B-2 PR 中明確說明 neighbor lookup 的輸入範圍，並確認：
1. Neighbor lookup 是對 MMR 輸出（存活的 results）還是 fusion 前的完整候選池？
2. 如果是後者，需要在 B-2 實作中加入獨立的 expiry filter，或等到 MMR 之後再過濾

---

## 衝突 2：MMR 去重與 B-2 的根本性衝突（Q5）

### 描述

Issue #538 的 Q5（AliceLJY 尚未回答）：MMR 已經刪除相似的 items，B-2 找不到它們的 neighbors。

AliceLJY 在 Q2 回答中說「在 MMR 之後插入」，理由是「MMR 負責多樣性，neighbor enrichment 是對 top-K 的補充」。但這個設計造成以下問題：

**MMR 刪除相似 items → B-2 無法對已刪除的 items 找 neighbors**

Pipeline 順序（MMR 在步驟 13）：
```
步驟 13: applyMMRDiversity()  ← MMR 刪除相似項目
步驟 14: slice(0, limit)
步驟 15: return
```

若 B-2 在 MMR 之後插入，則：
- MMR 已經對 `denoised` 做了去重，相似 items 已被刪除
- B-2 只能對「還在 MMR 輸出中的 items」找 neighbors
- **已進入 MMR 但被刪除的相似 items，它們的 neighbors 永遠無法被 B-2 擴展**

這與 AliceLJY 的本意相反——她說「neighbor enrichment 是對 top-K 的補充」，但事實上 MMR 已經在 top-K 層級做過去重了，B-2 的 neighbors 永遠不會包含 MMR 認為「太相似」的那些 items。

### 嚴重程度

🔴 **高風險**——這是 B-2 設計的核心矛盾，需要 maintainer 裁決

### 建議

**選項 A（推薦）**：將 B-2 插入點改為 MMR **之前**（步驟 12 之後、步驟 13 之前）。好處：
- B-2 可以對所有候選 items（包括會被 MMR 刪除的）找 neighbors
- MMR 仍然可以對 B-2 的輸出結果做多樣性控制
- 代價：MMR 的多樣性計算會被 neighbors 影響（AliceLJY 原本想避免的）

**選項 B**：維持 MMR 之後插入，但接受「B-2 neighbors 僅限於 MMR survivors」的限制，在 PR 文件中明確說明

**選項 C（爭議）**：完全跳過 MMR 的去重對 B-2 neighbors 的影響——如果 B-2 用的是 semantic similarity（而非 BM25 keyword overlap），則 B-2 neighbors 本來就應該是「語義相似但 MMR 認為不重複」的 items，MMR 不會刪除它們

---

## 衝突 3：auto-supersede（#452）與 B-1 的 BM25 expansion

### 描述

Issue #452 的 auto-supersede 机制：当相似度在 0.95-0.98 范围、相同 category 且符合 SUPERSEDE_ELIGIBLE 时，自动将旧 entry 标记为 superseded（设置 `superseded_by` 字段、`invalidated_at` 时间戳），同时存储新 entry（带 `supersedes` 链接）。

B-1 的 BM25 expansion 在 `loadAgentReflectionSlicesFromEntries()` 中執行，透過 `bm25Search()` 找 neighbors。問題在於：

- **Superseded entries 並未被刪除**，只是被標記了 `invalidated_at` 和 `superseded_by`
- B-1 的 `bm25Search()` 查詢**不會自動排除 superseded entries**（除非 store 有對應的過濾）
- 因此 B-1 可能對已被 superseded 的 entry 做 expansion，拉入已過時的 neighbors

### 嚴重程度

🟡 **中風險**——取決於 store 的 `bm25Search()` 是否自動過濾 `invalidated_at !== undefined` 的 entries

### 建議

在 B-1 實作中加入 `invalidated_at` filter，確保已被 superseded 的 entries 不會被當作 neighbors：
```typescript
// 在 bm25Search 的過濾條件中加
.filter(r => !r.entry.metadata?.invalidated_at)
```
或確認 store 層已自動排除 invalidated entries，並在 PR 文件中說明。

---

## 衝突 4：temporal-awareness（#453 expiry filter）與 B-2 neighbors 的互動

### 描述

這是衝突 1 的更深層分析。Issue #453 將 expiry filter 置於 scoring pipeline 之前，目的是「讓 expired memories 不佔用候選 slot」。但這對 B-2 的 semantics 有以下影響：

**場景**：假設 recall result A 是即將過期（但尚未 expired）的 entry，B-2 找到了它的 neighbor B，B 是一個已 expired 的 entry。

- A 在步驟 5 通過（尚未 expired）
- B-2 找到 B（expired），將其加入 neighbors
- 如果 B-2 的實作是在 MMR 之後加入 neighbors，B 會進入最終輸出
- 最終結果包含了一個 expired neighbor

這取決於 B-2 的 neighbor lookup 是否在 store 層做 expiry filter。如果 B-2 的 `vectorSearch()` 本身不过滤 expired entries（因為它在 MMR 之後，pipeline 的 expiry filter 已執行完），則 expired neighbors 會被加入輸出。

### 嚴重程度

🟡 **中風險**

### 建議

在 B-2 的 neighbor lookup 階段（無論插入點在哪）都應加入獨立的 expiry filter，確保 neighbors 不包含 expired entries：
```typescript
const neighborResults = await store.vectorSearch(neighborQuery, topK, scopeFilter, {
  excludeInactive: true,  // 或明確過濾 !isMemoryExpired()
});
```

---

## 衝突 5：tier-manager 的 coreImportanceThreshold = 0.8 與 Proposal A 的 feedback 機制

### 描述

`tier-manager.ts` 中 Core promotion 的三個門檻：
- `coreAccessThreshold = 10`（最小存取次數）
- `coreCompositeThreshold = 0.7`（最小 composite decay score）
- `coreImportanceThreshold = 0.8`（最小 importance）

Proposal A（動態重要性）的 feedback 調整幅度：
- 正向確認：`importance += 0.15`，上限 1.0
- 負向確認：`importance -= 0.10`，下限 0.1
- 被召回未使用：`importance -= 0.03`

**分析**：
- 初始 `importance` 通常從 0.5 開始。要從 0.5 到 0.8，需大約 2-3 次正向確認（每次 +0.15）
- 之後還需滿足 `accessCount >= 10` 和 `composite >= 0.7`
- 這個門檻意味著：需要有意義的互動確認 + 高頻使用 + 良好的 decay score，才能晋升 Core

### 嚴重程度

✅ **無衝突**——0.8 門檻設計合理，與 Proposal A 的 feedback 機制完全相容

### 補充說明

此門檻與 Proposal A 形成互補：
- Proposal A 的 +0.15 每次正向確認，逐漸累積 importance
- 0.8 門檻確保只有「真正重要的 memories」才能晋升 Core（避免少數幾次正向確認就觸發）
- Core tier 的 decay 最慢（floor 0.9），一旦晋升代價高，所以 0.8 是合理的保護門檻

---

## 衝突 6：auto-supersede 與 B-2 neighbors

### 描述

當 auto-supersede 標記一個 entry 為 superseded 時，該 entry 的 `superseded_by` 欄位指向新的 entry。如果 B-2 的 neighbor lookup 找到了這樣的 entry：

- 被 superseded 的 entry 仍然存在於 store 中（只是被標記為 `invalidated_at`）
- B-2 可能將其視為 valid neighbor 加入輸出
- 最終輸出包含已 superseded（已過時）的 neighbors

這比衝突 3 更嚴重，因為 B-2 是 retrieval-time 擴展，output 直接影響 prompt context。

### 嚴重程度

🟡 **中風險**

### 建議

在 B-2 的 neighbor lookup 中加入 `invalidated_at === undefined` filter（與衝突 3 相同）：
```typescript
const neighbors = await store.vectorSearch(query, topK, scope, {
  excludeInactive: true,  // 需確認 store 的 excludeInactive 包含 superseded 檢查
});
```
或在 PR 文件中說明 store 層默認排除 invalidated entries，並附上對應的單元測試。

---

## 衝突 7：vectorOnlyRetrieval() 路徑無 BM25 search——B-2 Q6 未解決

### 描述

Issue #538 的 Q6（AliceLJY 尚未回答）：`vectorOnlyRetrieval()` 沒有 BM25 search 階段，B-2 的 neighbor lookup 應如何實作？

上游 `vectorOnlyRetrieval()` pipeline：
```
1. embedQuery()
2. store.vectorSearch()
3. expiry filter
4. applyRecencyBoost
5. applyImportanceWeight
6. applyLengthNormalization
7. hardMinScore filter
8. applyDecayBoost / applyTimeDecay
9. filterNoise
10. applyMMRDiversity
11. slice(0, limit)
12. return
```

B-2 根據 Issue #513 Option B 應該用 **BM25** 找 neighbors（AliceLJY Q1 建議）。但 `vectorOnlyRetrieval()` 路徑沒有 BM25 search，要如何在該路徑實作 B-2？

### 嚴重程度

🔴 **高風險**——B-2 PR 無法完整實作（覆蓋 hybrid + vector-only 兩條路徑），需要 maintainer 確認 vector-only 的處理方式

### 建議

**選項 A**：B-2 只實作在 hybrid path，vector-only path 暂时不做 neighbor enrichment（並在 PR 文件中說明限制）

**選項 B**：在 vector-only path 也加入 BM25 search 階段（代價：增加 vector-only 的延遲）

**選項 C**：B-2 在 vector-only path 使用 `vectorSearch` 而非 `bm25Search` 找 neighbors（偏離 AliceLJY 的 BM25 建議，但可行）

---

## 衝突 8：AliceLJY 與 rwmjhb 對 B-1 的不一致意見（新鮮 session 問題）

### 描述

這不是程式碼衝突，而是 maintainer 之間的路線衝突：

- **AliceLJY**：fresh-session bypass 可接受（Issue #513 Comment 1）
- **rwmjhb**：fresh-session bypass 是 blocking 問題（PR #529 review）
- **結果**：PR #529 被 rwmjhb 以 BLOCKING 方式關閉，但 AliceLJY 的 APPROVED 標記仍在

### 嚴重程度

🔴 **高風險**——無法繼續 B-1 PR，除非 maintainer 達成共識

### 建議

在 Issue #513 Comment 3 的裁決請求尚未得到回覆。此衝突無法靠實作解決，需要 upstream maintainer team 明確裁決誰有最終決定權。

---

## 衝突 9：B-2 的 Pipeline 插入點存在兩種互相矛盾的说法

### 描述

存在三個相互衝突的 B-2 插入點描述：

| 來源 | 插入點 | 日期 |
|------|--------|------|
| Issue #445 Comment 3（AliceLJY） | MMR 之後 | 2026-04-03 |
| Issue #538 Comment 1（AliceLJY） | MMR 之後 | 2026-04-06 |
| Issue #445 Comment 7（jlin53882） | MMR 之前 | 2026-04-05 |

jlin53882 在 Comment 7 提議：
```
→ applyNeighborEnrichment  ← B-2 NEW（MMR 之前）
→ re-sort by combined score
→ applyMMRDiversity
```

AliceLJY Q2 回覆則明確說「在 MMR 之後」。

### 嚴重程度

🔴 **高風險**——實作者必須在 MMR 之前或之後之間做選擇，但兩者都有問題（見衝突 2）

### 建議

需要在 PR 開啟前明確。建议先取得 AliceLJY 對 Q5（ MMR 去重問題）的回覆，再確認插入點。

---

## 衝突 10：B-2 scope boundary（Q7）未定義

### 描述

Issue #538 的 Q7（AliceLJY 尚未回答）：B-2 的 neighbor lookup scope boundary 如何決定？

- 是用 recall result 各自的 scope？
- 還是 query 本身的 scope？
- 跨 scope 的 recall results 如何處理？

### 嚴重程度

🟡 **中風險**——影響 PR 實作細節，需要在實作前確認

### 建議

在 PR 中說明 scope 策略，並用 config 選項允許使用者調整。

---

## 衝突 11：B-2 Neighbor 附加方式（Q9）未定義

### 描述

Issue #538 的 Q9（AliceLJY 尚未回答）：neighbors 如何附加到 recall results？

- A：作為附屬上下文（`enriched.text = original.text + "\n\nNeighbors: ..."`）
- B：作為額外候選列表（`results = [...topK, ...neighbors]`）
- C：其他？

### 嚴重程度

🟡 **中風險**——影響 output schema 和下游消費者的處理方式

### 建議

在 PR 文件中明確定義 output 結構，並在整合測試中驗證。

---

## 衝突 12：B-2 預設值：Config flag 預設 disabled 與提案目標的張力

### 描述

AliceLJY 在 Q3 建議「config flag 控制，預設 disabled」，理由是「新行為需要 opt-in」。但這與 B-2 的目標（豐富 retrieval 結果）存在張力：

- 如果預設 disabled，多數用戶不會主動啟用，B-2 的價值無法驗證
- 如果預設 enabled，可能影響現有 retrieval 行為（延遲、輸出格式變化）

### 嚴重程度

🟡 **中風險**——實作細節，可以在 PR 中討論

### 建議

提供可衡量的 benchmark（enrichment 前後的 recall quality 對比），讓 maintainer 根據數據決定預設值。

---

## 衝突 13：BM25 self-filter 的 BM25 自匹配問題在 B-1 和 B-2 的差異處理

### 描述

PR #503 修復了 B-1 的 BM25 self-match 問題（`hit.entry.category === "reflection"` 的 self-filter）。但 B-2 若使用 BM25 找 neighbors，同樣的自匹配問題存在嗎？

在 B-2 的場景：
- 輸入是 recall results（非 reflection slices）
- 查詢文字是每個 recall result 的 `text`
- 如果 B-2 用 BM25，且找到了自己，會造成 self-enrichment

### 嚴重程度

🟡 **中風險**——取決於 B-2 的 neighbor lookup 機制（BM25 vs vector）

### 建議

若 B-2 使用 BM25 找 neighbors，確保有 self-filter；若使用 vector search，self-match 機率較低（因為是 semantic similarity 而非 keyword overlap）。

---

## 衝突 14：B-1 PR #503 修復的 bug 在 upstream 可能已不存在（需要驗證）

### 描述

PR #503 修復了三個 B-1 bug：
1. Neighbors 被 `.slice(0, 6)` 截斷
2. BM25 自匹配 reflection rows
3. 測試驗證本地副本而非生產代碼

這些修復是針對當時的 upstream 代碼。如果 upstream 自 PR #503 以來有新變更（例如 `loadAgentReflectionSlicesFromEntries` 的 sync→async 改動），這些 bug 可能已不存在，或以不同形式存在。

### 嚴重程度

🟡 **中風險**——需要在新 PR 中重新驗證這些 bug 是否仍然存在

### 建議

在提出新的 B-1 PR 之前，先在最新的 upstream master 上驗證這三個 bug 是否仍然存在。

---

## 衝突 15：B-1 Option B 與 B-2 BM25 neighbor lookup 的邊界模糊

### 描述

AliceLJY 在 Q1 建議 B-2 用 **BM25** 找 neighbors（而非 vector search）。但 B-1 Option B 本身就已經是「BM25 neighbor expansion」。兩者使用相同的 BM25 機制，只是觸發時機不同：
- B-1：reflection load time
- B-2：retrieval time

AliceLJY 在 Q4 說「保持獨立」，但若兩者都用 BM25，是否應該共享 BM25 lookup utility？

### 嚴重程度

✅ **無衝突**——AliceLJY 的「保持獨立」建議是合理的，BM25 lookup 底層可以共享 utility function，但 enrichment 邏輯本身應獨立

---

## 衝突 16：Pruning（#452 auto-supersede）與 B-2 neighbor lookup 的互動

### 描述

此為衝突 6 的延伸。auto-supersede 標記 `similarity > 0.95` 的 entry 為 superseded。B-2 的 neighbor lookup 尋找 `topK=2` 的相似 entries。如果一個 entry 有 supersede 者（即它已被標記為 superseded），B-2 在 neighbor lookup 時會：
- 找到它的 supersede 者（作為 neighbor）
- 將已过时的 supersede 者加入輸出

這可能導致：已废弃的 entry 被作為 context 加入 prompt，而非当前正确答案。

### 嚴重程度

🟡 **中風險**

### 建議

在 B-2 的 neighbor lookup 過濾條件中排除 `superseded_by !== undefined` 的 entries，確保 neighbors 是當前有效的 memories。

---

## 衝突 17：Proposal B 的 MMR 順序衝突（AliceLJY 確認 vs jlin53882 提議）

### 描述

這是衝突 9 的補充。AliceLJY 在 Q2 明確說「在 MMR 之後」，理由是「避免 neighbor 影響 MMR 的多樣性計算」。但這造成：

1. **MMR 已刪除相似 items** → B-2 找不到它們的 neighbors（衝突 2）
2. **MMR 之後沒有 scoring/boost 階段** → B-2 的 neighbors 無法參與 rescore

Pipeline 在 MMR 之後：
```
13. applyMMRDiversity()  ← MMR 去重
14. slice(0, limit)
15. return               ← B-2 在此插入
```
沒有任何 scoring 或 boost 機制，B-2 的 neighbors 只能直接附加在 slice 之後的結果上，無法重新排序。

### 嚴重程度

🔴 **高風險**

### 建議

需要重新评估 B-2 的插入點。如果要讓 neighbors 參與 rescoring，應插入在 MMR **之前**。如果堅持 MMR 之後，需要重新定義 neighbors 的附加方式（不經過 rescoring，直接附加）。

---

## 衝突 18：B-2 Tier Sort 在 MMR 之後的可行性

### 描述

PR #504（含 OpenCode adversarial review）提出了「Tier Sort」設計：neighbors 在各自的 tier 內按 vector similarity 排序。如果 B-2 在 MMR 之後插入：

- Tier Sort 需要知道每個 neighbor 的 tier 歸屬
- tier 資訊來自 entry 的 metadata
- 但 MMR 之後沒有任何 scoring 機制，Tier Sort 只能基於 static metadata 而非動態分數

### 嚴重程度

🟡 **中風險**

### 建議

在 PR 文件中說明 Tier Sort 在 MMR 之後的限制，並提供 fallback 行為（例如按 importance 排序）。

---

## 總結：衝突風險分級

### 🔴 高風險衝突（需要 maintainer 確認）

| # | 衝突名稱 | 描述 |
|---|---------|------|
| 2 | MMR 去重消滅 neighbors（Q5） | MMR 之後插入 B-2，導致相似 neighbors 被 MMR 預先刪除 |
| 7 | vectorOnlyRetrieval() 無 BM25 search（Q6） | B-2 依賴 BM25，但 vector-only path 沒有 BM25 階段 |
| 8 | AliceLJY vs rwmjhb 不一致（fresh-session） | 兩位 maintainer 對 B-1 fresh-session bypass 有衝突意見，PR 無法繼續 |
| 9 | Pipeline 插入點互相矛盾 | Issue #445 Comment 7 提議 MMR 之前，Issue #538 AliceLJY 確認 MMR 之後 |
| 17 | MMR 之後無 rescoring 機制 | B-2 在 MMR 之後插入，neighbors 無法參與 rescoring |

### 🟡 中風險衝突（需要在 PR 中說明）

| # | 衝突名稱 | 描述 |
|---|---------|------|
| 1 | expiry filter 位置影響 B-2 輸入範圍 | B-2 對哪個集合做 neighbor lookup 需明確 |
| 3 | auto-supersede 與 B-1 BM25 expansion | B-1 可能對 superseded entries 做 expansion |
| 4 | expiry filter 與 B-2 neighbors 的互動 | B-2 neighbors 是否會包含 expired entries |
| 6 | auto-supersede 與 B-2 neighbor lookup | B-2 可能找到已 superseded 的 entries |
| 10 | B-2 scope boundary 未定義（Q7） | Neighbor lookup 的 scope filter 需要確認 |
| 11 | B-2 Neighbor 附加方式未定義（Q9） | Output structure 需在 PR 中定義 |
| 12 | B-2 預設值策略 | Config flag 預設 disabled vs enabled 的價值衡量 |
| 13 | BM25 self-filter 邊界 | B-2 使用 BM25 時的自匹配處理 |
| 14 | B-1 PR #503 修復的 bug 需重新驗證 | 上游代碼可能已變更 |
| 16 | auto-supersede 導致 neighbors 過時 | B-2 neighbor lookup 可能找到已废弃的 supersede 者 |
| 18 | Tier Sort 在 MMR 之後的限制 | 無 rescoring 機制時 Tier Sort 只能基於 static metadata |

### ✅ 無衝突（可以安全實作）

| # | 內容 | 說明 |
|---|------|------|
| 5 | tier-manager coreImportanceThreshold = 0.8 | 與 Proposal A 的 feedback 機制完全相容 |
| 15 | B-1 與 B-2 的 BM25 共享策略 | AliceLJY 的「保持獨立」建議合理 |

---

## 行動建議

### 立即需要 maintainer 回覆的問題（Issue #538 Q5-Q9）

1. **Q5（🔴 最高優先）**：確認 B-2 插入點——MMR 之前還是之後？如果之後，如何處理 MMR 已刪除的 neighbors？
2. **Q6（🔴）**：vectorOnlyRetrieval() 路徑的 B-2 如何實作？
3. **Q7-Q9（🟡）**：scope boundary 和 neighbor 附加方式

### 對 James 的建議

1. **不要急於實作**：在 Q5-Q9 得到回覆之前，任何 B-2 實作都可能方向錯誤
2. **B-1 暫停**：等待 maintainer 裁決 AliceLJY vs rwmjhb 的衝突（Issue #513 Comment 3）
3. **PR #504 的 B-2 內容值得保留**：22 個測試 + OpenCode adversarial review，但需先確認 Q5-Q9 的方向
4. **衝突 2（Q5）是最關鍵的設計決策**：建議 James 去 Issue #538 催問，或基於自己的判斷做决定（建議：MMR 之前插入）
