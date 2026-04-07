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
