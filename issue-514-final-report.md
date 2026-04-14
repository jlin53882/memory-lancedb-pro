# Issue #514 & Per-agent Exclusion Mechanism 最終分析報告

> 整理日期：2026-04-09
> 整理者：AI 程式修改助手（主體分析 + 2 個 Sub-agent 交叉分析 + Claude Code 對抗式 Review + 主體驗證）
> 資料來源：Issue #492, #514 / PR #515, #516, #520, #521 / PR #516 diff 驗證

---

## ⚠️ 重要更正：對抗式 Review 的一個錯誤判斷

Claude Code 對抗式 Review 說「PR #516 的核心功能已被 Revert，只剩 isOwnedByAgent tiny fix」。

**這是錯誤的。**

驗證方法：實際 fetch PR #516 的 diff。

PR #516 的 GitHub diff 顯示：
- `isAgentOrSessionExcluded` helper 函式（仍在）
- `before_prompt_build` hooks 的 exclusion check（仍在）
- 三層 guard 實作（仍在）
- `serialCooldownMs` schema（仍在）
- `isInternalReflectionSessionKey` 內部 session guard（仍在）

**Revert commit message 是 jlin53882 的意圖說明，不是實際執行的 Revert**。PR #516 的所有內容都還在，尚未被 Revert。

---

## 一、源頭問題：Issue #492

| 欄位 | 內容 |
|------|------|
| Issue | [#492](https://github.com/CortexReach/memory-lancedb-pro/issues/492) |
| 標題 | memoryReflection hook in before_prompt_build starves user session (beta.10) |
| 狀態 | **Open**（尚未修復） |
| 嚴重性 | 🔴 高：30-50% 的 user sessions 無回覆 |

**問題根因**：
- `before_prompt_build` 鉤子（priority 12 和 15）同步執行 `await loadAgentReflectionSlices()` → `store.list()` 阻塞式 DB 查詢
- Session 完成但 JSONL 檔案從未建立，Gateway 直接標記 done

**建議的修復方向**（最終採納）：
- Per-agent opt-out：允許特定 agent 排除 reflection hooks

---

## 二、提案：Issue #514

| 欄位 | 內容 |
|------|------|
| Issue | [#514](https://github.com/CortexReach/memory-lancedb-pro/issues/514) |
| 標題 | Proposal: Per-agent exclusion mechanism for before_prompt_build hooks |
| 狀態 | **Open** |

### Protection Matrix（提案內容）

| Hook | 防護機制 |
|------|----------|
| `before_prompt_build` (auto-recall) | `isAgentOrSessionExcluded` check |
| `before_prompt_build` (priority 12) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `before_prompt_build` (priority 15) | `isInternal` guard + `isAgentOrSessionExcluded` |
| `command:new/reset → runMemoryReflection` | 三層 guard：internal session + re-entrant lock + serial cooldown |
| `appendSelfImprovementNote` | internal session guard |

### 4 個 Questions for Maintainers

| # | 問題 | 目前狀態 |
|---|------|----------|
| Q1 | `autoRecallExcludeAgents` 雙用途（auto-recall + reflection 排除）是否可接受？還是要拆成 `reflectionExcludeAgents`？ | ⚠️ **衝突** — AliceLJY 接受；rwmjhb 建議拆分 |
| Q2 | 120s cooldown (`SERIAL_GUARD_COOLDOWN_MS`) 是否合理？要不要做成可設定？ | ✅ **有共識** — 可設定（但 PR #520/#521 未經 review）|
| Q3 | 用 `globalThis` + `Symbol.for` 實作 lock maps 是否有疑慮？ | ❓ **未回覆** |
| Q4 | wildcard prefix match 是否太寬泛？（dash 被一起 strip）| ❌ **未解決** — rwmjhb 提出 Must Fix |

---

## 三、PR Chain 演進

```
Issue #492 ──(提案)──▶ Issue #514 (Open)
                              │
                              ├── PR #515 (Closed) ← 第一版，範圍過大，已廢棄
                              │
                              └── PR #516 (Open ⭐) ← 目前唯一有效的 Open PR
                                         ├── AliceLJY: CHANGES_REQUESTED (2 must-fix)
                                         └── rwmjhb:  CHANGES_REQUESTED (3 must-fix + 2 questions)
                                         
PR #520/#521 (Closed) ← 嘗試加 serialCooldownMs 可設定參數，無 review
```

### 目前狀態確認

| PR | 狀態 | 內容 |
|----|------|------|
| #515 | Closed | 第一版，範圍過大，已廢棄 |
| #516 | **Open** | **完整 per-agent exclusion 實作仍在**（diff 驗證）|
| #520 | Closed | 加 serialCooldownMs，無 review |
| #521 | Closed | 同 #520，已被 revert |

**PR #516 diff 驗證結果**：所有程式碼都在，尚未被 Revert。

---

## 四、PR #516 的 Must Fix（阻塞項目）

### AliceLJY（CHANGES_REQUESTED）

| # | 項目 | 說明 |
|---|------|------|
| 1 | **Template literal 編譯錯誤** | `)'` 單引號取代 backtick |
| 2 | **PluginConfig interface 重複宣告** | `autoRecallExcludeAgents` 舊+新版並存；`recallMode` 重複宣告 |

### rwmjhb（CHANGES_REQUESTED）

| # | 項目 | 說明 |
|---|------|------|
| 1 | **Wildcard prefix match 太寬泛** | `agent-*` 會把 dash separator 一起 strip |
| 2 | **Build 失敗** | template literal 問題（同 AliceLJY）|
| 3 | **Dead schema** | `openclaw.plugin.json` 有 `memoryReflection.excludeAgents` schema，但 TypeScript 無實作讀取 |
| Q1 | 雙用途 config 是否需拆分？ | 與 AliceLJY 建議衝突 |
| Q2 | `SERIAL_GUARD_COOLDOWN_MS` 常量是否應刪除？ | 已被 `cfg.memoryReflection.serialCooldownMs` 取代 |

### 合併後的 Must Fix 清單

| # | 項目 | 提出者 | Diff 可驗證 |
|---|------|--------|------------|
| 1 | Template literal 編譯錯誤（`)'`）| AliceLJY + rwmjhb | ⚠️ diff 有 old + new，new 版看起來正常，但需驗證 build |
| 2 | PluginConfig 重複宣告 | AliceLJY | ✅ diff 可見 `recallMode` 重複 + `autoRecallExcludeAgents` 註解重複 |
| 3 | Wildcard dash separator 問題 | rwmjhb | ⚠️ 程式碼使用 `p.slice(0, -1)` 會 strip 末碼「-」，導致 `pi-` 變成 `pi` |
| 4 | Dead schema (`memoryReflection.excludeAgents`) | rwmjhb | ⚠️ 需要確認 TypeScript 是否真的沒讀取這個欄位 |

---

## 五、衝突分析

### 衝突 1：Q1 的架構方向衝突（🔴 阻塞）

| 立場 | 建議 |
|------|------|
| AliceLJY | 接受 `autoRecallExcludeAgents` 雙用途 |
| rwmjhb | 建議拆成 `reflectionExcludeAgents` 明確區分 |

**這不是「未回覆」，而是兩個 maintainer 給了相反的意見。** 需要在 PR comment 中逼他們達成共識，否則 PR 會一直被 block。

---

### 衝突 2：rwmjhb 的要求比 AliceLJY 嚴格（🟡 中）

| 項目 | AliceLJY | rwmjhb |
|------|----------|--------|
| Template literal | 1個（共同）| 1個（共同）|
| PluginConfig 重複 | 1個 | ❌ 未提出 |
| Wildcard 太寬 | ❌ 未提出 | 1個 |
| Dead schema | ❌ 未提出 | 1個 |

rwmjhb 比 AliceLJY 多了 2 個功能性 Must Fix（wildcard + dead schema），都是實質問題。

---

### 衝突 3：serialCooldownMs 的上游接受度未知（🟡 中）

PR #520/#521 未經任何 review 直接關閉。這個功能的接受度完全未知。如果 upstream 認為這是 scope creep，可能不該實作。

---

### 衝突 4：Revert 的真正原因不明（🟡 中）

PR #521 的 Revert commit message 沒有說明為何 revert。這可能是：
- jlin53882 自行決定的清理行為
- 某個私下討論的結果
- 或者是還沒執行的「意圖」

---

## 六、真正能推進的方向

### 方案 A：繼續修 PR #516（推薦）

**前提**：
1. Q1 的衝突需要先解決（`autoRecallExcludeAgents` 雙用途 vs 拆分）
2. 4 個 Must Fix 需要全部修復

**Q1 的解決方式（需要 maintainer 確認）**：
- 如果接受雙用途 → 維持現有設計
- 如果要拆分 → 需要新的 `reflectionExcludeAgents` schema

**PR #516 目前仍 Open 的原因**：jlin53882 尚未處理 review 意見。應該在 PR #516 comment 中問 maintainer 是否還在處理。

### 方案 B：新建 Feature Branch 重做

如果 PR #516 的問題太多，可以基於 upstream/master 重建乾淨的 PR。

**優點**：避開 PR #516 的複雜歷史
**缺點**：重做所有工作，浪費之前的討論

---

## 七、給 James 的行動清單

### 🔴 最高優先

1. **向 maintainer 確認 Q1 的衝突解決方案**：在 PR #516 comment 中問：「AliceLJY 和 rwmjhb 對 Q1（雙用途 vs 拆分）給了相反的意見。請在這個 thread 裡達成共識，否則 PR 會一直 block。」

2. **確認 PR #516 的 build 狀態**：jlin53882 說「Build 失敗」是 Must Fix，但 diff 內容看起來正常。需要確認目前 build 是否通過。

### 🟡 中優先

3. **修復 Must Fix 1（Template literal）**：檢查 `src/plugin.ts` 中是否有 `)'` 取代 backtick 的問題。

4. **修復 Must Fix 2（PluginConfig 重複）**：移除重複的 `recallMode` 和 `autoRecallExcludeAgents` 註解。

5. **修復 Must Fix 3（Wildcard dash）**：`isAgentOrSessionExcluded` 函式中，`p.endsWith("-")` 的邏輯需要修正，確保 `pi-` 不會被錯誤解析為 `pi`。

6. **確認 Must Fix 4（Dead schema）**：`memoryReflection.excludeAgents` schema 是否在 TypeScript 中有對應的實作讀取。如果沒有，需要刪除 schema 或新增實作。

### 🟢 低優先

7. **確認 serialCooldownMs 的定位**：如果這是 feature request 而非 bug fix，應該在 Issue 中先討論，不要直接加進 PR。

8. **問清楚 Revert commit 的意圖**：PR #521 的 Revert message 說「remove autoRecallExcludeAgents → tracked separately in PR #516/#521」，但 diff 顯示程式碼還在。需要問 jlin53882 這個 commit 是「已執行」還是「計畫」。

---

## 八、維護者要我們做什麼 vs. 有問題的地方

| 維護者要求 | 有問題的地方 |
|-----------|-------------|
| 修復 template literal 編譯錯誤 | 需要確認是哪一行有 `)'` 問題 |
| 移除重複的 PluginConfig | diff 可見，可以直接修 |
| 修正 wildcard dash 問題 | `p.slice(0, -1)` 會把 `-` 也吃掉 |
| 處理 dead schema | TypeScript 有沒有實作 `memoryReflection.excludeAgents`？ |
| Q1 衝突需要解決 | AliceLJY vs rwmjhb 給了相反的答案 |
