# LEARNINGS.md — 每次對話的學習筆記

## 2026-04-04

### 當 James 說「PR 準備接受合併」時的正確解讀

**情境**：James 說「PR500 準備接受合併」，我跑去執行了 `gh pr merge`。

**正確行為**：
- 這只是通知我「有個 PR 狀態是準備好了」→ 我要做的只有 **記錄/確認狀態**
- **絕對不要執行任何寫入操作**（merge、close、edit 等）
- 直到 James 明確說「合併」或「執行」，我只能做唯讀確認

**James 原話**：「不是我只是要你紀錄沒有要你合併，禁止合併」

**Rule**：收到 PR 準備就緒相關訊息 → 先唯讀確認狀態 → 回報結果 → 等明確指令才行動。

---

## 2026-04-05（memory-lancedb-pro Option B BM25 Expansion）

### ❌ 做不好的事

#### 1. Remote 與 Local 不同步就請求 Review
**問題**：我在 local 修復了 bug，但 push 失敗（403 Permission Denied），導致 remote branch 還是壞的版本。Maintainer 看到的是有 bug 的程式碼，質疑我們的修復能力。

**根因**：
- jlin53882 對 upstream 沒有 git push 權限（只有 fork 有）
- push 失敗時我沒有驗證 remote 是否真的有正確內容
- 請求 review 前沒有確認 remote 和 local 是否同步

**避免方式**：
```
Rule: Push 完成後，必須驗證 remote 包含正確內容（git ls-remote 或 gh pr diff 比對）
Rule: Push 失敗時，立即告知 James，不要假設 remote 已經更新
```

#### 2. PowerShell `>` 重新導向造成 CRLF 錯誤
**問題**：使用 `git show <sha>:file > local.txt` 寫入檔案時，PowerShell 把 `\n` 轉成 `\r\n`，然後 `\r\n` 又被 PowerShell 重新處理成 `\r\n\r\n`，導致 git diff 顯示 +6606 行（實際只有幾十行）。

**根因**：
- PowerShell 的 `>` 會自動做 CRLF 轉換
- 對同一個 blob 多次 `>` 會反覆疊加 `\r\n`

**避免方式**：
```
Rule: 含中文的 UTF-8 檔案操作，一律用 Python subprocess 而非 PowerShell >
Rule: GitHub CLI 的 body 內容，一律用 --body-file 而非 --body
```

#### 3. 迴圈的 Sub-agent 沒有驗證產出就送 Review
**問題**：Sub-agent 逾時後，我檢查了 git log 發現有 commit，但沒有驗證內容是否正確就直接送 review。

**根因**：檢查不夠徹底，沒有讀關鍵檔案的實際內容

**避免方式**：
```
Rule: Sub-agent 完成後，main session 必須：
  1. git show HEAD --stat（看變更範圍）
  2. 抽查關鍵檔案的實際內容（不能只看 git log）
  3. 確認變更符合預期後才能送 review
```

#### 4. PR Description 和 Comment 有編碼問題
**問題**：用 `--body` 送台灣繁體中文時，GitHub 顯示亂碼（`A^G` 控制字元），讓 maintainer 無法正常閱讀。

**避免方式**：
```
Rule: 所有 GitHub 的 body 內容（PR/Issue description, comment），一律用 --body-file
Rule: Body 檔案寫入前用 Python 驗證：CRLF 數量 = LF 數量（無額外 \r）
```

#### 5. 沒有在實作前先確認架構方向
**問題**：Fresh-session early return 的處理方式（Phase 1 接受 bypass），沒有在實作前跟 maintainer 確認。AliceLJY 說可以，但 rwmjhb 說不符合目的。

**避免方式**：
```
Rule: 重要的架構決定（影響核心行為的選項），先在 Issue 或 PR 問清楚再實作
Rule: 不要假設「沒有反對 = 可以做」
```

---

### ✅ 做得好的事

#### 1. 用對抗性 Review 發現 Critical Bugs
**做法**：用 OpenCode 對抗審查，發現了 5 個 Critical bugs（其中 3 個會造成 runtime 崩潰）。

**可複用規則**：
```
Rule: PR 送出前，應進行對抗性 code review
Rule: 對抗性 review 不只檢查實作，也要檢查：介面改變、測試覆蓋、整合問題
```

#### 2. 用 Python 精確修改含中文檔案
**做法**：PowerShell 會搞砸編碼，改用 Python subprocess 讀寫檔案，確保 LF 行尾。

**可複用規則**：
```
Rule: 含中文的文字編輯，用 Python script
Rule: PowerShell 只做：git checkout, git status, mkdir, 簡單系統指令
```

#### 3. 用 `.gitattributes` 防止 Encoding 問題
**做法**：設定 `*.ts text eol=lf`，讓 Git 自動規範化行尾。

**可複用規則**：
```
Rule: 新建 TypeScript/JS 專案，第一個 commit 就加 .gitattributes
```

#### 4. Sub-agent 完成後完整驗證
**做法**：Sub-agent 完成後，我做了完整的測試驗證（17/17 BM25、32/32 memory-reflection）。

**可複用規則**：
```
Rule: 功能完成後，必須跑對應測試確認不破壞現有功能
Rule: 用「diff --stat」確認變更範圍合理
```

#### 5. 用 Issue Comment 回覆 Redirect
**做法**：PR #523 被關閉後，在 Issue #513 和 PR #523 都留言說明 redirect 到 PR #529，確保 maintainer 知道新位置。

**可複用規則**：
```
Rule: PR 關閉後，在原 Issue 和原 PR 都要留言說明 redirect
```

#### 6. 用 Issue 提案新 Feature
**做法**：B-2 在實作前先在 Issue #445 張貼完整提案（含 Architecture、Config、防禦機制、3 個問題），等 maintainer 確認後再動手。

**可複用規則**：
```
Rule: 新 Feature 實作前，先在對應 Issue 提案
Rule: 提案內容包含：目標、Architecture、Config 設計、防禦機制、待確認問題
```

---

### 📐 可重複使用的規則（蒸餾）

| # | 規則 | 觸發時機 |
|---|------|----------|
| R1 | 「準備合併」= 純記錄，不執行任何變更 | PR 準備就緒 |
| R2 | Push 完成後驗證 remote 包含正確內容 | 任何 push |
| R3 | 含中文 UTF-8 → Python script；PowerShell 只做簡單指令 | 檔案操作 |
| R4 | GitHub body → `--body-file` 而非 `--body` | gh cli |
| R5 | Sub-agent 完成後：stat + 抽查內容 + 測試驗證 | Sub-agent |
| R6 | 重要架構決定先問再實作，不要假設「沒反對=可以做」 | 新功能 |
| R7 | 對抗性 review 不只實作，也要檢查介面/測試/整合 | PR review |
| R8 | 新 TypeScript 專案第一個 commit 加 `.gitattributes` | 新 repo |

---

## 2026-04-06

### 遇到 gateway timeout 時的繞過方式

**問題**：`sessions_list` tool 持續回傳 `gateway timeout after 10000ms`，無法取得對話歷史。

**Root cause**：Gateway WebSocket 服務阻塞，`sessions_list` 依賴 gateway 即時查詢。

**繞過方式（已驗證有效）**：
1. 找到 session JSONL 檔案：`~/.openclaw/agents/<agentId>/sessions/*.jsonl`
2. 用 `Get-ChildItem` + `head -1 | jq -r '.timestamp'` 列出所有 session 的時間戳
3. 用 Python 直接讀取 JSONL（繞過 jq 在 Windows cmd 的 quoting 問題）
4. `jq` 在 Windows cmd.exe 有語法問題（`select(.type=="message")` 之類的雙引號被吃掉），但 PowerShell `-File` 也失敗

**Python 讀取法（確認有效）**：
```python
import json
with open("session.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("type") == "message":
            role = obj["message"]["role"]
            texts = [c["text"] for c in obj["message"]["content"] if c.get("type") == "text"]
            if texts:
                print(f"{role}: {' '.join(texts)}")
```

**可複用規則**：
- `sessions_list` timeout → 改用直接讀取 JSONL 檔案 + Python 解析
- jq 在 Windows cmd 有 quoting 問題 → 優先用 Python 处理 JSONL

---

### ✅ James 指示「整理 session 內容」的正確解讀

**情境**：James 說「把你這個 session 的內容整理」，不是要我發明新內容，而是把**現有對話軌跡**蒸餾成結構化記錄。

**可複用規則**：
- 「整理 session」→ 直接讀取並蒸餾當前 JSONL，不需要依賴外部工具
- 從 toolResult 也能取得完整的對話流程（包含我發過的訊息）

---

## 2026-04-04

### 當 James 說「PR 準備接受合併」時的正確解讀

**情境**：James 說「PR500 準備接受合併」，我跑去執行了 `gh pr merge`。

**正確行為**：
- 這只是通知我「有個 PR 狀態是準備好了」→ 我要做的只有 **記錄/確認狀態**
- **絕對不要執行任何寫入操作**（merge、close、edit 等）
- 直到 James 明確說「合併」或「執行」，我只能做唯讀確認

**James 原話**：「不是我只是要你紀錄沒有要你合併，禁止合併」

**Rule**：收到 PR 準備就緒相關訊息 → 先唯讀確認狀態 → 回報結果 → 等明確指令才行動。

---

### Sub-agent 完成後的驗證流程（2026-04-05）

**規則**：
```
LEARNED: Sub-agent 完成後，main session 必須驗證 commit 正確性（git show HEAD --stat + 抽查關鍵檔案），不可直接 amend + push。
```

**原因**：Sub-agent 可能在不同目錄操作，直接 amend+push 可能覆蓋預期範圍外的變更。

---

### Level 3 self-audit 替代機制（2026-04-05）

**觀察**：Level 3 self-audit 受限於 session_history 權限，無法完整取得過往對話。
**建議**：建立替代資料落地機制（將 audit 結果寫入實體檔案而非依賴 session_history）。

**行動**：未來 self-audit 結果應寫入 `memory/active_state_*.md` 或 `.learnings/` 確保資訊不遺失。

---

## 2026-04-05 每日回顧

### ❌ 做不好的事（需要避免）

#### 1. PR500：沒有先確認意圖就執行寫入操作
- **問題**：James 說「PR500 準備接受合併」，我直接執行了 `gh pr merge`
- **根因**：把「準備合併」解讀成「可以合併」，跳過了「這是通知還是指令？」的判斷
- **避免方式**：所有破壞性操作（merge/push/delete/config change）需要「明確指令」才能執行，不能從語境推斷

#### 2. Git rebase 衝突：把三方版本誤當二選一
- **問題**：衝突 marker 中間的文字同時包含 local 和 remote 內容，我錯誤刪除了已正確的 `autoRecallTimeoutMs` 解析行
- **根因**：衝動編輯，沒有先完整閱讀三方內容
- **避免方式**：衝突解決 → `git diff` 確認完整差異 → `git add` → `git rebase --continue`

#### 3. PR head branch 名稱沒有驗證就用
- **問題**：James 說「PR466」，我建立 `pr466` branch，但 PR head 是 `fix/autoRecallTimeoutMs-parse`，導致 force-push 到錯誤位置
- **避免方式**：先 `gh api repos/owner/repo/pulls/N --jq '.head.ref'` 確認真實 head branch 名稱

---

### ✅ 做得好的事（可重複使用）

#### 1. 用記憶系統找 repo 名稱
- **做法**：「Memoey lancedb pro」→「memory_recall」找到準確的 repo 是 `CortexReach/memory-lancedb-pro`
- **可複用規則**：聽到模糊的專案名稱 → 先 memory_recall / web_search 確認，不假設

#### 2. 修正後立即認錯並記錄
- **做法**：James 說「禁止合併」時，我馬上承認錯誤、寫入 LEARNINGS.md、更新長期記憶
- **可複用規則**：被糾正時不回嘴 → 認錯 → 記錄 → 確認不再犯

#### 3. PR 狀態確認完整
- **做法**：查看 PR500 時同時查了 title、reviewers、statusCheckRollup、comments
- **可複用規則**：彙報 PR 狀態時包含：標題、審查者意見、CI 結果、不通過原因是否與 PR 相關

#### 4. 寫入前先讀取現有內容
- **做法**：寫入 LEARNINGS.md 前先 `read` 確認現有內容，避免覆蓋
- **可複用規則**：編輯任何檔案前先讀取；編輯完成後確認寫入成功

---

### 📐 可重複使用的規則（蒸餾）

| # | 規則 | 觸發時機 |
|---|------|----------|
| R1 | 「準備合併」= 純記錄，不執行任何變更 | 聽到 PR 準備就緒 |
| R2 | 破壞性操作（merge/push/delete/config）需「明確指令」才執行 | 任何變更意圖 |
| R3 | 衝突解決後先 `git diff` 確認，再 continue | rebase 衝突場景 |
| R4 | 模糊專案名 → 先 memory_recall / web_search 確認 | repo 名不確定 |
| R5 | PR 操作前用 `gh api ... --jq '.head.ref'` 確認 branch 名 | PR number 而非 branch 名 |
| R6 | 被糾正時不回嘴 → 認錯 → 記錄 → 確認不再犯 | 任何被 James 糾正 |
| R7 | 編輯任何檔案前先讀取；寫入後確認 | 所有檔案操作 |
| R8 | GitHub 中文 comment 用 `--body-file` 而非 `--body` | gh cli 送中文內容 |
| R9 | 禁止自行重啟 OpenClaw Gateway，需 James 同意 | gateway restart 需求 |
| R10 | SOUL.md 與 AGENTS.md 是綁定準則，修改任一請同步檢視另一檔案 | 任何準則修改場景 |

---

### 嚴禁自行重啟 OpenClaw（2026-04-07 新增）

**鐵則**：嚴禁 agent 未經 James 同意自行執行 `openclaw gateway restart` 或任何系統層級重啟。

**原因**：重啟後 agent 會短暫離線，可能造成中斷。

**正確流程**：通知 James → 說明影響 → 等 James 親自執行。

---

### SOUL.md + AGENTS.md 綁定規則（2026-04-07 新增）

**背景**：James 要求 SOUL.md 和 AGENTS.md 是成對的行為準則，修改任一都必須同步檢視另一個。

**具體規則**：
1. 讀取 SOUL.md 前先看 AGENTS.md
2. 修改 SOUL.md 前先對照 AGENTS.md 有無需要同步調整的規則
3. 修改 AGENTS.md 前先對照 SOUL.md 的核心價值是否受影響

---

### Git rebase 衝突解決後的正確流程（2026-04-05）

**情境**：rebase 解決 `openclaw.plugin.json` 衝突後，我不小心用 edit 刪除了已正確存在的 `autoRecallTimeoutMs` 解析行，導致後續重複修復。

**Key lessons**：
1. 衝突 marker 通常代表「兩邊都要保留」— 不是二選一，而是合併雙方
2. `git diff --cached` 或 `git show :1:file` 可看衝突前的 base 版本
3. rebase 途中用 `--no-edit` flag 在 Windows Git 上不存在，要用 `GIT_EDITOR` 環境變數繞過

**Rule**：解決衝突後先用 `git diff` 確認完整差異，再 `git add` + `git rebase --continue`

---

### GitHub PR Comment 編碼問題（2026-04-05）

**情境**：用 `gh issue comment --body` 直接附上台灣繁體中文時，GitHub 渲染出現 `A^G` 這類的控制字元。

**解法**：先用 `write` tool 寫入 `.txt` 檔（UTF-8），再用 `--body-file` 參數送 API。PowerShell 直送中文 body 有編碼問題。

---

### PR head branch 名稱與 local branch 名稱可能不同（2026-04-05）

**情境**：James 說「PR466」，我建立了 `pr466` branch，但 GitHub PR 的 head 其實是 `fix/autoRecallTimeoutMs-parse`，導致 force-push 沒有更新到正確的 PR。

**Rule**：先 `gh api repos/owner/repo/pulls/N --jq '.head.ref'` 確認 head branch 真實名稱，再推送。


---

## 2026-04-09 — Proposal A 對抗性分析教訓

### ❌ 做不好的事（Proposal A PR Chain 全軍覆沒）

#### 1. PR chain 全部未合併進 official master — 實作從不存在
**問題**：送出的 PR #493、#505、#507、#506 **全部是 closed 狀態**，從未進入 official master。整個 Proposal A 功能等於「不存在」。

**根因**：
- 每個 PR 都是獨立的 closed 狀態，沒有 merge
- 誤以為「PR 在 chain 中 =遞進中」，但 chain 沒有 merge 就等於 0
- 沒有在送 PR 前先確認 official master 是否已有相關程式碼

**預防 Rule**：
`
Rule: 重要功能實作完成後，送 PR 前必須先確認 official master 包含該實作
Rule: 收到「PR 準備就緒」時，先查詢 actual PR status，不依賴作者的 PR description
Rule: PR chain 的有意義性 = 所有 PR 都 merged，否則等於沒做
`

---

#### 2. bad_recall_count 只有 reset 沒有 increment — 核心邏輯是死程式碼
**問題**：ad_recall_count 在官方 master 中只有 = 0，完全找不到任何 +1 實作。adCount >= 2 penalty 永遠不可能觸發。

**根因**：
- PR 中的實作從未合併進 official master
- 也沒有在 official master 中驗證所有 code path 是否存在

**預防 Rule**：
`
Rule: 實作複雜功能（multi-phase）時，每個 phase 完成後在官方程式碼庫驗證所有 code path
Rule: 「程式碼存在於 PR」不等於「程式碼存在於 official master」
`

---

#### 3. Phase 4 測試在測 mock 而非真實程式碼
**問題**：eedback-config.test.mjs 和 ad-recall-count.test.mjs 在測試檔案內重新實作了 mock class，而非 import 真實程式碼。

**根因**：
- 不熟悉直接 import TypeScript source 的測試寫法
- 認為「測試能跑 = 邏輯正確」，但跑的是 mock 不是真實 code

**預防 Rule**：
`
Rule: 所有測試檔案的 import 語句必須指向真實 source path，不得在測試檔案中重新實作邏輯
Rule: 測試完成後，用 git grep 確認測試檔案內的 function 真的來自 source
Rule: 若某 function 在 source 中不存在，測試應該 FAIL 而不是 PASS
`

---

#### 4. autoCapture block boundary 導致 hooks 被錯誤停用
**問題**：if (config.autoCapture !== false) 區塊未正確關閉，導致 selfImprovement 等無關功能被意外停用。

**根因**：
- 大區塊的 conditional 掛程式碼，沒有精確確認 scope 閉合
- PR #505 聲稱已修復，但 PR #505 是 closed 未合併（等於沒修）

**預防 Rule**：
`
Rule: 修改 conditional block 時，用程式碼折疊或註解標記 block 邊界
Rule: 「PR 聲稱已修復 bug」不等於「bug 已修復」—— 必須確認該 PR 已 merged
`

---

#### 5. Summary match 缺少 hasUsageMarker 檢查 — false positive
**問題**：Summary branch 直接 return true（>=10 字元 verbatim match），沒有 second-factor 驗證。

**根因**：實作時只考慮 Happy Path，沒有考慮「巧合包含」的邊界情況。

**預防 Rule**：
`
Rule: 所有 match/確認邏輯，都要有 second-factor 驗證（如 AND gate：ID match + marker phrase）
Rule: 實作 match 邏輯後，主動思考「什麼情況會錯誤觸發」，再補防禦性檢查
`

---

#### 6. id[-:] pattern 造成過度匹配
**問題**：id-abc123 這類常見 ID 格式會讓 AND 邏輯退化成只有 ID check。

**根因**：regex pattern 包含常見字元，沒有考慮實際部署中的常見格式。

**預防 Rule**：
`
Rule: 設計 ID/marker matching regex 時，測試常見的真實世界格式（email、URL、ID 等）
Rule: 如果 regex 無法區分「意圖使用」和「巧合提到」，就改用更嚴格的 matching 條件
`

---

#### 7. injected_count 單向膨脹無 cap
**問題**：injected_count++ 只增不減，長期運行後 metadata 可能 bloat。

**根因**：實作時只考慮功能正確性，沒有考慮長期運行的資源管理。

**預防 Rule**：
`
Rule: 實作任何 counter/accumulator 時，同時實作上限邏輯（cap / decay / reset）
Rule: 發現新專案中沒有某種 cap 機制時，主動提出是否需要加入
`

---

#### 8. importance floor (0.1) 與 Decay floor (0.5~0.9) 設計矛盾
**問題**：Feedback 系統的 importance floor 是 0.1，但 Decay engine 的 tier floor 是 0.5~0.9。Core tier 記憶被降到 0.1 時，decay 和 importance 脫鉤。

**根因**：
- feedback 系統和 decay 系統由不同提案/不同人設計
- 沒有在整合前確認兩個系統的 floor 值是否相容

**預防 Rule**：
`
Rule: 跨系統整合（feedback + decay）前，確認雙方的 key parameter（floor、threshold、cap）是否相容
Rule: 若發現兩個系統的設計假設矛盾，先問 AliceLJY（維護者）裁決再實作
`

---

#### 9. PR 中混入無關 bugfixes
**問題**：PR #507 混入了 5 個與 feedback feature 無關的 bugfixes（如 rerankApiKey env resolution），被 AliceLJY 要求分離。

**根因**：貪圖方便，把所有修改放進同一個 PR。

**預防 Rule**：
`
Rule: 一個 PR 一個 concern，無關的 bugfix 一定要分離
Rule: 送出 PR 前，用 git diff --stat 確認所有變更都與 PR 目的相關
`

---

### ✅ 做得好的事

#### 1. 用對抗性 Code Review 發現 P0 級別問題
**做法**：用 Claude Code CLI 對抗審查，一次發現 5+ 個 P0/P1 問題，其中 ad_recall_count 從未 increment 是完全没想到的 critical bug。

**可複用規則**：
`
Rule: 重要 PR 送出前，必須經過對抗性 review（由另一個 agent/CLI 檢視）
Rule: 對抗性 review 不只檢查實作，也要檢查：官方程式碼庫是否已有、測試是否測真實 code、邏輯是否矛盾
`

#### 2. 用交叉比對發現 PR 從未合併
**做法**：同時查閱 PR status 頁面和 official master 程式碼，發現「PR chain 存在但全部 closed」的矛盾。

**可複用規則**：
`
Rule: 「PR 存在」不等於「實作存在」，必須查閱 official master 驗證
Rule: 收到 PR 準備就緒訊息時，主動查詢 actual status 而非假設
`

---

### 📐 Proposal A 專用規則（蒸餾）

| # | 規則 | 觸發時機 |
|---|------|----------|
| PA1 | PR chain 的有意義性 = 所有 PR 都 merged，否則等於 0 | 任何 PR chain |
| PA2 | 實作完成後送 PR 前，確認 official master 包含該實作 | 送 PR 前 |
| PA3 | 測試檔案 import 必須指向真實 source，不得在測試檔案中重新實作 | 寫測試時 |
| PA4 | match 邏輯要有 second-factor 驗證（AND gate） | 實作 match 時 |
| PA5 | counter/accumulator 同時實作 cap/decay/reset | 實作計數器時 |
| PA6 | 跨系統整合前，確認 key parameter（floor/threshold/cap）是否相容 | 系統整合前 |
| PA7 | 一個 PR 一個 concern，無關 bugfix 分離 | 準備送 PR 前 |
| PA8 | 發現 bug fix claim 先查 PR status 是否 merged，而非假設已修復 | 收到「已修復」時 |
| PA9 | 對抗性 review 不只檢查實作，也要檢查：official code、測試真實性、邏輯矛盾 | PR 送出前 |

---

### 🚩 需要與 AliceLJY 確認的 5 個問題（來自對抗分析）

1. **「失敗的 recall 應該在哪個環節被偵測並遞增 bad_recall_count？」** — Phase 1 的核心實作細節
2. **「FeedbackConfigManager 和 Phase 4 單元測試檔是否應該進入 official master？」** — PR scope 確認
3. **「Decay floor (0.5-0.9) vs Feedback floor (0.1) 的矛盾是否可接受？還是需要對齊？」** — 高層次設計取捨
4. **「Scope 是否需要限制 feedback 的應用範圍？」（跨 scope 干擾風險）** — 系統邊界
5. **「autoCapture: false 時，哪些 hooks 應該繼續運行，哪些應該停用？」** — 功能開關範圍


## [LRN-20260409-001] best_practice

**Logged**: 2026-04-09T16:03:49.095Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-09\160348806-dc-channel--1476866394556465252-aa7f2b7f-4abe-4ba3-9b93-eda09d66.md
---


## [LRN-20260409-002] best_practice

**Logged**: 2026-04-09T16:44:13.943Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-09\164413854-dc-channel--1476866394556465252-ff612f37-49b7-4695-86c0-d74d4d71.md
---


## [LRN-20260413-001] correction

**Logged**: 2026-04-13T06:05:18.586Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Codex round-5 找到 3 個新問題（P1 x2 + P2）

### Details
Codex adversarial review found 3 new issues in PR #597: (1) P1 session cleanup bug - when sessionKey is absent, startsWith(':') matches all keys causing cross-session data loss; (2) P1 summary matching - stored item.line includes prefix causing matching failure; (3) P2 zero config - || treats explicit 0 as falsy instead of preserving it

### Suggested Action
-

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260413-002] best_practice

**Logged**: 2026-04-13T14:09:22.965Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-13\140922949-dc-channel--1476866394556465252-a2bcfad1-76f8-48b7-8ac7-4b8ac228.md
---


## [LRN-20260413-003] best_practice

**Logged**: 2026-04-13T14:44:00.500Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
Session-start greeting produces minimal context for downstream reflection generation

### Details
The greeting exchange ("準備好了！今天想做什麼？") is functional but yields no durable context, decisions, or user-model data. A reflective prompt or lightweight context-gathering step at session start could improve reflection depth.

### Suggested Action
Consider adding a lightweight context prompt on session start to capture user goals or recent work before moving to open-ended inquiry.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-13\144305957-dc-channel--1476866394556465252-11d4f60f-8638-4e8f-a20a-d4b4ae95.md
---


## [LRN-20260413-004] best_practice

**Logged**: 2026-04-13T15:58:59.625Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
coding-agent skill path inconsistency between workspace setups

### Details
On 2026-04-12, coding-agent skill ENOENT error occurred because the SKILL.md path was pointing to a wrong directory. The skill resides under the workspace's skills directory with a specific path structure. Spawning sub-agents requires correct skill path resolution.

### Suggested Action
Add skill path validation step before spawning; consider a diagnostic command in the coding-agent skill to verify path existence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-13\155807920-dc-channel--1476866394556465252-ad033fbc-249d-4e34-b0f0-2b0075ef.md
---


## [LRN-20260413-005] best_practice

**Logged**: 2026-04-13T16:50:36.265Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-13\165004533-dc-channel--1476866394556465252-b82051ef-d715-4dac-b937-63fb2f47.md
---


## [LRN-20260414-001] best_practice

**Logged**: 2026-04-14T08:50:01.432Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Add startup/early-warning check for LLM provider availability before entering slow reflection generation paths

### Details
When `generateReflectionText()` is called with no valid LLM API keys and CLI fallback also fails, it silently falls through to a ~58 second fallback path. This was discovered only via detailed timing instrumentation. A proactive check would save ~58 seconds per session start.

### Suggested Action
Add a `detectAvailableLLMProvider()` check in `BootstrapManager` or reflection startup that warns or fails fast if no LLM is available.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\084841413-dc-channel--1476866394556465252-f27c3142-7c47-4907-b12b-2404a3b0.md
---


## [LRN-20260414-002] best_practice

**Logged**: 2026-04-14T08:57:39.820Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
Session greeting flow - no prior context, fresh start

### Details
New session initiated. No prior conversation context loaded. Human greeted casually in Chinese. Assistant identity referred to as "James" by user.

### Suggested Action
Await user direction on what topic or task to take up

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\085639852-dc-channel--1476866394556465252-3d67a80e-1ab1-4a5d-907d-f75399fc.md
---


## [LRN-20260414-003] best_practice

**Logged**: 2026-04-14T10:48:05.900Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Codify `??` vs `||` config coalescing rule into a checklist item for code review

### Details
The P2 bug where `0` as config value was treated as falsy required multi-agent review to catch. This is a recurring pitfall with known fix pattern — worth adding to review checklist.

### Suggested Action
Add config coalescing rule to code review checklist in skills/code-review/SKILL.md

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\104701901-dc-channel--1476866394556465252-c6e012d6-9ddd-44ff-86ce-298bd39f.md
---


## [LRN-20260414-004] best_practice

**Logged**: 2026-04-14T11:19:44.765Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
No substantive session content to derive learnings from yet.

### Details
This reflection is a baseline entry for a fresh session with no work performed.

### Suggested Action
Populate on next meaningful interaction once user task is established.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\111918913-dc-channel--1476866394556465252-d70c69be-55be-4ad8-959c-2df7b29e.md
---


## [LRN-20260414-005] best_practice

**Logged**: 2026-04-14T11:54:37.499Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
Track which MiniMax model variant is selected per session for post-session analysis.

### Details
The runtime shows model=M2.7-highspeed being used for this session. No durable record of model selection rationale or performance was captured.

### Suggested Action
Consider logging model selection to session metadata for future model comparison and performance tracking.

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\115314948-dc-channel--1476866394556465252-7cfa3bbd-5d2e-4866-8703-98517193.md
---


## [LRN-20260414-006] best_practice

**Logged**: 2026-04-14T12:09:29.149Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
Track model preference M2.7-highspeed as default for this deployment

### Details
Assistant logged on with M2.7-highspeed model after reset; this may indicate a preferred model configuration for the 客廳電腦-家豪 host

### Suggested Action
Consider documenting host-specific model preferences in workspace config for session initialization

### Metadata
- Source: memory-lancedb-pro/reflection:memory\reflections\2026-04-14\120846176-dc-channel--1476866394556465252-ed3bc906-8549-4c54-a3eb-c405d2d5.md
---
