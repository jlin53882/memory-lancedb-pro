# PR #246 Proposal A & B 測試情境規劃（30 種）

> 日期：2026-04-02
> 對應設計：`pr246_proposal_ab_design_v8.md`
> 測試目標：`memory-lancedb-pro-import-markdown-test`

---

## 測試分類總覽

| 類別 | 數量 | 對應 Phase |
|------|------|------------|
| 單元測試（Phase 1 / B-1）| 10 | 鄰居擴展 |
| 整合測試（Phase 2 hooks）| 10 | Feedback Signal 三鉤子 |
| E2E 測試（Proposal A）| 10 | 動態 Importance 整體效果 |

---

## 第一類：單元測試（Phase 1 / B-1 鄰居擴展）

### 測試 1-1：基礎鄰居擴展數量驗證

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-increases-result-count` |
| **測試目的** | 驗證加入 neighbor items 後，Reflection injection 結果數量增加 |
| **輸入** | 3 個 derived slices，`bm25Search` 回傳 2 個 neighbor items |
| **預期輸出** | 回傳陣列包含 5 個 items（3 original + 2 neighbors），且 ID 不重複 |
| **驗證方式** | 斷言 `result.length === 5`，且用 Set 檢查 ID 唯一性 |

---

### 測試 1-2：相同 strictKey 範圍限制

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-scopes-to-same-strictKey` |
| **測試目的** | 確保 neighbor 搜尋只擴展同 strictKey 的 reflection items |
| **輸入** | slice A 屬於 `scope: "project-a"`，slice B 屬於 `scope: "project-b"` |
| **預期輸出** | slice A 的 neighbor 只能來自 `scope: "project-a"` |
| **驗證方式** | 檢查每個 neighbor 的 scope 與原始 slice 相同 |

---

### 測試 1-3：BM25 搜尋回傳格式驗證

| 項目 | 內容 |
|------|------|
| **測試名稱** | `bm25-search-returns-valid-reflection-entries` |
| **測試目的** | 確保 BM25 搜尋結果格式與現有 entries 相容 |
| **輸入** | BM25 搜尋回傳的 mock entries（包含 id, text, scope, metadata） |
| **預期輸出** | 每個 neighbor entry 具備必要欄位：`id`, `text`, `scope`, `metadata.type === "memory-reflection-item"` |
| **驗證方式** | 逐一檢查欄位存在性與型別 |

---

### 測試 1-4：去重複邏輯（deduplicateById）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `deduplicate-by-id-removes-duplicates` |
| **測試目的** | 當 neighbor 與原始 slice ID 相同時，應去重複 |
| **輸入** | 原始 slices IDs: `["id-1", "id-2"]`，neighbor IDs: `["id-2", "id-3"]` |
| **預期輸出** | 回傳 3 個 unique items（id-1, id-2, id-3） |
| **驗證方式** | 斷言 `result.length === 3`，且 IDs 唯一 |

---

### 測試 1-5：空 neighbor 結果處理

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-handles-empty-bm25-results` |
| **測試目的** | 當 BM25 搜尋無回傳時，應回傳原始 slices（不崩潰） |
| **輸入** | 2 個 derived slices，`bm25Search` 回傳空陣列 |
| **預期輸出** | 回傳 2 個 items（僅原始 slices） |
| **驗證方式** | 斷言 `result.length === 2`，且內容與輸入相同 |

---

### 測試 1-6：Neighbor 品質抽樣（人工驗收）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-relevance-manual-sampling` |
| **測試目的** | 人工抽查 neighbor items 與原 slice 主題相關性（設計文件驗收標準） |
| **輸入** | 5 組 real BM25 搜尋結果（需實際建立測試資料） |
| **預期輸出** | 每組至少 1 個 neighbor 與原始 slice 語意相關 |
| **驗證方式** | 人工檢視输出（建議記錄在測試文件註解） |

---

### 測試 1-7：topK 參數控制

| 項目 | 內容 |
|------|------|
| **測試名稱** | `bm25-search-respects-topk-parameter` |
| **測試目的** | 驗證 `topK` 參數正確限制 neighbor 數量 |
| **輸入** | 1 個 slice，`topK: 3`，BM25 回傳 5 個候選 |
| **預期輸出** | 最多 3 個 neighbor items |
| **驗證方式** | 斷言 `neighbors.length <= 3` |

---

### 測試 1-8：同義詞跳過（dedupe 優化）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-avoids-identical-text-duplicates` |
| **測試目的** | 當 neighbor text 完全相同時，應視為重複並跳過 |
| **輸入** | 原始 slice text: "Verify outputs"，neighbor 回傳 2 個相同 text 的 items |
| **預期輸出** | 只保留 1 個 "Verify outputs" |
| **驗證方式** | 檢查输出去重後數量正確 |

---

### 測試 1-9：效能基準（數量上限）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-performance-under-large-dataset` |
| **測試目的** | 確保大量 slices 時不會超過合理執行時間 |
| **輸入** | 100 個 derived slices，每個 BM25 回傳 2 個 neighbors |
| **預期輸出** | 執行完成時間 < 500ms |
| **驗證方式** | 測量 `performance.now()` 差值 |

---

### 測試 1-10：scope filter 整合

| 項目 | 內容 |
|------|------|
| **測試名稱** | `neighbor-expansion-applies-global-scope-filter` |
| **測試目的** | 驗證 global scope 搜尋時排除非 global entries |
| **輸入** | `scopeFilter: ["global"]`，BM25 回傳 mixed scope entries |
| **預期輸出** | 只回傳 scope === "global" 的 neighbors |
| **驗證方式** | 檢查每個 neighbor 的 scope 符合 filter |

---

## 第二類：整合測試（Phase 2 Feedback Signal 三鉤子）

### 測試 2-1：agent_end 鉤子儲存 recall IDs

| 項目 | 內容 |
|------|------|
| **測試名稱** | `agent-end-hook-stores-recall-ids-and-response` |
| **測試目的** | 驗證 `agent_end` 鉤子正確儲存本輪的 recall IDs 與回應文字 |
| **輸入** | `ctx.session.recalledMemoryIds: ["mem-1", "mem-2"]`，`ctx.messages[-1].content: "使用記憶回覆"` |
| **預期輸出** | `pendingRecall` Map 中有 sessionId 對應的 entry，包含 `recallIds` 與 `responseText` |
| **驗證方式** | 檢查 `pendingRecall.get(sessionId)` 存在且內容正確 |

---

### 測試 2-2：agent_end 處理無 recall 的常態

| 項目 | 內容 |
|------|------|
| **測試名稱** | `agent-end-handles-empty-recalledmemoryids` |
| **測試目的** | 確保無 recall 時不會寫入 pendingRecall（常態非錯誤） |
| **輸入** | `ctx.session.recalledMemoryIds: undefined` 或 `[]` |
| **預期輸出** | `pendingRecall` Map 無新增項目 |
| **驗證方式** | 斷言 `pendingRecall.size === 0` |

---

### 測試 2-3：before_prompt_build 比對並寫入 metadata

| 項目 | 內容 |
|------|------|
| **測試名稱** | `before-prompt-build-writes-last-confirmed-use-at` |
| **測試目的** | 驗證當 recall 被使用時，寫入 `last_confirmed_use_at` 時間戳 |
| **輸入** | pending 中有 `recallIds: ["mem-1"]`，response 包含 recall text |
| **預期輸出** | `store.update("mem-1", { last_confirmed_use_at: <now> })` 被呼叫 |
| **驗證方式** | Mock `store.update`，檢查呼叫參數包含 `last_confirmed_use_at` |

---

### 測試 2-4：before_prompt_build 重置 bad_recall_count

| 項目 | 內容 |
|------|------|
| **測試名稱** | `before-prompt-build-resets-bad-recall-count-on-usage` |
| **測試目的** | 驗證被使用的記憶重置 `bad_recall_count` 為 0 |
| **輸入** | pending 中有 `recallIds: ["mem-1"]`，response 包含 recall text |
| **預期輸出** | `store.update("mem-1", { bad_recall_count: 0 })` 被呼叫 |
| **驗證方式** | Mock `store.update`，檢查 `bad_recall_count: 0` |

---

### 測試 2-5：before_prompt_build 遞增 bad_recall_count

| 項目 | 內容 |
|------|------|
| **測試名稱** | `before-prompt-build-increments-bad-recall-count-on-miss` |
| **測試目的** | 驗證未被使用的記憶遞增 `bad_recall_count` |
| **輸入** | pending 中有 `recallIds: ["mem-1"]`，response 不包含 recall text |
| **預期輸出** | `store.update("mem-1", { bad_recall_count: 1 })`（假設原本為 0）|
| **驗證方式** | Mock `store.get` 回傳 `bad_recall_count: 0`，檢查 update 參數 |

---

### 測試 2-6：before_prompt_build 清理 pendingRecall

| 項目 | 內容 |
|------|------|
| **測試名稱** | `before-prompt-build-deletes-pending-after-processing` |
| **測試目的** | 確保 processing 後立即刪除 pending 項目，防止洩漏 |
| **輸入** | pending 中有 sessionId 對應的 entry |
| **預期輸出** | processing 完成後，`pendingRecall.get(sessionId)` 回傳 undefined |
| **驗證方式** | 檢查 Map 狀態 |

---

### 測試 2-7：session_end 鉤子清理残留

| 項目 | 內容 |
|------|------|
| **測試名稱** | `session-end-hook-cleans-up-pending-recall` |
| **測試目的** | 驗證 session 結束時清理所有 pendingRecall |
| **輸入** | pending 中有 3 個不同 sessionId 的 entries |
| **預期輸出** | `session_end` 觸發後，`pendingRecall` 為空 |
| **驗證方式** | 斷言 `pendingRecall.size === 0` |

---

### 測試 2-8：短文本全段匹配策略

| 項目 | 內容 |
|------|------|
| **測試名稱** | `is-recall-used-short-text-uses-full-match` |
| **測試目的** | 驗證短文本（≤90 字）使用全段匹配策略 |
| **輸入** | recall text: "User prefers tea"（16 字），response: "User prefers tea" |
| **預期輸出** | `isRecallUsed()` 回傳 `true` |
| **驗證方式** | 直接單元測試 `isRecallUsed` 函式 |

---

### 測試 2-9：中段匹配策略（長文本）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `is-recall-used-long-text-uses-middle-match` |
| **測試目的** | 驗證長文本（>90 字）使用中段（20-70）匹配策略 |
| **輸入** | recall text: 100 字長文本，取出中段 "核心段落"，response 包含該中段 |
| **預期輸出** | `isRecallUsed()` 回傳 `true` |
| **驗證方式** | 直接單元測試 `isRecallUsed` 函式 |

---

### 測試 2-10：TTL fallback 機制

| 項目 | 內容 |
|------|------|
| **測試名稱** | `ttl-fallback-clears-stale-pending-recall` |
| **測試目的** | 當 session_end 不可用時，TTL 定時清理殘留項目 |
| **輸入** | pending 中有 entry 的 `injectedAt` 為 10 分鐘前 |
| **預期輸出** | TTL 清理觸發後，該 entry 被刪除 |
| **驗證方式** | 模擬時間推進，檢查 Map 清理 |

---

## 第三類：E2E 測試（Proposal A 動態 Importance）

### 測試 3-1：完整 feedback loop（使用 → importance +0.05）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-feedback-loop-increments-importance-on-use` |
| **測試目的** | 從 recall 到 importance 調整的完整流程驗證 |
| **輸入** | 記憶 importance: 0.7，被使用 1 次 |
| **預期輸出** | `importance` 調整為 0.75（+0.05，上限 1.0）|
| **驗證方式** | 完整 hook 流程後，讀取 store 中該記憶的 importance |

---

### 測試 3-2：user 確認正確（+0.15 大幅提升）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-user-confirmation-boosts-importance-plus-0.15` |
| **測試目的** | 驗證 user 明確確認正確時的 +0.15 幅度 |
| **輸入** | 記憶 importance: 0.7，user 回應確認正確 |
| **預期輸出** | `importance` 調整為 0.85（+0.15）|
| **驗證方式** | 模擬 user 回應解析流程，檢查 update 參數 |

---

### 測試 3-3：user 標記錯誤（-0.20 大幅下降）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-user-correction-reduces-importance-minus-0.20` |
| **測試目的** | 驗證 user 標記錯誤時的 -0.20 幅度 |
| **輸入** | 記憶 importance: 0.7，user 標記錯誤 |
| **預期輸出** | `importance` 調整為 0.5（-0.20，下限 0.1）|
| **驗證方式** | 模擬錯誤標記流程，檢查 update 參數 |

---

### 測試 3-4：連續未使用（-0.03 溫和下降）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-consecutive-miss-reduces-importance-minus-0.03` |
| **測試目的** | 驗證連續 2 次未使用時的溫和 -0.03 調整 |
| **輸入** | 記憶 `bad_recall_count: 1`，新一輪 recall 後仍未使用 |
| **預期輸出** | `importance` 減少 0.03（0.7 → 0.67）|
| **驗證方式** | 模擬連續 miss 場景，檢查 decr 邏輯 |

---

### 測試 3-5：Importance 上限 clamp（1.0）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-importance-clamped-at-1.0` |
| **測試目的** | 確保多次提升不超過上限 |
| **輸入** | 記憶 importance: 0.95，經歷 2 次使用（+0.05 × 2）|
| **預期輸出** | `importance` 維持 1.0（不超過）|
| **驗證方式** | 檢查 update 參數中的 clamp 邏輯 |

---

### 測試 3-6：Importance 下限 clamp（0.1）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-importance-clamped-at-0.1` |
| **測試目的** | 確保多次下降不低于下限 |
| **輸入** | 記憶 importance: 0.25，經歷 2 次錯誤（-0.20 × 2）|
| **預期輸出** | `importance` 維持 0.1（不低於）|
| **驗證方式** | 檢查 update 參數中的 clamp 邏輯 |

---

### 測試 3-7：每日寫入率驗收（> 0）

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-last-confirmed-use-at-daily-write-rate` |
| **測試目的** | 驗收標準：每日 `last_confirmed_use_at` 寫入率 > 0 |
| **輸入** | 執行 1 天的模擬對話（多個 sessions）|
| **預期輸出** | 至少有 1 筆記錄的 `last_confirmed_use_at` 非空 |
| **驗證方式** | Query store 檢查 `last_confirmed_use_at` 非零的記錄數 |

---

### 測試 3-8：bad_recall_count 遞增記錄

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-bad-recall-count-increment-recorded` |
| **測試目的** | 驗收標準：`bad_recall_count` 有遞增記錄 |
| **輸入** | 執行多輪對話，部分記憶未被使用 |
| **預期輸出** | 至少有 1 筆記錄的 `bad_recall_count > 0` |
| **驗證方式** | Query store 檢查 `bad_recall_count` 大於 0 的記錄數 |

---

### 測試 3-9：多記憶同時處理

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-processes-multiple-recalls-in-parallel` |
| **測試目的** | 驗證單次 recall 多個記憶時的正確處理 |
| **輸入** | pending 中有 5 個 recall IDs，部分使用、部分未使用 |
| **預期輸出** | 每個記憶正確更新對應的 metadata（使用→重置，未使用→遞增）|
| **驗證方式** | Mock `store.get/update`，檢查各別呼叫參數 |

---

### 測試 3-10：跨 session 狀態隔離

| 項目 | 內容 |
|------|------|
| **測試名稱** | `e2e-isolates-state-across-sessions` |
| **測試目的** | 確保不同 session 的 pendingRecall 不會混淆 |
| **輸入** | Session A 與 Session B 同時進行，各自 recall 不同記憶 |
| **預期輸出** | 各 session 獨立處理，不相互影響 |
| **驗證方式** | 檢查 `pendingRecall` Map  Keys 正確分離 |

---

## 測試輔助工具需求

根據現有測試框架，需額外建立：

| 工具 | 用途 |
|------|------|
| `openclaw-plugin-sdk-stub.mjs` 擴展 | 增加 `agent_end`, `before_prompt_build`, `session_end` 事件模擬 |
| `mockCtx.ts` | 模擬 `ctx.session`, `ctx.messages`, `ctx.store` |
| `isRecallUsed-helper.test.mjs` | 獨立單元測試 `isRecallUsed` 函式 |

---

## 執行順序建議

1. **先跑單元測試（1-1 至 1-10）**：驗證 Phase 1 B-1 鄰居擴展
2. **再跑整合測試（2-1 至 2-10）**：驗證 Phase 2 三鉤子協作
3. **最後跑 E2E（3-1 至 3-10）**：驗證 Proposal A 整體效果

---

*本文件對應 PR #246 實作驗收*