# Claude Code 對抗性審查報告（繁體中文）
> 審查時間：2026-04-13
> 工具：Claude Code CLI v2.1.97 + minimax-portal/MiniMax-M2.7

---

## P0（阻斷性——必須修復才能合併）

### 1. Session_end 未觸發時的記憶體洩漏
`pendingRecall` Map 是模組級別，沒有 TTL 或 cleanup mechanism。如果 client 直接斷線、session_end 沒被調用、或 process crash，entries 永久留在記憶體直到重啟。長期下來會 OOM。

**修復方向**：加入 TTL-based cleanup 或 WeakRef-based cleanup。

### 2. bad_recall_count 的 read-modify-write race condition
並發 session 場景下，兩個 session 同時讀取、遞增、寫回，沒有 compare-and-swap 或 optimistic locking，最後值會低於實際次數。

**修復方向**：store.update() 使用 compare-and-swap 或 optimistic locking。

### 3. isRecallUsed() Summary path 缺少 AND gate
Codex Review 提出的 bug：summary verbatim match 時，`injectedSummaries` 有值但 `injectedIds` 為空，會繞過 AND 邏輯。

**修復方向**：summary path 也需要 AND gate（ID + marker 都存在才 return true）。

---

## P1（重要——應在合併前修復）

### 4. autoCapture block boundary 未驗證
需要實際 diff 確認 hooks 在 block 外，否則 `autoCapture: false` 時 feedback loop 完全消失。

### 5. 配置覆蓋靜默失敗
`fromRaw()` 對 `null` 值會 silent fallback，caller 無從得知哪些欄位被忽略。

### 6. Phase 4 測試 mock 問題
`feedback-config.test.mjs` 和 `bad-recall-count.test.mjs` 在測試檔內重新實作函式，沒有 import 真實程式碼。

### 7. 測試覆蓋率為零
373 行新程式碼（Phase 1）完全沒有測試。

---

## P2（建議改進——可在後續 Phase 處理）

- Hook registration 無 error handling
- before_prompt_build timing 未有正式 ordering guarantee
- Injection-based importance 腐化攻擊
- Index.ts 是衝突熱點

---

## 結論

Phase 1 的核心機制（hooks + scoring + cleanup）在概念上正確，但有兩個 P0 等級實作漏洞和一個 P0 邏輯漏洞，在修復前不建議合併進 master。
