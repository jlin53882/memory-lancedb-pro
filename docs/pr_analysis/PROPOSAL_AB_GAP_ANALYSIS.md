# Proposal A & B 架構分析報告

> 分析日期：2026-04-09
> 分析範圍：Issue #445、PR #493/#505/#506/#507、官方程式碼 master branch

---

## 1. 維護者確認的 Roadmap（AliceLJY 核准的實作順序）

### 官方核准的實作順序（Issue #445 Comment 1）

```
A-Phase 1 → B-1 → A-Phase 2 → B-2
```

### 各階段維護者確認狀態

| 階段 | 內容 | 維護者確認 | 確認方式 | 官方 master 現況 |
|------|------|-----------|---------|-----------------|
| **A-Phase 1** | agent_end 動態 feedback signals | ✅ AliceLJY Comment 1 明確核准 | "Solid RFC. Welcome to submit PRs" | ❌ **未合併**（PR #507 closed） |
| **B-1** | Reflection-scoped BM25 neighbor expansion | ✅ AliceLJY Comment 1：「B-1 is the right starting point」；PR #529 核准 | Comment + PR approval | ❌ **未實作**（官方 reflection-store.ts 無 BM25 expansion） |
| **A-Phase 2** | min_recall_count 閾值 + bad_recall_count 觸發 | ⚠️ Comment 1 提及方向 | 未正式 PR | ❌ 未實作 |
| **B-2** | Full retrieval vector neighbor enrichment | ✅ AliceLJY Comment 7 確認方向 | Comment 7 詳細規範 | ❌ 未實作 |
| **A-Phase 3** | FeedbackConfigManager 參數化 | ⚠️ 概念認可 | 未正式 PR | ❌ 未實作 |
| **A-Phase 4** | 單元測試覆蓋 | ⚠️ 需重寫 mock-based 測試 | AliceLJY CHANGES_REQUESTED | ❌ PR #506 open 但有嚴重問題 |

### AliceLJY 對 B-2 的 Comment 7 約束（2026-04-05）

維護者明確給出 5 項約束：
1. **same-scope only** — neighbor enrichment 限制在同 scope 內
2. **No additional MMR pass** — 簡單 effectiveScore 重排即可
3. **Original hits anchored** — 原始召回結果保留作為錨點
4. **Separate PR** — 不得與 Proposal A feedback 邏輯綑綁
5. **Regression tests + latency check** — 需独立 PR + 迴歸測試 + latency 檢查

---

## 2. 我們的現況 vs 維護者期待（Gap Analysis）

### Gap A-1：Proposal A 功能**從未進入官方 master**（嚴重程度：5/5）

**維護者期待**：PR #507（Phase 1）合併進 master，提供 agent_end feedback signals  
**官方程式碼現況**：
- `isRecallUsed()` — **不存在**於 `reflection-slices.ts`
- `FeedbackConfigManager` — **不存在**於 `src/feedback-config.ts`
- `pendingRecall` Map — **不存在**
- `agent_end` / `before_prompt_build` hooks for feedback — **不存在**
- `importanceBoostOnUse` / `importancePenaltyOnMiss` 配置 — **不存在**

**佐證**：`Select-String "isRecallUsed|FeedbackConfigManager|pendingRecall"` 在官方 master 全域無匹配。

**根本原因**：PR #507/#505/#506 都處於 `closed` 狀態（從未 merged）。#507 收到 AliceLJY CHANGES_REQUESTED 後被關閉，而非重新修改後再次提交。

---

### Gap A-2：`bad_recall_count` 只有 reset，**從未 increment**（嚴重程度：5/5）

**維護者期待**：Phase 2 中 miss path 正確遞增 `bad_recall_count`，使其能觸發 `badCount >= 2` penalty threshold  
**官方程式碼現況**：

```powershell
# 官方程式碼中 bad_recall_count 只有 = 0 的賦值
Select-String bad_recall_count 结果：
  smart-extractor.ts:1052    → bad_recall_count: 0
  smart-metadata.ts:62       → bad_recall_count: number;  (類型定義)
  tools.ts:596              → bad_recall_count: 0
# 搜尋 bad_recall_count + 1 或 bad_recall_count++ → 無結果
```

**後果**：`badCount >= 2` 的 penalty threshold **永遠不可能觸發**，因為計數器從未超過 0。

**修復方向**（需維護者確認）：
```typescript
// 在 before_prompt_build hook 的 miss path 中
const current = parseSmartMetadata(entry.metadata);
const nextBad = current.bad_recall_count + 1;  // ← 需要實作
```

---

### Gap A-3：Decay floor (0.5~0.9) 與 Feedback floor (0.1) 設計矛盾（嚴重程度：4/5）

**維護者期待**：動態 feedback 可以將 importance 降至 0.1 floor  
**官方程式碼現況**：
- Decay engine (`decay-engine.ts` L59-61)：
  ```
  coreDecayFloor = 0.9
  workingDecayFloor = 0.7
  peripheralDecayFloor = 0.5
  ```
- Feedback 設計：`importance -= 0.10, floor at 0.1`

**矛盾點**：
1. Core tier memory 若 importance 被压至 0.1，decay engine 的 `effectiveHL = halfLife × exp(1.5 × 0.1)` 幾乎不衰减，但 tier floor 0.9 強行拉高 composite score
2. importance 0.1 的 Core memory 在邏輯上是不一致的狀態

**需要維護者裁決**（3 種方案）：
- **方案 A**：feedback floor 與 tier-decay floor 掛鉤
- **方案 B**：decay floor 只約束 composite score，不約束 importance 欄位
- **方案 C**：文檔明確區分「重要性分數衰減」與「元資料重要性更新」

---

### Gap A-4：autoCapture block boundary 回歸（嚴重程度：4/5）

**維護者期待**：設定 `autoCapture: false` 時，其他 hooks（如 selfImprovement、feedback）不受影響  
**問題**：PR #505 Issue Comment 描述此 bug 並聲稱已修復，但 PR #505 是 closed 狀態，修復從未進入 master。

**風險配置**：
```json
{
  "autoCapture": false,
  "selfImprovement": { "enabled": true }
}
}
// 預期：selfImprovement 正常運行
// 實際（若 bug 存在）：selfImprovement 也被停用
```

---

### Gap A-5：Phase 4 單元測試**測 mock 而非真實程式碼**（嚴重程度：4/5）

**維護者期待**：所有測試直接 import 實際 source code  
**現況**：
- `isRecallUsed.test.mjs` — ✅ 正確（import 實際 `../src/reflection-slices.ts`）
- `feedback-config.test.mjs` — ❌ 在測試檔案內重新實作 FeedbackConfigManager mock
- `bad-recall-count.test.mjs` — ❌ `computeNextBadCount` 是 inline mock，實際 source 不存在

**後果**：若實際實作 drift，測試仍會 pass（false positive）。

---

### Gap B-1：B-1 官方 reflection-store 無 BM25 neighbor expansion（嚴重程度：4/5）

**維護者期待**：B-1 = Reflection-scoped BM25 neighbor expansion，PR #529 已核准  
**官方程式碼現況**：
```powershell
Select-String reflection-store.ts "bm25Search|BM25|neighbor"
  → 僅找到 loadAgentReflectionSlicesFromEntries 函式
  → 無 BM25 expansion 實作
```

**PR #529 狀態**：根據 Issue #445 Comment 6，B-1 指的是 PR #529（BM25 neighbor expansion for reflection），聲稱已核准。但官方 master 的 reflection-store.ts 中**完全找不到 BM25 expansion 程式碼**。

**可能的解釋**：
1. PR #529 是針對 jlin53882 的 fork 合併，而非官方 CortexReach/memory-lancedb-pro master
2. 或者 PR #529 的實作方式與官方 reflection-store.ts 的設計有衝突，導致無法合併

---

### Gap B-2：B-2 未實作（嚴重程度：3/5）

**維護者期待**：Comment 7 確認 B-2 方向，但要求獨立 PR + 迴歸測試  
**官方程式碼現況**：
```powershell
Select-String retriever.ts "neighborEnabled|neighborTopK|applyNeighborEnrichment"
  → 無結果
```

**我們的實作進度**（基於 PR chain 分析）：
- B-2 目前處於「設計確認」階段，實作程式碼尚未提出 PR

---

### Gap A-6：isRecallUsed 中「记得」重複（嚴重程度：1/5）

**問題**：`usageMarkers` 陣列中 `"记得"` 出現兩次（reflection-slices.ts L377-378）  
**狀態**：輕量 bug，無需維護者確認即可修復

---

### Gap A-7：Summary match branch 缺少 hasUsageMarker 檢查（嚴重程度：3/5）

**問題**：Codex P2 Badge 指出 ID path 需要 AND gate（ID + marker 都存在），但 summary path 只檢查 verbatim match >= 10 字元，沒有 hasUsageMarker 檢查  
**影響**：可能導致過度寬鬆的 confirm 判定

---

### Gap A-8：多語言關鍵字覆蓋不足（嚴重程度：2/5）

**問題**：
- 繁體「是對的」與簡體「确认」不互通
- 英文 confirm/error 關鍵字缺少「yes」「correct」「mistake」等常見表達

---

## 3. 待確認事項（需要問維護者的）

### 高優先順序

| # | 問題 | 背景 | 為什麼需要確認 |
|---|------|------|--------------|
| **Q1** | PR #507/#505/#506 為何被關閉而非合併？ | 所有 Phase 1~4 PR 都是 closed 狀態 | 如果是 branch targeting 錯誤，應重建正確的 stack chain |
| **Q2** | B-1 (PR #529) 是否已合併到 official master？ | 官方 reflection-store.ts 無 BM25 expansion | 若沒有，可能是 fork 合併而非官方合併，需要在官方 repo 重新提出 |
| **Q3** | `bad_recall_count` increment 是否為實作遺漏？ | 官方程式碼完全找不到 +1 邏輯 | 若確認為 bug，需要在 Phase 2 實作中修復 |
| **Q4** | Decay floor vs Feedback floor 矛盾如何解決？ | Core tier 的 0.9 floor 與 feedback 的 0.1 floor 衝突 | 需要 AliceLJY 在 A/B 兩方案中裁決 |

### 中優先順序

| # | 問題 | 背景 |
|---|------|------|
| **Q5** | `injected_count` 是否需要 decay 或 cap 機制？ | 目前單向膨脹無上限，長期運行可能 metadata bloat |
| **Q6** | Phase 4 的 test 策略是否接受 spec-test 形式？ | 若 FeedbackConfigManager source 不存在，可否先做 spec test |

---

## 4. 依賴關係圖

### Proposal A 依賴鏈

```
A-Phase 1 (PR #507) ──[需要合併]──→ A-Phase 2 ──[需要合併]──→ A-Phase 3 ──[需要合併]──→ A-Phase 4
     │                                        │                    │
     │ 依賴內容：                              │ 依賴內容：          │ 依賴內容：
     ├─ agent_end hook                       ├─ min_recall_count  ├─ FeedbackConfigManager
     ├─ isRecallUsed()                       ├─ bad_recall_count  │   (from Phase 3)
     ├─ pendingRecall Map                        +1 increment     └─ bad_recall_count
     ├─ before_prompt_build hook                                 └─ 實際實作位置
     └─ importance delta 計算
```

### Proposal B 依賴鏈

```
B-1 ──[需要確認是否在官方 master]──→ B-2
 │                                              │
 │ B-1 實作內容：                                │ B-2 實作內容：
 ├─ BM25 neighbor expansion in reflection-store  ├─ vectorSearch neighbor enrichment in retriever.ts
 └─ scope=same filter                           └─ same-scope filter (AliceLJY Comment 7 確認)
```

### A 和 B 之間的依賴關係

```
PR #507 (A-Phase 1) ──[獨立，無依賴]──→ B-2
                                           │
B-2 實作約束（AliceLJY Comment 7）：        │
  「do not bundle B-2 with Proposal A」      │
  → B-2 必須是獨立 PR                        │
                                           │
PR #529 (B-1) ──[B-1 先驗證]──→ B-2        │
  (若 B-1 證明有价值，才推 B-2)              │
```

### 官方 master 的實質依賴

```
decay-engine.ts ──[讀取 importance]──→ 任何 importance 變更自動影響 decay 分數
tier-manager.ts ──[promotion threshold]──→ importance >= 0.8 才升 Core tier
retriever.ts ──[applyImportanceWeight]──→ score *= (0.7 + 0.3 × importance)
reflection-store.ts ──[reflection-scoped]──→ B-1 的實作位置
```

---

## 5. 建議的下一步實作順序

### 立即行動（修復阻塞性問題）

```
優先順序 1：確認官方 master 的 B-1 狀態
  → 查詢 GitHub：PR #529 的 target branch 是誰？
  → 若 B-1 未進 official master，則 A-Phase 1 和 B-1 都需要重新提出

優先順序 2：重建正確的 PR stack chain
  目標分支結構：
  master
    └── feat/proposal-a-phase1-clean  (PR #507 的乾淨版本)
          └── feat/proposal-a-phase2-thresholds  (Phase 2)
                └── feat/proposal-a-phase3-config  (Phase 3)
                      └── feat/proposal-a-phase4-tests  (Phase 4)

優先順序 3：在 A-Phase 1 中實作 bad_recall_count increment
  → 在 before_prompt_build hook 的 miss path：
    const current = parseSmartMetadata(entry.metadata);
    const nextBad = current.bad_recall_count + 1;
    // 寫回 metadata

優先順序 4：修復 autoCapture block boundary
  → 確認 if (config.autoCapture !== false) { ... } 正確閉合
  → 所有 feedback hooks 在 if block 之外
```

### 中期行動（設計決策，需維護者參與）

```
優先順序 5：向 AliceLJY 提出 Decay floor vs Feedback floor 矛盾
  → 提供 3 種 solution options（見 Gap A-3）
  → 等候裁決後實作

優先順序 6：B-2 獨立 PR 準備
  → 遵守 AliceLJY Comment 7 的 5 項約束
  → 分離 Proposal A feedback 邏輯
  → 準備迴歸測試 + latency check
```

### 長期行動（架構完善）

```
優先順序 7：重寫 Phase 4 的 mock-based 測試
  → feedback-config.test.mjs：import 實際 FeedbackConfigManager
  → bad-recall-count.test.mjs：確認 computeNextBadCount 實作位置後重寫

優先順序 8：補充多語言關鍵字覆蓋
  → confirmKeywords 增加：'yes', 'correct', "that's right", '没错', '對'
  → errorKeywords 增加：'mistake', 'incorrect', "that's wrong", '错', '不对'

優先順序 9：修復 isRecallUsed 的 summary branch 缺少 hasUsageMarker 檢查
  → 與 ID path 保持一致：AND gate
```

---

## 附錄：官方程式碼關鍵位置佐證

| 驗證項目 | 檔案 | 行號 | 內容 |
|---------|------|------|------|
| decay floor 定義 | `decay-engine.ts` | L45-49 | `coreDecayFloor=0.9`, `workingDecayFloor=0.7`, `peripheralDecayFloor=0.5` |
| tier promotion threshold | `tier-manager.ts` | L52 | `coreImportanceThreshold: 0.8` |
| bad_recall_count 類型 | `smart-metadata.ts` | L62 | `bad_recall_count: number` |
| bad_recall_count reset | `smart-extractor.ts` | L1052 | `bad_recall_count: 0` |
| bad_recall_count reset | `tools.ts` | L596 | `bad_recall_count: 0` |
| importance weight in retrieval | `retriever.ts` | L1048-1051 | `score *= (0.7 + 0.3 × importance)` |
| isRecallUsed NOT in master | 全域搜尋 | - | `Select-String "isRecallUsed"` → 無結果 |
| FeedbackConfigManager NOT in master | 全域搜尋 | - | `Select-String "FeedbackConfigManager"` → 無結果 |
| neighbor enrichment NOT in master | `retriever.ts` | - | `Select-String "neighborEnabled"` → 無結果 |
| B-1 BM25 expansion NOT in master | `reflection-store.ts` | - | `Select-String "BM25|bm25Search"` → 無結果 |

---

## 驗證清單確認

- [x] Issue #445 完整內容已讀取（Proposal A & B 規格 + 7則 comments）
- [x] PR #493/#505/#506/#507 分析檔案已讀取
- [x] Claude 對抗分析報告已讀取
- [x] 官方程式碼（decay-engine.ts、tier-manager.ts、retriever.ts、smart-metadata.ts）已搜讀
- [x] 每個 Gap 都有維護者回覆或官方程式碼佐證
- [x] 每個依賴關係都有具體檔案或 comment 佐證
