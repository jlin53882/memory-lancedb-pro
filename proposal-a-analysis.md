# Proposal A 全面分析報告（完整版）

> 整理日期：2026-04-08
> 整理者：AI 程式修改助手（協助 James 分析 Issue #445）
> 資料來源：Issue #246、#445 及 PR #493、#507、#505、#506 的完整時間線

---

## 一、源頭背景

### Issue #246（2026-03-17，社群 Feature Request）

| 提案 | 目標 | 原始調整幅度建議 |
|------|------|----------------|
| Proposal A | 動態重要性學習 | +0.05 成功使用、+0.03 出現在回應、+0.10 用戶主動搜尋、-0.03 被忽略、-0.10 被標記錯誤、+0.15 用戶明確確認 |
| Proposal B | 記憶注意力網路 | — |
| Proposal C | 上下文感知檢索 | **已排除** |

### Issue #445（2026-04-01，jlin53882 的 RFC 分析）

**AliceLJY 確認的實作順序**：
1. Phase 1 — `agent_end` feedback loop
2. B-1 — Neighbor enrichment in reflection recall
3. Phase 2 — Wire up `last_confirmed_use_at` + `bad_recall_count` triggers
4. B-2 — Main retrieval neighbor enrichment

**AliceLJY 關鍵建議**：
- 調整幅度應可配置（最佳值因使用模式而異）
- Negative adjustment 前應有 `min_recall_count` 閾值
- Neighbor enrichment 預設僅限相同 scope

---

## 二、PR 生命週期與關閉原因

### PR #493 — ❌ 被 rwmjhb 關閉（2026-04-04）

**當時狀態**：已通過 AliceLJY 審查 → rwmjhb 審查中 → **rwmjhb `CHANGES_REQUESTED` → 直接關閉**

**rwmjhb 的 4 個關閉理由**（2026-04-04 02:56）：

1. **🔴 Per-memory scoring 被 global usage markers 破壞**
   - `isRecallUsed()` 在檢查特定 recall 內容前，先用通用片語（"remember", "as you mentioned", "from previous"）就返回 true
   - 結果：一個通用片語會 boost 所有注入的記憶，reset 所有 `bad_recall_count`
   - 這讓 per-item scoring 的核心目的失效

2. **🔴 Feedback hooks 意外被包在 `autoCapture` 條件內**
   - `agent_end`、`before_prompt_build`、`session_end` 三個 hooks 都在 `if (config.autoCapture !== false)` 區塊內
   - 停用 autoCapture 但保留 auto-recall 的用戶，會在無聲無息中失去 feedback scoring

3. **🟡 Scope drift — 5 個不相關的 bug fix 被包在一起**
   - rerankApiKey env 解析
   - recency double-boost guard
   - auto-capture-cleanup boilerplate stripping
   - smart-extractor regex fix
   - resetRegistration() WeakSet change
   - 這些應該各自獨立 PR

4. **🟡 新的 scoring 邏輯完全沒有測試**
   - 373 行新程式碼，6 個檔案，0 測試覆蓋

---

### PR #507 — ❌ 被 rwmjhb 關閉（2026-04-05）

**目標**：`#493` 的 re-org 版（針對關閉理由重新整理）
**當時狀態**：有 AliceLJY Codex review → **被直接關閉**

**AliceLJY 的 Codex Review 提出的問題**（2026-04-04 11:56）：

1. **Branch topology 錯誤**（所有 PR 的核心問題）
   - #507、#505、#506 三個 PR 都同時 targeting `master`
   - 三者修改相同的檔案（`index.ts`、`reflection-slices.ts`），會产生不可預期的衝突
   - **正確做法**：應該 stack 成 chain（#507 → #505 → #506，每個 base 到前一個）

2. **Phase 1 (#507) 的程式碼問題**
   - `autoCapture` block boundary 未確認
   - Unrelated fixes 仍然包在一起
   - `isRecallUsed` reverse-check 有 false positive 風險（「that's not right」會被當成確認）

3. **Phase 3 (#505) 需處理**
   - Keyword defaults 需要與 Phase 1 的 hardcoded 值對齊
   - **必須 rebase 到 Phase 1 branch**

4. **Phase 4 (#506) 需處理**
   - 應該 import 真正的 `FeedbackConfigManager` 而非 mock
   - 需要 hook lifecycle 的整合測試
   - **必須 rebase 到 Phase 3 branch**

**rwmjhb 關閉（2026-04-05）**：無額外留言（AliceLJY 已說明原因）

---

### PR #505 — ❌ 被 rwmjhb 關閉（2026-04-05）

**目標**：Phase 3（可配置 feedback 幅度）
**當時狀態**：有 AliceLJY review → **被直接關閉**

**AliceLJY 的關閉理由**（2026-04-04 11:56，在 #507 comment 中）：
> "See review on #507 — the branch topology for the Proposal A chain needs to be fixed first. This PR should target the Phase 1 branch, not master."

**rwmjhb 關閉（2026-04-05）**：無額外留言

---

### PR #506 — 🟡 目前唯一 Open（Phase 4 測試）

**當時狀態**：rwmjhb `CHANGES_REQUESTED`（2026-04-08）

**rwmjhb 的 `CHANGES_REQUESTED` 理由**（2026-04-08 07:13）：
1. Branch targeting 仍然錯誤（應 target Phase 3 branch，不該直接 target master）
2. **三個測試檔中有兩個在測 mock 而非真實程式碼**：
   - ✅ `isRecallUsed.test.mjs` — 從 `src/reflection-slices.ts` import（正確）
   - ❌ `feedback-config.test.mjs` — 在測試檔內重新實作 `FeedbackConfigManager`
   - ❌ `bad-recall-count.test.mjs` — `computeNextBadCount` 是測試檔內的本地函式

**Codex Review 對 `isRecallUsed()` 的 P2 bug**（2026-04-04 07:14）：

1. **`id[-:]` pattern 導致 false positive**：regex 包含 `id[-:]`，幾乎所有長回應都會讓 `hasUsageMarker=true`，讓 AND 邏輯實質上失效

2. **Summary path 缺少 `hasUsageMarker` 檢查**：有 verbatim summary match（>=10 chars）時直接返回 true，繞過 AND 邏輯

---

## 三、PR 結構的完整問題

### 核心問題：從未形成正確的 Stack Chain

jlin53882 的處理方式：
```
#493 關閉 → 打開 #507 → #507 關閉 → 打開 #505 + #506 → 全部關閉
```

**正確的 Stack Chain 應該是**：
```
master
  └── feat/proposal-a-v3-clean (#507)       ← Phase 1
        └── feat/proposal-a-v3-configurable (#505)  ← Phase 3
              └── feat/proposal-a-v3-tests (#506)   ← Phase 4
```

**實際發生的情況**：
```
master  ←── #507（應 base 到 Phase 1 branch）
master  ←── #505（應 base 到 #507）  
master  ←── #506（應 base 到 #505）
```

三個 PR 完全独立，修改同樣的檔案，每次都被以「branch topology 錯誤」為由關閉。

### 為什麼 #493 被批准後又被關閉？

AliceLJY 批准了 #493，但 rwmjhb 後來審查時給了 `CHANGES_REQUESTED` 並直接關閉——因為他發現了更深層的問題（global usage markers 破壞 per-item scoring、feedback hooks 在 autoCapture 內）。

---

## 四、實際狀態總結

| 項目 | 狀態 |
|------|------|
| Phase 1 實作程式碼 | ❌ 從未進 master |
| Phase 3 FeedbackConfigManager | ❌ 從未進 master |
| Phase 4 測試 | ⚠️ #506 Open 但有 `CHANGES_REQUESTED` |
| `isRecallUsed()` 函式 | ⚠️ 在 master 上不存在（#506 只帶 stub）|
| Branch topology 問題 | ❌ 從未被修復 |
| 正確的 Stack Chain | ❌ 從未被建立起來 |

---

## 五、A 階段是否足夠詳細？

**❌ 否，目前無法往下做。**

所有實作 PR 從未被 merge；#506 是唯一 open 的 PR，但它的問題與其前身（#507/#505）完全相同——branch topology 從未正確過。

---

## 六、待與 maintainer 確認的事項

1. **rwmjhb 在 #493 上的 `CHANGES_REQUESTED` 與直接關閉**：AliceLJY 先批准，rwmjhb 後來否決。這個 decision chain 是否正確？還是其實 Phase 1 已經足夠好，只需要修復 branch topology？

2. **正確的下一步是什麼？** 是要重新建立 Stack Chain（#507/#505/#506 各自 re-target 正確的 base），還是要從頭開始？

3. **Phase 2 的範圍**：`last_confirmed_use_at` 和 `bad_recall_count` triggers 需要单独定義 RFC 嗎？

4. **`isRecallUsed` 的兩個 Codex bug** 是否需要在 Phase 1 re-submit 時一併修復？
