# Proposal B 全面分析報告

> 整理日期：2026-04-09
> 整理者：AI 程式修改助手
> 資料來源：Issue #445、PR #3/#450/#456/#458/#6/#497/#503/#504/#529、Issue #513/#538/#514 的完整時間線

---

## 一、Proposal B 架構總覽

Issue #445 中定義的實作順序：

| Phase | 內容 | 觸發條件 |
|-------|------|---------|
| Phase 1（B-1）| Reflection slice load-time BM25 neighbor expansion | — |
| Phase 2（B-2）| Retrieval-time neighbor enrichment | Phase 1 穩定後 |
| ~~Phase 3~~ | ~~原 Phase 3 Proposal C~~ | **已排除** |
| ~~Phase 4~~ | ~~B-2 全域 retrieval neighbor enrichment~~ | 被 B-2 取代 |

**AliceLJY 對 Proposal B 的確認方向**（Issue #445）：
- B-1 是正確的起點
- Neighbor enrichment 預設僅限相同 scope
- MMR 衝突問題需注意
- B-1 驗證穩定後再推進 B-2

---

## 二、B-1 PR 演進史（全部 ❌ 關閉，未合併）

### PR #3 — jlin53882/fork（已關閉）

- **分支**：`feat/proposal-b1-neighbor-expansion`
- **狀態**：❌ jlin53882 self-closed，1 commit
- **penggaolai 審查**（2026-04-02）：
  > "Add `loadAgentReflectionSlicesWithBm25Expansion()` function — scope-aware BM25 expansion，用 `[entry.scope]` 而非 `undefined` 來限制 neighbors 在同 scope 範圍內"
- **詳情**：最早期版本。之後因同步 upstream #365/#307/#369 等內容，fork branch 持續更新但 B-1 實作未進 upstream

---

### PR #450 — CortexReach（已關閉）

- **分支**：`feat/proposal-b1-neighbor-expansion`（與 #3 同分支）
- **狀態**：❌ 關閉
- **🔑 關閉原因**：分支上的檔案在 earlier rebase/cherry-pick 操作中被從 origin/master 刪除（unintentional）。從 upstream/master Restore 了大量 src/ 和 test/ 檔案
- **詳情**：將 #3 的內容同步到 upstream fork

---

### PR #456 — CortexReach（已關閉）

- **分支**：`feat/B-1-clean`
- **狀態**：❌ 關閉
- **🔑 關閉原因**：同 #450 — 分支檔案被誤刪，從 upstream/master restore
- **詳情**：清理版本，B-1 重新整理

---

### PR #6 — jlin53882/fork（已關閉）

- **分支**：`feat/proposal-b1-v3`
- **狀態**：❌ self-closed，14 commits（來自多個 contributor）
- **時間**：2026-04-02 ~ 2026-04-03
- **詳情**：v3 版本，大量迭代（14 commits），Scope-aware BM25 neighbor expansion for reflection derived slices
- **重要**：這個 PR 的 commits 夾雜了對 upstream 其他 PR（#365、#307、#369、#338、#452、#471）的趕上進度，而非只有 B-1 內容

---

### PR #497 — CortexReach（已關閉）

- **分支**：`feat/proposal-b1-v3`（與 #6 同分支）
- **狀態**：❌ 關閉，5 commits
- **時間**：2026-04-03
- **詳情**：將 #6 同步到 upstream

---

### PR #503 — CortexReach（已關閉）

- **分支**：`feat/proposal-b1-v3-fix`
- **狀態**：❌ 關閉，1 commit
- **時間**：2026-04-04
- **詳情**：v3 版本修復，Scope-aware BM25 neighbor expansion for reflection slices (v3)

**PR #503 修復了三個重大 bug**（v2 版本的問題）：

| Bug | 等級 | 問題 | 修復 |
|-----|------|------|------|
| Neighbors 被截斷 | CRITICAL | `.slice(0, 6)` 讓 neighbors 無法進入 prompt | 改為 `return [...neighbors, ...derived].slice(0, MAX_TOTAL)`，neighbors 在前 |
| BM25 自匹配 reflection rows | MAJOR | `bm25Search` 無過濾時返回自己 | 加 `if (hit.entry.category === "reflection") continue;` |
| 測試驗證本地副本非生產代碼 | MAJOR | 測試自己實作了函式，與生產脫節 | 抽取為 `expandDerivedWithBm25()` 獨立導出函式 |
| `null.split()` TypeError | P2 | `\|\| ""` 保護放在 `.split()` 之後 | 移到 `.split()` 之前 |

**Defense 機制（D1-D6）保留**：seen=Set()、scopeFilter guard、16 cap、120 char truncation、neighbors before base derived、fail-safe

---

## 三、B-1 方向轉折：Option B（Issue #513）

### Issue #513 — 重新確認方向

**標題**：[Proposal B Phase 1] Seeking guidance: redesign approach for BM25 neighbor expansion
**狀態**：🟡 Open（討論中）
**发起者**：jlin53882

jlin53882 在 Issue #513 中提出三個選項：
- **Option A**：Query-time BM25 as ranking signal（將 BM25 結果當成額外評分信號）
- **Option B**：Query-time BM25 for neighbor expansion（用 BM25 找 neighbors）
- **Option C**：其他架構

---

### AliceLJY 的確認（2026-04-04 11:48）

**→ 選擇 Option B（query-time BM25 as ranking signal）**

理由：
1. **無 schema 變更** — 避免 migration 複雜度
2. **適用所有 entries** — 新舊資料都能用，無 cold-start 問題
3. **符合 reviewer 核心訴求** — enrichment 在 slice cutoff **之前**發生
4. **可逆** — 如果效能有問題，可以從 config flag 關掉

**具體建議**：
- 將 BM25 搜尋範圍限制在 top-N candidates（top 5-10），不搜尋全部 entries
- 加上 config 選項：`bm25NeighborExpansion: { enabled: true, maxCandidates: 5, maxNeighborsPerCandidate: 3 }`
- 參考 `applyRecencyBoost()` 的 pattern 來 blend BM25 neighbor 信號
- 參考 `vectorOnlyRetrieval()` 的 chain 方式（vector search → rerank → score merge）
- **Fresh-session bypass 可以接受** — Phase 1 需要有 stored data 才能 query

---

## 四、PR #529 — B-1 最新版（AliceLJY 批准 → ❌ rwmjhb 封鎖）

**分支**：`feature/option-b-v4`
**狀態**：❌ closed by rwmjhb（2026-04-06 01:12）
**標題**：feat(reflection): Option B BM25 neighbor expansion for fresh sessions (Issue #513)

### AliceLJY 審查（2026-04-05 14:14）— ✅ `APPROVED` / `LGTM`

- `loadAgentReflectionSlicesFromEntries` sync→async 必要且正確
- 6 個防御機制（D1-D6）完整：空陣列 early return、無 bm25Search bypass、scopeFilter guard、16 條 cap、120 char truncation、neighbors prepend
- BM25 error fail-safe（catch + warn 不阻塞 reflection pipeline）
- `Promise.all` 並行搜尋效能好
- Config 通過 `parsePluginConfig` 正確解析，defaults 合理
- 454 行單元測試覆蓋每個防御點

### rwmjhb 審查（2026-04-06 01:12）— ❌ `BLOCKING` / 關閉

**2 個 Blocking Issues**：

1. **🔴 Core feature 不適用於 fresh sessions**
   - `expandDerivedWithBm25BeforeRank()` 在 `derived.length === 0` 時直接 `return []`
   - 新 session 沒有 prior reflection history（主要 use case）仍然得不到 BM25 neighbors
   - 與聲稱的功能矛盾

2. **🔴 TypeScript 編譯錯誤**
   - `candidateTimestamp` 在 `.then()` callback 的 destructuring 中被 drop
   - `({ hits, queryText, normalizedKey })` 少了 `candidateTimestamp`
   - 導致 `result.candidateTimestamp` 是 `undefined`

**其他顧慮**：
- XL-sized change，value-to-complexity ratio 低（value score: 29%）
- 預設開啟會對所有現有用戶新增額外 BM25 queries
- Tests hard-code 了錯誤的 fresh-session behavior 而非 intended feature path
- Duplicate derived lines 消耗多個 BM25 query slots

**rwmjhb 建議**：
> "Consider a smaller, focused PR that addresses just the fresh-session path with the compile issue fixed."

---

## 五、B-2 PR 演進史（全部 ❌ 關閉，未合併）

### PR #458 — CortexReach（已關閉）

- **分支**：`feat/B-2`
- **狀態**：❌ 關閉，2 commits
- **時間**：2026-04-02 ~ 2026-04-03
- **標題**：feat: Proposal B Phase 2 - full retrieval neighbor enrichment
- **詳情**：最早的 B-2 版本
- **🔑 關閉原因**：同 #450/#456 — 分支檔案在 rebase/cherry-pick 操作中被從 origin/master 刪除（unintentional）。從 upstream/master Restore 了大量檔案

---

### PR #504 — CortexReach（已關閉）

- **分支**：`feat/proposal-b2-v4`
- **狀態**：❌ 關閉，2 commits
- **時間**：2026-04-03 ~ 2026-04-04
- **標題**：feat(B-2): Full retrieval neighbor enrichment for auto-recall (v4)
- **詳情**：v4 版本

**PR #504 的內容**：
- **Anchor mode + Tier Sort**：original results preserved，neighbors 按 vector similarity 在各自的 tier 內排序
- 新增 `enrichWithNeighbors()` method，含完整過濾 pipeline
- 新增 `RetrievalConfig.enableNeighborEnrichment` config
- **22 tests 全部通過**
- **OpenCode adversarial review 發現並修復**：
  - MAJOR-1：加 `minScore` quality gate
  - MAJOR-2：修復 inner loop counter（只在成功新增時 increment）
  - MAJOR-3：加 Tier Sort — neighbors 在 tier 內按相似度排序
  - MINOR：加 negative assertion、quality gate test、Tier Sort ordering test
- **Self-filter fix**：加 `if (text === derivedLine) continue;` 防止 entry 成為自己的 neighbor
- **整合測試（9 tests，9/9 pass on real LanceDB）**：涵蓋 B-1 和 B-2 的 scopeFilter guard、empty derived、no neighbors、self-filter、auto-recall no crash、manual skipped、no dup IDs、anchored、limit cap
- 測試檔：`test/b1-b2-integration.test.mjs`

---

## 六、Issue #538 — B-2 方向確認討論（🟡 Open）

**標題**：[Question] B-2 Neighbor Enrichment: Confirm direction before implementation
**狀態**：🟡 Open（等待回覆）
**发起者**：jlin53882

### AliceLJY 的 B-2 方向確認（2026-04-06 12:45）

| 問題 | AliceLJY 答案 |
|------|--------------|
| Q1: BM25 vs Vector search | **BM25** — 能找到與 recall 結果詞彙重疊的相鄰記憶，與 vector search 形成互補 |
| Q2: Insertion point（MMR 之前或之後）| **MMR 之後** — MMR 負責多樣性，neighbor enrichment 是對 top-K 的補充 |
| Q3: Gating mechanism | **Config flag 控制，預設 disabled** — 新行為需要 opt-in |
| Q4: 與 B-1 共享代碼 | **保持獨立** — B-1 在 write path，B-2 在 read path，硬共享會造成耦合 |

**AliceLJY 的額外建議**：
- **先聚焦 B-2，B-1 暫不重開**
- 如果有共用的 BM25 查詢邏輯，可以抽取為 utility function
- 建議 PR 包含 benchmark（enrichment 前後 recall quality 對比）

---

### jlin53882 追加的 5 個實作缺口（2026-04-06 13:16）

jlin53882 在 Issue #538 追加了 5 個 Q，等待 maintainer 回覆：

| 問題 | 內容 | 緊急度 |
|------|------|--------|
| **Q5**: MMR 去重是否會消滅 neighbors？ | MMR 已經刪掉的相似 items，B-2 找不到它們的 neighbors | 🔴 阻塞 |
| **Q6**: `vectorOnlyRetrieval()` 路徑的 B-2 如何實作？ | vector-only 沒有 BM25 search 階段，如何找 neighbors？ | 🔴 阻塞 |
| **Q7**: Neighbor search 的 scope boundary 如何決定？ | 用 recall result 的 scope？還是 query 的 scope？ | 🟡 需確認 |
| **Q8**: B-2 的 Phase 4 依賴關係被跳過，觸發條件是否重新定義？ | 從「B-1 穩定 1 個月」變成直接實作 | 🟡 需確認 |
| **Q9**: BM25 neighbor lookup 的輸入範圍？Neighbors 如何附加？ | Input scope？數量？附加方式 A/B/C？Output 結構？ | 🟡 需確認 |

**目前狀態**：rwmjhb 和 AliceLJY 都被 tag，但還沒有回覆（截至 2026-04-09）。

---

## 七、Issue #514 — Per-agent Exclusion Mechanism（🟡 Open）

**標題**：Proposal: Per-agent exclusion mechanism for before_prompt_build hooks (related to #492)
**狀態**：🟡 Open
**发起者**：jlin53882

### Issue #492 背景
記憶 reflection hooks 在 before_prompt_build 時同步執行 LanceDB 查詢，導致 30-50% 用戶 session 回應失敗。原因是兩個 before_prompt_build hooks（priority 12 和 priority 15）都呼叫 `await loadAgentReflectionSlices()`（blocking DB operation）。

### PR #516 的解法（最終 → PR #520）
1. **新增 helper：`isAgentOrSessionExcluded`**
   - Exact match：`memory-distiller`
   - Wildcard prefix：`pi-`（匹配 `pi-agent`、`pi-coder`）
   - Special pattern：`temp:*`（內部 reflection sessions）

2. **修復 auto-recall `before_prompt_build` exclusion check**
   - 移除無效的 `agentId !== undefined` check（因為有 `|| "main"` fallback，永遠是 true）

3. **三層保護 on `runMemoryReflection` command hook**
   - Internal session guard
   - Re-entrant guard（`globalThis` + `Symbol.for` lock）
   - Serial cooldown guard（120s）

4. **Config**
```json
{
  "memory-lancedb-pro": {
    "autoRecallExcludeAgents": ["memory-distiller", "pi-", "temp:*"]
  }
}
```

**PR #520**（最終版本）：
- 包含 `serialCooldownMs` 可配置參數
- 在 `openclaw.plugin.json` schema 中可設定
- 用法：`memoryReflection.serialCooldownMs: 60000`

**目前狀態**：PR #520 已開，**尚未得到 maintainer 回覆**

---

## 八、完整 PR 狀態總表

| 編號 | 類型 | 分支 | 標題 | 狀態 | 關閉原因 |
|------|------|------|------|------|---------|
| #3 | B-1 | feat/proposal-b1-neighbor-expansion | scope-aware BM25 neighbor expansion | 🔵 **Open** | jlin53882 持續 push，綁定 #417 |
| #450 | B-1 | feat/proposal-b1-neighbor-expansion | scope-aware BM25 neighbor expansion | ❌ Closed | **還原被刪除檔案**（非功能 PR）|
| #456 | B-1 | feat/B-1-clean | Proposal B Phase 1 | ❌ Closed | **還原被刪除檔案**（非功能 PR）|
| #458 | B-2 | feat/B-2 | full retrieval neighbor enrichment | ❌ Closed | **還原被刪除檔案**（非功能 PR）|
| #6 | B-1 v3 | feat/proposal-b1-v3 | scope-aware BM25 for derived slices | 🔵 **Open** | 9 人協作版，jlin53882 持續 push |
| #497 | B-1 v3 | feat/proposal-b1-v3 | scope-aware BM25 for derived slices | ❌ Closed | 同步上游版 |
| #503 | B-1 v3-fix | feat/proposal-b1-v3-fix | BM25 neighbor expansion (v3) | ❌ Closed | 修復後等 CI |
| #504 | B-2 v4 | feat/proposal-b2-v4 | Full retrieval neighbor enrichment (v4) | 🔵 **Open** | 22 tests pass + OpenCode adversarial |
| #529 | B-1 Option B | feature/option-b-v4 | Option B BM25 for fresh sessions | ❌ Closed | AliceLJY ✅ → rwmjhb ❌ |
| #520 | Exclusion | — | Per-agent exclusion mechanism | 🟡 Open | 未審查 |
| **#513** | Issue | — | B-1 方向重新確認 | 🟡 Open | AliceLJY 確認 Option B ✅ |
| **#538** | Issue | — | B-2 方向確認 | 🟡 Open | AliceLJY Q1-Q4 ✅，Q5-Q9 待回覆 |
| **#514** | Issue | — | Per-agent exclusion mechanism | 🟡 Open | 未回覆 |

---

## 九、核心阻塞點分析

### 🔴 根本原因：Branch 檔案被誤刪

```
PR #450、#456、#458 的關閉原因不是代碼問題，
而是「分支上的檔案在 rebase/cherry-pick 操作中被從 origin/master 刪除」（unintentional）。
Restore 自 upstream/master，但導致 branch history 混亂，難以 merge。
```

這是**基礎設施/操作失誤**，不是設計或實作問題。

### B-1 的核心問題（從未合併）

經過 9 個 PR，仍有以下問題未解決：

| 問題 | 提出者 | 緊急度 |
|------|--------|--------|
| `derived.length === 0` early return 讓 fresh-session B-1 無效 | rwmjhb | 🔴 |
| TypeScript 編譯錯誤（candidateTimestamp drop in `.then()`）| rwmjhb | 🔴 |
| Branch topology 從未正確 stack（#450 → #456 → #503 各自 targeting master）| — | 🔴 |
| PR #503 的三個 bug（neighbors 截斷、BM25 自匹配、測試脫節）| — | ⚠️ 已修復在 #503 但 PR 仍關閉 |

### B-2 的核心問題（等待確認）

Issue #538 中有 5 個 Q（Q5-Q9），**全部未得到回覆**：

- 🔴 Q5：MMR 去重是否消滅 neighbors？
- 🔴 Q6：`vectorOnlyRetrieval()` 路徑如何做 B-2？
- 🟡 Q7：Neighbor scope boundary？
- 🟡 Q8：觸發條件是否重新定義？
- 🟡 Q9：Neighbors 如何附加？

### AliceLJY vs rwmjhb 權力問題

Issue #513 中記錄了一個尚未回答的問題：
> "When AliceLJY and rwmjhb disagree on a feature, who has final say?"

- AliceLJY 批准了 #529 → rwmjhb 關閉了 #529
- **目前沒有共識機制**

---

## 十、「好內容」盤點：值得保留下次使用的實作

雖然全部 PR 都關閉了，但有價值的內容分散在這些 PR 中，下次提出時可以直接用：

### B-1 值得保留的實作：
| 內容 | 來自 PR | 狀態 |
|------|---------|------|
| `expandDerivedWithBm25()` 獨立導出函式 | #503 | ✅ 設計正確 |
| D1-D6 defense 機制（scopeFilter、cap 16、truncation、self-filter）| #503/#504 | ✅ 完整 |
| BM25 error fail-safe（catch + warn）| #503 | ✅ 正確 |
| Neighbors prepend 邏輯（neighbors 在前、base derived 在後）| #503 | ✅ 修復後正確 |
| `Promise.all` 並行 bm25Search | #529 (AliceLJY 確認) | ✅ 效能好 |
| BM25 self-filter（`hit.entry.category === "reflection" continue`）| #503 | ✅ 正確 |
| `text === derivedLine` self-filter | #504 | ✅ 正確 |
| MinScore quality gate | #504 | ✅ 正確 |
| Integration tests（9/9 on real LanceDB）| #504 | ✅ 完整 |

### B-2 值得保留的實作：
| 內容 | 來自 PR | 狀態 |
|------|---------|------|
| `enrichWithNeighbors()` method | #504 | ✅ 設計正確 |
| Anchor mode（original results preserved）| #504 | ✅ 正確 |
| Tier Sort（neighbors 在 tier 內按相似度排序）| #504 | ✅ 正確 |
| 22 unit tests | #504 | ✅ 完整 |

---

## 十一、Issue #445 Comment 5 的 Branch Topology 分析（重要）

jlin53882 在 Issue #445 的 Comment 5（2026-04-04）提出了完整的 Branch Topology 分析：

### #507 需要清理的 commits（已拆分為獨立 PR）：
- #498：`WeakSet.clear()` fix
- #510：`stripEnvelopeMetadata` full fix
- #500：recency double-boost guard

### #507 仍需修復的問題：
- **P1**：autoCapture block boundary（確認回饋評分在正確的 `if (this.config.autoCapture)` 範圍內）

### 建議的堆疊式 chain：
```
master → #507(Phase1) → #505(Phase3) → #506(Phase4)
```

---

## 十二、AliceLJY 對 B-2 的關鍵約束（2026-04-03）

AliceLJY 在 Issue #445 Comment 3 明確說明：
> "不要將 B-2 與 Proposal A 回饋邏輯綁在一起。作為獨立的 PR 來審查，附上自己的迴歸測試和小延遲檢查。"

這是 Proposal B 實作的重要原則：**B-2 必須完全獨立於 Proposal A 之外**。

---

## 十三、建議 James 與 Maintainer 確認的事項

### 🔴 緊急（阻塞）

**1. 誰有最終決定權？**（AliceLJY 批准 vs rwmjhb 否決的爭議）
→ 在 Issue #513 中提出，但從未得到回答

**2. B-1 的 fresh-session 問題**：rwmjhb 說 `derived.length === 0` 是 blocking；但 AliceLJY 說 fresh-session bypass 可以接受
→ 需要 rwmjhb 親自確認是否接受 Option B 的設計方向

**3. B-2 Q5-Q9**：Issue #538 的 5 個實作缺口全部未得到回覆
→ 建議 James 去催，或自己根據以下原則做决定：
> - Q5（MMR）：neighbors 在 MMR **之前**插入，避開去重問題  
> - Q6（vector-only）：vector-only path 暫時不實作 B-2，只做 hybrid path  
> - Q7（scope）：用 recall result 各自的 scope  
> - Q9（附加方式）：作為附屬上下文（`text + "\n\nNeighbors: ..."`）

### 🟡 重要

**4. Branch 重建**：#450、#456、#458 的 branch topology 從未正確。需要從頭建立乾淨的 stack chain：
```
master
  └── feat/b1-clean (B-1 Phase 1)
        └── feat/b2-clean (B-2）
```

**5. PR #520（Per-agent exclusion）**：解決了 #492 的實際問題，但 maintainer 還沒審查。建議 James 去催 review。

**6. PR #504 的 B-2 實作**（22 tests + OpenCode adversarial review）值得重新提出，但需要先回答 Issue #538 的 Q5-Q9

**7. B-2 必須完全獨立於 Proposal A**：AliceLJY 明確說明 B-2 不能與 Proposal A 回饋邏輯綁在一起，必須各自獨立 PR
