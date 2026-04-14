# Issue #445 — Proposal A & B Implementation Analysis

## 基本資訊

| 欄位 | 值 |
|------|-----|
| **標題** | [RFC] Proposal A & B Implementation Analysis |
| **狀態** | Open |
| **作者** | jlin53882 |
| **建立時間** | 2026-04-01T16:36:31Z |
| **更新時間** | 2026-04-05T14:48:21Z |
| **Labels** | （無 labels） |
| **連結** | https://github.com/CortexReach/memory-lancedb-pro/issues/445 |
| **Related** | #246 |

---

## Issue 描述

### Context

Following up on #246. I've done a deep-dive analysis of the memory-lancedb-pro codebase to determine the best approach for implementing Proposal A and B.

### Key Findings

#### Existing systems (already in place)

| Mechanism | File | What it does |
|-----------|------|-------------|
| Frequency reinforcement | `access-tracker.ts` | High access count → longer half-life (up to 3x), via `log1p(effectiveAccessCount)` |
| Weibull decay | `decay-engine.ts` | `importance` modulates half-life: `effectiveHL = halfLife × exp(1.5 × importance)` |
| Tier promotion | `tier-manager.ts` | Core (β=0.8, slowest decay) / Working / Peripheral (β=1.3, fastest) |
| Importance weight in recall | `retriever.ts` | `applyImportanceWeight()`: `score *= (0.7 + 0.3 × importance)` |
| `last_confirmed_use_at` field | `smart-metadata.ts` | **Field exists but NOT actively used** in decay/boost calculations |
| `bad_recall_count` field | `smart-metadata.ts` | **Field exists but NOT actively triggered** |
| Reflection quality weighting | `reflection-store.ts` | `quality × logistic(age) × baseWeight` already implements dynamic decay |

#### Critical gap

The system has **frequency-based reinforcement** but **no feedback-based importance adjustment**. The `importance` field is written once at store time and never updated based on usage quality.

---

### Proposal A — Dynamic Importance (Recommended)

**Goal**: Make `importance` dynamic — not a one-time write, but adjusted after each recall based on usage quality.

#### Recommended feedback signals

| Signal | When to capture | Adjustment |
|--------|----------------|-----------|
| Memory was recalled AND used in response | `agent_end` — compare recall results vs final response | `importance += 0.05`, cap at 1.0 |
| User explicitly confirmed correctness | User says "correct"/"yes"/"right" | `importance += 0.15`, cap at 1.0 |
| User explicitly marked as wrong | User says "no"/"wrong"/"not right" | `importance -= 0.10`, floor at 0.1 |
| Recalled but never used (2+ consecutive times) | Next recall cycle check | `importance -= 0.03` |
| Long unused (>30 days) | Decay naturally handles this | No additional logic needed |

#### Why `agent_end` hook is the right place

- `before_agent_start` happens before the response, so it can't determine if memory was actually used
- `agent_end` has full `event.messages` — can compare recall results against the final response
- No new lifecycle triggers needed; just add a post-processing step to the existing `agent_end` flow

#### No changes needed to

- `decay-engine.ts` — it already reads `importance`; changes propagate automatically
- `tier-manager.ts` — Core promotion requires `importance >= 0.8`; dynamic importance naturally triggers/deters promotions
- `access-tracker.ts` — frequency tracking and importance adjustment are complementary, not conflicting

---

### Proposal B — Attention-Like Neighbor Enrichment (Recommended)

**Goal**: When a memory is recalled, proactively find its "neighbor" memories and bring them into context too.

#### Recommended path: B-1 (Reflection-focused, lower risk)

Reflection already has a neighbor-modeling mechanism in `loadAgentReflectionSlicesFromEntries()`. Extend it:

```
loadAgentReflectionSlicesFromEntries() → N results
  → For each result: bm25Search(text, topK=2, scope=same)
  → Merge + deduplicate
  → Output (originals + neighbors)
```

**Pros**: Contained within `reflection-store.ts`, doesn't affect main retrieval latency.
**Cons**: Only affects reflection memories, not the main memories table.

#### B-2 (Full retrieval, if B-1 proves valuable)

In `retriever.ts`, after MMR diversity and before returning results:
- For each recalled memory, do one more `vectorSearch(text, topK=2, scope=same)`
- Merge neighbors, re-sort by similarity + importance
- Cap: max 2 neighbors per recalled memory, total output cap 20 entries

**Note**: MMR diversity and neighbor enrichment may conflict — MMR pushes similar items later, neighbor enrichment brings them in. Need to adjust MMR order if implementing B-2.

---

### Why Proposal C is Excluded

| Concern | Reason |
|---------|--------|
| Classification accuracy | No session-level domain classifier exists; building one adds latency and can degrade results if wrong |
| Wrong classification cost | If the domain is misclassified, the wrong memories get boosted and right ones get diluted |
| A + B already covers the main need | A makes important memories last longer; B enriches context. C's benefit is unproven for this use case |
| Maturity | No user feedback indicating "context-aware recall is broken" |

---

### Proposed Implementation Order

1. **Proposal A Phase 1** — Add `agent_end` feedback loop (lowest risk, highest clarity)
2. **Proposal B Path B-1** — Neighbor enrichment in reflection recall
3. **Proposal A Phase 2** — Wire up `last_confirmed_use_at` and `bad_recall_count` triggers
4. **Proposal B Path B-2** — Main retrieval neighbor enrichment (if B-1 proves valuable)

---

### Questions for the Author

1. Does the feedback signal design (recall → used in response → importance boost) match your intent in #246?
2. For Proposal B — should neighbor enrichment be scoped to the same `scope` filter, or should it cross scopes?
3. Is there a specific use case driving Proposal C that we should reconsider for?

---

## 討論內容（時間線）

### Timeline 事件摘要（30 事件）

| 類型 | 數量 |
|------|------|
| cross-referenced | 18 |
| referenced | 5 |
| commented | 4 |
| assigned | 1 |
| mentioned | 1 |
| subscribed | 1 |

---

### Comment 1 — AliceLJY（2026-04-02T09:28:19Z）

> Impressive analysis — the codebase audit is thorough and the existing-mechanism inventory is exactly right.
>
> **Proposal A (Dynamic Importance):** Agree this is the highest-value change. The current `importance` being write-once is the most obvious gap. A few notes:
>
> - The `agent_end` hook placement is correct — it's the only point where you have both the recall results and the final response to compare
> - The adjustment magnitudes (+0.05/+0.15/-0.10/-0.03) look reasonable as starting points; they should be tunable via config since optimal values will depend on usage patterns
> - Consider adding a `min_recall_count` threshold before applying negative adjustments — a memory recalled only once and not used isn't necessarily bad, it might just be the wrong context for that session
>
> **Proposal B (Neighbor Enrichment):** B-1 (reflection-scoped) is the right starting point. The conflict you flagged between MMR diversity and neighbor enrichment is real — good to see it noted upfront. For B-1, since reflection slices are already a bounded set, the performance impact should be minimal.
>
> **Implementation order:** Agree with A-Phase1 → B-1 → A-Phase2 → B-2. Each stage can be validated independently.
>
> **To your questions:**
> - Q2: Neighbor enrichment should be scoped to the same `scope` filter by default — crossing scopes risks pulling in context that was intentionally partitioned
> - Q3: Proposal C exclusion rationale is sound. If a concrete use case emerges later, it can be reconsidered
>
> Solid RFC. Welcome to submit PRs following the proposed order.

---

### Comment 2 — jlin53882（2026-04-02T16:59:21Z）

## Phase 4：B-2 全域 Retrieval Neighbor Enrichment

目前 Phase 1（`feat/proposal-b1-v2`，PR #463）和 Phase 2（`feat/proposal-b2-v2`，PR #464）已在 `feat` 分支實作完成。Phase 4 是 B-2 的完整實作方向，以下是我的設計建議，請 @AliceLJY 幫忙確認方向是否正確。

#### 設計目標

在 `MemoryRetriever.retrieve()` 的 auto-recall 路徑上，於結果回傳前加入 neighbor enrichment：
- 對每個候選 entry，以其 text 向量搜尋同一 scope 內的 top-2 neighbors
- 合併進結果後，以 `effectiveScore = similarity * (0.7 + 0.3 * importance)` 重新排序
- 總上限：20 筆

#### 實作位置

- `src/retriever.ts`：`retrieve()` 方法末尾、access tracking 之後

#### 觸發條件

| 設定 | 值 |
|------|-----|
| `source === "auto-recall"` | ✅ 執行 |
| `source === "manual"` | ❌ 跳過 |
| `source === "cli"` | ❌ 跳過 |
| `config.enableNeighborEnrichment !== false` | ✅ 執行（預設 true）|

#### 風險與疑慮

1. **MMR 衝突**：neighbors 可能稀釋高度相關的原本結果。是否需要 MMR（Maximal Marginal Relevance）重排？
2. **Scope 顆粒度**：目前 neighbors 與原本結果共享同一 scope，跨 scope 干擾機率低。是否需要更細的 scope 控制？
3. **Latency**：每個 entry 都多做一次 vectorSearch，假設 top-5 results × 2 neighbors = 10 次額外查詢。是否可接受？

#### 問題

@AliceLJY 請問：
1. 這個方向與你對 B-2 的理解一致嗎？
2. MMR 是否有必要？還是簡單的 effectiveScore 排序就足夠？
3. 有沒有其他潛在問題我沒考慮到？

#### 進度追蹤

| Phase | 內容 | PR | 狀態 |
|-------|------|-----|------|
| Phase 1 B-1 | BM25 expansion for reflection | #463 | ✅ 完成 |
| Phase 2 | Feedback signal + importance | #462 | ✅ 完成 |
| Phase 4 B-2 | Full retrieval neighbor enrichment | — | ⏳ 待確認方向 |

---

### Comment 3 — AliceLJY（2026-04-03T00:26:30Z）

> Direction is broadly right. A few constraints so this stays reviewable:
>
> - Keep neighbor enrichment same-scope only for v1.
> - Do not add another MMR pass in the first B-2 cut; re-sorting by your effective score is enough initially.
> - Keep the original recalled hits anchored in the result set and cap neighbor fan-out hard.
> - Most important: do not bundle B-2 with Proposal A feedback logic. Review it as a separate PR with its own regression tests and a small latency sanity check.
>
> B-1 should still be the proving ground. If you want to proceed with B-2, keep the scope tight.

---

### Comment 4 — jlin53882（2026-04-03T17:55:01Z）

## PR #493 — Proposal A Phase 1 已完成

Phase 1 動態重要性回饋訊號已實作完成，PR 連結：https://github.com/CortexReach/memory-lancedb-pro/pull/493

#### 已實作內容

| Signal | 條件 | 調整 |
|--------|------|------|
| 用戶明確確認 | 使用者回答「正確」/「是」/「對」/「right」 | importance += 0.15 上限 1.0 |
| 用戶明確標記錯誤 | 使用者表示「不」/「錯誤」/「not right」 | importance -= 0.10 下限 0.1 |

#### Phase 2 預計處理

- min_recall_count 閾值（AliceLJY 建議）
- 調整幅度可配置化

---

### Comment 5 — jlin53882（2026-04-04T16:15:25Z）

## Branch Topology Analysis — PR Chain #507 / #505 / #506

#### Current State（all target master — conflicts）

```
master
  ├── feat/proposal-a-v3-clean           (PR #507, Phase 1)
  ├── feat/proposal-a-v3-configurable-v2 (PR #505, Phase 3)
  └── feat/proposal-a-v3-tests           (PR #506, Phase 4)
```

All three modify the same files (`index.ts`, `reflection-slices.ts`, `src/retriever.ts`, `src/smart-extractor.ts`, `src/auto-capture-cleanup.ts`). Merging independently will cause unpredictable diff conflicts.

#### Proposed Stack Chain

```
master
  └── feat/proposal-a-v3-clean           (PR #507, Phase 1)
        └── feat/proposal-a-v3-configurable-v2 (PR #505, Phase 3)
              └── feat/proposal-a-v3-tests       (PR #506, Phase 4)
```

#### Recommended Next Step

1. Merge or close #498, #500, #510 (or keep them open and rebase #507 after they merge)
2. Rebase #507 onto latest master — the 3 split commits will disappear from #507 diff
3. Push update → request re-review from AliceLJY
4. After #507 merges, rebase #505 onto `feat/proposal-a-v3-clean`, then #506 onto #505

---

### Comment 6 — jlin53882（2026-04-04T18:27:49Z）

## PR #523 更新（Option B BM25 Neighbor Expansion）

此 PR 實作了 Option B Phase 1 的 BM25 neighbor expansion 功能，解決 Issue #513 中提出的 fresh session 問題。

**主要變更：**
- 在 `loadAgentReflectionSlicesFromEntries` 的 `rankReflectionLines()` 之前執行 BM25 expansion
- 乘法加成 quality 分數（`quality = 0.2 + 0.6 * bm25Score`）
- 新增 `Bm25NeighborExpansion` config 開關

**PR #523：** https://github.com/CortexReach/memory-lancedb-pro/pull/523

目前正在等待 maintainer 審查中。

---

### Comment 7 — jlin53882（2026-04-05T14:48:20Z）

## B-2 Proposal: Full Retrieval Neighbor Enrichment

Following the successful implementation of B-1 (PR #529, approved), here is the plan for B-2.

#### Goal

In retriever.ts, after MMR diversity and before returning results, enrich recalled memories with their semantic neighbors.

#### Architecture

Pipeline insertion point (hybridRetrieval, after applyMMRDiversity):

```
hybridRetrieval()
  → vectorSearch + bm25Search
  → RRF fusion → noise filter → rerank
  → applyRecencyBoost → applyImportanceBoost → applyLengthNormBoost
  → applyNeighborEnrichment  ← B-2 NEW
  → re-sort by combined score
  → applyMMRDiversity
  → slice(0, limit)
```

#### Key Design Decisions

1. **NE before MMR**: Neighbor enrichment first expands semantic neighborhood, then MMR does final diversity control. This avoids neighbors being unfairly suppressed by MMR.
2. **Parallel vectorSearch**: Use Promise.all to parallelize N vectorSearch calls (max 5 candidates, topK=2 each), not sequential.
3. **Config**: Add to `RetrievalConfig`:
   - `neighborEnabled?: boolean` (default: true)
   - `neighborTopK?: number` (default: 2)
   - `neighborMaxCandidates?: number` (default: 5)
   - `neighborMaxPerRecalled?: number` (default: 2)
   - `neighborTotalCap?: number` (default: 20)
4. **Differences from B-1**:
   - B-1 uses `bm25Search` (keyword matching) in reflection-store.ts
   - B-2 uses `vectorSearch` (vector similarity) in retriever.ts
   - Different mechanisms, no code sharing needed
5. **Defense mechanisms**:
   - D1: Empty recalled return as-is
   - D2: No scopeFilter return as-is
   - D3: Total cap at neighborTotalCap
   - D5: seen Set dedup
   - D6: Promise.all + per-call .catch(() => []) fail-safe
   - D7: Latency budget (max N candidates)
   - D8: Scope consistency (neighbors inherit scopeFilter)

#### Questions

1. Should neighbor enrichment be gated behind a config flag, or always-on?
2. Should we use `bm25Search` instead of `vectorSearch` (to match B-1 approach)?
3. Is the proposed pipeline order (NE before MMR) acceptable?

---

## 標籤分析

### Proposal A — 動態重要性調整（核心訴求）

**問題根源**：`importance` 欄位在寫入後從不改變，屬於靜態欄位。系統有頻率強化（frequency reinforcement）但缺乏回饋型重要性調整。

**解決方案**：
1. 在 `agent_end` hook 階段，根據用戶回饋動態調整 `importance` 分數
2. 觸發信號：
   - 用戶明確確認正確 → `+0.15`，上限 1.0
   - 用戶明確標記錯誤 → `-0.10`，下限 0.1
   - 被召回但連續 2+ 次未使用 → `-0.03`
3. Phase 2 進一步引入 `min_recall_count` 閾值，避免新記憶被過早懲罰

**實作進度**：
- PR #493 已完成 Phase 1（明確正確/錯誤回饋）
- PR #507（Phase 1 v3 clean）、#505（Phase 3 configurable）、#506（Phase 4 tests）在棧式審查中

---

### Proposal B — 鄰居豐富化（Neighbor Enrichment）

**問題根源**：召回記憶時只返回精確匹配的記憶，忽略了語義上相關的「鄰居」記憶。

**解決方案（B-1 → B-2 路線圖）**：

| 階段 | 範圍 | 技術 | 檔案 | 狀態 |
|------|------|------|------|------|
| B-1 | Reflection slices 專用 | BM25 keyword expansion | `reflection-store.ts` | ✅ PR #529 已核准 |
| B-2 | 全域 retrieval | Vector similarity search | `retriever.ts` | ⏳ 待方向確認（最後 comment） |

**B-2 關鍵設計決策**（已獲 AliceLJY 確認方向）：
1. same-scope only（不跨 scope）
2. 不再叠代 MMR，簡單 effectiveScore 重排即可
3. 原始召回結果保留作為錨點
4. 需獨立 PR + 迴歸測試 + latency 檢查

---

### 協作脈絡

| 角色 | 參與者 | 主要貢獻 |
|------|--------|---------|
| 作者 | jlin53882 | RFC 全文、實作方向、B-2 設計、各階段進度更新 |
| Maintainer | AliceLJY | 確認實作順序、B-1/B-2 範圍約束、Phase 1 review |

### 重要共識（Maintainer 確認）

1. **Scope filter 預設不跨域**：Neighbor enrichment 限制在同 scope 內
2. **B-1 先驗證再推 B-2**：B-1 為 B-2 的 proof of concept
3. **B-2 獨立 PR**：不得與 Proposal A 回饋邏輯綑綁審查
4. **Proposal C 暫排除**：準確率不足，建設成本過高，現有 A+B 已滿足需求
