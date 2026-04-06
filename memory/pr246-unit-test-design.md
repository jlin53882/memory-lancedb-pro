# PR #246 Phase 2 單元測試設計文件

> 分析日期：2026-04-02  
> 狀態：最終版（分析覆蓋缺口後產出）
> 更新：v9 — 設計文件 `isRecallUsed` 邏輯已修復（threshold `> 90` → `> 24`），TC-8 需重新評估

---

## 驗證結果摘要

| 問題 | 答案 |
|------|------|
| getSlices 插入點 | `extractReflectionSlicesWithSanitizer` → `return` 前一刻；derived slices 產生後、return 之前 |
| bm25Search 函式名 | ✅ `bm25Search`（`store.ts:522`，`Store` 類別方法）|
| bm25Search scope 參數名 | ⚠️ 應為 `scopeFilter?: string[]`（陣列），非 `scope: 'same'` |
| text.length=20-24 問題 | ✅ 已修復（design doc v9 threshold `> 90` 改為 `> 24`）|

---

## 一、現有草稿覆蓋矩陣

### 1.1 `isRecallUsed` 覆蓋狀態

| # | 案例描述 | 草稿狀態 | 對應實作邏輯 | 備註 |
|---|---------|---------|------------|------|
| 1 | 長文本：回應包含中段片段 → true | ✅ 有 | `responseText.toLowerCase().includes(snippet.toLowerCase())` | |
| 2 | 短文本（≤90字）：全段比對命中 → true | ✅ 有 | snippet = text，全部比對 | |
| 3 | 短文本：未命中 → false | ✅ 有 | includes() 回傳 false | |
| 4 | text.length < 20 → false | ✅ 有 | 第一關 `if (text.length < 20)` | |
| 5 | snippet 全是標點 → false | ✅ 有 | `/^[\s\p{P}]+$/u.test(snippet)` | |
| 6 | 大小寫不同仍命中 → true | ✅ 有 | `.toLowerCase()` 標準化 | |
| 7 | 長文本：前20字是固定前綴，回應只含前綴 → false | ✅ 有 | snippet = text.slice(20,70)，前綴不在 snippet 內 | |
| 8 | text.length = 20（trim 後）| ✅ 修復後達標 | snippet = text（20字全段）→ length=20 ≥ 5 → 進入正邏輯 | v9 threshold `> 24`，TC-8 重新設計 |
| 9 | text.length = 21~24 → 進入正邏輯 | ✅ 修復後達標 | snippet = text（全部）→ length=21~24 ≥ 5 → 進入正邏輯 | v9 threshold `> 24`，行為改變 |
| 10 | text.length = 25 → 全部作為 snippet | ✅ 修復後達標 | snippet = text（25字全段）→ length=25 ≥ 5 | v9 threshold `> 24` vs 舊 `> 90`，行為改變 |
| 11 | text.length = 90 vs 91 邊界 | ❌ 缺口 | 90 用全部，91 用 slice(20,70) | 見缺口 2.2 |
| 12 | text.length > 90 但 snippet 取完後 < 5 | ❌ 缺口 | 即 text.length 20~24 的長文本特殊情況 | 見缺口 2.1 |
| 13 | snippet 全是空白（` `）→ false | ⚠️ 覆蓋但未明確 | `/^[\s\p{P}]+$/u` 包含空白，理論上有覆蓋 | 建議補測 |
| 14 | responseText 為空字串 → false | ❌ 缺口 | includes("") 永遠 false | 見缺口 2.3 |
| 15 | text.trim() 後 < 20，但原始 text ≥ 20 | ✅ v9 仍有效 | trim() 在長度判斷之前 | 第一關 `if (text.length < 20)` 在 trim 後攔截 |

### 1.2 `extractUserResponseAfter` 覆蓋狀態

| # | 案例描述 | 草稿狀態 | 對應實作邏輯 | 備註 |
|---|---------|---------|------------|------|
| 1 | 找到時間戳之後的 user 訊息 → 回傳 content | ✅ 有 | `.find()` 找到第一個 | |
| 2 | 沒有比 afterTimestamp 更新的 user 訊息 → null | ✅ 有 | `.find()` 回傳 undefined | |
| 3 | messages 沒有 timestamp → null | ✅ 有 | `m.timestamp ?? 0` fallback | |
| 4 | 空陣列 → null | ✅ 有 | `.find()` 在空陣列回傳 undefined | |
| 5 | 多個 user 訊息：只回傳第一個 | ❌ 缺口 | `.find()` 只取第一個 | 見缺口 2.4 |
| 6 | user 訊息的 timestamp 剛好等於 afterTimestamp | ❌ 缺口 | `> afterTimestamp`（不包含相等）| 見缺口 2.5 |

### 1.3 Hook 邏輯覆蓋狀態

| # | 案例描述 | 草稿狀態 | 備註 |
|---|---------|---------|------|
| 1 | agent_end 正常：寫入 pendingRecall | ✅ 有 | |
| 2 | agent_end：recalledMemoryIds 為空 → 不寫入 | ✅ 有 | |
| 3 | before_prompt_build：命中 → 寫入 last_confirmed_use_at，bad_recall_count 重置為 0 | ✅ 有 | |
| 4 | before_prompt_build：未命中 → bad_recall_count +1 | ✅ 有 | |
| 5 | before_prompt_build：取完後 pendingRecall 立即清除 | ✅ 有 | |
| 6 | session_end：清除對應 session 的殘留 | ✅ 有 | |
| 7 | agent_end 同一 session 兩次：覆蓋而非重複 | ❌ 缺口 | 見缺口 2.6 |
| 8 | before_prompt_build 多筆 recallIds：每筆都正確比對 | ❌ 缺口 | 見缺口 2.7 |
| 9 | responseText 為 null 時的處理 | ❌ 缺口 | extractUserResponseAfter 可能回傳 null |
| 10 | before_prompt_build 時 pendingRecall 已不存在 | ❌ 缺口 | 競走（race condition）測試 |

### 1.4 TTL Cleanup 覆蓋狀態

| # | 案例描述 | 草稿狀態 | 備註 |
|---|---------|---------|------|
| 1 | 超過 5 分鐘的殘留項目會被清除 | ✅ 有 | |
| 2 | 未超過 5 分鐘的項目不被清除 | ❌ 缺口 | 見缺口 2.8 |
| 3 | 正在比對中的項目不被清除 | ❌ 缺口 | 見缺口 2.8 |

---

## 二、缺口詳細分析

### 缺口 2.1：`isRecallUsed` 的 snippet.length < 5 臨界區間（text.length 20~24）

**實作邏輯：**
```typescript
if (text.length > 90) {
  snippet = text.slice(20, 70); // 50 chars
} else {
  snippet = text;               // 全部
}
if (snippet.length < 5) return false;
```

**分析：**

| text.length | snippet 取法 | snippet.length | 結果 |
|-------------|-------------|----------------|------|
| 19 | —（第一關攔截）| — | false（第一關）|
| 20 | text.slice(20,70) | 0 | false（< 5）|
| 21 | text.slice(20,70) | 1 | false（< 5）|
| 22 | text.slice(20,70) | 2 | false（< 5）|
| 23 | text.slice(20,70) | 3 | false（< 5）|
| 24 | text.slice(20,70) | 4 | false（< 5）|
| 25 | text.slice(20,70) | 5 | 進入正邏輯 |
| 26~90 | text（全部）| text.length | 取決於內容 |
| 91 | text.slice(20,70) | 50 | 進入正邏輯 |

**缺口嚴重性：中**  
這不是罕見場景——使用者可能在回憶時輸入剛好 20~24 字的中文句子，這些輸入會被直接 return false 而非進入試探邏輯。

**修復（v9）**：threshold 從 `> 90` 改為 `> 24`，text.length=20~24 全部走全段 snippet，length 20~24 ≥ 5，進入正邏輯，不再被 guard 攔截。

---

### 缺口 2.2：`isRecallUsed` 的 text.length = 90 vs 91 邊界

**實作邏輯：**
```typescript
if (text.length > 90) {   // > 90，不是 >= 90
  snippet = text.slice(20, 70);
} else {
  snippet = text;
}
```

| 情境 | text.length | snippet 取法 | 影響 |
|------|-------------|-------------|------|
| 邊界 90 | 90 | 全部（90字）| 整段作為 snippet |
| 邊界 91 | 91 | text.slice(20,70)（50字）| 跳過前20字 |

**缺口嚴重性：低**  
90 字以下的文本本來就會用全部作為 snippet，91 字以上則跳過前 20 字。這個分界是設計决策，草稿未測試這個邊界 case，但 90 vs 91 的差異會造成 snippet 取法不同，可能在特定輸入時造成非預期行為。

---

### 缺口 2.3：`responseText` 為空字串

**實作邏輯：**
```typescript
return responseText.toLowerCase().includes(snippet.toLowerCase());
```

當 `responseText = ""` 時，`"".includes(anything)` 永遠回傳 `false`，函式直接回傳 false。草稿沒有覆蓋這個 case。

**缺口嚴重性：中**  
`extractUserResponseAfter` 在找不到 user 訊息時會回傳 `null`，但草稿的 hook 測試未覆蓋這個 null 值傳入 `isRecallUsed` 的結果。

---

### 缺口 2.4：`extractUserResponseAfter` 多個 user 訊息只取第一個

**實作邏輯：**
```typescript
const userMsg = messages.find(
  m => m.role === "user" && (m.timestamp ?? 0) > afterTimestamp
);
return userMsg?.content ?? null;
```

`.find()` 只會找到**第一個**符合條件的 user 訊息。如果有多個 user 訊息在同一時間之後，會取最舊的那個。

**缺口嚴重性：中**  
這是一個**設計决策**（只取最近一個），但測試應驗證這個行為是否符合預期。草稿完全未覆蓋。

---

### 缺口 2.5：`extractUserResponseAfter` timestamp 等於 boundary

**實作邏輯：**
```typescript
(m.timestamp ?? 0) > afterTimestamp
```

使用 `>` 而非 `>=`，所以 timestamp **等於** `afterTimestamp` 時不會被視為「比 afterTimestamp 更新」，會被跳過。

**缺口嚴重性：低**  
這是標準的「半開區間」設計，但草稿未明確測試 `timestamp = afterTimestamp` 的 case。

---

### 缺口 2.6：`agent_end` 同一 session 兩次呼叫（覆蓋行為）

**實作邏輯：**
```typescript
// agent_end handler
pendingRecall.set(sessionId, { recallIds, responseText, injectedAt });
```

使用 `Map.set()`，同一 key 會覆蓋而非重複新增。

**缺口嚴重性：中**  
草稿只測了「一次寫入」，未測「兩次寫入時第二次覆蓋第一次」的行為。如果沒有妥善覆蓋，第二次呼叫會重複殘留而非覆蓋。

---

### 缺口 2.7：`before_prompt_build` 多筆 recallIds

**實作邏輯（推測）：**
```typescript
// before_prompt_build handler
const pending = pendingRecall.get(sessionId);
if (!pending) return;
for (const recallId of pending.recallIds) {
  const used = isRecallUsed(recallId.text, responseText);
  // store.update(recallId, used);
}
pendingRecall.delete(sessionId);
```

**缺口嚴重性：高**  
草稿的 hook 測試暗示 `recallIds` 是單一 ID（`recalledMemoryIds`），但設計文件 v8 的狀態機暗示是多筆。如果 recallIds 是 Array，但比對邏輯只做一次，會有嚴重錯誤。

---

### 缺口 2.8：TTL cleanup 的「未超過 5 分鐘」和「正在比對中」

**實作邏輯（推測）：**
```typescript
// TTL cleanup（定時或每次 hook 觸發）
for (const [sessionId, entry] of pendingRecall) {
  if (Date.now() - entry.injectedAt > 5 * 60 * 1000) {
    pendingRecall.delete(sessionId);
  }
}
```

**缺口嚴重性：中**  
草稿只測了「超時清除」，未測「未超時不清除」和「正在比對時不清除」。

---

## 三、補充測試案例

### 3.1 `isRecallUsed` 補充案例

#### TC-1：text.length = 20（修復後：全段作為 snippet）

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_edge_text_length_20` |
| **目的** | 驗證 v9 threshold `> 24` 後，text.length = 20 走全段策略（20字全作為 snippet）|
| **輸入** | recallText = `"ABCDEFGHIJKLMNOPQRST"`（20字）, responseText = `"ABCDEFGHIJKLMNOPQRST"` |
| **預期輸出** | `true`（v9: text.length=20 ≤ 24，走全段 snippet=text，length=20 ≥ 5，命中 responseText）|
| **對比舊行為** | 舊 threshold `> 90` → slice(20,70) = "" → false；修復後 → true |
| **測試資料建議** | text exactly 20 chars（含邊界），response 包含完整 20 字 |

#### TC-2：text.length = 25（v9：走全段 snippet = text）

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_edge_text_length_25_snippet_5` |
| **目的** | 驗證 v9 threshold `> 24` 後，text.length = 25 走全段策略（全部 25 字作為 snippet）|
| **輸入** | recallText = `"ABCDEFGHIJKLMNOPQRSTUVWXY"`（25字）, responseText = `"ABCDEFGHIJKLMNOPQRSTUVWXY"` |
| **預期輸出** | `true`（v9: text.length=25 ≤ 24？→ 否，25 > 24，所以走 slice(20,70)）|
| **⚠️ 注意** | 25 > 24，所以走 slice(20,70) → 仍取後 5 字 "UVWXY"，行為與舊 threshold `> 90` 相同 |
| **測試資料建議** | text exactly 25 chars，response 包含全部 25 字 |

#### TC-3：text.length = 90 vs 91 邊界分界（v9 threshold `> 24`）

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_boundary_90_vs_91` |
| **目的** | 驗證 v9 threshold `> 24` 後，text.length = 90 和 91 都走 slice(20,70)，不再有 90/91 分界 |
| **輸入 90** | recallText = `"ABCDEFGHIJKLMNOPQRST".repeat(4) + "ABCDE"`（90字，前20字為 "ABCDEFGHIJKLMNOPQRST"），responseText = `"ABCDEFGHIJKLMNOPQRST" + "XXXX..."` → 只含前20字 |
| **預期輸出** | `false`（90 > 24 → snippet = slice(20,70) = 後50字 "XXXX..."，response 不含後50字）|
| **輸入 91** | recallText = `"ABCDEFGHIJKLMNOPQRST".repeat(4) + "ABCDEX"`（91字）, responseText = 含後50字 → `true` |
| **對比舊行為** | 舊 threshold `> 90`：text.length=90 用全段 → 包含前20字 → true；text.length=91 用 slice → 後50字 → false。v9 修復後兩者都走 slice |
| **測試資料建議** | 前20字固定為「前綴」，後50字與 response 比對 |

#### TC-4：text.length > 90 但前 20~69 字全部相同（snippet 取自重複區域）

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_long_text_repeated_pattern` |
| **目的** | 驗證長文本 slice 邏輯與短文本邏輯的一致性 |
| **輸入** | recallText = `"AAAA".repeat(25)`, responseText = `"AAAA".repeat(25)` |
| **預期輸出** | `true`（text.length=100 > 90，snippet = slice(20,70) = "AAAA".repeat(12)+"AA"，包含 "AAAA"）|
| **測試資料建議** | 全重複字元，長度 > 90 |

#### TC-5：snippet 全是空白（空白字元）

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_snippet_all_whitespace` |
| **目的** | 驗證全是空白的 snippet 被正確拒絕 |
| **輸入** | recallText = `"                    "`（20+ spaces）, responseText = `"                    "` |
| **預期輸出** | `false`（snippet 是空白字元，regex 應命中 `[\s]`）|
| **測試資料建議** | 90+ spaces |

#### TC-6：responseText 為空字串

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_empty_response` |
| **目的** | 驗證 responseText 為空時，回傳 false |
| **輸入** | recallText = `"這是一個正常的回收文本長度超過二十個字"`, responseText = `""` |
| **預期輸出** | `false`（`"".includes(...)` 永遠 false）|
| **測試資料建議** | recallText 符合最低長度要求（≥ 25 chars）|

#### TC-7：snippet 全是中文標點

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_snippet_all_chinese_punctuation` |
| **目的** | 驗證中文標點（`\p{P}`）被正確識別 |
| **輸入** | recallText = `"，。、；！？：「」『』（）——……"`（20+ chars）, responseText = `"同上"` |
| **預期輸出** | `false`（snippet 全是 `\p{P}`）|
| **測試資料建議** | 25+ 中文標點字元 |

#### TC-8：text.trim() 後 < 20，但原始 text > 20

| 欄位 | 內容 |
|------|------|
| **名稱** | `isRecallUsed_trim_reduces_length` |
| **目的** | 驗證 `trim()` 先於長度判斷 |
| **輸入** | recallText = `"                  xyz"`, responseText = `"xyz"` |
| **預期輸出** | `false`（trim 後 text.length = 3 < 20）|
| **測試資料建議** | 前後大量空白 |

### 3.2 `extractUserResponseAfter` 補充案例

#### TC-9：多個 user 訊息，只取第一個（`.find()` 行為）

| 欄位 | 內容 |
|------|------|
| **名稱** | `extractUserResponseAfter_multiple_users_returns_first` |
| **目的** | 驗證 `.find()` 只取第一個符合條件的訊息 |
| **輸入** | `messages = [{role:"user",content:"第一個",timestamp:100}, {role:"user",content:"第二個",timestamp:200}], afterTimestamp = 50` |
| **預期輸出** | `"第一個"`（而非"第二個"）|
| **測試資料建議** | 2+ user 訊息，有明確的時間順序 |

#### TC-10：timestamp 等於 afterTimestamp（邊界，半開區間）

| 欄位 | 內容 |
|------|------|
| **名稱** | `extractUserResponseAfter_timestamp_equal_boundary` |
| **目的** | 驗證 `> afterTimestamp`（不含相等）的邊界行為 |
| **輸入** | `messages = [{role:"user",content:"等於",timestamp:100}], afterTimestamp = 100` |
| **預期輸出** | `null`（timestamp = 100，不滿足 > 100）|
| **測試資料建議** | timestamp = afterTimestamp |

#### TC-11：混合 role（user + assistant），只取 user

| 欄位 | 內容 |
|------|------|
| **名稱** | `extractUserResponseAfter_mixed_roles` |
| **目的** | 驗證 `.find()` 忽略 non-user role |
| **輸入** | `messages = [{role:"assistant",content:"助理",timestamp:150}, {role:"user",content:"使用者",timestamp:200}], afterTimestamp = 50` |
| **預期輸出** | `"使用者"`（忽略 assistant）|
| **測試資料建議** | assistant 和 user 訊息混合 |

#### TC-12：user 訊息 timestamp 為 undefined（fallback 為 0）

| 欄位 | 內容 |
|------|------|
| **名稱** | `extractUserResponseAfter_missing_timestamp_fallback` |
| **目的** | 驗證 `m.timestamp ?? 0` fallback 行為 |
| **輸入** | `messages = [{role:"user",content:"無時間",timestamp:undefined}], afterTimestamp = 1` |
| **預期輸出** | `null`（timestamp fallback 為 0，0 > 1 為 false）|
| **測試資料建議** | timestamp 明確為 undefined |

### 3.3 Hook 邏輯補充案例

#### TC-13：agent_end 同一 session 兩次呼叫（覆蓋而非重複）

| 欄位 | 內容 |
|------|------|
| **名稱** | `agent_end_same_session_overwrites` |
| **目的** | 驗證第二次呼叫覆蓋第一次，而非產生兩筆殘留 |
| **操作序列** | 1. agent_end(sessionId="s1", recallIds=["id1"], responseText="text1") 2. agent_end(sessionId="s1", recallIds=["id2"], responseText="text2") |
| **預期輸出** | pendingRecall 只有一筆（id2 的 entry），第一筆被覆蓋 |
| **驗證方式** | mock pendingRecall.get("s1")，確認回傳的是第二次的 entry |
| **測試資料建議** | 兩次不同的 recallIds |

#### TC-14：before_prompt_build 多筆 recallIds

| 欄位 | 內容 |
|------|------|
| **名稱** | `before_prompt_build_multiple_recall_ids` |
| **目的** | 驗證多筆 recallIds 時，每筆都正確比對和寫入 |
| **操作序列** | 1. agent_end(sessionId="s1", recallIds=["id1","id2"], responseText="包含 id1 內容") 2. before_prompt_build(sessionId="s1") |
| **預期輸出** | store.update 至少被呼叫 2 次（id1 命中，id2 未命中），pendingRecall 被清除 |
| **驗證方式** | mock isRecallUsed，確認被呼叫 2 次；mock store.update，確認參數正確 |
| **測試資料建議** | responseText 只包含 id1 的內容 |

#### TC-15：before_prompt_build 時 pendingRecall 已不存在

| 欄位 | 內容 |
|------|------|
| **名稱** | `before_prompt_build_no_pending_recall` |
| **目的** | 驗證 pendingRecall 已被清除時，before_prompt_build 不會錯誤 |
| **操作序列** | 1. agent_end(sessionId="s1", ...) 2. before_prompt_build(sessionId="s1") 3. before_prompt_build(sessionId="s1")（第二次） |
| **預期輸出** | 第二次呼叫平安无事，不拋例外 |
| **驗證方式** | mock pendingRecall.get 回傳 undefined，確認不 crash |

#### TC-16：TTL cleanup 未超過 5 分鐘的項目不清除

| 欄位 | 內容 |
|------|------|
| **名稱** | `ttl_cleanup_within_5_minutes_preserved` |
| **目的** | 驗證 TTL cleanup 不會誤刪未超時的項目 |
| **操作序列** | 1. agent_end(sessionId="s1", ...) with injectedAt = Date.now() - 4分鐘 2. 執行 TTL cleanup |
| **預期輸出** | pendingRecall.get("s1") 仍存在 |
| **測試資料建議** | injectedAt 設為 4 分鐘前 |

#### TC-17：TTL cleanup 正在比對中的項目（injectedAt 符合）不被清除

| 欄位 | 內容 |
|------|------|
| **名稱** | `ttl_cleanup_active_session_preserved` |
| **目的** | 驗證 TTL cleanup 有正確的 session 比對邏輯 |
| **操作序列** | 1. agent_end(sessionId="s1", ...) 2. before_prompt_build(sessionId="s2") 3. TTL cleanup |
| **預期輸出** | pendingRecall.get("s1") 仍存在（s1 正在比對中，不應被清除）|
| **測試資料建議** | 兩個不同的 sessionId |

### 3.4 整合測試案例（跨模組）

#### TC-18：完整流程（agent_end → before_prompt_build → session_end）

| 欄位 | 內容 |
|------|------|
| **名稱** | `integration_full_recall_lifecycle` |
| **目的** | 驗證完整生命周期的狀態變化 |
| **操作序列** | 1. agent_end(sessionId="s1", recallIds=["id1"], responseText="包含回憶內容") 2. before_prompt_build(sessionId="s1") 3. session_end(sessionId="s1") |
| **預期輸出** | 步驟 2 後 store.update 被正確呼叫，步驟 3 後 pendingRecall 清除 |
| **測試資料建議** | 完整的三步流程 |

#### TC-19：responseText 為 null 時的完整流程

| 欄位 | 內容 |
|------|------|
| **名稱** | `integration_null_response_text` |
| **目的** | 驗證 extractUserResponseAfter 回傳 null 時，整個流程不受影響 |
| **操作序列** | 1. agent_end(sessionId="s1", recallIds=["id1"], responseText=null) 2. before_prompt_build(sessionId="s1") |
| **預期輸出** | pendingRecall entry 存在但 responseText 為 null，isRecallUsed 收到 null 回傳 false，bad_recall_count +1 |
| **測試資料建議** | responseText = null 或 undefined |

---

## 四、測試資料建議

### 4.1 測試資料生成策略

```
isRecallUsed 所需的最小長度覆蓋：
- text.length = 19  (第一關 false)
- text.length = 20  (snippet = "" → false)
- text.length = 25  (snippet.length = 5 → 達標)
- text.length = 90  (短文本分支，全部作為 snippet)
- text.length = 91  (長文本分支，slice(20,70))
- text.length = 100 (典型長文本)
```

### 4.2 測試資料矩陣

| 用途 | text 長度 | text 內容 | responseText | 預期 |
|------|----------|----------|-------------|------|
| 最小達標 | 25 | 25個不同中文字 | 包含最後5字 | true |
| 短文本命中 | 50 | 正常句子 | 包含完整原句 | true |
| 短文本未命中 | 50 | 正常句子 | 空 | false |
| 長文本命中 | 100 | 正常句子 | 包含20~70之間片段 | true |
| 長文本只含前綴 | 100 | 固定前綴20字+內容 | 只有前綴 | false |
| 臨界：trim 後不足 | 25 | 12空白+13字 | 包含那13字 | false（trim後不足20）|

---

## 五、Phase 1（B-1）`reflection-slices.ts` BM25 鄰居擴展測試需求評估

### 5.1 元件職責分析

`reflection-slices.ts` 預計職責（根據設計文件 v8）：
- 維護「切片」的向量表示（reflection slices）
- 提供 BM25 相似度查詢，擴展回憶的鄰居範圍
- 可能在 `before_prompt_build` 或 `store.update` 時被呼叫

### 5.2 建議的單元測試範圍

假設 `reflection-slices.ts` 包含以下公開函式（需與 James 確認實際 API）：

| 函式 | 建議測試案例 |
|------|------------|
| `upsertSlice(reflectionId, embedding, content)` | 正常寫入、覆蓋更新、 invalid input |
| `queryNeighbors(embedding, k)` | 返回 k 個最近鄰居、k 為 0/負數、超出總量 |
| `deleteSlice(reflectionId)` | 正常刪除、刪除不存在的 ID |
| `getSlice(reflectionId)` | 正常讀取、讀取不存在的 ID 回傳 null |
| BM25 排序邏輯 | 多個候選時的排序正確性、相同分數時的穩定性 |

### 5.3 與 Phase 2 的關係

`reflection-slices.ts` 是 Phase 1 的核心元件，其測試應**早於** Phase 2 的 hook 邏輯，因為 Phase 2 的 hook 邏輯依賴 `isRecallUsed` 等函式，而那些函式可能會呼叫 `reflection-slices` 來取得切片文字。

**建議順序**：
1. **Phase 1 先完成**：`reflection-slices.ts` 的 BM25 查詢邏輯
2. **Phase 2 其次**：`isRecallUsed` 和 `extractUserResponseAfter` 純函數
3. **Phase 3**：Hook 邏輯 mock 測試
4. **Phase 4**：TTL cleanup 和整合測試

---

## 六、假設驗證清單

| 假設 | 來源依據 | 驗證狀態 |
|------|---------|---------|
| `agent_end` hook 在收到 `recalledMemoryIds` 時觸發 | 設計文件 v8 狀態機 | ⚠️ 待確認 |
| `before_prompt_build` hook 依序處理 `recallIds` array | 設計文件 v8 狀態機描述 | ⚠️ 待確認 |
| pendingRecall 使用 `Map<sessionId, ...>` 而非 Array | 設計文件 v8：`pendingRecall.set(...)` | ⚠️ 待確認 |
| TTL cleanup 在每次 hook 呼叫時被動觸發 | 設計文件 v8 未明確 | ⚠️ 待確認 |
| `extractUserResponseAfter` 的 `messages` 來自 conversation history | 設計文件 v8 未明確指定來源 | ⚠️ 待確認 |
| `reflection-slices.ts` 會呼叫 `isRecallUsed` | 推測，Phase 1 與 Phase 2 的依賴關係 | ⚠️ 待確認 |
| `recalledMemoryIds` 是 Array 而非單一 ID | 設計文件 v8 未明確 | ⚠️ 待確認 |
