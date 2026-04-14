# Proposal B Issue 脈絡分析報告

> 資料來源：GitHub Issues #445、#513、#514、#538  
> 整理時間：2026-04-09  
> Repo：CortexReach/memory-lancedb-pro

---

## 一、Issue #445 — 源頭 RFC：Proposal A & B Implementation Analysis

| 欄位 | 內容 |
|------|------|
| **標題** | [RFC] Proposal A & B Implementation Analysis |
| **狀態** | OPEN |
| **標籤** | 無 |
| **作者** | jlin53882 |

### Issue Body 摘要

這是 Proposal A 與 Proposal B 的**源頭分析 RFC**，同時排除了 Proposal C。

#### 現有系統盤點

| 機制 | 檔案 | 功能 |
|------|------|------|
| Frequency reinforcement | `access-tracker.ts` | 高存取頻率 → 半衰期最長 3x（via `log1p(effectiveAccessCount)`） |
| Weibull 衰減 | `decay-engine.ts` | `importance` 調整半衰期：`effectiveHL = halfLife × exp(1.5 × importance)` |
| Tier  promotion | `tier-manager.ts` | Core (β=0.8 最慢衰減) / Working / Peripheral (β=1.3 最快) |
| Importance 權重 | `retriever.ts` | `applyImportanceWeight()`：`score *= (0.7 + 0.3 × importance)` |
| `last_confirmed_use_at` | `smart-metadata.ts` | 欄位存在但**未被主動使用** |
| `bad_recall_count` | `smart-metadata.ts` | 欄位存在但**未被觸發** |
| Reflection quality weighting | `reflection-store.ts` | `quality × logistic(age) × baseWeight` 已實作動態衰減 |

**關鍵缺口**：系統只有頻率強化，沒有**回饋式重要性調整**。`importance` 在寫入後從不更新。

---

#### Proposal A — 動態重要性（推薦）

目標：讓 `importance` 根據使用品質動態調整，而非一次性寫入後靜態。

**建議的回饋訊號：**

| 訊號 | 觸發時機 | 調整幅度 |
|------|----------|----------|
| 記憶被召回**並**在回應中被使用 | `agent_end`：比較 recall 結果與最終回應 | `importance += 0.05`，上限 1.0 |
| 用戶明確確認正確 | 用戶回覆「正確」/「是」/「對」/「right」 | `importance += 0.15`，上限 1.0 |
| 用戶明確標記錯誤 | 用戶回覆「不」/「錯誤」/「not right」 | `importance -= 0.10`，下限 0.1 |
| 被召回但連續 2+ 次未使用 | 下一個召回週期檢查 | `importance -= 0.03` |

**為什麼用 `agent_end` hook**：`before_agent_start` 在回應產生前，無法判斷記憶是否真的被用到；`agent_end` 擁有完整的 `event.messages`，可以比較 recall 結果與最終回應。

**不需要修改的檔案**：`decay-engine.ts`（已讀取 importance）、`tier-manager.ts`（Core 晉升需要 `importance >= 0.8`）、`access-tracker.ts`（頻率追蹤與重要性調整互補）。

---

#### Proposal B — 類似注意力機制的鄰居擴展（推薦）

目標：當一個記憶被召回時，主動找出其「鄰居記憶」一併帶入上下文。

**B-1（Reflection-scoped，風險較低）**：

在 `loadAgentReflectionSlicesFromEntries()` 中延伸：
```
loadAgentReflectionSlicesFromEntries() → N 個結果
  → 對每個結果執行 bm25Search(text, topK=2, scope=same)
  → 合併 + 去重
  → 輸出（原始結果 + 鄰居）
```
優點： contained within `reflection-store.ts`，不影響主檢索延遲。  
缺點：只影響 reflection memories，不影響 main memories table。

**B-2（完整檢索路徑，若 B-1 驗證成功）**：

在 `retriever.ts`，MMR diversity 之後、回傳結果之前：
- 對每個被召回的記憶，多做一次 `vectorSearch(text, topK=2, scope=same)`
- 以 `similarity + importance` 合併鄰居並重新排序
- 上限：每個被召回記憶最多 2 個鄰居，總輸出上限 20 筆

**注意**：MMR diversity 與鄰居擴展可能衝突——MMR 將相似項目推後，鄰居擴展將其帶入。需要調整 MMR 順序。

---

#### 為何排除 Proposal C

| 疑慮 | 原因 |
|------|------|
| 分類準確性 | 沒有 session 等級的領域分類器；建置一個會增加延遲且分類錯誤會降級結果 |
| 錯誤分類代價 | 若領域被錯誤分類，正確的記憶被稀釋，錯誤的記憶被提升 |
| A + B 已覆蓋主要需求 | A 讓重要記憶更持久；B 豐富上下文；C 的效益未經證實 |
| 成熟度 | 沒有用戶回饋指出「情境感知召回已壞掉」 |

---

#### 建議的實作順序

1. Proposal A Phase 1 — 加入 `agent_end` 回饋迴圈（最低風險、最高清晰度）
2. Proposal B Path B-1 — 在 reflection recall 中實作鄰居擴展
3. Proposal A Phase 2 — 接入 `last_confirmed_use_at` 與 `bad_recall_count` 觸發器
4. Proposal B Path B-2 — 主檢索路徑的鄰居擴展（若 B-1 驗證成功）

---

### Comments（#445）

#### Comment 1 — AliceLJY（2026-04-02 09:28 UTC）
> **印象深刻的分析——codebase 審查非常透徹，現有機制清單也完全正確。**
>
> **Proposal A（動態重要性）：** 同意這是最高價值的變更。`importance` 一次性寫入是最明顯的缺口。幾點備註：
> - `agent_end` hook 位置正確——這是唯一同時擁有 recall 結果和最終回應可供比較的地方
> - 調整幅度（+0.05/+0.15/-0.10/-0.03）作為起始值看起來合理；應該可透過 config 調整，因為最佳值會取決於使用模式
> - 建議加入 `min_recall_count` 閾值再套用負向調整——只被召回一次且未使用的記憶不一定是壞的，可能只是那個 session 的上下文不對
>
> **Proposal B（鄰居擴展）：** B-1（reflection-scoped）是正確的起點。你標記的 MMR 與鄰居擴展之間的衝突是真实存在的，很高興看到這點被提前提出。對於 B-1，因為 reflection slices 已經是有界集合，性能影響應該很小。
>
> **實作順序：** 同意 A-Phase1 → B-1 → A-Phase2 → B-2。每個階段可以獨立驗證。
>
> **回答你的問題：**
> - Q2：鄰居擴展預設應該限於同一 `scope` filter 內——跨 scope 會拉入被刻意分區的上下文
> - Q3：Proposal C 排除理由合理。若後續有具體使用案例，可以重新考慮

#### Comment 2 — jlin53882（2026-04-02 16:59 UTC）
> **Phase 4：B-2 全域 Retrieval Neighbor Enrichment**
>
> 目前 Phase 1（`feat/proposal-b1-v2`，PR #463）和 Phase 2（`feat/proposal-b2-v2`，PR #464）已在 `feat` 分支實作完成。Phase 4 是 B-2 的完整實作方向。
>
> **設計目標**：在 `MemoryRetriever.retrieve()` 的 auto-recall 路徑上，於結果回傳前加入鄰居擴展。
> - 對每個候選 entry，以其 text 向量搜尋同一 scope 內的 top-2 neighbors
> - 合併進結果後，以 `effectiveScore = similarity * (0.7 + 0.3 * importance)` 重新排序
> - 總上限：20 筆
>
> **實作位置**：`src/retriever.ts`：`retrieve()` 方法末尾、access tracking 之後
>
> **觸發條件**：`source === "auto-recall"` + `config.enableNeighborEnrichment !== false`（預設 true）
>
> **風險與疑慮**：
> 1. MMR 衝突：neighbors 可能稀釋高度相關的原本結果
> 2. Scope 顆粒度：neighbors 與原本結果共享同一 scope，跨 scope 干擾機率低
> 3. Latency：每個 entry 都多做一次 vectorSearch，假設 top-5 × 2 = 10 次額外查詢
>
> **問題**：向 AliceLJY 請教三個問題（方向一致性、MMR 必要性、其他潛在問題）

#### Comment 3 — AliceLJY（2026-04-03 00:26 UTC）
> **方向大方向正確。幾點約束以保持可審查性：**
>
> - v1 版本保持鄰居擴展 same-scope only
> - 第一個 B-2 版本不要加入另一個 MMR pass；先用 effective score 重新排序就夠了
> - 保持原始召回命中結果在結果集中固定，鄰居展開要有硬上限
> - **最重要：不要將 B-2 與 Proposal A 回饋邏輯綁在一起。作為獨立的 PR 來審查，附上自己的迴歸測試和小延遲檢查**
>
> B-1 仍然是驗證場。若要繼續 B-2，保持 scope 精簡。

#### Comment 4 — jlin53882（2026-04-03 17:55 UTC）
> **PR #493 — Proposal A Phase 1 已完成**
>
> Phase 1 動態重要性回饋訊號已實作完成。
>
> 已實作內容：
>
> | Signal | 條件 | 調整 |
> |--------|------|------|
> | 用戶明確確認 | 使用者回答「正確」/「是」/「對」/「right」 | importance += 0.15 上限 1.0 |
> | 用戶明確標記錯誤 | 使用者表示「不」/「錯誤」/「not right」 | importance -= 0.10 下限 0.1 |
>
> Phase 2 預計處理：min_recall_count 閾值 + 調整幅度可配置化

#### Comment 5 — jlin53882（2026-04-04 16:15 UTC）
> **Branch Topology Analysis — PR Chain #507 / #505 / #506**
>
> 三個 PR 都修改相同檔案（`index.ts`、`reflection-slices.ts`、`src/retriever.ts`、`src/smart-extractor.ts`、`src/auto-capture-cleanup.ts`），獨立 merge 會造成衝突。
>
> 建議改為堆疊式 chain：`master → #507(Phase1) → #505(Phase3) → #506(Phase4)`
>
> **#507 需要清理的 commits**（已拆分為獨立 PR）：
> - #498：`WeakSet.clear()` fix
> - #510：`stripEnvelopeMetadata` full fix
> - #500：recency double-boost guard
>
> **#507 仍需修復的問題**：
> - P1：autoCapture block boundary（確認回饋評分在正確的 `if (this.config.autoCapture)` 範圍內）
> - MAJOR：`isRecallUsed` false positive（回應包含「that's not right」不應被當作 confirm，需增加 injected-summary 特異性）
>
> **Q&A**：  
> Q1：bundled fixes 已拆分，rebase #507 到最新 master 後這三個 commits 會消失  
> Q2：#462 已過時，被 #505（Phase 3，FeedbackConfigManager）取代  
> Q3：stack chain 方向正確，只需將每個 PR 的 base branch 改為 chain 到前一個 phase

#### Comment 6 — jlin53882（2026-04-04 18:27 UTC）
> **PR #523 更新（Option B BM25 Neighbor Expansion）**
>
> 此 PR 實作了 Option B Phase 1 的 BM25 neighbor expansion 功能，解決 Issue #513 中提出的 fresh session 問題。
>
> **主要變更**：
> - 在 `loadAgentReflectionSlicesFromEntries` 的 `rankReflectionLines()` 之前執行 BM25 expansion
> - 乘法加成 quality 分數（`quality = 0.2 + 0.6 * bm25Score`）
> - 新增 `Bm25NeighborExpansion` config 開關
>
> PR #523 正在等待 maintainer 審查中。

#### Comment 7 — jlin53882（2026-04-05 14:48 UTC）
> **B-2 Proposal: Full Retrieval Neighbor Enrichment**
>
> B-1（PR #529，已獲准）成功實作後，提出 B-2 完整計畫。
>
> **目標**：在 `retriever.ts`，MMR diversity 之後、回傳結果之前，以 semantic neighbors 豐富被召回的記憶。
>
> **Pipeline 插入點**：
> ```
> hybridRetrieval()
>   → vectorSearch + bm25Search
>   → RRF fusion → noise filter → rerank
>   → applyRecencyBoost → applyImportanceBoost → applyLengthNormBoost
>   → applyNeighborEnrichment  ← B-2 NEW
>   → re-sort by combined score
>   → applyMMRDiversity
>   → slice(0, limit)
> ```
>
> **關鍵設計決策**：
> 1. **NE before MMR**：先擴展語義鄰域，再由 MMR 做最終多樣性控制，避免鄰居被 MMR 不公平地壓制
> 2. **Parallel vectorSearch**：用 `Promise.all` 平行化 N 次 vectorSearch（最多 5 個 candidates，每個 topK=2），非順序執行
> 3. **Config**：新增 `RetrievalConfig` 欄位：`neighborEnabled`、`neighborTopK`、`neighborMaxCandidates`、`neighborMaxPerRecalled`、`neighborTotalCap`
> 4. **與 B-1 的差異**：B-1 用 `bm25Search`（關鍵詞匹配）在 `reflection-store.ts`；B-2 用 `vectorSearch`（向量相似度）在 `retriever.ts`；不同機制，不需要共享程式碼
> 5. **防御機制**：D1 空白回傳、D2 無 scopeFilter 回傳、D3 總上限、D5 seen Set 去重、D6 Promise.all + per-call `.catch` 容錯、D7 Latency budget、D8 Scope 一致性
>
> **問題**：
> 1. 應該用 config flag 控制還是 always-on？
> 2. 應該用 `bm25Search` 而非 `vectorSearch`（與 B-1 一致）？
> 3. 提議的 pipeline 順序（NE before MMR）是否可接受？

---

## 二、Issue #513 — [Proposal B Phase 1] Seeking guidance: redesign approach for BM25 neighbor expansion

| 欄位 | 內容 |
|------|------|
| **標題** | [Proposal B Phase 1] Seeking guidance: redesign approach for BM25 neighbor expansion |
| **狀態** | OPEN |
| **標籤** | 無 |
| **作者** | jlin53882 |

### Issue Body 摘要

這是 B-2 Option 的初始討論 issue，試圖在 PR #529 關閉後確認 B-2 方向。

**B-2 核心概念**：不是在 load time 豐富 reflection slices，而是在**retrieval time 豐富召回結果**：
```
hybridRetrieval()
  → vectorSearch + bm25Search
  → RRF fusion → noise filter → rerank
  → applyRecencyBoost → applyImportanceBoost
  → applyMMRDiversity
  → [INSERT: enrich recalled results with their BM25 neighbors]
  → return top-K results
```

**B-2 相比 B-1 的關鍵優勢**：
- 適用於所有查詢，包含 fresh sessions（查詢文字永遠可取得）
- 架構更簡單直觀
- 不依賴 derived reflection slices 是否存在

**4 個 Open Questions**：
1. BM25 vs Vector search：應該用哪一個找 neighbors？
2. 插入點：MMR diversity 之後還是之前？
3. Gating 機制：config flag 控制還是 always enabled？
4. 與 B-1 共享程式碼？

### Comments（#513）

#### Comment 1 — AliceLJY（2026-04-04 11:48 UTC）
> **推薦採用 Option B（query-time BM25 作為 ranking signal）做 Phase 1**
>
> **理由**：
> 1. **無 schema 變更**——避免遷移複雜性，保持資料層乾淨
> 2. **適用所有 entries**——新舊皆可，無 cold-start 問題
> 3. **解決 reviewer 的核心疑慮**——enrichment 在 slice cutoff **之前**發生，而非事後補救
> 4. **可逆**——若效能有問題，可以 config flag 閘門控制，不需要清理資料
>
> **關於延遲疑慮**：
> - 將 BM25 搜尋範圍限於初始衰減排名後的 top-N candidates（例如 top 5-10），而非所有 entries，這樣可以控制成本
> - 新增 config 選項 `bm25NeighborExpansion: { enabled: true, maxCandidates: 5, maxNeighborsPerCandidate: 3 }` 讓使用者可以調整或停用
>
> **可參考的現有模式**：
> - `vectorOnlyRetrieval()` 的 chain：vector search → rerank → score merge。BM25 boost 應該以同樣方式插入，作為最終排序前的 score signal
> - `applyRecencyBoost()` 模式（乘法 score 調整）是很好的模板，展示如何將 BM25 neighbor signal 混合進排名
>
> **回答問題**：
> 1. 是的，Option B 與 reviewer 的「整合進初始查詢」意圖一致
> 2. 從 top-5 candidates 擴展 BM25 開始——更簡單，覆蓋 80% 的價值
> 3. 見 `applyRecencyBoost()` 的評分模式
> 4. Fresh-session bypass 對 Phase 1 可接受——enrichment 需要有儲存的內容才能查詢，這是任何方法的固有限制

#### Comment 2 — jlin53882（2026-04-05 12:52 UTC）
> **PR #529 已準備好審查**
>
> 我們已重新提交乾淨版本的 Option B BM25 neighbor expansion 為 **PR #529**。
>
> 根據先前 review 的關鍵修復：
> 1. **Encoding**：加入 `\.gitattributes\` 確保一致的 LF 行尾。Diff 現在是 +691/-21（之前是 +6606/-5941）
> 2. **candidateTimestamp**：已修復（neighbors 繼承 parent candidate timestamp）
> 3. **Config**：`bm25NeighborExpansion` 現在在 `parsePluginConfig` 中正確解析
> 4. **Async**：所有 `loadAgentReflectionSlicesFromEntries` 呼叫都有 `await`
>
> 關於 **fresh-session early return**：我們保留了 Phase 1 討論的 D1 early return。如果需要修改，請告訴我們。

#### Comment 3 — jlin53882（2026-04-06 06:14 UTC）
> **衝突解決請求：AliceLJY 與 rwmjhb 對 Fresh-Session BM25 Expansion 的不同意見**
>
> AliceLJY 和 rwmjhb 對 fresh-session BM25 expansion 問題給出了衝突的指導。本 issue 請求 maintainer team 做出最終裁決。
>
> **衝突點**：
>
> **AliceLJY 的立場**（在 Issue #513 comments 中獲准）：
> > "Fresh-session bypass 對 Phase 1 可接受——enrichment 需要有儲存的內容才能查詢，這是任何方法的固有限制。"
>
> **rwmjhb 的立場**（來自 PR #529 review）：
> > "核心功能對 fresh sessions 無效——`expandDerivedWithBm25BeforeRank()` 在 `derived.length === 0` 時直接 `return []`，所以零先前 reflection 歷史的 sessions 仍然沒有 BM25 neighbors。"
>
> rwmjhb 將 PR #529 以 BLOCKING 方式關閉，表示 fresh-session early return 是不可接受的，因為所聲稱的使用案例被實作方式破壞了。
>
> **具體的 Blocking 問題**：
> 1. **Fresh-session early return (D1)**：`derived.length === 0` → `return []` 對新 sessions 完全繞過 BM25 擴展
> 2. **TypeScript 編譯錯誤**：`candidateTimestamp` 在 `.then()` callback 解構中被丟棄
>
> **請求 Maintainer 裁決的問題**：
> 1. 當 AliceLJY 和 rwmjhb 不同意時，誰有最終決定權？是否應該將 rwmjhb 的 review 視為 blocking？
> 2. Fresh-session 行為：BM25 擴展是否應該對 `derived.length === 0` 的 sessions 有效？如果是，應該用什麼查詢材料？
> 3. PR 重新開啟：是否應該用包含已修復 commits 的 #529 重新開啟，或者開一個新的 PR？
> 4. 範圍縮小：專注於 fresh-session 修復的較小 PR（不包含完整 BM25 擴展）是否更容易被接受審查？

#### Comment 4 — jlin53882（2026-04-06 06:19 UTC）
> 參見 Issue #538 中的詳細 B-2 提案討論。Issue #538 涵蓋：
> - B-2 Neighbor Enrichment 架構（在 retrieval time 擴展，而非 reflection load time）
> - 關於 BM25 vs vectorSearch、MMR 排序、gating 和 B-1 關係的開放問題
> - 等候 maintainer 確認的提議下一步

---

## 三、Issue #538 — [Question] B-2 Neighbor Enrichment: Confirm direction before implementation

| 欄位 | 內容 |
|------|------|
| **標題** | [Question] B-2 Neighbor Enrichment: Confirm direction before implementation |
| **狀態** | OPEN |
| **標籤** | 無 |
| **作者** | jlin53882 |

### Issue Body 摘要

與 Issue #513 body 相同，是正式請求 maintainer 在實作前確認 B-2 方向的 issue。Body 中包含相同的流程圖與 4 個 Open Questions。

### Comments（#538）

#### Comment 1 — AliceLJY（2026-04-06 12:45 UTC）
> 感謝 jlin53882 在開始實作前確認方向，這是很好的工作習慣。
>
> **關於 B-2 方向**：B-2（retrieval-time neighbor enrichment）的整體方向是合理的，相比 B-1（load-time reflection slice enrichment）有明確的優勢：
> 1. **適用範圍更廣**：不依賴 derived reflection slices 是否存在，fresh session 也能受益
> 2. **架構更簡單**：在 retrieval pipeline 的一個明確位置插入，不需要修改 reflection store 的寫入邏輯
>
> **對 4 個 Open Questions 的建議**：
>
> **Q1: BM25 vs Vector search for neighbors**  
> 建議 **BM25**。理由：
> - 主檢索已經包含了 vector search，neighbor enrichment 的目標是補充語義相似但詞彙相關的上下文
> - BM25 能找到與 recall 結果詞彙重疊的相鄰記憶，與 vector search 形成互補
> - 如果 neighbor 也用 vector search，容易和主檢索結果高度重疊，enrichment 價值下降
>
> **Q2: Insertion point — before or after MMR**  
> 建議 **在 MMR 之後插入**。理由：
> - MMR 負責多樣性保障，應該先讓 top-K 通過 MMR 去重
> - Neighbor enrichment 是對 top-K 結果的補充（附加上下文），而非額外候選
> - 如果在 MMR 之前插入，neighbor 可能影響 MMR 的多樣性計算
>
> **Q3: Gating mechanism**  
> 建議 **config flag 控制，預設 disabled**。理由：
> - B-2 是新行為，需要使用者 opt-in，避免改變現有檢索行為
> - 可以在後續版本驗證穩定後改為預設 enabled
> - 例如：`retrieval.neighborEnrichment.enabled: true`
>
> **Q4: 是否與 B-1 共享程式碼**  
> 建議 **保持獨立**。B-1 和 B-2 的觸發時機、資料流、作用物件完全不同：
> - B-1 作用於 reflection slices（write path）
> - B-2 作用於 recall results（read path）
> 硬共享程式碼容易造成耦合。如果有共用的 BM25 查詢邏輯，可以抽取為 utility function，但 enrichment 邏輯本身應該獨立。
>
> **關於 B-1 的處理**：PR #529 已關閉。建議：
> - **先聚焦 B-2**，B-1 暫不重開
> - 如果後續有場景需要 write-time enrichment，再單獨評估 B-1
>
> **Next Steps**：
> 1. 基於以上方向，可以開始 B-2 的 implementation PR
> 2. 建議 PR 中包含一個簡單的 benchmark（對比 enrichment 前後的 recall 品質），方便 review 評估效果
> 3. config flag + 預設 disabled，降低合入風險

#### Comment 2 — jlin53882（2026-04-06 13:16 UTC）
> **B-2 方向確認收到，追加 5 個實作缺口**
>
> 謝謝 Q1-Q4 的詳細答案，B-2 的實作方向現在非常清晰。基於這些確認，提出 5 個在實作前需要先確定的點：
>
> **Q5：MMR 去重是否會消滅 neighbors？【🔴 阻塞】**
>
> B-2 的插入點在 `applyMMRDiversity` 之後，但 MMR 的核心功能是「對相似的 items 去重」。如果某個 neighbor 與 MMR 選中的 result 相似度過高，**MMR 已經在去重階段把它刪掉了**。
>
> 執行流程：
> ```
> applyMMRDiversity(top-K)
>   → 相似 items 被刪除，某些潛在 neighbors 也消失
>   → B-2 在 MMR 這時才插入，只對「還活著的」items 找 neighbors
>   → 被 MMR 刪掉的 neighbors 永遠找不到
> ```
> 問題：neighbor enrichment 是在 MMR 去重**前**還是**後**執行？如果在 MMR 之後，是否有補救機制找回被 MMR 預先刪掉的潛在 neighbors？
>
> **Q6：`vectorOnlyRetrieval()` 路徑的 B-2 如何實作？【🔴 阻塞】**
>
> B-2 流程圖是基於 `hybridRetrieval()`：
> - ✅ hybrid path 有 `bm25Search()` → 可直接對 recall results 做 neighbor lookup
> - ❌ `vectorOnlyRetrieval()` **沒有 BM25 search 階段** → 如何找 neighbors？
>
> 問題：B-2 是否只實作在 hybrid path？vector-only path 是否需要不同的 neighbor 實作方式？
>
> **Q7：Neighbor search 的 scope boundary 如何決定？**
>
> - 以 recall result 的 scope 為準？每個 result 各自在自己的 scope 內找 neighbor
> - 以 query 本身的 scope 為準？所有 neighbors 都用 query 的 scope filter
> - 跨 scope 的 recall results：neighbor search 的 scope filter 用哪一個？
>
> **Q8：B-2 的 Phase 4 依賴關係被跳過，觸發條件是否重新定義？【🟡 需確認】**
>
> 依據 Issue #445 的設計文件，B-2 原為 **Phase 4**：觸發條件為「Phase 1（B-1 reflection neighbor enrichment）運行 1 個月無異常」。但目前的方向是「先聚焦 B-2，B-1 暫不重開」，意味著 B-2 的觸發條件從「B-1 穩定 1 個月」變成「直接實作」，缺少 Phase 1 的實證基礎。
>
> **Q9：BM25 neighbor lookup 的輸入範圍？Neighbors 如何附加？【🟡 需確認】**
>
> - **Input scope**：對所有 recall results 找 neighbors？還是只對 MMR 過濾後的 top-K？
> - **Neighbors 的數量**：每個 result 找固定 topK=2 嗎？
> - **附加方式**：
>   - A. 作為附屬上下文（`enriched.text = original.text + "\n\nNeighbors: ..."`）
>   - B. 作為額外候選列表（`results = [...topK, ...neighbors]`）
>   - C. 其他？
> - **Output 結構**：最終 return 的 items 是否包含 neighbors？還是 neighbors 只作為 injection context 不出現在 return 中？
>
> **建議的 Next Steps**：
> ```
> 1. 確認 Q5-Q9（本次回覆）
> 2. 開啟 B-2 實作 issue（包含 neighbor scope、input range、附加方式等設計決策）
> 3. Implementation PR + benchmark
> 4. Review → Merge
> ```

---

## 四、Issue #514 — Proposal: Per-agent exclusion mechanism for before_prompt_build hooks

| 欄位 | 內容 |
|------|------|
| **標題** | Proposal: Per-agent exclusion mechanism for before_prompt_build hooks (related to #492) |
| **狀態** | OPEN |
| **標籤** | 無 |
| **作者** | jlin53882 |

### Issue Body 摘要

**問題背景**：Issue #492 描述了 `memoryReflection` hooks 在 `before_prompt_build` 中同步執行 LanceDB 查詢，導致 30-50% 的 user sessions 無法產生回覆。根本原因是兩個 `before_prompt_build` hooks（priority 12 和 15）呼叫 `await loadAgentReflectionSlices()`（執行 `store.list()`——一個在 prompt build 期間的 blocking DB 操作）。

**提案解決方案**：透過現有的 `autoRecallExcludeAgents` config 欄位，擴展以保護 `memoryReflection` hooks 的 per-agent 排除機制。

**變更（PR #516）**：

1. **新 helper function `isAgentOrSessionExcluded`**
   - 支援三種 pattern 類型：exact match（`memory-distiller`）、wildcard prefix（`pi-` 匹配 `pi-agent`、`pi-coder`）、special `temp:*` 給內部 reflection sessions

2. **修復 auto-recall `before_prompt_build` 排除檢查**
   - 移除無效的 `agentId !== undefined` 檢查（因為 `|| "main"` fallback 永遠為 true）

3. **在兩個 reflection `before_prompt_build` hooks（priority 12 & 15）加入排除檢查**
   - 兩個 hooks 都先有 `isInternalReflectionSessionKey` guard，再做 `isAgentOrSessionExcluded` 檢查

4. **三層 guard 保護 `runMemoryReflection` command hook**
   - Internal session guard
   - Re-entrant guard（global lock via `Symbol.for` + `globalThis`）
   - Serial cooldown guard（120s）

5. **`appendSelfImprovementNote` 加入 internal session guard**
   - 與 `agent:bootstrap` hook 行為一致

6. **增強 early-return logging**
   - 所有 early returns 現在都包含 `sessionKey/sessionId` 以便觀測

**Protection Matrix：**

| Hook | 防護方式 |
|------|----------|
| `before_prompt_build`（auto-recall） | exclusion check |
| `before_prompt_build`（priority 12） | isInternal guard + exclusion |
| `before_prompt_build`（priority 15） | isInternal guard + exclusion |
| `command:new/reset -> runMemoryRefl.` | 三層 guard |
| `appendSelfImprovementNote` | internal session guard |

**使用方式：**
```json
{
  "memory-lancedb-pro": {
    "autoRecallExcludeAgents": ["memory-distiller", "pi-", "temp:*"]
  }
}
```

**向 Maintainers 提問**：
1. 這個方法可以接受嗎？`autoRecallExcludeAgents` 現在同時服務 auto-recall 和 reflection exclusion 兩個目的
2. 是否應該拆分為 `reflectionExcludeAgents` 以提高清晰度？
3. 120s cooldown（`SERIAL_GUARD_COOLDOWN_MS`）合理嗎？應該可配置嗎？
4. 對使用 `globalThis` + `Symbol.for` 處理 lock maps 有疑慮嗎？

### Comments（#514）

#### Comment 1 — jlin53882（2026-04-04 10:39 UTC）
> 另見：
> - 原始問題：#492
> - 實作：PR #516（取代已關閉的 PR #515）

#### Comment 2 — jlin53882（2026-04-04 13:38 UTC）
> 實作已更新：PR #520（取代 #515 和 #516）。現在在 `openclaw.plugin.json` schema 中包含可配置的 `serialCooldownMs`。
>
> 使用範例（`openclaw.json`）：
> ```yaml
> memory-lancedb-pro:
>   memoryReflection:
>     serialCooldownMs: 60000
> ```

---

## 五、脈絡總覽與關聯圖

```
#246 (Feature Request: Dynamic Importance & Memory Attention Network)
  │
  └── #445 (RFC: Proposal A & B Implementation Analysis) ──── 源頭 RFC
        │
        ├── Proposal A (動態重要性)
        │     ├── Phase 1 → PR #493 ✅
        │     ├── Phase 2 → 被 #505 取代
        │     └── Phase 3 → PR #505, Phase 4 → PR #506
        │
        └── Proposal B (Neighbor Enrichment)
              ├── B-1 (Reflection-scoped) ──→ PR #529 ❌ CLOSED (rwmjhb blocking)
              │     └── PR #523（新版本，等待審查中）
              │
              └── B-2 (Full Retrieval) ──→ #513（衝突討論）+ #538（方向確認）
                    │
                    └── Issue #538 Comment 1: AliceLJY 確認方向
                    └── Issue #538 Comment 2: jlin53882 追加 Q5-Q9（待回覆）

#492 (問題：memoryReflection hooks 造成 30-50% sessions 失敗)
  │
  └── #514 (提案：Per-agent exclusion mechanism)
        ├── PR #515 ❌ CLOSED
        ├── PR #516 ❌ CLOSED
        └── PR #520 ✅ 實作版本
```

---

## 六、關鍵張力與待解決問題

### 1. B-1 vs B-2 誰先誰後？
- AliceLJY 在 #538 建議「先聚焦 B-2，B-1 暫不重開」
- 但 #445 的原始分析認為 B-1 應該先做（作為 B-2 的驗證場）
- **目前狀態**：B-2 方向已獲確認（Q1-Q4 已答覆），但 Q5-Q9（包含 MMR 衝突、vector-only path 等）仍未回覆

### 2. AliceLJY vs rwmjhb 對 fresh-session 的衝突
- AliceLJY：「fresh-session bypass 可接受」
- rwmjhb：「核心功能對 fresh sessions 無效，BLOCKING」
- PR #529 被 rwmjhb 以 BLOCKING 方式關閉
- **目前狀態**：衝突未解決，Issue #513 中請求 maintainer 裁決，但尚未有回覆

### 3. B-2 的五個實作缺口（Q5-Q9）
Issue #538 的 Comment 2 由 jlin53882 提出，仍**待 maintainer 回覆**：
- Q5（🔴 阻塞）：MMR 去重會不會消滅 neighbors？
- Q6（🔴 阻塞）：`vectorOnlyRetrieval()` 路徑如何實作 B-2？
- Q7：Neighbor search 的 scope boundary 定義
- Q8（🟡）：B-2 的 Phase 4 依賴關係被跳過是否合理？
- Q9（🟡）：BM25 neighbor lookup 的輸入範圍與附加方式

### 4. Issue #514 的實作演進
- PR #516 → 被 PR #520 取代（加入可配置的 `serialCooldownMs`）
- 四個向 maintainers 的問題（Q1-Q4）**尚未得到回覆**

---

## 七、總結

| Issue | 主題 | 核心狀態 |
|-------|------|----------|
| #445 | RFC 源頭（Proposal A & B 分析） | OPEN，7 comments，主要問題獲 AliceLJY 回覆 |
| #513 | B-2 Phase 1 重新設計討論 | OPEN，4 comments，存在 AliceLJY vs rwmjhb 衝突待裁決 |
| #538 | B-2 Neighbor Enrichment 方向確認 | OPEN，2 comments，Q1-Q4 已回覆，Q5-Q9 待回覆 |
| #514 | Per-agent exclusion mechanism | OPEN，2 comments，四個 maintainer 問題未回覆 |

**主要趨勢**：
- B-2（retrieval-time neighbor enrichment）已獲 AliceLJY 初步認可，但具體實作仍有 Q5-Q9 等阻塞問題
- B-1（reflection-scoped BM25 expansion）被 rwmjhb 以 BLOCKING 方式否決後，社群轉向 B-2
- 動態重要性（Proposal A）進展順利，PR #493 已完成，後續還有多個 Phase PR 在 chain 中
- `before_prompt_build` hooks 的效能問題（#492/#514）已提出多版實作，進入可審查狀態
