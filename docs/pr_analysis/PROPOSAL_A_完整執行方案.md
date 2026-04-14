# Proposal A Phase 1-4 完整執行方案
> 整理日期：2026-04-13
> 依據：Issue #445 + Issue #569 (AliceLJY 確認回覆)

---

## 1. 現況

### 1.1 分支狀態

| Branch | Phase | 最新 commit | 落後官方 master |
|--------|-------|------------|----------------|
| `feat/proposal-a-v3-clean` | Phase 1 | `649e90631b` | 落後 12 個 commits，領先 13 個 |
| `feat/proposal-a-v3-configurable-v2` | Phase 3 | `4ce42d63be` | 待確認 |
| `feat/proposal-a-v3-tests` | Phase 4 | `52d822d080` | 待確認 |

### 1.2 Issue #569 AliceLJY 確認的回覆

- **Stack Chain 順序**：Phase 1 → Phase 3 → Phase 4
- **Phase 2**：獨立的，可以晚點再做
- **必須先 rebase 到最新 master** 再提交第一個 PR
- **提交時附上與 #507/#505 的變更摘要**

---

## 2. Stack Chain 架構

```
CortexReach/memory-lancedb-pro:master
  └── feat/proposal-a-v3-clean           (Phase 1) → PR against master
      └── feat/proposal-a-v3-configurable-v2  (Phase 3) → PR against Phase 1 branch
          └── feat/proposal-a-v3-tests         (Phase 4) → PR against Phase 3 branch
```

每個 PR 以上一個 phase branch 為 base。Phase 1 合併後，Phase 3 rebase 到 master，再提交。

---

## 3. Phase 1 實作內容（來自 PR #507 body + commits）

### Hooks
- `agent_end` (priority 20)：捕捉 agent 回應文字寫入 pendingRecall
- `before_prompt_build` (priority 5)：在下個 turn 評分 recall 使用情況
- `session_end` (priority 20)：清理 pendingRecall  entries

### isRecallUsed() AND Logic
檢查特定 memory ID 存在 AND generic usage marker（兩者都要滿足）：
```typescript
const hasSpecificRecall = injectedIds.some(id => response.includes(id));
if (hasSpecificRecall) {
  for (const marker of usageMarkers) {
    if (response.includes(marker)) return true;
  }
}
```

### Per-Recall Scoring
每個 recallId 單獨計分，memory之間不互相污染。

### Key Fixes（從 #493 review 來的修復）
- AND logic 防止通用片語錯誤提升所有 injected memories
- `bad_recall_count` 在 error/miss paths 正確遞增
- `sessionKey:agentId` composite key 防止跨 agent 干擾
- `session_end` 正確清理 composite keys（autoCapture=false 時不 memory leak）

### 實作檔案範圍
- `index.ts`：+272 lines（hooks, scoring loop, pendingRecall map）
- `src/reflection-slices.ts`：+95 lines（isRecallUsed function）
- `src/auto-capture-cleanup.ts`：+11 lines
- `src/smart-extractor.ts`：+2 lines（regex fix）
- `src/retriever.ts`：+9 lines（recency double-boost guard）

### 與 #507 相比的變更摘要（提交 PR 時需要）
| # | 修復內容 | commit |
|---|---------|--------|
| 1 | session_end hook 清理 composite keys 防止 memory leak | `649e9063` |
| 2 | AND logic + bad_recall_count increment fix | `bd0c582a` |
| 3 | bad_recall threshold 從 3 改為 2（符合 spec）| `b92c47ce` |
| 4 | 更長的 CJK keywords + session_end pendingRecall cleanup | `3a5c61c5` |
| 5 | per-recall scoring 修正、event.messages user prompt、agentId keying | `ee5c176f` |
| 6 | 4 個 feedback hooks bugs | `4a6fe62c` |
| 7 | 重要性 fallback、pendingRecall cleanup、env-resolve gate、recency double-boost | `469e069d` |

---

## 4. Phase 2 實作內容（尚未實作）

| 項目 | 說明 |
|------|------|
| `min_recall_count` | Threshold for triggering feedback |
| `bad_recall_count` increment | 在 miss path 中正確遞增 |

---

## 5. Phase 3 實作內容（FeedbackConfigManager）

### FeedbackConfigManager (src/feedback-config.ts)
```typescript
class FeedbackConfigManager {
  computeImportanceDelta(event: 'use'|'confirm'|'miss'|'error', recallCount, badRecallCount): number
  isConfirmKeyword(text: string): boolean
  isErrorKeyword(text: string): boolean
  static fromRaw(raw): FeedbackConfigManager
}
```

### 實作檔案範圍
- `feedback-config.ts`：FeedbackConfigManager 類別
- `index.ts`：使用 FeedbackConfigManager 替代硬編碼參數

---

## 6. Phase 4 實作內容（單元測試）

### 測試檔案
- `test/feedback-config.test.mjs`：10 tests
- `test/isRecallUsed.test.mjs`：7 tests
- `test/bad-recall-count.test.mjs`：（需要重寫，見下方問題清單）

---

## 7. 已知的問題清單（提交 PR 前需要修復）

### P1 問題
1. **autoCapture block boundary**：`if (config.autoCapture !== false)` 的 `}` 需要確認正確閉合
2. **Phase 4 測試在測 mock 而非真實程式碼**：`bad-recall-count.test.mjs` 需要重寫 import

### P2 問題
3. **Summary match 缺少 hasUsageMarker AND gate**：與 ID path 保持一致需加 AND gate
4. **配置覆寫靜默失敗**：加 schema validation 防止 `confirmKeywords`/`errorKeywords` 傳入 non-array

---

## 8. 執行步驟

### Step 1：Rebase Phase 1 branch 到官方 master
```bash
cd memory-lancedb-pro
git fetch upstream
git checkout feat/proposal-a-v3-clean
git rebase upstream/master
# 解決可能的 conflict
```

### Step 2：檢查 autoCapture block boundary
確認 `index.ts` 中 `if (config.autoCapture !== false)` 的 `}` 正確閉合

### Step 3：準備變更摘要
整理與 #507/#505 相比的變更摘要（見第 3 節表格）

### Step 4：提交 Phase 1 PR
```bash
gh pr create --repo CortexReach/memory-lancedb-pro \
  --base master \
  --head jlin53882:feat/proposal-a-v3-clean \
  --title "feat: Proposal A Phase 1 - Dynamic Importance Feedback Signals" \
  --body "..."
```

### Step 5：等 Phase 1 合併後，提 Phase 3 PR
- target: `feat/proposal-a-v3-configurable-v2`
- base: Phase 1 branch（等 Phase 1 合併後 rebase 到 master）

### Step 6：等 Phase 3 合併後，提 Phase 4 PR
- target: `feat/proposal-a-v3-tests`
- base: Phase 3 branch（等 Phase 3 合併後 rebase 到 master）

---

## 9. 待確認事項

- [ ] Phase 3 和 Phase 4 的準確實作範圍
- [ ] Phase 3 的 `feedback-config.ts` 是否需要新增檔案
- [ ] PR 提交時的準確 body 內容
