# Proposal B PR 分析報告

> 報告日期：2026-04-09
> 目標 repo：jlin53882/memory-lancedb-pro 與 CortexReach/memory-lancedb-pro
> 報告語言：繁體中文

---

## PR #3｜jlin53882/memory-lancedb-pro

**標題：** Phase 1 B-1 scope-aware BM25 neighbor expansion for reflection slices

**狀態：** 🔵 Open（曾被關閉又重新開啟）

**PR 描述（Body）：**

```
Issue: CortexReach#445 (AliceLJY reviewer feedback)

Changes:
- Add loadAgentReflectionSlicesWithBm25Expansion() function to src/reflection-slices.ts
- This function performs scope-aware BM25 expansion: for each reflection slice entry,
  it does bm25Search(text, topK=2, scopeFilter=[entry.scope]) instead of global expansion
- Uses [entry.scope] instead of undefined to scope neighbors to the same scope as the original entry
- Merges and deduplicates original entries with their neighbors

Config options:
- topK: number of neighbor results per entry (default: 2)
- minScore: minimum BM25 score threshold (default: 0.1)
```

**主要 Commit 摘要：**

- 4/2：初次提出，加入 BM25 expansion 函式
- 4/4：大量修訂（Fix #1～#7），包含 DM fallback、cumulative counting、REPLACE vs APPEND 邏輯、Math.min cap、MAX_MESSAGE_LENGTH guard 等，共 29 個測試全部通過
- 4/5：加入 turn counting test + changelog
- 4/7、4/8：持續 push commit，修訂內容與 4/4 類似
- 與 upstream CortexReach#417 綁定

**特殊紀錄：**
此 PR 在 CortexReach/memory-lancedb-pro 的對應 PR 為 #450（已 Closed）。

---

## PR #450｜CortexReach/memory-lancedb-pro

**標題：** Phase 1 B-1 scope-aware BM25 neighbor expansion for reflection slices

**狀態：** 🔴 Closed

**PR 描述：**

```
Files were deleted from origin/master during earlier rebase/cherry-pick operations.
These deletions were unintentional — the PRs were meant to add features, not delete
existing functionality.

Restored from upstream/master:
- src/: admission-control, admission-stats, auto-capture-cleanup, batch-dedup,
  clawteam-scope, identity-addressing, intent-analyzer, llm-oauth,
  memory-compactor, preference-slots, retrieval-stats, retrieval-trace,
  session-compressor, workspace-boundary
- scripts/: governance-maintenance.mjs, migrate-governance-metadata.mjs
- test/: 25 test files restored
- README translations: DE, ES, FR, IT, JA, KO, PT-BR, RU, TW
```

**分析：** 此 PR 為還原被意外刪除檔案之用，來自 upstream/master 的恢復操作，並非功能實作。PR 本身已被關閉。

---

## PR #456｜CortexReach/memory-lancedb-pro

**標題：** Proposal B Phase 1 — scope-aware BM25 neighbor expansion for reflection slices

**狀態：** 🔴 Closed

**PR 描述：** 與 PR #450 相同，均為還原被刪除檔案的維護性 PR，無功能實作內容。

---

## PR #458｜CortexReach/memory-lancedb-pro

**標題：** feat: Proposal B Phase 2

**狀態：** 🔴 Closed

**PR 描述：** 與 PR #450、#456 相同，均為還原被刪除檔案的維護性 PR，無獨立的 Phase 2 內容。

---

## PR #6｜jlin53882/memory-lancedb-pro

**標題：** Scope-aware BM25 neighbor expansion for reflection derived slices

**狀態：** 🔵 Open

**參與者人數：** 9+ 人（jlin53882, ggzeng, dingguagua996-stack, ChaoYang78, rwmjhb, slj130, AliceLJY, king6731253, Claude Opus 4.6）

**主要 Commit 內容（摘要）：**

| 編號 | 作者 | 內容 |
|------|------|------|
| C1 | jlin53882 | 加入 idempotent guard + governance detail logging；WeakSet 取代 module-level boolean |
| C2 | ggzeng | 防止 reflection loop：加入 global cross-instance re-entrant guard |
| C3 | dingguagua996-stack | 修復 LLM 回傳 null entry 導致的 TypeError crash |
| C4 | Claude Opus 4.6 | 新增 auto-supersede similar memories 功能（isLatest rule-based, similarity > 0.95）|
| C5 | king6731253 | 註冊 memory runtime stub 滿足 openclaw doctor check |
| C6 | jlin53882 | Scope-aware expansion、seen=new Set()、merge base+expanded cap 16、try/catch fail-safe |

**Code Review 摘要：**

- AliceLJY 提出 Issue [#445](https://github.com/CortexReach/memory-lancedb-pro/issues/445)，要求 scope-aware BM25 expansion
- rwmjhb 審查回饋：narrow SUPERSEDE_ELIGIBLE 範圍僅限 preference + entity
- OpenCode adversarial review 發現 MAJOR-1/2/3 問題（見 PR #504）
- 包含 cortex#417 的大量 Fix（#1～#7），共 29 個測試全部通過

---

## PR #497｜CortexReach/memory-lancedb-pro

**標題：** Scope-aware BM25 neighbor expansion for reflection derived slices

**狀態：** 🔴 Closed（對應 jlin53882/memory-lancedb-pro PR #6 的 upstream 版本）

**PR 描述摘要：**

```
Summary: Proposal B Phase 1: Scope-aware BM25 neighbor expansion for reflection slices.

在 loadAgentReflectionSlices 包裝函式內，對每個 derived slice 做 scope-aware BM25 expansion，
找出跨 session 的語義相關 prior decisions。
```

**Phase 1 完成內容（✅）：**

- **實作：** index.ts +39 行（BM25 expansion 邏輯）
- **測試：** test/b1-bm25-expansion.test.mjs，+316 行，15 個測試（15/15 全部通過）

**Defense 要點（來自 PR #463 失敗教訓）：**

| Defense | 內容 |
|---------|------|
| D1 | seen = new Set() 空初始化（不預放 base items）|
| D2 | scopeFilter !== undefined guard（scope 明確才 expansion）|
| D3 | merge 後 cap 16（[...derived, ...expanded].slice(0, 16)）|
| D4 | snippet truncate：取第一行，最大 120 字 |
| D6 | expand, not replace（base derived 在前，neighbors 在後）|
| Fail-safe | Bm25Search 失敗時 try/catch，不 crash |

**Linked Issue：** Closes #445（Proposal B Phase 1）

---

## PR #503｜CortexReach/memory-lancedb-pro

**標題：** Scope-aware BM25 neighbor expansion for reflection slices (v3)

**狀態：** 🔴 Closed（v3 版本，已被 PR #504 取代）

**PR 描述（重要修正）：**

### 處理了三個 Critical/Major Issue：

**Issue 1：Neighbors 被截斷（CRITICAL）**
- 問題：v2 實作把 neighbors 附加在 derived 陣列末尾，prompt builder 只取 `.slice(0, 6)`，當 base derived 已有 6+ 條目時，neighbors 完全進不了 prompt，feature 成為靜默無操作。
- 修復：改為 `return [...neighbors, ...derived].slice(0, MAX_TOTAL)`，確保 `.slice(0, 6)` 優先捕獲 neighbors。

**Issue 2：BM25 可自匹配 reflection rows（MAJOR）**
- 問題：`store.bm25Search` 在未加 category 過濾的情況下搜索全表，可能返回發起的 reflection 條目本身，占據 slots。
- 修復：加入 `if (hit.entry.category === "reflection") continue;` 過濾。

**Issue 3：測試驗證的是本地副本而非生產代碼（MAJOR）**
- 問題：test/b1-bm25-expansion.test.mjs 定義了一個 standalone `applyBm25Expansion()` 函式，與生產代碼脫節。
- 修復：將 B-1 邏輯提取為獨立導出函式 `expandDerivedWithBm25()`，測試直接 import 生產函式。

**額外發現並修復的 Bug：**
`|| ""` 保護放在 `.split()` 之後，導致 `null.split()` 先拋 TypeError 被 fail-safe 吞掉。修復：將 `|| ""` 移至 `.split()` 之前。

**測試覆蓋：** 12 個原有測試 + 7 個新邊界 case = **19/19 通過**

**檔案變更：**

- `src/bm25-expansion.ts`：新增，BM25 expansion 邏輯（+41 行）
- `test/b1-bm25-expansion.test.mjs`：新增，19 個測試覆蓋（+280 行）
- `index.ts`：呼叫 `expandDerivedWithBm25()`（+3 行）
- `package.json`：註冊測試到 npm test（+1 行）

---

## PR #504｜CortexReach/memory-lancedb-pro

**標題：** Full retrieval neighbor enrichment for auto-recall (v4)

**狀態：** 🔵 Open（v4 最新版本）

**PR 描述：**

### 主要功能：Anchor mode + Tier Sort

**變更摘要：**

- 新增 `enrichWithNeighbors()` method，包含完整過濾 pipeline
- 新增 `RetrievalConfig.enableNeighborEnrichment` 配置項
- 22 個測試全部通過

### OpenCode adversarial review 修復（來自 Code Review）：

| 等級 | 問題 | 修復內容 |
|------|------|----------|
| MAJOR-1 | 缺少 minScore quality gate | neighbors 需通過相同閾值 |
| MAJOR-2 | 內層迴圈計數器錯誤 | 只在成功加入時遞增 |
| MAJOR-3 | 缺少 Tier Sort | neighbors 在各 tier 內依相似度排序 |

### MINOR 修復：

- 新增 TC-16 inactive neighbor test 陰性斷言
- 新增 TC-21 quality gate test
- 新增 TC-22 Tier Sort ordering test

### Self-filter 修復（jlin53882 最後一次 commit）：

加入 `if (text === derivedLine) continue;` 防止已儲存的條目成為自己的 neighbor。

### 整合測試（9 個測試，9/9 通过在真實 LanceDB）：

- B-1：scopeFilter guard、empty derived、no neighbors、self-filter
- B-2：auto-recall no crash、manual skipped、no dup IDs、anchored、limit cap

測試檔案：`test/b1-b2-integration.test.mjs`

---

## 總結與脈絡分析

### PR 版本進化路線

```
PR #450/456/458 (CortexReach) → 維護性：還原意外刪除的檔案
PR #3 (jlin53882)             → Phase 1 B-1 初始實作（基於 Issue #445 AliceLJY feedback）
PR #6 (jlin53882)             → 多人協作版：包含多項 Fix + Auto-supersede + Reflection loop guard
PR #497 (CortexReach)         → Phase 1 上游版：15 個 Defense 測試（15/15 ✅）
PR #503 (CortexReach)         → Phase 1 v3：修復 3 個 Critical/Major Issue（19/19 ✅）
PR #504 (CortexReach)         → Phase 1 v4 / B-2：Anchor mode + Tier Sort（22/22 ✅，整合測試 9/9 ✅）
```

### 核心功能（Proposal B Phase 1）

**目標：** 在 `loadAgentReflectionSlices` 包裝函式內，對每個 derived slice 做 scope-aware BM25 expansion，找出跨 session 的語義相關 prior decisions。

**關鍵 Defense 設計（屢次迭代後的共識）：**

1. **D1**：`seen = new Set()` 空初始化 — 不預放 base items，避免重複
2. **D2**：`scopeFilter !== undefined` guard — scope 明確才 expansion
3. **D3**：Merge 後 cap 16 — `[...neighbors, ...derived].slice(0, 16)`
4. **D4**：snippet truncate — 取第一行，最大 120 字
5. **D6**：Neighbors 在前、base derived 在後 — 確保 `.slice(0, 6)` 優先捕獲 neighbors
6. **Fail-safe**：bm25Search 錯誤時 try/catch，不 crash

### 重要Lessons Learned（來自迭代教訓）

| 問題 | 發現版本 | 嚴重性 | 教訓 |
|------|----------|--------|------|
| neighbors 被 slice(0,6) 截斷 | v2 | CRITICAL | neighbors 順序比內容更重要 |
| BM25 自匹配 reflection rows | v2 | MAJOR | 需過濾 category === "reflection" |
| 測試脫離生產代碼 | v2 | MAJOR | 測試函式必須直接 import 生產函式 |
| null.split() 先拋 TypeError | v3 | BUG | `\|\| ""` 要放在 `.split()` 之前 |
| 內層迴圈計數器錯誤 | v4 (adversarial review) | MAJOR | 只在成功加入時遞增 |
| 自己成為自己的 neighbor | v4 (self-review) | BUG | 需 self-filter `text === derivedLine` |

### Linked Issue

- **#445**（Proposal B Phase 1）— 由 PR #497 和 PR #503 分別關閉
- **#417**（上游 Discord DM 修補）— 綁定在 PR #3/#6 多個 Fix 中
- **#434**（openclaw doctor 警告）— 由 PR #6 的 king6731253 修復
- **#137**（autoRecallExcludeAgents）— 由 PR #6 的 jlin53882 實作
