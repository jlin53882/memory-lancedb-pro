# AGENTS.md — 技術操作規範

> 本檔案定義具體的技術操作流程與決策規則。
> 與 SOUL.md 配對使用，修改其一請同時檢視另一檔案。

---

## 版本與環境

| 項目 | 版本 |
|------|------|
| Flet（桌面翻譯工具） | 0.82.2 |
| Python 測試 | `uv run pytest -q`（需在專案目錄執行）|
| 預設模型 | minimax-portal/MiniMax-M2.7 |
| 備用模型 | minimax-portal/MiniMax-M2.5（當 timeout）|

---

## 鐵則（不可違背）

### R1｜破壞性操作需明確指令
- 觸發詞：「準備合併」「可以動手」「執行」
- 正確行為：唯讀確認 → 回報狀態 → 等 James 說「執行」才行動
- 涵蓋：`merge`, `push --force`, `delete`, `gateway restart`, `config change`

### R2｜Sub-agent 完成後必須驗證
- 完成後執行 `git show HEAD --stat` + 抽查關鍵檔案
- 不可直接 `git amend` 或 `git push`
- 確認變更範圍符合預期後才能推送

### R3｜衝突解決流程
1. 衝突 marker（三方版本）不是二選一，而是合併雙方
2. 解決後：`git diff` 確認完整差異
3. `git add` + `git rebase --continue`
4. 確認與 SOUL.md 綁定規則無衝突

### R4｜PR 操作前確認 branch 名稱
- 收到 PR number（而非 branch 名）時，先：
  ```
  gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.ref'
  ```
- 確認 head branch 真實名稱後再操作

### R5｜GitHub 中文內容用 --body-file
- 送中文 comment 時，先 `write` tool 寫入 UTF-8 檔案
- 用 `gh ... --body-file path.txt` 而非 `--body "中文"`
- 避免控制字元渲染問題

### R6｜寫入前必讀
- 編輯任何檔案前先 `read` 現有內容
- 寫入後確認成功
- 避免覆蓋 James 的重要內容

### R7｜Gateway 重啟需 James 同意
- 嚴格禁止自行重啟 OpenClaw Gateway
- 先通知 James（含「agent 會暫時離線」預警）
- 等 James 親自執行重啟指令

### R8｜模糊專案名先確認
- repo 名稱不確定時，用 `memory_recall` 或 `gh search repos` 確認
- 不假設，不猜測

### R9｜Sub-agent 任務設計規則
- 任務 prompt 必須明確定義 scope，不能模糊帶過
- 任務 prompt 必須包含「工作開始前檢查清單」與「完成後驗證清單」
- 任務 prompt 必須告知 sub-agent：「同一方法失敗 3 次就停下來回報」
- 任務 prompt 必須告知 sub-agent：「不確定就問，不要自己假設」
- 任務 prompt 的禁止事項必須明確列出（不跳測試、不執行破壞性操作等）
- 參考：`docs/SUBAGENT_TASK_TEMPLATE.md`

### R10｜Sub-agent 派工時的紀律
- 派工前先確認 sub-agent 的工作目錄是否正確
- 派工後追蹤 sub-agent 的進度，不要假設它會自己完成
- sub-agent 完成後 main session 必須驗證（git status + 抽查 commit）
- 不要讓 sub-agent 自己 amend 或 push，main session 確認後再操作

### R11｜Rebase 前先確認 upstream
- schema / config 檔案 rebase 前，先確認 upstream/master 是否已有相同內容
- 指令：`git show upstream/master:{path} | grep {keyword}`
- 如果 upstream 已有 → 視情況 skip 或 rebase，否則可能白做工

### R12｜模糊指令先問清楚
- 收到的指令有兩種以上可能的解讀時，先停在原地問清楚
- 不要自己假設意圖然後蠻幹

### R13｜含中文 UTF-8 強制用 Python
- 含中文的文字檔操作（讀寫 .md/.json/.txt 等），一律用 Python subprocess
- PowerShell `>` 重新導向會搞砸 UTF-8 和 CRLF，禁止用於文字檔操作
- PowerShell 只做：git checkout, git status, mkdir, 簡單系統指令

### R14｜Push 完成後驗證 remote 內容
- Push 完成後必須確認 remote branch 包含正確內容
- 驗證方式：`gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.ref'` 確認 head branch
- Push 失敗時立即告知 James，不要假設 remote 已經更新

### R15｜Sub-agent 監督檢查清單
Sub-agent 完成後，main session 必須依序執行：
1. `git show HEAD --stat`（看變更範圍）
2. 抽查關鍵檔案的實際內容（不能只看 git log）
3. 確認變更範圍符合預期
4. 才能送 review 或 push

---

### R16｜複雜 JSON 衝突處理
- 複雜 JSON 衝突 → 用 Python script 處理（`json.load()` 驗證 + 字串替換）
- 每次編輯後立即驗證：`python -c "import json; json.load(open('file.json'))"`
- 不要用 PowerShell `Select-String` 對大 JSON 做關鍵字比對（會誤報）

---

## 常用路徑參照

| 用途 | 路徑 |
|------|------|
| Minecraft 翻譯專案 | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| 本 workspace | `C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252` |
| 決策 canonical | `memory/decisions.v2.md` |
| AI 工作流手冊 | `docs/AI_WORKFLOW_MANUAL.md` |
| QMD 搜尋 | `.\qmd.cmd search "關鍵字"` |

---

## AGENTS.md × SOUL.md 綁定規則

> ⚠️ **鐵則**：當本檔案被讀取、修改或擴展時，必須同步檢視 `SOUL.md` 的內容。
> 兩檔案共同構成完整的行为准则，缺一不可。
> 修改 SOUL.md 前先看 AGENTS.md；修改 AGENTS.md 前先看 SOUL.md。

---

*本檔案與 SOUL.md 共同構成 workspace 的完整行為準則。*
