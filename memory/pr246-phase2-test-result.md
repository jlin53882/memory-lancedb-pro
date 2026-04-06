# PR #246 Phase 2 測試報告

> 測試日期：2026-04-02  
> 執行環境：Node.js test runner  
> 測試檔案：`test/pr246-feedback-signal.test.mjs`

---

## 測試結果摘要

| 指標 | 數值 |
|------|------|
| **總測試數** | 42 |
| **通過** | 42 |
| **失敗** | 0 |
| **執行時間** | 83.4 ms |

---

## 各模組測試結果

### 1. isRecallUsed（v9 threshold > 24）— 21 個測試 ✅

| # | 測試案例 | 狀態 |
|---|---------|------|
| 1 | 長文本：回應包含中段片段 → true | ✅ |
| 2 | 短文本（20-24字）：全段比對命中 → true | ✅ |
| 3 | 短文本：未命中 → false | ✅ |
| 4 | text.length < 20 → false | ✅ |
| 5 | snippet 全是標點 → false | ✅ |
| 6 | 大小寫不同仍命中 → true | ✅ |
| 7 | 長文本：前20字是前綴，回應只含前綴 → false | ✅ |
| 8 | text.length = 20 → 全段作為 snippet → true | ✅ |
| 9 | text.length = 25 → slice(20,70) 取後5字 → 匹配 → true | ✅ |
| 10 | text.length = 24 → 全段 snippet = 24字 → true | ✅ |
| 11 | text.length = 90 → slice(20,70) 取後50字 → false | ✅ |
| 12 | text.length = 91 → slice(20,70) 取後50字 → true | ✅ |
| 13 | snippet.length = 5 邊界 → true | ✅ |
| 14 | snippet 全是空白 → false | ✅ |
| 15 | responseText 為空字串 → false | ✅ |
| 16 | responseText 為 null → false | ✅ |
| 17 | responseText 為 undefined → false | ✅ |
| 18 | recallText 為空字串 → false | ✅ |
| 19 | recallText 為 null → false | ✅ |
| 20 | text.trim() 後 < 20 → false | ✅ |
| 21 | snippet 包含中文標點 → 匹配 → true | ✅ |
| 22 | 長文本重複模式 → 匹配 → true | ✅ |

**覆蓋重點**：
- v9 threshold `> 24` 的行為驗證（20-24 字走全段，25+ 字走 slice）
- 長文本 slice(20,70) 邏輯
- 邊界 case（length=20, 24, 25, 90, 91）
- 空值處理（null, undefined, ""）

---

### 2. extractUserResponseAfter — 9 個測試 ✅

| # | 測試案例 | 狀態 |
|---|---------|------|
| 1 | 找到時間戳之後的 user 訊息 → 回傳 content | ✅ |
| 2 | 沒有比 afterTimestamp 更新的 user 訊息 → null | ✅ |
| 3 | messages 沒有 timestamp → fallback 為 0 | ✅ |
| 4 | 空陣列 → null | ✅ |
| 5 | 多個 user 訊息：只回傳第一個 | ✅ |
| 6 | timestamp 等於 boundary（半開區間）→ null | ✅ |
| 7 | 混合 role：只取 user，忽略 assistant | ✅ |
| 8 | timestamp 明確為 undefined → fallback 為 0 → null | ✅ |
| 9 | timestamp 為 null → fallback 為 0 → null | ✅ |

**覆蓋重點**：
- `.find()` 行為（只取第一個符合條件的訊息）
- timestamp fallback 邏輯（`m.timestamp ?? 0`）
- 半開區間邊界（`>` 而非 `>=`）

---

### 3. pendingRecall 狀態機 — 5 個測試 ✅

| # | 測試案例 | 狀態 |
|---|---------|------|
| 1 | agent_end 正常：寫入 pendingRecall | ✅ |
| 2 | agent_end：recallIds 為空 → 不寫入或寫入空陣列 | ✅ |
| 3 | 同一 session 兩次呼叫：覆蓋而非重複 | ✅ |
| 4 | before_prompt_build：處理 pendingRecall | ✅ |
| 5 | pendingRecall 不存在時不 crash | ✅ |

**覆蓋重點**：
- `Map.set()` 覆蓋行為
- 空 recallIds 處理

---

### 4. TTL cleanup — 4 個測試 ✅

| # | 測試案例 | 狀態 |
|---|---------|------|
| 1 | 超過 5 分鐘的殘留項目會被清除 | ✅ |
| 2 | 未超過 5 分鐘的項目不被清除 | ✅ |
| 3 | 剛好 5 分鐘 → 不清除（因為 `>` 不是 `>=`）| ✅ |
| 4 | 多個 session：只清除超時的 | ✅ |

**覆蓋重點**：
- 5 分鐘 TTL 門檻
- 邊界行為（`>` vs `>=`）

---

### 5. 整合測試 — 2 個測試 ✅

| # | 測試案例 | 狀態 |
|---|---------|------|
| 1 | 完整流程：agent_end → before_prompt_build → session_end | ✅ |
| 2 | responseText 為 null 時的完整流程 | ✅ |

---

## 測試發現的問題

### 無重大問題

所有 42 個測試案例均通過，測試函式邏輯正確。

### 測試資料構造的收穫

1. **slice(20,70) 行為**：slice 取的是第 21-70 字（50 字），不是字元位置 20-70
2. **responseText 匹配方向**：需要 `response.includes(snippet)`，不是 `snippet.includes(response)`
3. **中文字元長度**：JS 中 `length` 是按字元計算，`"前綴".repeat(20)` = 40 字

---

## 假設驗證清單（測試結果）

| 假設 | 測試驗證結果 |
|------|-------------|
| `isRecallUsed` threshold `> 24` | ✅ 確認正確（20-24 字走全段，25+ 走 slice）|
| `extractUserResponseAfter` 用 `.find()` | ✅ 確認只取第一個 |
| TTL 5 分鐘門檻 | ✅ 確認 `>` 行為 |
| pendingRecall 使用 Map 覆蓋 | ✅ 確認覆蓋行為 |

---

## 交付產物

1. **測試檔案**：`test/pr246-feedback-signal.test.mjs`（已執行通過）
2. **本報告**：`memory/pr246-phase2-test-result.md`

---

*報告產生時間：2026-04-02*