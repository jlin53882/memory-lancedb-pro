# Proposal A & B 完整分析最終報告
> 整理日期：2026-04-09
> 分析對象：CortexReach/memory-lancedb-pro Issue #445 — Proposal A & B
> 分析工具：MiniMax M2.7 × 4 sub-agents + Claude Code CLI 對抗性 Code Review + Bug Learnings 整理

---

## ⚠️ 執行摘要

**James，你負責的 PR #493/#505/#506/#507 全部是 closed 狀態，沒有一個進入官方 master。**

更重要的是，連 PR #529（B-1，BM25 neighbor expansion）聲稱已核准，但官方 master 的 reflection-store.ts 中也找不到 BM25 expansion 程式碼。

這意味著：**Proposal A 和 Proposal B 的所有實作，可能從未進入過官方 CortexReach/memory-lancedb-pro master。**

---

## 🔴 P0 必須優先處理的問題（共 3 個）

### P0-1：所有 PR 從未合併進官方 master

| PR | 內容 | 狀態 | 問題 |
|----|------|------|------|
| #493 | Phase 1 動態 feedback | closed | 未合併 |
| #505 | Phase 3 FeedbackConfigManager | closed | 未合併 |
| #506 | Phase 4 單元測試 | **open**（有 CHANGES_REQUESTED）| 未合併 |
| #507 | Phase 1 v3 clean | closed | 未合併 |
| #529 | B-1 BM25 expansion | 聲稱 approved | 官方無 BM25 expansion |

**根本問題**：PR #507/#505/#506 都收到 AliceLJY 的 CHANGES_REQUESTED 後被關閉，而非修改後重新提出。

---

### P0-2：bad_recall_count 只有 reset，從未 increment

**現狀**：官方 master 中 `bad_recall_count` 只有 `= 0`（reset），從未有任何 `+ 1`（increment）。

```powershell
# 搜尋 "bad_recall_count + 1" 或 "bad_recall_count++" → 零結果
```

**後果**：`bad_recall_count >= 2` 的 penalty 條件**永遠不會觸發**。Phase 2 的核心功能完全失效。

**修復方向**（需確認）：
```typescript
// 在 before_prompt_build hook 的 miss path 中
const current = parseSmartMetadata(entry.metadata);
const nextBad = current.bad_recall_count + 1;  // ← 需要實作
```

---

### P0-3：last_confirmed_use_at 從未被寫入

**現狀**：官方 master 中 `last_confirmed_use_at` 只有被讀取（parseSmartMetadata），從未被任何地方寫入。

**後果**：`staleInjected` 判斷中 `typeof meta.last_confirmed_use_at !== "number"` 幾乎永遠為 true，導致 `bad_recall_count` 在幾乎每次 injection 都錯誤遞增。

**修復方向**：
```typescript
// feedback 確認時寫入
{ last_confirmed_use_at: Date.now() }
```

---

## 🟡 P1 需要修復的問題（共 5 個）

### P1-1：Phase 4 測試在測 mock 而非真實程式碼

- `feedback-config.test.mjs` — 在測試檔案中重新實作 FeedbackConfigManager，沒有 import 真正的 source code
- `bad-recall-count.test.mjs` — `computeNextBadCount` 是 inline mock，實際 source 不存在
- 唯一正確的是 `isRecallUsed.test.mjs` — 有正確 import

**修復**：重寫為直接 import 實際 source code。

### P1-2：autoCapture block boundary 回歸

- `if (config.autoCapture !== false)` 區塊**未正確關閉**
- 設定 `autoCapture: false` 會一併停用 selfImprovement 等無關功能
- PR #505 聲稱已修復，但從未進入官方 master

**修復**：在 feedback hooks 區段前確認 `}` 正確閉合。

### P1-3：Decay floor (0.5~0.9) 與 Feedback floor (0.1) 設計矛盾

- Decay floor: Core=0.9, Working=0.7, Peripheral=0.5
- Feedback 設計的 floor 是 0.1
- **矛盾**：Core tier 的記憶被 feedback 降到 0.1，但搜尋時仍有 0.9 的 boost

**需要 AliceLJY 裁決**（3 種方案）：
- 方案 A：feedback floor 與 tier-decay floor 掛鉤
- 方案 B：decay floor 只約束 composite score，不約束 importance
- 方案 C：文檔明確區分兩個概念

### P1-4：B-1 BM25 expansion 官方不存在

- PR #529 聲稱已核准，但官方 reflection-store.ts 中無 BM25 expansion
- 可能原因：PR #529 是對 jlin53882 fork 的合併，而非官方 CortexReach/master

**需要確認**：PR #529 的 target branch 是誰？

### P1-5：isRecallUsed 的 "that's not right" false positive

- 用戶說「That's not right, it's at 3pm」會被錯誤匹配為 error signal（-0.10 penalty）
- 這是在否認時間，不是否認記憶

**修復**：加入意圖分類，或移除 "not right" 關鍵字。

---

## 🟢 P2 建議修復的問題（共 6 個）

| # | 問題 | 嚴重程度 |
|---|------|---------|
| P2-1 | Summary match 缺少 hasUsageMarker 檢查 | 2/5 |
| P2-2 | id[-:] pattern 過度匹配 | 2/5 |
| P2-3 | confirmKeywords/errorKeywords 語言覆蓋不足 | 2/5 |
| P2-4 | injected_count 單向膨脹無 cap | 2/5 |
| P2-5 | "记得" 在 usageMarkers 中重複 | 1/5 |
| P2-6 | 配置覆寫靜默失敗 | 2/5 |

---

## 🚩 需要與 AliceLJY 確認的 6 個問題

### Q1（高優先）
**PR #507/#505/#506 為何被關閉而非合併？是 branch targeting 錯誤嗎？**

### Q2（高優先）
**B-1 (PR #529) 是否已合併到 official CortexReach/memory-lancedb-pro master？**（官方程式碼找不到 BM25 expansion）

### Q3（高優先）
**bad_recall_count increment 是否為實作遺漏？還是不打算實作？**

### Q4（高優先）
**Decay floor (0.9) 與 Feedback floor (0.1) 矛盾如何解決？**

### Q5（中優先）
**injected_count 是否需要 decay 或 cap 機制？**

### Q6（中優先）
**Scope 是否需要限制 feedback 的應用範圍？**

---

## 📋 PR 鏈 Gap 總表

### Proposal A 依賴鏈

```
A-Phase 1 ──→ A-Phase 2 ──→ A-Phase 3 ──→ A-Phase 4
   (#507)       (未PR)      (#505)        (#506)
   ❌ closed   ❌ 未實作   ❌ closed    ⚠️ open
```

### Proposal B 依賴鏈

```
B-1 ──→ B-2
(#529)   (未PR)
⚠️ 不確定  ❌ 未實作
```

---

## ✅ 已完成的動作

1. **4 個 sub-agent 分析完成**
2. **Claude Code CLI 對抗性 Code Review 完成**
3. **Bug 整理寫入 learnings 檔案**
   - ERRORS.md：15 筆新 bug 記錄
   - LEARNINGS.md：新增 Proposal A 專用規則
   - FEATURE_REQUESTS.md：新建，6 筆功能需求
4. **4 筆關鍵記憶寫入 LanceDB**

---

## 📁 分析檔案路徑

```
docs/pr_analysis/
├── PROPOSAL_A_完整分析報告.md      ← 完整分析摘要
├── PROPOSAL_AB_GAP_ANALYSIS.md    ← 架構 Gap 分析
├── CLAUDE_ADVERSARIAL_REVIEW.md   ← Claude Code 對抗性審查
├── issue_0445.md                  ← Issue #445 內容
├── pr_0493.md / pr_0505.md / pr_0506.md / pr_0507.md
└── pr_0004.md / pr_0451.md / pr_0455.md
```

```
.learnings/
├── ERRORS.md                      ← 15 筆新 bug 記錄
├── LEARNINGS.md                   ← 新增 PA1-PA9 規則
└── FEATURE_REQUESTS.md            ← 6 筆功能需求
```

---

## 🎯 下一步建議

### 立即行動
1. 在 issue #445 問 AliceLJY：「PR #529 B-1 是否已合併進 official master？」
2. 確認 PR #507/#505/#506 被關閉的原因
3. 重建正確的 PR stack chain：
   ```
   master
     └── feat/proposal-a-phase1-clean  → A-Phase 1
           └── feat/proposal-a-phase2      → A-Phase 2（實作 bad_recall_count +1）
                 └── feat/proposal-a-phase3  → A-Phase 3（FeedbackConfigManager）
                       └── feat/proposal-a-phase4 → A-Phase 4（重寫 mock 測試）
   ```

### 獲得裁決後行動
4. 解決 Decay floor vs Feedback floor 矛盾
5. 準備 B-2 獨立 PR（遵守 AliceLJY Comment 7 的 5 項約束）

---

*本報告由 MiniMax M2.7 × 4 sub-agents + Claude Code CLI 對抗性分析 + Bug Learnings 整理整合生成*
*整理時間：2026-04-09*
