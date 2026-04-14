# Issue #514 & Per-agent Exclusion Mechanism 完整分析報告

> 整理日期：2026-04-09
> 整理者：AI 程式修改助手
> 分析層次：2 個 Sub-agent 交叉分析 + 主體驗證 + Claude Code 對抗式 Review
> 資料來源：Issue #492, #514 / PR #515, #516, #520, #521 / Sub-agent 報告

---

## 一、源頭問題：Issue #492

| 欄位 | 內容 |
|------|------|
| Issue | [#492](https://github.com/CortexReach/memory-lancedb-pro/issues/492) |
| 標題 | memoryReflection hook in before_prompt_build starves user session (beta.10) |
| 狀態 | **Open**（尚未修復） |
| 嚴重性 | 🔴 高：30-50% 的 user sessions 無回覆（Telegram 看不到回應） |
| 開立者 | nchcalvin-calvinapp |
| 環境 | Plugin 1.1.0-beta.10, OpenClaw v2026.4.3-dev |

**問題根因**：
- `before_prompt_build` 鉤子（priority 12 和 15）同步執行 `await loadAgentReflectionSlices()` → 內含 `store.list()` 阻塞式 DB 查詢
- 使用「全域 re-entrant guard」無法根本解決，session 仍會被 blocking
- Session 完成但 JSONL 檔案從未建立，Gateway 直接標記 done
- User 在 Telegram 上看到無回覆，沒有任何錯誤訊息

**建議的修復方向**（由 issue opener 提出）：
1. 將 reflection 移到 `session_end`（回覆之後）
2. 非同步 / detached process 執行
3. **Per-agent opt-out**（最終採納的方向）

---

## 二、提案：Issue #514

| 欄位 | 內容 |
|------|------|
| Issue | [#514](https://github.com/CortexReach/memory-lancedb-pro/issues/514) |
| 標題 | Proposal: Per-agent exclusion mechanism for before_prompt_build hooks |
| 狀態 | **Open** |
| 作者 | jlin53882（也是 #492 提議修復方向的人）|

### Protection Matrix（提案內容）

| Hook | 防護機制 |
|------|----------|
| `before_prompt_build` (auto-recall) | `isAgentOrSessionExcluded` check |
| `before_prompt_build` (priority 12) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `before_prompt_build` (priority 15) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `command:new/reset → runMemoryReflection` | 三層 guard：internal session + re-entrant lock + serial cooldown |
| `appendSelfImprovementNote` | internal session guard |

### Exclusion Pattern Matching

| Pattern | 範例 | 匹配 |
|---------|------|------|
| Exact | `"memory-distiller"` | 只有完全相等才匹配 |
| Wildcard prefix | `"pi-"` | 所有以 `pi-` 開頭的 agent |
| Temp wildcard | `"temp:*"` | 所有 `temp:` 前綴的 session |

### 4 個 Questions for Maintainers

| # | 問題 | 目前狀態 |
|---|------|----------|
| Q1 | `autoRecallExcludeAgents` 雙用途（auto-recall + reflection 排除）是否可接受？還是要拆成 `reflectionExcludeAgents`？ | ⚠️ **爭議中** — AliceLJY 接受；rwmjhb 建議拆分 |
| Q2 | 120s cooldown (`SERIAL_GUARD_COOLDOWN_MS`) 是否合理？要不要做成可設定？ | ⚠️ **部分共識** — PR #520/#521 嘗試實作可設定參數，但 PR 已被關閉 |
| Q3 | 用 `globalThis` + `Symbol.for` 實作 lock maps 是否有疑慮？ | ❌ **未回覆** — maintainer 未表態 |
| Q4 | wildcard prefix match 是否太寬泛？（`agent-*` 會把 dash separator 一起 strip 導致排除範圍過大） | ❌ **未解決** — rwmjhb 在 PR #516 Review 中特別提出 Must Fix |

---

## 三、PR Chain 演進歷史

```
Issue #492 ──(提案)──▶ Issue #514 (Open)
                              │
                              ├── PR #515 (Closed) ← 第一版，範圍過大，已廢棄
                              │
                              ├── PR #516 (Open ⭐) ← 目前唯一有效的 Open PR
                              │      ├── AliceLJY: CHANGES_REQUESTED (2 must-fix)
                              │      └── rwmjhb:  CHANGES_REQUESTED (3 must-fix + 2 questions)
                              │
                              ├── PR #520 (Closed) ← 嘗試加 serialCooldownMs，無 review
                              │
                              └── PR #521 (Closed) ← 同時在 Apr 4 revert，只保留 isOwnedByAgent fix
```

### PR #515 → Closed（第一版，已廢棄）

- **作者**：jlin53882
- **關閉時間**：2026-04-04
- **問題**：範圍過大（包含 isAgentOrSessionExcluded helper、reflection hooks 保護、三層 guard、logging 增強）
- **評審**：無
- **結論**：被 PR #516 取代

---

### PR #516 → Open（⭐ 目前唯一有效的 Open PR）

- **作者**：jlin53882
- **標題**：fix: complete Issue #492 protection — per-agent exclusion + internal session guards
- **狀態**：**Open（未 merge）**

**⚠️ 重大問題**：jlin53882 在 Apr 4 進行了大規模 Revert commit（SHA a0f5689），聲明「只保留 `src/reflection-store.ts` 的 `isOwnedByAgent` 修復」。**這意味著 per-agent exclusion 功能在 PR #516 裡也已被移除**，PR 目前只剩下無關緊要的 tiny fix。

**AliceLJY 審查意見（CHANGES_REQUESTED）**：
- ✅ **正面**：三層 guard 設計方向正確；`autoRecallExcludeAgents` 雙用途方案可行
- ❌ **Must Fix 1**：PluginConfig interface 中有**重複宣告** `autoRecallExcludeAgents`（舊的+新的並存），需移除舊的
- ❌ **Must Fix 2**：auto-recall exclusion log 中的 template literal **用單引號 `)'` 取代 backtick**，導致編譯錯誤
- Non-blocking：priority 12 和 15 的 exclusion check 程式碼高度相似，可提取成共享函式
- Non-blocking：120s hardcoded cooldown 目前可以接受

**rwmjhb 審查意見（CHANGES_REQUESTED）**：
- ❌ **Must Fix 1**：Wildcard prefix match **太寬泛** — `agent-*` 會把 dash separator 一起 strip，導致排除範圍過大
- ❌ **Must Fix 2**：Build 失敗（template literal 單引號問題，與 AliceLJY 提出的同一問題）
- ❌ **Must Fix 3**：`openclaw.plugin.json` 增加了 `memoryReflection.excludeAgents` schema，但**沒有對應 TypeScript 實作讀取該欄位**（dead schema）
- ❌ **Question**：硬編碼的 `SERIAL_GUARD_COOLDOWN_MS` 常量是否應刪除？（已被 `cfg.memoryReflection.serialCooldownMs` runtime config 取代）
- ❌ **Question**：`autoRecallExcludeAgents` 雙用途是否需要拆分？

---

### PR #520 → Closed（嘗試加可設定 cooldown，無 review）

- **作者**：jlin53882
- **標題**：fix: complete Issue #492 protection -- per-agent exclusion + **configurable serial cooldown**
- **狀態**：**Closed**（未 merge）
- **評審**：無

**與 PR #516 的差異**：
- 新增 `serialCooldownMs` 可設定參數（從 120s hardcoded 改為 `openclaw.json` 可配置）
- PR #516 是單純修復 bug，#520 是新增功能 feature

---

### PR #521 → Closed（revert，只保留 isOwnedByAgent fix）

- **作者**：jlin53882
- **標題**：fix: complete Issue #492 protection -- per-agent exclusion + configurable serial cooldown
- **狀態**：**Closed**（未 merge）
- **評審**：無
- **Commit a0f5689 說明**：Revert all changes except `isOwnedByAgent` fix

**被 revert 的項目**：
- import-markdown CLI → 需單獨追蹤（PR #426/#482）
- autoRecallExcludeAgents config → 需單獨追蹤（PR #516/#521）
- Idempotent register guard → 需單獨 feature request
- recallMode parsing → 與 #448 無關
- dual-memory docs → PR #367 已 merge
- script mode changes → 無關
- embedder/llm-client changes → 無關
- nvidia test file → Restore，與 #448 無關

**結論：PR #521 的最終狀態 = 只有 `src/reflection-store.ts` 的 `isOwnedByAgent` 修復。**

---

## 四、目前整體狀態

### 核心問題：Per-agent exclusion 功能從未 merge

```
PR #515  → Closed（範圍過大）
PR #516  → Open 但內容已被 Revert，只剩 isOwnedByAgent tiny fix
PR #520  → Closed（無 review）
PR #521  → Closed（revert，只剩 isOwnedByAgent）
```

**Per-agent exclusion 功能經過 4 個 PR、2 次 revert，仍未進入 master。**

---

## 五、衝突分析

### 衝突 1：PR #516 的 Revert 讓功能原地踏步

| 項目 | 內容 |
|------|------|
| **提出者** | Sub-agent 衝突分析 |
| **緊急度** | 🔴 最高 |

PR #516 的 Revert commit 訊息說「autoRecallExcludeAgents config → 需單獨追蹤（PR #516/#521）」，但 PR #516 本身已經是承擔這個功能的 PR。這個 Revert 等於把 PR #516 的核心內容刪除，讓功能進度歸零。

**真正發生的情況**：jlin53882 似乎是意識到 PR 範圍太大，所以先簡化到只剩 `isOwnedByAgent` fix，等待之後再重建 per-agent exclusion 功能。但這個「重建」目前還沒有發生。

---

### 衝突 2：AliceLJY ✅ vs rwmjhb ❌ 的 Must Fix 數量差異

| Reviewer | Must Fix 數量 | 重點 |
|----------|-------------|------|
| AliceLJY | 2 個 | 介面重複宣告 + template literal 編譯錯誤 |
| rwmjhb | 3 個 Must Fix + 2 個 Question | wildcard 太寬 + dead schema + build fail |

**問題**：雙方的 Must Fix 有重疊（template literal），但 rwmjhb 多了 wildcard 和 dead schema 兩個額外 Must Fix。此外，rwmjhb 的 Q1（`autoRecallExcludeAgents` 雙用途 vs 拆分）與 AliceLJY 的接受態度直接衝突。

---

### 衝突 3：Q1 的架構方向未解決

| 立場 | 建議 |
|------|------|
| AliceLJY | 接受 `autoRecallExcludeAgents` 雙用途（auto-recall + reflection 排除）|
| rwmjhb | 建議拆成 `reflectionExcludeAgents` 明確區分 |

**問題**：Q1 從未被 maintainer 討論區中正式回答。這個問題決定了 config schema 的未來結構，不能在 PR 中自己決定。

---

### 衝突 4：serialCooldownMs 功能被 revert

| PR | serialCooldownMs |
|----|-----------------|
| #516 | 120s hardcoded |
| #520/#521 | 可設定（openclaw.json schema）|

PR #520/#521 已經實作了 `serialCooldownMs` 的可設定功能，但這兩個 PR 都被關閉/ revert。如果要保留這個功能，需要重新實作或 cherry-pick 到 PR #516。

---

## 六、維護者要求我們做但尚未解決的事項

### 必須修復才能推進的事項

| # | 項目 | 提出者 | 緊急度 |
|---|------|--------|--------|
| 1 | Template literal 編譯錯誤（`)'` 單引號取代 backtick）| AliceLJY + rwmjhb | 🔴 |
| 2 | PluginConfig interface 重複宣告 `autoRecallExcludeAgents` | AliceLJY | 🔴 |
| 3 | Wildcard prefix match 太寬泛（dash 被一起 strip）| rwmjhb | 🔴 |
| 4 | `memoryReflection.excludeAgents` schema 是 dead schema，無對應實作 | rwmjhb | 🔴 |
| 5 | Build 失敗 | rwmjhb | 🔴 |

---

## 七、給 James 的行動清單

### 高優先（直接影響 Issue #492 / #514 關閉）

1. **重建 PR**：基於 upstream/master 的最新狀態，重新實作 per-agent exclusion 功能，並確保：
   - Template literal 使用 backtick（不是單引號）
   - PluginConfig interface 不重複宣告
   - Wildcard prefix 處理 dash separator 正確
   - `memoryReflection.excludeAgents` schema 有對應 TypeScript 實作（或者刪除 schema）
   - Build 能通過

2. **向 maintainer 確認 Q1**：在 comment 中問清楚 `autoRecallExcludeAgents` 的雙用途是否可接受（AliceLJY 接受，但 rwmjhb 建議拆分）

3. **決定 serialCooldownMs 的未來**：要保留 PR #520/#521 的可設定版本，需要在下一個 PR 中重新實作

### 中優先

4. **補上 Revert 的原因**：jlin53882 的 Revert commit 沒有說明為何 revert（是 CI 失敗？還是有人提出反對意見？）

5. **重新 fetch Issue #514 完整 body**：確認 Issue #514 的 4 個問題的原始表述，與 PR #516 中的問題是否一致
