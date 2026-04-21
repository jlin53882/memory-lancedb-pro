# ERRORS.md — 已知的工具錯誤

## 2026-04-06

### sessions_list 持續 gateway timeout

**錯誤訊息**：`gateway timeout after 10000ms`，`Gateway target: ws://127.0.0.1:18789`

**影響**：`sessions_list` 完全無法使用，無法查詢其他 session 的歷史。

**狀態**：已知問題，gateway 服務 WebSocket 阻塞。

**繞過方式**（見 LEARNINGS.md）：
- 直接讀取 `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
- 用 Python 解析 JSONL 而非依賴 `sessions_list`
- 列出 session：`Get-ChildItem *.jsonl | ForEach-Object { (Get-Content $_.FullName -First 1 | jq -r '.timestamp') + " " + $_.Name }`
- 時間範圍過濾：用 `head -1` 確認 timestamp，Python 過濾 `>= 2026-04-05T16:00`

---

## 2026-04-09 — Proposal A Bugs（from Claude Code 對抗性分析）

### Bug: bad_recall_count 只有 reset，**從未 increment**（P0）

- **問題**：`bad_recall_count` 在官方 master 中只有 `= 0` 的賦值（smart-extractor.ts 第 1002/1100/1164/1220 行，tools.ts 第 595/843/934/1872 行），完全找不到任何 `+ 1` 遞增邏輯。
- **觸發條件**：任何 miss path（記憶未被使用）場景，計數器永遠是 0。
- **嚴重程度**：P0 — `badCount >= 2` penalty 條件**永遠不可能觸發**，Phase 1 設計的第三個信號是 dead code path。
- **相關檔案**：
  - `memory-lancedb-pro/src/smart-extractor.ts`（官方）
  - `memory-lancedb-pro/src/tools.ts`（官方）
  - PR #507 中聲稱已修復，但 PR #507 從未合併進 master
- **修復建議**：在 `before_prompt_build` hook 的 miss path 中，正確遞增 `bad_recall_count`：
  ```typescript
  const current = parseSmartMetadata(entry.metadata);
  const nextBad = current.bad_recall_count + 1;
  // 寫回 metadata
  ```
- **是否已記錄**：否（新發現）

---

### Bug: last_confirmed_use_at 從未被寫入（P0）

- **問題**：`staleInjected` 判斷依賴 `last_confirmed_use_at`，但官方程式碼中此欄位從未被寫入任何值。
- **觸發條件**：任何 injection 後，判斷是否 stale 時，都因為 `last_confirmed_use_at = null/undefined` 而錯誤觸發 `staleInjected = true`。
- **嚴重程度**：P0 — 幾乎所有 injected 記憶都會被錯誤視為 stale，造成 recall 反饋信號失真。
- **相關檔案**：`memory-lancedb-pro/src/tools.ts`、`smart-extractor.ts`
- **修復建議**：在 confirm path（記憶被成功使用並確認）中，正確寫入 `last_confirmed_use_at = Date.now()`。
- **是否已記錄**：否（新發現）

---

### Bug: autoCapture block boundary 導致 hooks 被錯誤停用（P1）

- **問題**：`if (config.autoCapture !== false)` 區塊在 `api.on("agent_end", ...)` 以後**沒有正確關閉**，導致後續程式碼被錯誤地 conditional 化。
- **觸發條件**：
  ```json
  { "autoCapture": false, "selfImprovement": { "enabled": true } }
  ```
  預期：`selfImprovement` 正常運行。實際：selfImprovement 也被停用（因為在 block 內）。
- **嚴重程度**：P1 — 功能開關失效，使用者關閉 autoCapture 時會意外停用無關功能。
- **相關檔案**：PR #507 / #505 中 `index.ts` 的 hook 註冊位置。
- **修復建議**：確認 `if (config.autoCapture !== false)) {` 的 `}` 有正確閉合；確保 feedback hooks、self-improvement hooks 在 if block 之外。
- **是否已記錄**：否（新發現）

---

### Bug: Summary match 缺少 hasUsageMarker 檢查（P2）

- **問題**：`isRecallUsed()` 的 summary branch 在 verbatim match >= 10 字元時直接 `return true`，**沒有檢查 hasUsageMarker**。若用戶回應巧合包含了一段注入的 summary text，就會被錯誤視為「記憶被使用」。
- **觸發條件**：agent 回應包含 >= 10 字元的 summary verbatim match，但實際上 agent 完全沒有主動使用該記憶。
- **嚴重程度**：P2 — recall feedback 信號準確度下降，可能造成 false positive（錯誤獎勵未真正使用的記憶）。
- **相關檔案**：`memory-lancedb-pro/src/reflection-slices.ts`（官方程式碼中此函式不存在，來自 PR #507）
- **修復建議**：在 summary match branch 加入 `hasUsageMarker` 檢查，或要求 summary match 需搭配 `hasSpecificRecall = true`（即需有 ID match，而非單獨成立）。
- **是否已記錄**：否（新發現）

---

### Bug: "that's not right" false positive（P2）

- **問題**：`errorKeywords: ['錯誤', '不對', 'wrong', 'not right']` 使用 substring match（`toLowerCase().includes()`）。
  用戶說 "That's not right — the meeting is at 3pm, not 2pm"（針對具體事實的糾正），會被錯誤視為 error signal，導致 `importance -= 0.10`（懲罰被使用的記憶）。
- **觸發條件**：用戶口語糾正具體事實（時間、數字等），而非否定記憶本身。
- **嚴重程度**：P2 — recall feedback 系統錯誤懲罰了正確的記憶使用。
- **相關檔案**：`memory-lancedb-pro/src/feedback-config.ts`
- **修復建議**：改用更精確的 error keyword：`['錯誤的', '不對的', 'wrong answer', 'incorrect']` 而非 `['wrong', 'not right']`；或增加 context 判斷（需同時包含被注入的 memory ID/摘要才視為 error）。
- **是否已記錄**：否（新發現）

---

### Bug: id[-:] pattern 過度匹配（P2）

- **問題**：`id[-:]` pattern 使任何包含 `id-abc123` 這類常見 ID 格式的回應都滿足 `hasUsageMarker = true`，導致 `hasMatchingId && hasUsageMarker` 的 AND 檢查實際上退化成只有 `hasMatchingId`。
- **觸發條件**：用戶回應中任何地方提到 "id-xxx" 格式的 ID。
- **嚴重程度**：P2 — marker 的 second-factor 驗證意義失效。
- **相關檔案**：`memory-lancedb-pro/src/reflection-slices.ts`（usage marker regex）
- **修復建議**：從 usage marker regex 中移除 `id[-:]`；或要求 ID 匹配同時要有具體的 usage marker phrase。
- **是否已記錄**：否（新發現）

---

### Bug: confirmKeywords/errorKeywords 語言覆蓋不足（P2）

- **問題**：關鍵字只覆蓋部分語言：
  - 缺少繁體：「是對的」（簡體），「對的」（正體）；繁體用戶說「是對的」不會匹配
  - 缺少簡體：「確認」（繁體），簡體用戶說「确认」不會匹配
  - 缺少英文 confirm：「yes」/「correct」/「that's right」
  - 缺少英文 error：「that's wrong」/「incorrect」/「mistake」
- **觸發條件**：非中文（繁/簡）或非英語關鍵字表達的回應，都被忽略。
- **嚴重程度**：P2 — 多語言部署時 feedback 信號有語言偏差。
- **相關檔案**：`memory-lancedb-pro/src/feedback-config.ts`
- **修復建議**：
  ```typescript
  confirmKeywords: ['yes','correct',"that's right",'没错','對','確認','正確','right']
  errorKeywords: ['mistake','incorrect',"that's wrong",'错','不对','錯誤','不對','wrong']
  ```
- **是否已記錄**：否（新發現）

---

### Bug: injected_count 單向膨脹無 cap（P2）

- **問題**：每次 injection `injected_count++`，但從未有任何 decay 或 reset 機制，長期運行後可能造成 metadata bloat。
- **觸發條件**：長期運行的 agent，injected_count 持續累加無上限。
- **嚴重程度**：P2 — metadata storage 浪費，長期影響效能。
- **相關檔案**：`smart-extractor.ts`、`tools.ts`
- **修復建議**：加入 metadata array size cap（與 `MAX_SOURCES`/`MAX_HISTORY`/`MAX_RELATIONS` 同樣模式）。
- **是否已記錄**：否（新發現）

---

### Bug: importance floor (0.1) 與 Decay floor (0.5~0.9) 矛盾（P1）

- **問題**：
  - Decay engine：`coreDecayFloor=0.9`、`workingDecayFloor=0.7`、`peripheralDecayFloor=0.5`
  - Feedback 設計：`importance floor = 0.1`
  - 當 Core tier memory 的 importance 被 feedback 降至 0.1 時，decay engine 的 effectiveHL 幾乎不衰減，但 tier floor 0.9 仍會把 composite score 拉高，造成邏輯不一致。
- **觸發條件**：Core tier 記憶被連續多筆 error feedback 降至低 importance。
- **嚴重程度**：P1 — Core tier 的 decay floor 與 importance 脫鉤，造成 memory 行為不可預測。
- **相關檔案**：`decay-engine.ts`、`feedback-config.ts`
- **修復建議**：
  - 方案 A：feedback floor 與 tier-decay floor 掛鉤
  - 方案 B：decay floor 只約束 composite score，不約束 importance 欄位
  - 方案 C：明確區分「重要性分數衰減」與「元数据重要性更新」概念
- **是否已記錄**：否（新發現）

---

### Bug: Phase 4 測試在測 mock 而非真實程式碼（P1）

- **問題**：
  - `feedback-config.test.mjs`：在測試檔案中重新實作了 `FeedbackConfigManager` 而非 import 真正的實作
  - `bad-recall-count.test.mjs`：`computeNextBadCount` 定義在測試檔案內，而非測試真正的 source code
  - 結果：若實際 source code 的實作邏輯改變，測試仍會通過（false pass）
- **觸發條件**：實際 source code 的計算邏輯邊界條件有任何改動，CI 無法捕捉。
- **嚴重程度**：P1 — CI 無法驗證實際行為，測試失去保護意義。
- **相關檔案**：`test/feedback-config.test.mjs`、`test/bad-recall-count.test.mjs`（皆在 PR #506 中）
- **修復建議**：
  1. 重寫測試檔案，直接 import 真正的 source code
  2. 確認 `computeNextBadCount` 在 source code 中的實際位置，若不存在則調整實作
- **是否已記錄**：否（新發現）

---

### Bug: PR #493/#505/#507/#506 全部未合併進官方 master（P0）

- **問題**：所有 Proposal A 相關 PR 均為 closed 狀態，官方 master 分支從未收到任何 Proposal A 程式碼。整個 feature 是「未實現的願望清單」。
- **觸發條件**：查閱 GitHub PR 頁面狀態即可確認。
- **嚴重程度**：P0 — 功能根本不存在於官方程式碼中，所有實作等於白做。
- **相關檔案**：
  - PR #493: closed (2026-04-04)
  - PR #505: closed (2026-04-05)
  - PR #507: closed (2026-04-05)
  - PR #506: open（但 AliceLJY 給了 CHANGES_REQUESTED）
- **修復建議**：
  1. 先聯繫 AliceLJY 確認分支策略
  2. 重建正確分支鏈：`feat/proposal-a-v3-clean` → target `master`
  3. 逐一解決 CHANGES_REQUESTED 後重新提出
- **是否已記錄**：否（新發現）

---

### Bug: Branch topology 錯誤導致合併衝突（P3）

- **問題**：PR #507/#505/#506 都 targeting master 且修改同樣檔案，若同時合併會產生無法預測的 diff conflicts。
- **觸發條件**：同時打開多個 targeting master 的相關 PR。
- **嚴重程度**：P3 — 維護困難，合併順序不可預測。
- **修復建議**：建立 stack chain：`feat/proposal-a-v3-clean` → `feat/proposal-a-v3-configurable-v2` → `feat/proposal-a-v3-tests`。
- **是否已記錄**：否（新發現）

---

### Bug: unrelated bug fixes 混入同一 PR（P3）

- **問題**：PR #507 混入了 5 個與 feedback feature 無關的 bugfixes（如 rerankApiKey env resolution），AliceLJY 要求分離。
- **觸發條件**：PR 包含多個不相關的變更，reviewer 無法聚焦。
- **嚴重程度**：P3 — PR 審查困難，容易被要求重做。
- **修復建議**：分離獨立的 bugfix 到各自 PR，一個 PR 一個 concern。
- **是否已記錄**：否（新發現）

---

### Bug: 配置覆寫靜默失敗（P3）

- **問題**：使用者錯誤設定 `confirmKeywords: "not an array"`（傳入 string 而非 array），目前是 silent fallback（用預設值），但用戶可能以為自定義生效了。
- **觸發條件**：plugin config 中 confirmKeywords/errorKeywords 傳入非 array 類型。
- **嚴重程度**：P3 — 配置失敗無任何錯誤提示，難以 debug。
- **相關檔案**：`parsePluginConfig()` 或 `FeedbackConfigManager.fromRaw()`
- **修復建議**：加入 schema validation，拒絕時明確報錯而非 silent fallback。
- **是否已記錄**：否（新發現）

---

### Bug: isRecallUsed "记得" 重複出現（P3）

- **問題**：`usageMarkers` 陣列中 `"记得"` 出現兩次（reflection-slices.ts 第 356 和 357 行）。
- **觸發條件**：正常執行即觸發（陣列中無意義重複）。
- **嚴重程度**：P3 — 輕量 bug，無實際功能性影響，但影響程式碼品質。
- **修復建議**：刪除重複的 `"记得"` 項目。
- **是否已記錄**：否（新發現）


## 2026-04-21

### PowerShell heredoc << 語法在 append 模式失敗

**錯誤訊息**：'<' 運算子需要 '<<' 之後要有輸入來源

**錯誤指令**：
\cat >> test.mjs << 'ENDOFTEST'
...content...
ENDOFTEST
\
**原因**：PowerShell 把 << 視為 input redirection operator，不支援 heredoc 語法。'' 字元被錯誤處理。

**繞過方式**：用 Python script 寫入檔案：
\\python
with open('file.mjs', 'a', encoding='utf-8') as f:
    f.write(content)
\
**預防 Rule**：向現有檔案追加內容時，統一用 Python script。

---

### gh api --body-file 不存在，應用 --input

**錯誤訊息**：unknown flag: --body-file

**錯誤指令**：
\gh api repos/owner/repo/issues/N/comments --body-file file.txt
\
**正確參數**：--input file（不是 --body-file）

**替代方式**：Python urllib 直 call API（繞過 gh CLI 限制）。

---

### 對 bulkStore 實作的錯誤假設

**問題**：一開始說「bulkStore 內部是 store.store() loop」，所以担心 1000 entry 會觸發 stale threshold。

**實際**：bulkStore 是單次 	able.add(fullEntries) batch write，41ms 完成 1000 筆。

**預防 Rule**：對程式碼行為有假設時，先讀 source code 確認再下結論。
