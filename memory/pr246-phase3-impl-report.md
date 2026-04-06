# PR #246 Phase 3 實作報告

> 日期：2026-04-02
> 任務：Phase 3 Importance 直接調整機制實作
> 目標 Repo：`memory-lancedb-pro-import-markdown-test`（未找到）
> 設計來源：`pr246_proposal_ab_design_v9.md`

---

## 📋 任務狀態：無法執行

### 原因

目標 repository `memory-lancedb-pro-import-markdown-test` 在 workspace 中**不存在**。

```bash
# 搜尋結果
$ ls -R memory-lancedb-pro-import-markdown-test
NOT_FOUND
```

現有相關目錄：
- `memory\memory-lancedb-pro-codebase`（僅有學習文件，無實作碼）

---

## 📊 Phase 3 設計邏輯（從 v9 提取）

### 觸發條件

| 條件 | 說明 |
|------|------|
| `last_confirmed_use_at` 每日寫入率 | 連續 7 天 > 10 筆 |
| `bad_recall_count` | **觀察依據**（非觸發門檻）|

### 實作方式

**位置**：Phase 2 的 `before_prompt_build` hook（同一個 hook）

```typescript
// ============================================================
// Phase 3: 根據 bad_recall_count 調整 importance
// 位置：before_prompt_build hook 內，Phase 2 邏輯之後
// ============================================================

if (used) {
  // 記憶被使用：調升 importance
  const newImportance = Math.min(
    1.0,
    (recallEntry.importance ?? 0.7) + 0.05
  );
  await store.update(id, { importance: newImportance });

  // 同時更新 last_confirmed_use_at 和重置 bad_recall_count
  await store.patchMetadata(id, {
    last_confirmed_use_at: Date.now(),
    bad_recall_count: 0,
  });
} else {
  // 記憶未被使用：bad_recall_count + 1
  const count = recallEntry.bad_recall_count ?? 0;

  // 連續 2 次未使用：調降 importance
  if (count >= 2) {
    const newImportance = Math.max(
      0.1,
      (recallEntry.importance ?? 0.7) - 0.03
    );
    await store.update(id, { importance: newImportance });
  }

  // 更新 bad_recall_count
  await store.patchMetadata(id, {
    bad_recall_count: count + 1,
  });
}
```

### 技術約束

| 項目 | 約束 |
|------|------|
| importance 調整 | `store.update()` 的 `importance` 欄位 |
| metadata 調整 | `store.patchMetadata()` 的 `last_confirmed_use_at` / `bad_recall_count` |
| 調升幅度 | `+0.05`（使用）|
| 調降幅度 | `-0.03`（連續 2 次未使用）|
| importance 上限 | `1.0` |
| importance 下限 | `0.1` |

---

## 🔗 與 Phase 2 的整合

### Phase 2 現有狀態

從 `pr246-phase2-test-result.md`：
- ✅ **42/42 測試通過**
- ✅ `isRecallUsed()` 函式已實作並驗證
- ✅ `pendingRecall` Map 狀態機已實作
- ✅ TTL cleanup（5 分鐘）已實作

### Phase 3 整合點

Phase 3 與 Phase 2 共用同一個 `before_prompt_build` hook，在 Phase 2 的 feedback signal 判斷**之後**執行：

```
┌─────────────────────────────────────────────────────────────┐
│ before_prompt_build hook                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. Phase 2: 執行 recallWork() → 取得 selected IDs       │
│ 2. Phase 2: 存入 pendingRecallBySession                  │
│ 3. [Agent 生成回應]                                        │
│ 4. Phase 2 (agent_end):                                    │
│    - 取出 pendingRecall                                    │
│    - 執行 isRecallUsed() 判斷                               │
│    - 寫入 last_confirmed_use_at / bad_recall_count         │
│                                                              │
│ 5. Phase 3: ← 在同一次 before_prompt_build 執行          │
│    - 根據 bad_recall_count 調整 importance                 │
│    - 使用 store.update() + store.patchMetadata()            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ 假設驗證清單

| 假設 | 來源 | 狀態 |
|------|------|-------|
| Phase 2 的 `before_prompt_build` hook 結構支援 Phase 3 整合 | 設計 v9 2.3 節 | ⚠️ 待確認 |
| `store.update()` 支援 `importance` 欄位 | 設計 v9 1.1 節 | ⚠️ 待確認 |
| `store.patchMetadata()` 支援 `last_confirmed_use_at` / `bad_recall_count` | 設計 v9 1.1 節 | ⚠️ 待確認 |
| Phase 2 執行後 `last_confirmed_use_at` 每日寫入率可達 > 10 筆 | 設計 v9 第五章 | ⚠️ 需觀察 |

---

## 📦 交付產物

因目標 repo 不存在，無實際程式碼產出。以下為**設計文件**：

| 檔案 | 說明 |
|------|------|
| `pr246_proposal_ab_design_v9.md` | 完整設計文件（含 Phase 2/3）|
| `pr246-phase2-test-result.md` | Phase 2 測試結果（42/42 通過）|
| `pr246-phase3-impl-report.md` | 本報告 |

---

## 🔜 後續建議

1. **建立測試 repo**：如果需要實作 Phase 3，需先建立 `memory-lancedb-pro-import-markdown-test` repository
2. **等待 Phase 2 數據累積**：Phase 3 需要 `last_confirmed_use_at` 連續 7 天 > 10 筆的觀察數據
3. **手動觸發決策**：Phase 3 的 importance 調整需要**人工確認**觸發（設計 v9 第五章）

---

*報告產生時間：2026-04-02*