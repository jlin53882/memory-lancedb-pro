# Issue #514 & Per-agent Exclusion Mechanism 分析

> 資料來源：GitHub CortexReach/memory-lancedb-pro
> 抓取時間：2026-04-09 03:08 GMT+8

---

## Issue #492（背景問題）

**標題：** memoryReflection hook in before_prompt_build starves user session (beta.10)

**嚴重程度：** 高（30-50% 的 user sessions 失敗）

**環境：**
- Plugin version: 1.1.0-beta.10
- OpenClaw: v2026.4.3-dev
- LLM for reflection: gemini-3-flash-preview
- Config: sessionStrategy: "memoryReflection", timeoutMs: 20000

**問題描述：**
`memoryReflection` session strategy（beta.9 引入，beta.10 用 global re-entrant guard 修補）仍然導致 user-facing sessions 失敗且無錯誤回饋。

**觀察到的行為：**
1. User 發送訊息 → Gateway 建立新 session（出現在 sessions.json）
2. Agent 處理序啟動 → `before_prompt_build` hook 觸發 reflection sub-session
3. Reflection sub-session 執行完畢（寫入 ~50-80KB 到自己的 JSONL）
4. 實際 user session 從未產生 JSONL 檔案 — sessions.json 中的 sessionFile 指向不存在的檔案
5. Gateway 將 session 標記為 done，但沒有產生任何 user 回應
6. User 在 Telegram 上看到無回覆

**根本原因：**
Reflection 在 `before_prompt_build` 內同步執行，blocking 住 user session pipeline。

**Workaround：**
設定 `sessionStrategy: "none"` 可消除問題，autoRecall 和 autoCapture 正常運作。

**建議修復方向：**
- 將 reflection 移到 `session_end`（response 之後）而非 `before_prompt_build`
- 非同步執行 reflection / 在 detached process 執行
- 支援 per-agent opt-out（例如 `memoryReflection.excludeAgents: ["iris"]`），因為目前 config 是全域的

**此 issue 由 OpenClaw agent (Ivy) 在 production 環境中診斷發現。**

---

## PR #515

**標題：** complete Issue #492 protection — per-agent exclusion + internal session guards

**作者：** jlin53882

**狀態：** Open（根據 fetch 到的內容無法確定是否已 merge）

**內容摘要：**
實作 per-agent exclusion + internal session guards，包含以下變更：

| 變更項目 | 說明 |
|---------|------|
| `isAgentOrSessionExcluded` helper | 支援 exact match / wildcard-prefix / `temp:*` pattern |
| 修復 auto-recall hook | 移除無效的 `agentId !== undefined` check |
| Reflection hooks 新增 exclusion check | priority 12 和 priority 15 hook 都加入 `isInternal` guard + exclusion check |
| `runMemoryReflection` command hook 三層 guard | Internal session guard + Re-entrant guard (Symbol.for + globalThis) + Serial cooldown guard |
| `appendSelfImprovementNote` 新增 internal session guard | 與 `agent:bootstrap` hook 保持一致 |
| Early-return logging 增強 | 加入 sessionKey/sessionId context |

**Guard 定義：**
- `getGlobalReflectionLock`
- `getSerialGuardMap`
- `SERIAL_GUARD_COOLDOWN_MS`

---

## PR #516

**標題：** complete Issue #492 protection -- per-agent exclusion + internal session guards

**作者：** jlin53882

**狀態：** Open

**內容摘要：**
基本與 PR #515 相同，**但在 Apr 4 進行了大規模 Revert**。

### Apr 4 Commit 變更摘要

jlin53882 在 PR #516 中新增了一個 commit，明確說明：

> **Revert all changes except the `isOwnedByAgent` fix (src/reflection-store.ts)**

| 項目 | 處理方式 | 追蹤 |
|------|---------|------|
| import-markdown CLI (cli.ts) | Remove | PR #426 / #482 |
| autoRecallExcludeAgents config | Remove | PR #516 / #521 |
| Idempotent register guard | Remove | 需单独 feature request |
| recallMode parsing | Remove | 與 #448 無關 |
| Dual-memory docs (README.md) | Remove | PR #367 已合併 |
| Script mode changes | Remove | 無關 |
| embedder/llm-client changes | Remove | 無關 |
| nvidia test file | Restore | 與 #448 無關 |

**結論：此 PR 最終只保留 `src/reflection-store.ts` 中的 `isOwnedByAgent` 修復。**

---

## PR #520

**標題：** complete Issue #492 protection -- per-agent exclusion + configurable serial cooldown

**作者：** jlin53882

**狀態：** Open

**內容摘要：**
此 PR 繼續朝向 Issue #492 保護方向實作，**加入了可設定的 serial cooldown**：

### 實作內容

| # | 變更 | 說明 |
|---|------|------|
| 1 | `isAgentOrSessionExcluded` helper | 支援 exact / wildcard-prefix / `temp:*` patterns |
| 2 | 修復 auto-recall `before_prompt_build` exclusion check | 移除無效的 `agentId !== undefined` check |
| 3 | 兩組 reflection `before_prompt_build` hooks 新增 exclusion check | Priority 12 和 Priority 15 都加入 `isInternal` guard + exclusion check |
| 4 | `runMemoryReflection` command hook 三層 guard | Internal session + Re-entrant (Symbol.for+globalThis) + Serial cooldown |
| 5 | `serialCooldownMs` 改為可設定 | 加入 PluginConfig interface 和 openclaw.plugin.json schema |
| 6 | `appendSelfImprovementNote` 新增 internal session guard | 與 `agent:bootstrap` hook 一致 |
| 7 | Early-return logging 增強 | 加入 sessionKey/sessionId context |

### openclaw.json 設定範例

```json
{
  "memory-lancedb-pro": {
    "memoryReflection": {
      "serialCooldownMs": 60000
    },
    "autoRecallExcludeAgents": ["memory-distiller", "pi-", "temp:*"]
  }
}
```

### 作者提出的問題（需 maintainer 回覆）

1. **autoRecallExcludeAgents 是否可以 dual-purpose？** 還是應該拆成 `reflectionExcludeAgents`？
2. **預設 120s cooldown 是否合理？**
3. **對 `globalThis + Symbol.for` 實作 lock maps 是否有疑慮？**

**關聯：** 相關於 #492。也可見 Issue #514。

---

## PR #521

**標題：** complete Issue #492 protection -- per-agent exclusion + configurable serial cooldown

**作者：** jlin53882

**狀態：** Open

**內容摘要：**
基本與 PR #520 相同，**同樣在 Apr 4 進行了與 PR #516 相同的大規模 Revert**。

### Apr 4 Commit 變更摘要

與 PR #516 的 revert commit 完全一致：

> **Revert all changes except the `isOwnedByAgent` fix (src/reflection-store.ts)**

被 revert 的項目（與 PR #516 完全相同）：
- import-markdown CLI (cli.ts) → Remove
- autoRecallExcludeAgents config → Remove
- Idempotent register guard → Remove
- recallMode parsing → Remove
- Dual-memory docs → Remove
- Script mode changes → Remove
- embedder/llm-client changes → Remove
- nvidia test file → Restore

**結論：此 PR 最終也只保留 `src/reflection-store.ts` 中的 `isOwnedByAgent` 修復。**

---

## Issue #514 的 4 個問題與目前狀態

> 根據 PR #515/#516/#520/#521 的內容交叉比對，推斷 Issue #514 可能提出的 4 個問題如下：

| # | 問題 | 現況 |
|---|------|------|
| 1 | `memoryReflection` 在 `before_prompt_build` 同步執行 blocking user session | PR #515/#520 嘗試用 per-agent exclusion 解決，但兩 PR 都被 revert |
| 2 | `autoRecallExcludeAgents` 設定項的去留爭議 | PR #516/#521 中被移除，改由單獨的 PR 追蹤 |
| 3 | `serialCooldownMs` 可設定性的實作 | PR #520 有實作，但在 PR #521 的 revert commit 中被移除 |
| 4 | Internal session guard 的實作一致性 | `appendSelfImprovementNote` 和 `runMemoryReflection` 都需要此 guard |

**目前瓶頸：** 兩組 PR (#515 vs #516, #520 vs #521) 的最後 commit 都是 revert，只保留 `isOwnedByAgent` 修復。Per-agent exclusion 功能尚未正式 merge。

---

## 完整 Protection Matrix

根據 PR #515/#520 的實作規劃，Protection Matrix 應為：

### Session Type × Feature Intersection

| Session Type | autoRecall Hook | memoryReflection Hook | selfImprovement Hook |
|-------------|----------------|----------------------|---------------------|
| User session (normal) | ✅ 受 `autoRecallExcludeAgents` 影響 | ✅ 受 exclusion check 影響 | ✅ 受 internal guard 影響 |
| Internal reflection session | ⛔ Internal guard | ⛔ Internal guard + re-entrant lock | ⛔ Internal guard |
| Temp/ephemeral session | ⛔ `temp:*` pattern excluded | ⛔ `temp:*` pattern excluded | ⛔ `temp:*` pattern excluded |
| Bootstrap agent session | ⛔ Internal guard | ⛔ Internal guard | ⛔ Internal guard |
| 特定 agent (e.g. pi-, memory-distiller) | ⛔ Pattern excluded | ⛔ Pattern excluded | ✅ 正常執行 |

### Guard Layers（runMemoryReflection command hook）

| Layer | 機制 | 說明 |
|-------|------|------|
| Layer 1 | Internal session guard | 防止 internal reflection sessions 被再次 trigger |
| Layer 2 | Re-entrant guard (Symbol.for + globalThis) | 防止同一 session 重複進入 |
| Layer 3 | Serial cooldown guard (configurable) | 預設 120s，可透過 `serialCooldownMs` 調整 |

### Exclusion Pattern Matching

| Pattern | 範例 | 匹配 |
|---------|------|------|
| Exact | `"memory-distiller"` | 只有完全相等才匹配 |
| Wildcard prefix | `"pi-"` | 所有以 `pi-` 開頭的 agent |
| Temp wildcard | `"temp:*"` | 所有 `temp:` 前綴的 session |

---

## 衝突分析

### 衝突 1：PR #515 vs PR #516 對立性變更

- PR #515：提出完整的 per-agent exclusion + internal guards
- PR #516：最終 commit revert 所有變更，只保留 `isOwnedByAgent` fix
- **問題：** 兩個 PR 指向同一 target，卻有衝突的最終狀態

### 衝突 2：PR #520 vs PR #521 對立性變更

- PR #520：提出 per-agent exclusion + **可設定的 serial cooldown**
- PR #521：同樣在 Apr 4 revert 所有變更（包含 serialCooldownMs 的設定性）
- **問題：** `serialCooldownMs` 已經實作Schema 支援，但被 revert 掉

### 衝突 3：autoRecallExcludeAgents 的 dual-purpose 爭議

- PR #520 的 open question：這個設定項是給 autoRecall 和 reflection 共同使用，還是應該拆成兩個？
- 被 revert 後：變成需在單獨 PR 中追蹤（PR #516/#521 的 revert message 有提到）
- **建議：** 需有明確 decision — 拆成兩個獨立的 config 項是否更清晰？

### 衝突 4：Revert 原因不明

- Revert commit 訊息列出了多個 removal 項目，但**沒有說明 revert 的原因**（為何這些變更需要被 revert？）
- **可能的解讀：**
  1. 這些變更引發了新的問題（例如 Issue #514）
  2. 與其他已存在的 PR/branch 產生衝突
  3. 作者在發現需要拆分成更小的 PR 才能 merge

---

## 建議的行動清單

### 高優先（直接影響 Issue #514 關閉）

- [ ] **確認 Issue #514 的完整內容**：目前只知道有 4 個問題，但缺乏 Issue #514 的直接 body 內容，需再次 fetch 確認
- [ ] **決定 autoRecallExcludeAgents 的架構**：dual-purpose 還是拆分？盡快在 comment 中與 maintainer (jlin53882) 確認
- [ ] **重建 PR 以 merge per-agent exclusion**：建議基於最新的 upstream/master，拆分成更小的 PR（避免一次變更過多）
- [ ] **為 serialCooldownMs 建立獨立的 tracking PR**：目前在 PR #520 中，但已被 revert，需單獨處理

### 中優先（架構改善）

- [ ] **評估將 reflection 從 `before_prompt_build` 遷移到 `session_end`**：這是 Issue #492 建議的根本解決方案，per-agent exclusion 只是緩解措施
- [ ] **建立 internal session 的標準定義**：哪些 session key pattern 算是 internal？需有一個统一的名稱約定
- [ ] **補上 Revert 的原因記錄**：在 PR #516/#521 的 revert commit 中補充 revert 的具體原因（是 CI 失敗？還是有人提出 review comment？）

### 低優先（長期改進）

- [ ] **為 `globalThis + Symbol.for` lock maps 撰寫技術文件**：PR #520 的 maintainer question 中有提到，需有明確的設計決策記錄
- [ ] **Idempotent register guard 的单独 feature request**：PR #516 revert message 有提到，需新建一個 issue 追蹤

---

## 附錄：時間線摘要

```
2026-04-04 之前   PR #515, #516, #520, #521 相繼建立
2026-04-04       jlin53882 在 PR #516 和 #521 中同時新增 revert commit
                 內容：Revert all changes except isOwnedByAgent fix
                 → 只保留 src/reflection-store.ts 的 isOwnedByAgent 修復
2026-04-08       Issue #514 提出（內容需確認）
現在              所有 4 個 PR 都處於 Open 狀態
                 per-agent exclusion 功能未被 merge
```
