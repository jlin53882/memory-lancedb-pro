# PR #493 Proposal A 踩坑記錄

> 建立時間：2026-04-04
> 分支：feat/proposal-a-v3-clean
> PR：#493

---

## 程式碼 Bug（已修復）

### Bug 1: injectedIds regex 永遠匹配不到（Critical）

- **問題**：`before_prompt_build` feedback hook 使用 `/\[([a-f0-9]{8,})\]/gi` regex 解析 injected IDs，但 auto-recall 注入的是 `[preferences:global]`、`[facts:dc-channel]` 格式，而非 hex ID。
- **根因**：開發 feedback hook 與 auto-recall injection 的人沒有對齊資料格式，雙方各自用了不同的 ID 表示方式。
- **修復**：直接從 `pendingRecall` Map 讀取 `recallIds`（auto-recall 在寫入 pendingRecall 時已存入），不再做字串 regex 解析。
- **教訓**：跨模組介面（auto-recall ↔ feedback hook）應在文件或介面層明確定義資料格式，並用 TypeScript interface 強制約束，不能靠猜測。

---

### Bug 2: parseSmartMetadata 吃進空白 metadata，回傳錯誤的 fallback 值（Major）

- **問題**：`parseSmartMetadata()` 被呼叫時傳入的是空物件 placeholder，回傳變成 fallback 值而非真實 entry 資料。
- **根因**：呼叫端沒有先 fetch 真實 entry，直接傳了空殼 metadata。
- **修復**：在 parse 前先 `store.getById(recallId)` 取回真實 entry，再傳入 `parseSmartMetadata`。
- **教訓**：取資料 → 解析 → 使用的流程必須順序正確；不要對尚未取得的資料做 parse。

---

### Bug 3: patchMetadata 只更新 JSON blob，未更新 ROW 層級的 importance 欄位（Major）

- **問題**：`patchMetadata()` 只更新了 metadata JSON，但 `applyImportanceWeight()` 讀的是 `entry.importance`（ROW 欄位），所以重要性調整從未生效。
- **根因**：同一筆 entry 有兩處都可表達重要性，patchMetadata 只修了其中一個。
- **修復**：改用 `store.update(id, { importance: newValue })` 直接更新 ROW 欄位。
- **教訓**：存取同一筆資料的多個欄位時，確認所有讀端和寫端指向同一個欄位；建議用 unit test 驗證 store.get/getById 回傳的欄位與 update/write 寫入的欄位是同一個。

---

### Bug 4: pendingRecall 的 recallIds 與 responseText 來自不同 Turn（Critical）

- **問題**：`pendingRecall` 在 Turn N 被寫入 recallIds，但在 Turn N+1 feedback hook 才寫入 responseText，導致 Turn N 的回饋分數打在錯誤的記憶組合上。
- **根因**：`before_prompt_build`（auto-recall）負責建立 pendingRecall 條目，`agent_end` feedback hook 負責寫入 responseText，兩個鉤子非同步觸發於不同 Turn。
- **修復**：`before_prompt_build`（auto-recall）負責 CREATE pendingRecall；`agent_end` 只 WRITE responseText 到已存在的 entry（不再 CREATE）；`feedback` hook 最後負責 DELETE。
- **教訓**：多人共同寫入同一個共享狀態（Map）時，必須在架構層明定「誰创建、誰写入、谁删除」的責任邊界，並用文件或程式強迫遵守。

---

### Bug 5: bad_recall_count 重複累加（double-increment）導致懲罰提前觸發（Major）

- **問題**：`bad_recall_count` 在 auto-recall injection path 與 feedback hook 兩處都 +1，變成每 Miss 2 次就累積 4 點，讓本應 3 次才觸發的連續失敗懲罰提早到 2 次就觸發。
- **根因**：兩個團隊（寫 auto-recall 的人與寫 feedback hook 的人）都覺得自己應該 increment，沒有對齊哪邊是「單一事實來源」。
- **修復**：counter 只在 auto-recall injection path 的 `staleInjected` 評估時增加一次，feedback hook 移除 +1。
- **教訓**：同一個 counter 不應在兩處獨立地做 +1；需要先對齊「寫入點只有一個」的原則，或在實作前grep整個專案確認沒有其他地方寫同一個變數。

---

### Bug 6: confirmed use 未重置 bad_recall_count，破壞「連續失敗」語意（P2）

- **問題**：使用者確認使用某筆記憶時，`bad_recall_count` 未歸零，導致 interleave（確認→失敗→確認→失敗）時也會錯誤觸發懲罰。
- **根因**：回憶確認信號（user confirmation）加入時，忘記同步更新 counter 重置邏輯。
- **修復**：在 confirmed use 的 case 加上 `bad_recall_count = 0`。
- **教訓**：新增一個信號（confirmation signal）時，必須列出所有與其相關的狀態機狀態，確保狀態轉換封閉。

---

### Bug 7: pendingRecall.delete() 放在錯誤的 hook，破壞 feedback 正確性（P2）

- **問題**：`pendingRecall.delete()` 原本放在 `session_end` hook，但 session_end 在feedback評分完成後才觸發，導致同一組 recallIds + responseText 被重複評分。
- **根因**：誤以為 session_end 適合做 cleanup，但 session_end 比 feedback hook 更晚執行。
- **修復**：改在 feedback hook 的 finally 區塊立即刪除。
- **教訓**：了解每個 hook 的觸發順序（before_prompt_build → agent_end → feedback → session_end），並據此決定狀態清理責任放在哪個階段。

---

### Bug 8: isRecallUsed() 未檢查 injected summary text verbatim（P1）

- **問題**：`isRecallUsed()` 只檢查 stock phrases 與原始 ID，但 auto-recall 注入的是 `[category:scope]` 格式的 summary text。
- **根因**：auto-recall 注入的是 `item.line`（摘要文字），但 isRecallUsed 不知道要檢查這個格式。
- **修復**：在 auto-recall 注入時同步把 `injectedSummaries`（item.line）存入 `pendingRecall`；isRecallUsed 新增檢查 response 是否包含這些 summary text 的邏輯。
- **教訓**：記憶注入格式與回饋檢查格式必須同時演化，否則一邊改格式另一邊就斷裂。建議把 injection format 列為 interface 文件的一環。

---

### Bug 9: 確認/否認關鍵字比對目標錯誤（用錯了 responseText 而非 user prompt）（P1）

- **問題**：`confirm/error` 關鍵字比對拿 `pending.responseText`（上一輪 assistant 回覆）比對，而非 current-turn 的 user prompt。
- **根因**：`event.prompt` 在原始假設中是 plain string，但實際上是 `messages[]` 陣列；直接拿字串比對當然錯誤。
- **修復**：在 `before_prompt_build` feedback hook 中從 `event.messages` 取最後一條 user message，再比對關鍵字。
- **教訓**：使用 event 物件前應先查閱實際型別定義，不要靠假設。遇到不確定的格式時，先寫一個小型測試印出來確認。

---

### Bug 10: parsePluginConfig() 未回傳 cfg.feedback，導致設定永遠用不到（Major）

- **問題**：`parsePluginConfig()` 只複製了部分欄位，`cfg.feedback` 從未被拷貝進回傳值，所有 deployment 都回退到 hardcoded defaults。
- **根因**：新增 feedback 設定時忘記更新 return object，沒有類型檢查強制約束（interface 定義了但實作漏掉）。
- **修復**：在 parsePluginConfig 的 return object 中加入 `feedback: cfg.feedback`。
- **教訓**：interface 定義了欄位不等於實作會回傳；每次在 interface 新增欄位，應同時搜尋所有實作點確保都有處理，或用 TypeScript strict mode 強制編譯檢查。

---

### Bug 11: pendingRecall key 未包含 agentId，跨 agent 互相覆寫（Major）

- **問題**：`pendingRecall[sessionKey]` 在多 agent 情境下會被後寫入的 agent 覆寫前一個 agent 的 recallIds。
- **根因**：key 只有 sessionKey，沒有多租戶隔離。
- **修復**：key 格式改為 `sessionKey:agentId`（同時在 auto-recall 與 feedback/agent_end hooks 更新）。
- **教訓**：有 shared state（模組層級 Map）的程式，永遠要考虑「誰有權寫這個 key」，多 agent 或 concurrent 情境下要用 compound key。

---

### Bug 12: CJK 確認關鍵字太短，誤觸率高（P1）

- **問題**：使用單字「是/對/不/錯」當關鍵字，普通對話中隨便出現這些字就會觸發，導致大量 false positive。
- **根因**：低估了 CJK 語境中單字的常見程度。
- **修復**：替換為更長的 phrases：`是對的/確認/錯誤/更正`。
- **教訓**：關鍵字/pattern 設計時要考慮 natural language 的多義性；建議在 staging 環境先用真實對話 log 做回測，確認誤觸率可接受。

---

### Bug 13: session_end hook 完全沒清理 pendingRecall（P3）

- **問題**：`session_end` hook 是空的，沒有執行任何 pendingRecall cleanup。
- **根因**：session_end 的清理邏輯忘記實作，只有 feedback hook 在運作。
- **修復**：在 session_end 中新增邏輯，清理所有符合 sessionId 或 `sessionKey:agentId` 複合 key 的 pendingRecall 條目。
- **教訓**：建立鉤子時要有「鉤子啟動→鉤子測試」的配套，確保每個鉤子起碼有 smoke test。

---

### Bug 14: bad_recall threshold 設為 3，spec 說是 2（issue #445）

- **問題**：實作中 threshold 寫 3，但規格說應該是 2。
- **根因**：implementor 讀 spec 不夠仔細，或 spec 本身有更新但實作未同步。
- **修復**：改為 2。
- **教訓**：實作前要對照 spec 逐欄確認，threshold/常數類的值要額外標註「spec value」，避免日後 diff spec 時漏掉。

---

### Bug 15: isRecallUsed() 的 AND邏輯錯誤 + bad_recall_count increment 位置錯誤（Last fix）

- **問題**：`isRecallUsed()` 邏輯用 AND 判斷（所有 injected 都出現才算使用），但應為 OR（任一出現即算使用）；同時 bad_recall_count increment 位置導致計數錯誤。
- **根因**：邏輯判斷式的設計錯誤，未充分考慮「任一記憶被使用」就算成功的语义。
- **修復**：改為 OR 邏輯，並修正 increment 位置。
- **教訓**：布林邏輯要對照業務語意確認（ALL vs ANY）；threshold/counter 的遞增位置要在整個流程圖上標註，避免在非預期路徑重複執行。

---

### Bug 16: WeakSet.clear() 不存在（Major）

- **問題**：`resetRegistration()` 中呼叫了 `_registeredApis.clear()`，但 `WeakSet` 沒有 `clear()` 方法，導致 runtime error。
- **根因**：開發者從 `Map.clear()` 或 `Set.clear()` 的使用經驗類推到 `WeakSet`，未查文件。
- **修復**：移除 `.clear()` 呼叫（WeakSet 的生命週期由 GC 管理，無法手動清理）。
- **教訓**：每個資料結構的 API 不完全相同；跨語言或跨類別複製 API 前要先確認該類別是否支援。

---

### Bug 17: smart-extractor.ts 中 regex 包含 literal backspace (0x08)（Major）

- **問題**：在 `src/smart-extractor.ts` 第 76 行，regex pattern 中間有一個 literal backspace byte (0x08)，變成 `agent[0x08].*?` 而非預期的 word boundary。
- **根因**：不明（可能是編輯器 bug 或非預期的字元貼上）。
- **修復**：把 0x08 byte 替換為正確的 `\b` word boundary。
- **教訓**：含 regex 的程式碼建議在 repo 用 pre-commit hook 做 trailing whitespace / invisible char 檢查；或用 `cat -A` / hexdump 確認無異常 byte。

---

### Bug 18: rerank env vars 未加 enabled guard（P1）

- **問題**：當 `rerank='none'`（停用）但 `rerankApiKey` 仍有未解析的 placeholder 時，程式啟動失敗。
- **根因**：env resolve 邏輯在 rerank 未啟用時也會執行，拿到未解析的 placeholder 就爆了。
- **修復**：在 resolve env placeholders 前先確認 `rerank` 是否為 `'none'`。
- **教訓**：可選功能（feature flag）的 env 處理必須在 guard 後執行，不能假設功能啟用才會有那些 env 變數。

---

### Bug 19: AUTO_CAPTURE_RUNTIME_WRAPPER 行首 boilerplate 未被剝除（P2）

- **問題**：stripLeadingRuntimeWrappers 在某些情況下保留了 runtime wrapper 行首的 boilerplate（如「Results auto-announce to your requester.」「Do not use any memory tools.」），而非一并移除。
- **根因**：boilerplate lines 未被納入 strip 規則，只是 strip 了 wrapper prefix line。
- **修復**：在 stripLeadIn 為 true 時，一並移除符合 `AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE` 的行。
- **教訓**：文字清理規則容易有 edge case；建議建立一個「清理前 → 清理後」的 golden file test cases，防止 regression。

---

### Bug 20: retrieveWithTrace 未 forwarding source 參數（Minor）

- **問題**：`retrieveWithTrace()` 呼叫 `hybridRetrieval()` 時未傳遞 `source` 參數，導致 trace/debug 模式的檢索結果與實際手動 recall 行為不一致。
- **根因**：新增 `retrieveWithTrace` 時未完整對齊原有 `hybridRetrieval` 介面。
- **修復**：forward `source` 參數。
- **教訓**：wrapper function 必須完整 forward 所有參數；建立 wrapper 時要逐一對照原 function signature，避免日後無意中破壞預設行為。

---

## 流程坑

### 坑 1: Sub-agent 擅自 push 到 remote

- **問題**：Sub-agent 在 local 修改後自行執行 `git push`，將未經 review 的程式碼上傳到 remote。
- **教訓**：Sub-agent 應只在 local 工作，嚴禁未經主agent/user確認就上傳。開發用的 feature branch 應視為「草稿」，未 merge 前不應出現在 remote history。
- **預防措施**：在 sub-agent 的工作規範中明確寫入「只 local commit，不 push to remote」；或限制 sub-agent 的 git 許可權，移除 push 權限。

---

### 坑 2: OpenCode API model 參數格式錯誤

- **問題**：呼叫 OpenCode API 時 model 參數格式錯誤（如多了 namespace 前綴或格式不符），導致 API 回傳 400/422。
- **教訓**：在叫用第三方 API 前，應先查閱該 API 的 schema 定義，確認 model field 的正確格式（如 `provider/model-name` 或只給 `model-name`）。
- **預防措施**：建立一個 API schema cheat sheet，放在 workspace 文件中；或先對 staging endpoint 做一次 smoke test 確認 request format。

---

### 坑 3: PowerShell 變數展開與 `&&` 語法問題

- **問題**：在 Windows PowerShell 環境執行包含 `&&` 的命令時，PowerShell 將 `&&` 視為語法錯誤（`&&` 在 PowerShell 中不是有效的語句連接符）；`$` 字元也可能被錯誤展開。
- **教訓**：跨平台（Linux/macOS/Windows）指令要先確認 shell 語法差異；bash 的 `&&` 在 PowerShell 應改為 `;` 或 `-and`；`$` 在 PowerShell 字串中要小心處理。
- **預防措施**：在指令碼文件或 SKILL.md 中註明各平台的語法差異；或在 script template 中標註「確認你使用的 shell 類型」。

---

### 坑 4: PR review 過程中多個 fix commit 散落在多個獨立 branch/時間點

- **問題**：從 initial feature commit 到最終穩定版，中間經歷了 11 個 fix commits，散落在不同時間、不同的 sub-agent session，不容易追蹤全貌。
- **教訓**：大型 PR 建議用 `git worktree` 或明確的 branch 策略，避免在同一 branch 反覆 commit 追蹤混亂；或用 PR description 維護一個 "fix changelog" 表格。
- **預防措施**：建立 PR template，強迫在每個 fix commit 後更新 changelog；或使用 GitHub 的「被修復的 issue」功能，讓每個 bug commit reference 到對應的 issue。

---

## 技術債

1. **Hook 觸發順序文件化**：目前 hook 的觸發順序（before_prompt_build → agent_end → feedback → session_end）是靠程式碼 trial-and-error 確認的，應該建立一份 Hook Order 文件並寫入 `docs/`。
2. **shared state（Map）操作的 interface 約束**：`pendingRecall` Map 同時被多個 hook 寫入，缺乏類型安全的 interface 約束。建議用 TypeScript class 包裝，所有寫入都通過 class methods，並註明誰 call 什麼。
3. **counter/score 的「單一寫入點」原則未文件化**：bad_recall_count、importance weighting 等共享狀態缺乏「只能在一處修改」的約定，導致 double-increment 等 bug。
4. **Injection format vs. Detection format 的同步機制**：auto-recall injection format（`[category:scope]` summary text）與 feedback detection format（`isRecallUsed` 檢查清單）需要同步演化，目前靠人工比對容易出錯。建議在程式碼中以 constant/export 的方式明確定義 injection format，讓 detection code 直接 import 使用。
5. **Regex 程式碼的 invisible char 檢測**：建議加入 pre-commit hook（使用 `git diff --check` 或 `zizhi/no-invisible`之類的 linter）防止 literal backspace 或其他 invisible 字元進入程式碼。
