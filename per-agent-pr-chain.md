# Issue #514 & PR Chain 分析報告

> 目標 repo：`CortexReach/memory-lancedb-pro`
> 報告日期：2026-04-09
> 分析者：sub-agent（per-agent-pr-chain 任務）

---

## 一、源頭：Issue #492

| 欄位 | 內容 |
|------|------|
| Issue 編號 | [#492](https://github.com/CortexReach/memory-lancedb-pro/issues/492) |
| 標題 | memoryReflection hook in before_prompt_build starves user session (beta.10) |
| 狀態 | **Open**（尚未修復） |
| 開立者 | nchcalvin-calvinapp |
| 嚴重性 | 30-50% 使用者 session 無回覆（Telegram 看不到回應） |

**問題根因**：
- `before_prompt_build` 鉤子（priority 12 和 15）同步執行 `await loadAgentReflectionSlices()` → 內含 `store.list()` 阻塞式 DB 查詢
- 使用「全域 re-entrant guard」無法根本解決，session 仍會被 blocking
- Session 完成但 JSONL 檔案從未建立，gateway 直接標記 done

**Issue #492 提議的修復方向**：
1. 將 reflection 移到 `session_end`（回覆後）
2. 非同步 / detached process 執行
3. **Per-agent opt-out**（最終採納的方向）

---

## 二、Issue #514：Proposal 文件

| 欄位 | 內容 |
|------|------|
| Issue 編號 | [#514](https://github.com/CortexReach/memory-lancedb-pro/issues/514) |
| 標題 | Proposal: Per-agent exclusion mechanism for before_prompt_build hooks |
| 狀態 | **Open** |
| 開立者 | jlin53882（同一作者） |
| 關聯 | 解決 Issue #492 的具體提案 |

### Protection Matrix（提案內容）

| Hook | 防護機制 |
|------|----------|
| `before_prompt_build` (auto-recall) | `isAgentOrSessionExcluded` check |
| `before_prompt_build` (priority 12) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `before_prompt_build` (priority 15) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `command:new/reset → runMemoryReflection` | 三層 guard：internal session + re-entrant lock + serial cooldown |
| `appendSelfImprovementNote` | internal session guard |

### 4 個 Questions for Maintainers（目前狀態）

| # | 問題 | 目前狀態 |
|---|------|----------|
| Q1 | `autoRecallExcludeAgents` 雙用途（auto-recall + reflection 排除）是否可接受？還是要拆成 `reflectionExcludeAgents`？ | **❌ 未回覆** — AliceLJY 和 rwmjhb 均有提出，但雙方建議不同（見下方） |
| Q2 | 120s cooldown (`SERIAL_GUARD_COOLDOWN_MS`) 是否合理？要不要做成可設定？ | **⚠️ 部分解決** — PR #520/#521 試圖加入 `serialCooldownMs` 可設定參數，但 PR 本身被關閉 |
| Q3 | 用 `globalThis` + `Symbol.for` 實作 lock maps 是否有疑慮？ | **❌ 未回覆** |
| Q4 | wildcard prefix match 是否太寬泛？（`agent-*` 會把 dash 一起 strip 導致排除範圍過大） | **❌ 未解決** — rwmjhb 在 PR #516 Review 裡特別提出，但尚未修復 |

---

## 三、PR Chain 演進歷史

### PR #515 → **Closed**（被取代）
| 欄位 | 內容 |
|------|------|
| PR 編號 | [#515](https://github.com/CortexReach/memory-lancedb-pro/pull/515) |
| 作者 | jlin53882 |
| 標題 | fix: complete Issue #492 protection — per-agent exclusion + internal session guards |
| 狀態 | **Closed**（未 merge）|
| 關閉時間 | 2026-04-04T10:37:02Z |
| 評審 | 無 |

**概述**：第一版，範圍過大（包含 `isAgentOrSessionExcluded` helper、reflection hooks 保護、三層 guard、logging 增強）。後續被 PR #516 取代。

---

### PR #516 → **Open（待解決）**⭐
| 欄位 | 內容 |
|------|------|
| PR 編號 | [#516](https://github.com/CortexReach/memory-lancedb-pro/pull/516) |
| 作者 | jlin53882 |
| 標題 | fix: complete Issue #492 protection — per-agent exclusion + internal session guards |
| 狀態 | **Open（仍開啟）** |
| 評審 | AliceLJY ✅, rwmjhb ✅（均為 CHANGES_REQUESTED）|

**Timeline 事件順序**：
1. jlin53882 開啟 PR #516
2. chatgpt-codex-connector[bot] 留言
3. jlin53882 多次 commit、comment
4. AliceLJY → **CHANGES_REQUESTED**
5. jlin53882 再次 commit
6. rwmjhb → **CHANGES_REQUESTED**
7. jlin53882 大量 comment 回覆討論
8. jlin53882 將 PR **關閉**
9. jlin53882 重新 **Reopen** PR #516（目前狀態）

**AliceLJY 審查意見（CHANGES_REQUESTED）**：
- ✅ **正面**：三層 guard 設計方向正確；`autoRecallExcludeAgents` 雙用途方案可行
- ❌ **Must Fix 1**：PluginConfig interface 中有**重複宣告** `autoRecallExcludeAgents`（舊的+新的並存），需移除舊的
- ❌ **Must Fix 2**：auto-recall exclusion log 中的 template literal **用單引號 `)'` 取代 backtick**，導致編譯錯誤
- Non-blocking：priority 12 和 15 的 exclusion check 程式碼高度相似，可提取成共享函式
- Non-blocking：120s hardcoded cooldown 目前可以接受

**rwmjhb 審查意見（CHANGES_REQUESTED）**：
- ❌ **Must Fix 1**：Wildcard prefix match **太寬泛** — `agent-*` 會把 dash separator 一起 strip，導致排除範圍過大
- ❌ **Must Fix 2**：Build 失敗（template literal 單引號問題，AliceLJY 已指出但 diff 中仍未修復）
- ❌ **Must Fix 3**：`openclaw.plugin.json` 增加了 `memoryReflection.excludeAgents` schema，但**沒有對應 TypeScript 實作讀取該欄位**（dead schema）
- ❌ **Question**：硬編碼的 `SERIAL_GUARD_COOLDOWN_MS` 常量是否應刪除？（已被 `cfg.memoryReflection.serialCooldownMs` runtime config 取代）
- ❌ **Question**：`autoRecallExcludeAgents` 雙用途是否需要拆分？

---

### PR #520 → **Closed**（被取代）
| 欄位 | 內容 |
|------|------|
| PR 編號 | [#520](https://github.com/CortexReach/memory-lancedb-pro/pull/520) |
| 作者 | jlin53882 |
| 標題 | fix: complete Issue #492 protection -- per-agent exclusion + configurable serial cooldown |
| 狀態 | **Closed**（未 merge）|
| 關閉時間 | 2026-04-04T13:44:05Z |
| 評審 | 無 |

**與 PR #516 的差異**：
- 新增 `serialCooldownMs` 可設定參數（從 120s hardcoded 改為 `openclaw.json` 可配置）
- PR #516 是單純修復 bug，#520 是新增功能 feature

**為何被關閉**：同一時間段（#520 關閉後 1.7 分鐘）作者立即開啟了 PR #521（幾乎相同內容），推測 #520 是為了對比測試或討論而短暫開啟。

---

### PR #521 → **Closed**（被取代）
| 欄位 | 內容 |
|------|------|
| PR 編號 | [#521](https://github.com/CortexReach/memory-lancedb-pro/pull/521) |
| 作者 | jlin53882 |
| 標題 | fix: complete Issue #492 protection -- per-agent exclusion + configurable serial cooldown |
| 狀態 | **Closed**（未 merge）|
| 關閉時間 | 2026-04-04T13:45:44Z |
| 評審 | 無 |

**注意**：PR #516 和 #521 的 commit SHA 相同（`a0f5689`），表示 #521 的最終 commit 是從 #516 的同一 commit 來的。

**作者在 commit 中的回滾說明**：
> Revert all changes except the isOwnedByAgent fix (src/reflection-store.ts):
> - Remove import-markdown CLI → tracked separately in PR #426/#482
> - **Remove autoRecallExcludeAgents config** → tracked separately in PR #516/#521
> - Remove idempotent register guard → separate feature request needed
> - Remove recallMode parsing → unrelated
> - Remove dual-memory docs → already merged in PR #367
> - Remove script mode changes → unrelated
> - Remove embedder/llm-client changes → unrelated
> - Restore deleted nvidia test file → unrelated
>
> **Only src/reflection-store.ts isOwnedByAgent fix remains.**

→ 這是作者在 PR #521 上的隔離變更，與主 PR #516 是不同範圍。

---

## 四、PR #516 與 PR #520 核心差異

| 項目 | PR #516 | PR #520/#521 |
|------|---------|--------------|
| `serialCooldownMs` | 120s **hardcoded** (`SERIAL_GUARD_COOLDOWN_MS`) | **可配置**（寫入 `openclaw.plugin.json` schema） |
| 評審狀態 | 2 位 reviewer（AliceLJY + rwmjhb，均 CHANGES_REQUESTED）| 無評審 |
| PR 狀態 | Open（目前）| Closed |
| 問題範圍 | Bug fix + 功能變更 | 功能變更（configurable cooldown）|
| Issue #492 解決 | 完整三層 guard | 多了可配置參數 |

---

## 五、Issue #514 四個問題目前狀態摘要

| 問題 | 狀態 | 說明 |
|------|------|------|
| Q1: `autoRecallExcludeAgents` 雙用途 vs 拆分？ | ⚠️ **爭議中** | AliceLJY 接受；rwmjhb 建議拆分 |
| Q2: 120s cooldown 是否合理/可設定？ | ✅ **有共識（可設定）** | PR #520/#521 嘗試實作，但 PR 已被關閉；目前 PR #516 仍是 hardcoded |
| Q3: `globalThis` + `Symbol.for` lock maps 安全疑慮？ | ❓ **未回覆** | maintainer 未表态 |
| Q4: wildcard prefix match 太寬泛？ | ❌ **待修** | rwmjhb 提出的 Must Fix，尚未修復 |

---

## 六、目前整體狀態判斷

```
Issue #492 ──(提案)──▶ Issue #514 (Open)
                              │
                              ├── PR #515 (Closed) ← 第一版，已廢棄
                              │
                              └── PR #516 (Open ⭐) ← 目前唯一有效的 Open PR
                                         │
                                         ├── AliceLJY: CHANGES_REQUESTED (2 must-fix)
                                         └── rwmjhb:  CHANGES_REQUESTED (3 must-fix + 2 questions)
                                         
PR #520/#521 (Closed, 已被取代) ← 嘗試加 serialCooldownMs 可設定參數
```

**結論**：
- **PR #516 是目前唯一 Open 的 PR**，但兩個 reviewer 都提出了 Must Fix 項目尚未修復
- 主要阻塞問題：`autoRecallExcludeAgents` 重複宣告、template literal 編譯錯誤、wildcard 範圍過寬、dead schema
- `serialCooldownMs` 可設定功能在 #520/#521 中已實作但這兩個 PR 已被關閉，若要保留該功能需要再重新開 PR 或 cherry-pick 到 #516
- Issue #514 的 4 個 Q 中，**只有 Q2 達到某種程度的共識**（做成可設定），其餘 Q1/Q3/Q4 均懸而未決
