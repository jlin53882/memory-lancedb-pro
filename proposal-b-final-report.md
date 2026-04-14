# Proposal B 實作前衝突分析完整報告（最終版）

> 整理日期：2026-04-09
> 整理者：AI 程式修改助手
> 分析層次：主體分析 + 2 個 Sub-agent 交叉分析 + Claude Code MiniMax M2.7 對抗式 Review
> 資料來源：proposal-b-analysis.md、proposal-b-issue-details.md、proposal-b-pr-details.md、proposal-b-codebase-conflicts.md、proposal-b-missed-issues.md、上游 `memory-lancedb-pro-master/src/`
> Claude Code 對抗式審查工具：Claude Code CLI（MiniMax M2.7）

---

## 零、對抗式 Review 發現的最大錯誤

> ⚠️ **在繼續閱讀之前，先看這裡——報告有兩個根本性的錯誤**

### 錯誤 1：將「BM25 neighbor lookup」和「BM25 search」當成同一個東西

這是報告最嚴重的概念混淆：

- `runBM25Search()`（步驟 2）是**用戶 Query 找相關文件**的搜尋引擎
- B-2 的 neighbor lookup 是**對每個 recall result 做 secondary lookup**
- 兩者輸入/輸出/目的**完全不同**
- 報告說「B-2 在步驟 2 的 Promise.all 中」是**完全錯誤的**——BM25 neighbor lookup 是步驟 2 的輸出的**消費者**，不是步驟 2 的一部分

### 錯誤 2：衝突 A 的三個方案都基於錯誤假設

報告說「如果是對每個 recall result 做獨立的資料庫查詢，則 MMR 完全不影響」，但立刻又說需要 maintainer 確認。

**實際上這個假設完全可以自己決定**——B-2 neighbor lookup 的輸入就是每個 recall result 本身，這是功能需求，不是架構約束。

---

## 一、上游最新 Pipeline（hybridRetrieval）精確順序

```
1.  embedQuery() + buildBM25Query()
2.  Promise.all([runVectorSearch(), runBM25Search()])   ← 這是「用戶 Query 找文件」
3.  fuseResults()                                       ← RRF fusion
4.  filter: score >= minScore
5.  filter: !isMemoryExpired()                         ← #8111e26 移至此
6.  rerankResults()
7.  applyRecencyBoost()
8.  applyImportanceWeight()
9.  applyLengthNormalization()
10. filter: score >= hardMinScore
11. applyDecayBoost() 或 applyTimeDecay()
12. filterNoise()
13. applyMMRDiversity()                                ← MMR 多樣性去重
14. slice(0, limit)
15. return

B-2 Neighbor Lookup 應該插入在哪裡？
→ 對每個 recall result 的 text 做獨立的 vectorSearch()/bm25Search() 查詢
→ 不是 MMR 的消費者，是 recall result 的消費者
→ MMR 是否影響，取決於 B-2 的輸入是「recall results 本身」還是「MMR 輸出」
```

---

## 二、🔴 高優先級衝突（需要馬上處理）

### 衝突 P0-1：Neighbors 的重複計分問題（memory leak）

| 項目 | 內容 |
|------|------|
| **提出者** | Claude Code 對抗式 Review |
| **緊急度** | 🔴 **P0 — 最高優先級** |
| **狀態** | ❌ **從未被任何報告提及，這是新發現** |

**問題**：

如果 B-2 neighbors 被附加到 recall results 作為 context，這些 neighbors 本身會不會在下一輪（用戶下一個 query）被當成獨立的 recall results 被召回？

```
用戶 Query A
  → recall results: [memory_1, memory_2]
  → B-2 neighbors: [neighbor_a, neighbor_b]
  → 輸出: [memory_1 + neighbor_a, memory_2 + neighbor_b]

用戶 Query B
  → recall results: [memory_1, memory_2, neighbor_a, neighbor_b]  ← 上一輪的 neighbors 被當成獨立記憶召回
  → B-2 neighbors: [neighbor_a2, neighbor_b2, neighbor_a3...]
  → 無限擴展 = memory leak
```

**解決方案**：
在 B-2 的 neighbor lookup 中加入去重機制，確保 neighbors 不會被重複選中為 recall results。或者在下一輪的 recall 中標記這些是 neighbors，讓它們不會再次被 B-2 擴展。

**這是功能性的 bug，不解決的話 neighbor enrichment 會造成 memory leak。**

---

### 衝突 P0-2：Schema 版本與向後相容

| 項目 | 內容 |
|------|------|
| **提出者** | Claude Code 對抗式 Review |
| **緊急度** | 🔴 **P0 — 最高優先級** |
| **狀態** | ❌ **從未被任何報告提及，這是新發現** |

**問題**：

B-2 如果新增 `neighborEnrichment` config flag 和任何新的 return 欄位，這些是否需要 schema migration？任何 consumer 如果依賴目前的 return type，會不會 break？

**需要在實作前確認**：
- `hybridRetrieval()` 的 return type 是否改變？
- 如果 B-2 的 neighbors 附加在 text 裡（不新增 return 欄位），則 schema 不受影響
- 如果有新的 return 欄位，需要確認所有 consumer 是否能接受

---

### 衝突 P0-3：Q6 — neighbor lookup 用 BM25 還是 vector？

| 項目 | 內容 |
|------|------|
| **緊急度** | 🔴 **P0** |
| **狀態** | ❌ **從未得到回覆** |

**分析**：

如果 B-2 用 `vectorSearch()` 而非 `bm25Search()` 做 neighbor lookup：
- `vectorOnlyRetrieval()` path 完全不需要擔心
- Neighbor lookup 是 semantic similarity，不是 keyword overlap
- 與 B-1（BM25）不一致，但這是正確的 trade-off

**如果用 vector search，衝突 B 和衝突 G 都是假議題。**

---

### 衝突 P1-1：衝突 A（MMR 衝突）

| 項目 | 內容 |
|------|------|
| **緊急度** | 🟡 P1（原本 🔴）|
| **狀態** | 降級——如果不是對 MMR 輸出做查詢，則 MMR 完全不影響 |

**重新分析**：

如果 B-2 是對每個 recall result 做獨立的資料庫查詢（`vectorSearch(result.text, topK=2, scope=result.scope)`），則 MMR 完全不影響 B-2 的 neighbors 範圍。

**建議**：
> 在 PR 中明確說明「B-2 neighbor lookup 是對每個 recall result 的 text 做獨立的 vectorSearch() 查詢，不是對 MMR 輸出做查詢」。如果 maintainer 有不同意見，可以在 review 中討論。

---

### 衝突 P1-2：權力問題（AliceLJY ✅ vs rwmjhb ❌）

| 項目 | 內容 |
|------|------|
| **緊急度** | 🟡 P1（原本 🔴）|
| **Workaround** | 如果 repo 允許單一 maintainer merge，則下一個 PR 只提給 rwmjhb |

**注意**：如果 repo 要求所有 maintainers 的 approval 才能 merge，則提給 rwmjhb 不提給 AliceLJY 不會繞過問題。需要確認 repo 的 merge policy。

---

## 三、🟡 中優先級衝突（在 PR 中說明即可）

### 衝突 D：expiry_filter 與 B-2 的互動

| 項目 | 內容 |
|------|------|
| **提出者** | Sub-agent 衝突分析 |
| **緊急度** | 🟡 P2 |

**重新分析**：

如果 B-2 是對每個 recall result 做獨立的資料庫查詢，則 expiry_filter 只影響「哪些 recall results 有機會被擴展」，不影響 B-2 找 neighbors 時是否找到 expired entries。

**真正需要確認的**：B-2 的 `vectorSearch()` 或 `bm25Search()` 本身是否支持 `excludeInactive` 選項。

---

### 衝突 E：auto-supersede（#452）與 B-1 的 interaction

| 項目 | 內容 |
|------|------|
| **提出者** | Sub-agent 衝突分析 |
| **緊急度** | 🟡 P2 |

**重新分析**：

需要確認 `store.bm25Search()` 是否有 `invalidated_at` filter。如果沒有，這是 store API 的 enhancement request，不是 B-1 的實作問題。

---

### 衝突 G：pipeline 插入點的兩種說法

| 說法 | 來源 | 內容 |
|------|------|------|
| AliceLJY | Issue #538 Q2 | 在 MMR 之後插入 |
| jlin53882 | Issue #538 Comment 2 | 在 MMR 之前插入 |

**重新分析**：

如果 B-2 是對每個 recall result 做獨立的資料庫查詢，則 MMR 完全不影響 neighbors 的範圍。此時 AliceLJY 和 jlin53882 的爭論是**假議題**——插入點在 MMR 之前或之後都不影響 neighbors 的範圍，因為 MMR 管不到獨立的資料庫查詢。

**建議**：在 PR 中明確說明這個分析，讓 maintainer 知道這個討論是基於錯誤的前提。

---

## 四、✅ 低優先級衝突

### 衝突 F：temporal-awareness（#453）— **降級為 🟢**

`temporalType: "dynamic"` 的 3x decay 是 neighbors 自身的屬性，不需要在 B-2 中做特殊處理。只要 neighbors 的 `temporalType` 欄位是正確設定的（這是上游 B-1 的責任），B-2 不需要做任何處理。

---

### 衝突 H：tier-manager 的 promotion 門檻 — **✅ 無衝突**

`coreImportanceThreshold = 0.8` 與 Proposal A 的 feedback 機制相容。

---

### 衝突 I：Scope boundary — **✅ 可以自己決定**

用 recall result 各自的 scope 作為 neighbor search 的 scope filter。

---

### 衝突 J：B-1 與 B-2 的依賴關係 — **🟡 部分有效**

B-1 是 B-2 的 smoke test，不可能完全獨立。但這不意味著 B-1 必須先 merge——只要 B-2 的實作足夠完整，可以不依賴 B-1 的驗證。

---

## 五、Claude Code Review Checklist 對抗式審查結果

| 檢查項 | 結果 |
|--------|------|
| Schema 新增欄位 → 確認有對應實作讀取 | ⚠️ B-2 的 config flag 需要在 `parsePluginConfig()` 中解析；neighbors 是否出現在 return 陣列需要確認 |
| Pattern matching 函式 → 提供邊界條件測試 | ⚠️ `applyMMRDiversity` 的相似度 threshold 需要測試 |
| 常數/函式定義 → 確認沒有被取代後遺留 | ✅ 無此問題 |
| 改動範圍 → 只涵蓋需要修改的範圍 | ⚠️ 需要確認 B-2 只改 `retriever.ts`，不影響其他檔案 |
| Error logging → 確認錯誤處理完整 | ⚠️ B-2 的 vectorSearch/bm25Search failure 需要 fail-safe |
| 向後相容 → 確認沒有破壞性變更 | ⚠️ 需要確認 return type 不受影響 |
| **新增：Memory leak** | ❌ **Neighbors 重複計分問題從未被報告提及** |
| **新增：Schema 向後相容** | ❌ **從未被報告提及** |

---

## 六、最終優先級清單（對抗式 review 版）

| 優先級 | 衝突 | 行動 |
|--------|------|------|
| 🔴 P0 | **Neighbors 重複計分（memory leak）** | 馬上設計解決方案，加入 PR |
| 🔴 P0 | **Schema 向後相容** | 確認 B-2 是否改變 return type |
| 🔴 P0 | **Q6（neighbor lookup 用 BM25 還是 vector）** | 決定後可以降級衝突 B 和 G |
| 🟡 P1 | **衝突 A（MMR）** | 確認 neighbor lookup 是獨立查詢後降級 |
| 🟡 P1 | **衝突 C（權力）** | 確認 repo merge policy 後降級 |
| 🟡 P2 | **衝突 D/E（expiry/auto-supersede）** | 確認 store API 是否支援過濾選項 |
| 🟢 P3 | **衝突 F（temporal-awareness）** | 不需要特殊處理 |
| 🟢 P3 | **衝突 H/I/J** | 無需 blocking |

---

## 七、給 James 的行動清單

### 馬上要做的 2 件事

1. **去 Issue #538 回覆**（直接複製貼上）：

> @AliceLJY @rwmjhb 在實作 B-2 之前，需要確認一個核心問題：B-2 的 neighbor lookup 是對每個 recall result 的 text 做獨立的 vectorSearch()/bm25Search() 查詢，還是對 MMR 輸出做一次查詢？如果是前者（這是合理的功能需求），則：
> 1. MMR 完全不影響 B-2 的 neighbors 範圍——衝突 G 是假議題
> 2. expiry_filter 只影響「哪些 recall results 有機會被擴展」，不影響 neighbors 本身
> 3. vector-only path 可以實作 B-2——衝突 B 是假議題（如果用 vector search）
>
> 另外，B-2 neighbors 是否會在下一輪被當成獨立記憶召回（memory leak 問題）？需要在實作中確認。

2. **設計 Neighbors 去重機制**（不等 maintainer 回覆，先自己想清楚）：
   - 選項 A：在 neighbor lookup 中過濾掉即將被召回的 neighbors
   - 選項 B：在下一輪 recall 中標記 neighbors，讓它們不參與 B-2 expansion
   - 選項 C：限制 neighbors 的 scope 或 category，讓它們不易被召回

### 可以自己決定的 5 個問題

| 問題 | 決策 |
|------|------|
| Scope boundary | 用 recall result 各自的 scope |
| B-2 input range | 只對 MMR 之後的 top-K results 做 enrichment |
| Neighbors 附加方式 | 作為附屬上下文（`text + "\n\n--- Related ---\n" + neighbor.text`）|
| B-1 與 B-2 依賴 | 兩者可以獨立實作 |
| B-2 trigger | config flag 控制，預設 disabled |
