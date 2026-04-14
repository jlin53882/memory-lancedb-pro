# Proposal B 被忽略的問題點分析

> 整理日期：2026-04-09
> 整理者：AI 程式修改助手（Subagent）
> 資料來源：proposal-b-analysis.md、proposal-b-pr-details.md、proposal-b-issue-details.md

---

## 被忽略的問題（Q5-Q9 狀態）

### Q5 — MMR 去重是否會消滅 neighbors？
**標記緊急度：🔴 阻塞**
**狀態：❌ 未回覆，但在邏輯上可以自己推導**

**分析：**

AliceLJY 在 Issue #538 Comment 1 明確說「在 MMR 之後插入」B-2，理由是 MMR 負責多樣性保障，neighbor enrichment 是對 top-K 結果的補充。

但這裡有一個內在矛盾：

```
hybridRetrieval()
  → applyMMRDiversity(top-K)    ← MMR 刪除相似 items
  → enrichWithNeighbors()       ← B-2 在這裡插入（MMR 之後）
  → return top-K results
```

MMR 已經把「與現有結果太相似的 items」砍掉了，所以 B-2 在 MMR 之後執行時，能找到的 neighbors 數量會大幅減少。

**可以自己決定的點**：
> 將 B-2 的插入點改為 MMR **之前**，讓 neighbors 在 MMR 去重之前就進入候選池。這樣 MMR 可以在 neighbors 與原始結果之間做更好的多樣性取捨。

**需要向 reviewer 交代的點**：
> 如果維持 MMR 之後的設計，則需要說明：為什麼接受 neighbors 數量減少的代價？這個代價是否合理？

---

### Q6 — `vectorOnlyRetrieval()` 路徑的 B-2 如何實作？
**標記緊急度：🔴 阻塞**
**狀態：❌ 未回覆，需要自己實作决策**

**分析：**

B-2 的設計圖是基於 `hybridRetrieval()`（有 `bm25Search` 階段）。但 `vectorOnlyRetrieval()` 路徑完全沒有 BM25 search，無法直接套用 B-2 的 neighbor lookup。

**選項分析：**

| 選項 | 優點 | 缺點 |
|------|------|------|
| A. 只實作 hybrid path，vector-only 跳過 B-2 | 簡單，符合「先做核心路徑」原則 | 功能不完整，vector-only users 體驗不一致 |
| B. 對 vector-only 也做一次 BM25 search | 功能完整一致 | 增加一次額外查詢，違背 vector-only 的初衷（節省時間）|
| C. vector-only 用 vector search 找 neighbors | 不需要 BM25，架構統一 | 與 B-1（BM25）不一致，neighbors 類型改變 |
| D. 兩者皆做：hybrid 用 BM25，vector-only 用 vector | 最完整 | 最複雜，可能需要合併邏輯 |

**建議**：選項 A（先只實作 hybrid path），在 PR 中說明 vector-only 的限制。這符合 AliceLJY 的「先做核心路徑、scope 精簡」的建議。

---

### Q7 — Neighbor search 的 scope boundary 如何決定？
**標記緊急度：🟡 需確認**
**狀態：❌ 未回覆，但有隱含共識可以自己推斷**

**分析：**

AliceLJY 在 Issue #445 Comment 1 說：「Neighbor enrichment 預設僅限相同 scope」，以及 Issue #538 Comment 1 說「BM25 能找到與 recall 結果詞彙重疊的相鄰記憶」。

從 PR #503 的實作可見，`bm25Search(text, topK=2, scopeFilter=[entry.scope])` 明確用 `entry.scope` 作為 scope boundary。

**Scope boundary 推斷（可自己決定）：**

> 每個 recall result 用**自己的 scope** 去找 neighbors，不論 query 的 scope 為何。

這樣的好處：
1. 符合「相同 scope」的約束
2. 每個 result 獨立的 scope filter 不會跨 scope 污染
3. 跨 scope 的 recall results 各自在自己的 scope 內找 neighbor，不會有 scope 衝突

---

### Q8 — B-2 的 Phase 4 依賴關係被跳過，觸發條件是否重新定義？
**標記緊急度：🟡 需確認**
**狀態：❌ 未回覆**

**分析：**

原始 Issue #445 的實作順序是：
```
A-Phase1 → B-1 → A-Phase2 → B-2 (Phase 4: B-1 穩定後)
```

但後來 AliceLJY 在 #538 Comment 1 說「先聚焦 B-2，B-1 暫不重開」，完全跳過了 B-1 驗證的步驟。

**自己可以做的決定**：
> B-2 的觸發條件從「B-1 穩定 1 個月」改為「config flag 控制的 opt-in 行為」，預設 disabled。

這相當於用 config 替換了時間驗證，是合理的替代方案。但需要在 PR 中說明這個 design change。

---

### Q9 — BM25 neighbor lookup 的輸入範圍？Neighbors 如何附加？
**標記緊急度：🟡 需確認**
**狀態：❌ 未回覆，需要自己決定**

**Input range（可以自己決定）：**
> 只對 MMR 過濾後的 top-K results 做 B-2 enrichment，而非對所有 recall results。

這符合 AliceLJY「neighbors 是對 top-K 結果的補充」的定位。

**附加方式（可以自己決定）：**
> **選項 A（推薦）**：作為附屬上下文，合併進 entry.text。
> ```
> enriched.text = original.text + "\n\n--- Related Memory ---\n" + neighbor.text
> ```
> 理由：不需要改變 return 結構，neighbors 只作為額外上下文注入 prompt。

**Output 結構（可以自己決定）：**
> Neighbors 只作為 injection context，不出現在 return 的 items 陣列中。

這與 AliceLJY「neighbors 是對 top-K 結果的補充」的定位完全一致。

---

## 被忽略的衝突（B-1 vs B-2 依賴關係）

### 衝突點 1：AliceLJY 的前後不一致

| 時間 | 發言 | 內容 |
|------|------|------|
| Issue #445 Comment 3（2026-04-03）| AliceLJY | 「B-1 仍然是驗證場。若要繼續 B-2，保持 scope 精簡。」 |
| Issue #538 Comment 1（2026-04-06）| AliceLJY | 「先聚焦 B-2，B-1 暫不重開」 |

**分析**：

第一句話暗示 B-1 是 B-2 的必要前置條件；第二句話則完全繞過 B-1 直接做 B-2。

從技術角度，如果 B-2 使用 retrieval-time enrichment 而非 reflection-load-time enrichment，則**兩者確實可以完全獨立實作**，因為：
- B-1 在 `reflection-slices.ts` 的 write path
- B-2 在 `retriever.ts` 的 read path
- 兩者沒有共享程式碼（B-1 用 BM25，B-2 用 BM25...但 AliceLJY 說保持獨立）

**結論（可以自己決定）**：
> B-1 和 B-2 可以完全獨立實作。AliceLJY 後來的發言（#538 Comment 1）可視為對依賴關係的更新。

---

### 衝突點 2：Issue #513 中 rwmjhb 的 BLOCKING 問題

Issue #513 Comment 3 提到 PR #529 被 rwmjhb 以 BLOCKING 關閉，理由有兩個：

#### 問題 1：`derived.length === 0` early return 使 fresh-session 無效

**狀態：❌ 仍然是 open 問題**

PR #529 被關閉後，沒有新的 PR 來修復這個問題。這個 early return 意味著：
- 沒有 prior reflection history 的 fresh session
- `derived.length === 0` → 直接 `return []`
- BM25 expansion 完全不執行

**對 B-2 的影響**：
> B-2 是 retrieval-time enrichment，不依賴 `derived.length`，所以**這個問題對 B-2 沒有影響**。但如果未來要重新開 B-1，這仍是 blocking 問題。

#### 問題 2：TypeScript 編譯錯誤（candidateTimestamp drop）

**狀態：❌ 仍然是 open 問題**

`candidateTimestamp` 在 `.then()` callback 的 destructuring 中被 drop，導致 `result.candidateTimestamp` 是 `undefined`。

**對 B-2 的影響**：
> 這個 bug 存在於 B-1 的實作中（`expandDerivedWithBm25BeforeRank()`），不直接影響 B-2。但如果 B-1 未來要重新開，需要一併修復。

---

## 被忽略的技術細節

### 1. Scope 的邊界在哪裡？

根據 PR #503 的實作：
```typescript
bm25Search(text, topK=2, scopeFilter=[entry.scope])
```

Scope boundary 就是 `entry.scope`。Neighbor enrichment 僅限相同 scope 內。

**對 B-2 的影響**：
> B-2 的 neighbor scope boundary 也應該用 recall result 各自的 scope。這與現有 B-1 實作一致。

---

### 2. Issue #514 的 4 個問題全部未得到回覆

Issue #514 Comment 中向 maintainers 提出了 4 個問題：

| 問題 | 內容 | 目前狀態 |
|------|------|---------|
| Q1 | `autoRecallExcludeAgents` 同時服務 auto-recall 和 reflection exclusion 是否可接受？ | ❌ 未回覆 |
| Q2 | 是否應該拆分為 `reflectionExcludeAgents` 提高清晰度？ | ❌ 未回覆 |
| Q3 | 120s cooldown 是否合理？應該可配置嗎？ | ❌ 未回覆（但 PR #520 已實現 `serialCooldownMs` 可配置） |
| Q4 | 對使用 `globalThis` + `Symbol.for` 處理 lock maps 有疑慮嗎？ | ❌ 未回覆 |

**重要**：PR #520 已經實作了 `serialCooldownMs` 可配置參數，但 maintainers 從未確認這 4 個設計決策是否正確。

---

### 3. AliceLJY vs rwmjhb 的權力問題

Issue #513 Comment 3 中記錄了一個從未被回答的根本性問題：
> 「當 AliceLJY 和 rwmjhb 對一個功能意見不合時，誰有最終決定權？」

目前沒有共識機制。建議 James 在與 maintainer 溝通時提出這個問題。

---

### 4. Branch 檔案被誤刪的根本問題

PR #450、#456、#458 的關閉原因是「分支上的檔案在 rebase/cherry-pick 操作中被從 origin/master 刪除」，這不是代碼問題，而是基礎設施/操作失誤。

**對未來 PR 的影響**：
> 未來開 PR 時，需要確保 branch topology 正確，避免與 upstream/master 的歷史產生衝突。

---

## 行動分類清單

### 🔴 需要馬上問 maintainer 的問題（沒有答案就不能實作）

| # | 問題 | 為什麼沒有答案就不能實作 |
|---|------|------------------------|
| 1 | **Q6（Issue #538）**：`vectorOnlyRetrieval()` 路徑的 B-2 要怎麼處理？ | B-2 目前只設計了 hybrid path，vector-only path 完全沒有 neighbor lookup 的起點 |
| 2 | **Q5（Issue #538）**：B-2 插入點在 MMR 之前還是之後？ | 如果在 MMR 之後，neighbors 數量會大幅減少；如果在之前，違背 AliceLJY 的建議 |
| 3 | **AliceLJY vs rwmjhb 衝突**：誰有最終決定權？ | 否則下一個 PR 可能又被另一個人以 BLOCKING 關閉 |

---

### 🟢 可以自己決定的問題（可以在實作中自己做決定）

| # | 問題 | 建議的自己做決定的方向 |
|---|------|----------------------|
| 1 | **Q9 Input range** | 只對 MMR 之後的 top-K results 做 B-2 enrichment |
| 2 | **Q9 附加方式** | 作為附屬上下文合併進 entry.text，不改變 return 結構 |
| 3 | **Q7 Scope boundary** | 用 recall result 各自的 scope，與 B-1 實作一致 |
| 4 | **Q8 觸發條件** | 用 config flag 控制的 opt-in 替代「B-1 穩定 1 個月」的時間驗證 |
| 5 | **B-1 vs B-2 依賴關係** | 兩者完全獨立實作，以後者（AliceLJY #538 Comment 1）為準 |
| 6 | **vectorOnlyRetrieval() 處理方式** | 先只實作 hybrid path，在 PR 中說明限制 |

---

### 🟡 需要在 PR 中說明的問題（可以實作，但需要向 reviewer 交代）

| # | 問題 | 需要在 PR 中說明的內容 |
|---|------|----------------------|
| 1 | **MMR 之後的設計選擇** | 為什麼接受 neighbors 數量減少的代價？是否嘗試過 MMR 之前的設計？ |
| 2 | **B-2 不包含 B-1** | 為什麼跳過 B-1 直接做 B-2？依據是 AliceLJY #538 Comment 1 |
| 3 | **config flag 預設 disabled** | 為什麼預設關閉？這是降低 review 風險的策略 |
| 4 | **PR #520 的 4 個未回覆問題** | 在 B-2 PR 中一併說明這些設計決策的選擇理由 |
| 5 | **BM25 self-filter** | 需要過濾掉 `hit.entry.category === "reflection"` 的項目，避免自匹配 |

---

## 總結

**最關鍵的 3 件事**：

1. **Q5 和 Q6 是 B-2 實作的直接阻塞點**。Q5 可以自己決定（MMR 之前），但需要向 reviewer 交代；Q6 需要 maintainer 確認 vector-only path 的策略。

2. **rwmjhb 的 BLOCKING 是 B-1 的永久阻塞點**，但對 B-2 沒有影響。B-2 應該完全繞過 B-1 獨立實作。

3. **Issue #514 的 4 個問題在 PR #520 中已經被實作解決**，但 maintainer 從未確認。這些設計決策在 B-2 PR 中需要一併說明。
