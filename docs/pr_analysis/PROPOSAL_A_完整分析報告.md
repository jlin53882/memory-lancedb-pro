# Proposal A 完整分析報告
> 整理日期：2026-04-09
> 分析對象：CortexReach/memory-lancedb-pro Issue #445 — Proposal A
> 分析工具：MiniMax M2.7 × 4 sub-agents + Claude Code CLI 對抗性 Code Review

---

## ⚠️ 最重要發現：所有 PR 都未進入官方程式碼

James，你送出去的 PR #493、#505、#507、#506 **全部都是 closed 狀態，沒有一個進入官方 master**。分析的是官方 master 程式碼，和你 PR 裡的實作是**獨立的兩份程式碼**。

---

## 🔴 嚴重問題（5 個，必須修復才能繼續）

### P0-1：bad_recall_count 只有 reset，從未 increment
- **現狀**：`bad_recall_count` 在官方 master 中只有 `= 0`（reset），**從未有任何 `+1` 的實作**
- **後果**：`bad_recall_count >= 2` 的 penalty 條件**永遠不會觸發**
- **另外**：官方有個 bug——`last_confirmed_use_at` 從未被寫入，導致 `staleInjected` 幾乎每次都是 true，造成錯誤遞增
- **Claude Code 對抗發現**：PR #507 說「bad_recall_count increments correctly」是**誤導**——該實作從未進入 master

### P0-2：整個 feedback 信號系統不存在於官方程式碼
- `isRecallUsed`、`usageMarkers`、`confirmKeywords`、`errorKeywords`、`FeedbackConfigManager` **全部不存在**
- 你的 PR 實作等於從零開始興建，但 PR 本身從未合併

### P1-3：Phase 4 的單元測試在測 mock 而非真實程式碼
- `feedback-config.test.mjs` 和 `bad-recall-count.test.mjs` **不在官方 test/ 目錄**
- **AliceLJY CHANGES_REQUESTED**：這些測試檔重新實作了 FeedbackConfigManager 而非 import 真正的程式碼，無法驗證實際行為
- **修復**：需重寫為直接 import source code

### P1-4：autoCapture block boundary 回歸
- Codex P1 Badge 和 AliceLJY 都指出：`if (config.autoCapture !== false)` 區塊**未正確關閉**
- 設定 `autoCapture: false` 會一併停用 selfImprovement 等無關功能
- PR #505 聲稱已修復，但 PR #505 是 closed 未合併

### P1-5：Decay floor (0.5~0.9) 與 Feedback floor (0.1) 設計矛盾
- Decay floor: Core=0.9, Working=0.7, Peripheral=0.5
- Feedback 設計的 importance floor 是 0.1
- **矛盾**：Core tier 的記憶被 feedback 降到 0.1，但搜尋時仍有 0.9 的 boost
- **需要 AliceLJY 裁決**：這個設計是否可接受？

---

## 🟡 中等問題（5 個，建議修復）

### P2-6："that's not right" false positive
- `isRecallUsed()` 的 AND 邏輯（ID存在 + marker存在）可能無法正確過濾
- 用戶說「That's not right, it's at 3pm」——這是針對時間的否認，不是針對記憶
- 會被錯誤匹配為 error signal（-0.10 penalty）

### P2-7：Summary match 缺少 hasUsageMarker 檢查
- **Codex P2 Badge** 指出的問題
- Summary branch 直接 return true（>=10字元 verbatim match），沒有檢查 hasUsageMarker
- 會讓「巧合包含 summary text」的長回應錯誤觸發

### P2-8：id[-:] pattern 過度匹配
- **Codex P2 Badge** 指出的問題
- `id-abc123` 這類常見 ID 格式會讓 AND 邏輯失效（實際變成只有 ID check）

### P2-9：injected_count 單向遞增無重置
- `injected_count` 只增不減，長期運行可能 metadata bloat
- 需要考慮 cap 機制

### P2-10：confirmKeywords/errorKeywords 語言覆蓋不足
- 缺少簡體中文：「对」、「正确」、「没错」
- 缺少繁體中文：「對的」
- 缺少英文常見表達：「yes」、「correct」、「that's wrong」

---

## 🟢 輕微問題（3 個，可選修復）

### P3-11：Branch topology 錯誤
- #507、#505、#506 各自 target master，會產生檔案衝突
- **建議**：建立 stack chain：`feat/proposal-a-v3-clean` → `feat/proposal-a-v3-configurable-v2` → `feat/proposal-a-v3-tests`

### P3-12：unrelated bug fixes 混入同一 PR
- PR #507 混入了 5 個無關的 bugfixes（如 rerankApiKey env resolution）
- AliceLJY 要求分離

### P3-13：配置覆寫靜默失敗
- 使用者錯誤設定 `confirmKeywords: "not an array"`（傳入 string 而非 array）
- 目前是 silent fallback，但用戶可能以為自定義生效了

---

## 🔍 維護者回饋狀態總表

| 問題 | PR | 官方程式碼現狀 | 狀態 |
|------|-----|-------------|------|
| `bad_recall_count` 未遞增 | #493 | 從未 increment | ❌ 待修復 |
| `isRecallUsed` "记得" 重複 | #493 | 函式不存在 | ⚠️ 無意義 |
| Branch 目標錯誤 | #506 | PR 未合併 | ❌ 待修復 |
| test 檔 mock 問題 | #506 | 測試檔不存在於 official | ❌ 待修復 |
| `id[-:]` pattern overcount | #506 | 無法確認位置 | ❓ 需 Codex 澄清 |
| Summary match 缺 hasUsageMarker | #506 | 函式不存在 | ❌ 待修復 |
| Branch topology 問題 | #507 | PR 未合併 | ❌ 待修復 |
| autoCapture block boundary | #507 | hooks 在 block 內 | ❌ 待修復 |
| isRecallUsed false positive | #507 | 函式不存在 | ❌ 待重建 |

---

## ⚔️ Claude Code 對抗性審查精華

### AliceLJY 會問的尖銳問題

1. **「這些 PR 從未合併進 master。你現在的目標分支是什麼？」**
2. **「你說 bad_recall_count increments correctly，但我們查閱官方程式碼完全看不到 increment 邏輯。請給我出具體的檔案路徑和行號。」**
3. **「你的 importance floor 是 0.1，但 decay floor 是 0.5~0.9。當 importance 被压到 0.1 時，decay engine 的 intrinsic component 是 0.03，而 tier floor 是 0.9。你有沒有做過 end-to-end simulation？」**
4. **「Phase 4 的兩個測試文件在測 mock，你什麼時候會重寫這些測試？」**
5. **「你在一個 PR 中混合了 feature code 和 8 個無關 bugfixes，什麼時候會分離開？」**

### 邊界條件攻擊場景

1. **空輸入**：用戶說「yes」（3 字元），但 confirmKeywords 中無「yes」→ 可能漏確認
2. **Unicode 干擾**：「that's not right✔」→ "not right" 仍在，仍被當作 error keyword
3. **長文本噪音**：5000字回應中隨機包含 "id-abc123" → 直接匹配
4. **併發多 agent**：sessionKey:agentId 複合鍵若 agentId 不 stable，會失效
5. **極端 importance 值**：Core tier memory 被降到 0.1，但仍是 Core tier，decay 和 importance 脫鉤

---

## 🚩 需要與 AliceLJY 確認的 5 個問題

1. **「失敗的 recall 應該在哪個環節被偵測並遞增 bad_recall_count？」**
2. **「FeedbackConfigManager（feedback-config.ts）和 Phase 4 單元測試檔是否應該進入 official master？」**
3. **「Decay floor (0.5-0.9) vs Feedback floor (0.1) 的矛盾是否可接受？還是需要對齊？」**
4. **「Scope 是否需要限制 feedback 的應用範圍？」（跨 scope 干擾風險）**
5. **「autoCapture: false 時，哪些 hooks 應該繼續運行，哪些應該停用？」**

---

## 📁 分析檔案

路徑：`docs/pr_analysis/`

| 檔案 | 內容 |
|------|------|
| issue_0445.md | Issue #445 完整內容 |
| pr_0004.md | PR #4（fork）|
| pr_0451.md | PR #451 |
| pr_0455.md | PR #455（Phase 1）|
| pr_0493.md | PR #493 |
| pr_0505.md | PR #505（Phase 3）|
| pr_0506.md | PR #506（Phase 4）|
| pr_0507.md | PR #507 |
| CLAUDE_ADVERSARIAL_REVIEW.md | **Claude Code 對抗性 Code Review 完整報告** |

---

## 下一步建議

### 立即行動
1. 在 issue #445 聯繫 AliceLJY，確認分支策略
2. 修復 bad_recall_count increment 邏輯（在 `before_prompt_build` hook 的 miss path）
3. 修復 autoCapture block boundary
4. 重寫兩個 mock-based 測試檔

### 中期行動
5. 解決 Decay floor vs Feedback floor 矛盾（需 AliceLJY 裁決）
6. 補充多語言關鍵字覆蓋
7. 修復 isRecallUsed false positive（加入意圖分類）
8. 建立正確的 stack PR chain

---

*本報告由 MiniMax M2.7 × 4 sub-agents + Claude Code CLI 對抗性分析整合生成*
