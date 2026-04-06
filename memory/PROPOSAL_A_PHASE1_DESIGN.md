# Proposal A v3 - Phase 1 完整設計稿

> 基於 PR #493 feat/proposal-a-v3-clean，commit `bd0c582` 最新狀態

---

## Phase 命名對照

| 命名 | 內容 | PR/分支 | 狀態 |
|------|------|---------|------|
| Phase 1 | Feedback signals 核心 | #493 (`feat/proposal-a-v3-clean`) | ✅ 完成 |
| Phase 3 | 可配置化（min_recall_count、boost/penalty 幅度） | `feat/proposal-a-v3-configurable` | 進行中 |
| Phase 4 | 單元測試覆蓋 | `feat/proposal-a-v3-tests` | 進行中 |

---

## 一、Phase 1 實作摘要

### 1.1 核心功能點

| 功能點 | 檔案/位置 | 狀態 |
|--------|-----------|------|
| `agent_end` 鉤子（捕捉回應文字） | index.ts:3039 | ✅ |
| `isRecallUsed()` AND 邏輯重構 | src/reflection-slices.ts:323-415 | ✅ 含 bd0c582 |
| `injectedSummaries` verbatim match | src/reflection-slices.ts:377-395 | ✅ |
| `before_prompt_build` feedback hook (priority 5) | index.ts:3066 | ✅ |
| pendingRecall Map（複合鍵 sessionKey:agentId） | index.ts:2028-2035, 2616 | ✅ |
| session_end cleanup | index.ts:3208（priority 20）<br>index.ts:2668（priority 10） | ⚠️ 兩處，優先級不同 |
| per-recall 獨立評分 | index.ts:3150-3195 | ✅ |
| bad_recall_count 遞增修復 | index.ts:3187, 3193 | ✅ bd0c582 |
| 使用者確認/錯誤關鍵字萃取 | index.ts:3108-3109, 3137-3139 | ✅ |
| minRecallCountForPenalty threshold | index.ts:3107（預設 2） | ✅ |

---

## 二、isRecallUsed() 邏輯（已修復）

### 2.1 現在的邏輯流程

```
Step 1: 如果 responseText <= 24 字元 → 回傳 false
Step 2: 如果 injectedIds 和 injectedSummaries 都為空 → 回傳 false
Step 3: 檢查是否有特定 ID 在 response 中（hasSpecificRecall = injectedIds.some(...)）
Step 4: 如果 hasSpecificRecall 為 true，進一步檢查 usage markers（AND 邏輯）
Step 5: 如果未通過前兩步，檢查 injectedSummaries verbatim match（獨立於 AND 之外）
Step 6: 以上皆未通過 → 回傳 false
```

### 2.2 AND 邏輯（bd0c582 修復）

舊邏輯（OR）：通用 marker 或 ID 任一存在就回傳 true
新邏輯（AND）：需要特定 ID 存在 **且** 通用 marker 也存在才回傳 true

### 2.3 injectedSummaries Verbatim Match

當 response 包含 injected summary 的完整文字（>=10 chars）時，回傳 true。
這補足 ID-based 和 marker-based 檢測不到的情境（agent 直接引用記憶內容）。

---

## 三、評分迴圈邏輯

### 3.1 評分路徑

```
CONFIRM path（usedRecall + 含確認關鍵字）：
  importance += boostOnUse + boostOnConfirm
  bad_recall_count = 0

ERROR path（未 usedRecall + 含錯誤關鍵字）：
  importance -= penaltyOnError
  bad_recall_count += 1

MISS path（未 usedRecall + badCount >= 2）：
  importance -= penaltyOnMiss
  bad_recall_count += 1

MISS path（未 usedRecall + badCount < 2）：
  不做任何評分也不遞增（設計選擇，非 bug）
```

### 3.2 bad_recall_count 遞增（bd0c582 修復）

舊邏輯：ERROR 和 MISS path 沒 +1，導致 threshold 永遠達不到
新邏輯：兩條 path 都正確 +1

---

## 四、配置解析

### 4.1 支援的參數（parsePluginConfig feedback 區塊）

- `confirmKeywords`：明確確認關鍵字（預設：是對的、確認、正確、right）
- `errorKeywords`：明確錯誤關鍵字（預設：錯誤、不對、wrong、not right）
- `importanceBoostOnUse`：確認使用增幅（預設 0.05）
- `importanceBoostOnConfirm`：明確確認增幅（預設 0.15）
- `importancePenaltyOnMiss`：未使用 penalty（預設 0.03）
- `importancePenaltyOnError`：明確錯誤 penalty（預設 0.10）
- `minRecallCountForPenalty`：觸發 penalty 的最少 recall 次數（預設 2）

---

## 五、P1 問題與修復狀態

| # | 問題 | 嚴重度 | 狀態 |
|---|------|--------|------|
| 1 | session_end priority 20 不清理複合鍵（autoCapture=false 時記憶體洩漏） | P1 | ❌ 未修復 |
| 2 | badCount < 2 時的 MISS path 不 penalty | 設計選擇 | ✅ 文件化 |
| 3 | responseText 太短（<=24）跳過評分 | 預期行為 | ✅ 文件化 |
| 4 | confirmKeywords/errorKeywords 寬泛 | 輕微 | ✅ 可接受 |
| 5 | injectedSummaries verbatim 可能假阳性 | 設計選擇 | ✅ 有意 |

### 5.1 P1 問題：session_end 複合鍵清理缺口（未修復）

**問題**：Phase 1 的 session_end hook（priority 20）只刪除簡單的 sessionKey，不處理複合鍵 `sessionKey:agentId`。

當 `config.autoCapture === false` 時，auto-capture 的 session_end（priority 10，在 `if (autoCapture)` 區塊內）不會執行，導致複合鍵 entry 永遠留在 Map 裡。

**建議修復**：
```typescript
api.on("session_end", (_event, ctx) => {
  const sessionKey = ctx?.sessionKey || "default";
  for (const key of pendingRecall.keys()) {
    if (key === sessionKey || key.startsWith(`${sessionKey}:`)) {
      pendingRecall.delete(key);
    }
  }
}, { priority: 20 });
```

---

## 六、與 Proposal A 目的的關係

Phase 1 的核心目的：動態重要性反饋——記憶被使用就 boost，未被使用就 penalty。

**已破壞的問題（已修復）**：
- ✅ isRecallUsed() AND 邏輯重構（bd0c582）
- ✅ bad_recall_count 遞增（bd0c582）
- ✅ 重複 usageMarker（已修復）

**需要修復才能合併**：
- ❌ session_end 複合鍵清理缺口（P1）

---

## 七、合併前的檢查清單

- [ ] session_end 複合鍵清理缺口已修復
- [ ] isRecallUsed() AND 邏輯已驗證正確
- [ ] bad_recall_count 遞增已驗證正確
- [ ] 所有 18 個 bug 修復已確認
- [ ] 配置解析完整且向後相容

---

## 八、相關檔案位置

| 檔案 | 說明 |
|------|------|
| `index.ts` | 評分邏輯、hooks、pendingRecall |
| `src/reflection-slices.ts` | isRecallUsed() 函式 |
| `src/auto-capture-cleanup.ts` | subagent wrapper stripping |
| `src/smart-extractor.ts` | envelope metadata regex |
| `src/retriever.ts` | recency double-boost guard |

---

*本文件由 OpenClaw Agent 整理，2026-04-04*
