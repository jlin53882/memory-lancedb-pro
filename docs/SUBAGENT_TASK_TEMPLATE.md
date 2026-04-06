# Sub-Agent 任務模板（加強版）

> 目的：解決 sub-agent 常犯的奇怪錯誤——任務模糊、驗證鍊斷裂、環境不一致、缺乏停止機制。
> 適用場景：spawn sub-agent 任務前，把這份 template 的相關章節貼進 task prompt。

---

## 通用守則（所有 sub-agent 任務都必須遵守）

### 🎯 工作開始前檢查清單

```
[ ] 確認 repository 位置
[ ] 確認目前 git branch（git branch --show-current）
[ ] 確認 branch 是否乾淨（git status --short）
[ ] 如果是 PR 任務：用 gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.ref' 確認 head branch 真實名稱
[ ] 確認 upstream/master 是否已有相同修改（git show upstream/master:path/to/file | grep keyword）
```

### ✅ 完成後驗證清單

```
[ ] git status --short 確認變更範圍
[ ] git show HEAD --stat 抽查 commit 內容
[ ] 實際執行測試（不是只看程式碼）
[ ] 確認變更沒有破壞其他功能
```

### ⚠️ 紀律紅線（禁止違反）

| 紅線 | 說明 |
|------|------|
| 不確定就問 | 遇到模糊地帶 → 回報 main session，等指示再繼續 |
| 同一方法失敗 3 次就停 | 停止蠻幹，回報目前狀態與卡點 |
| 不跳測試 | 任何修改後必須跑對應測試 |
| 不假設環境 | 用 git status / gh api 確認當前狀態，不靠記憶 |

---

## 任務 Prompt 範本

```markdown
# 任務：{任務名稱}

## 基本資訊
- Repository：{owner/repo}
- Branch：{branch 名稱}
- 工作目錄：{絕對路徑}
- 聯絡方式：完成後回報 main session

## 任務範圍（Scope）
{具體描述要做什麼，不要含糊}

## 具體步驟
1. {第一個步驟}
2. {第二個步驟}
3. {第三個步驟}

## 禁止事項
- 不要修改 scope 外的檔案
- 不要執行破壞性操作（merge / push --force / delete）
- 不要跳過測試
- 不要在環境未確認前執行 git push

## 驗證要求
完成後必須：
1. git status --short
2. git show HEAD --stat
3. 執行相關測試：{測試指令}
4. 確認沒有破壞其他功能

## 停止條件（重要！）
遇到以下情況請立即停止並回報：
- 同一個方法失敗 3 次
- 發現與預期不符的重大問題
- 需要變更 scope
- 不確定如何繼續

## 完成回報格式
```
✅ 完成
變更檔案：{list}
Commit SHA：{sha}
測試結果：{pass/fail}
待確認：{如有}
```
```

---

## 不同任務類型的專用附錄

### 🔧 PR Bug 修復任務

```markdown
## PR Bug 修復附加規則

### 上游確認（第一步）
在開始修復前，先確認 upstream/master 是否已有相同內容：
git show upstream/master:{檔案路徑} | grep {關鍵字}
如果 upstream 已有 → 視情況 rebase 或 skip 此 commit

### Branch 確認
用以下指令確認 PR head branch：
gh api repos/{owner}/{repo}/pulls/{PR#} --jq '.head.ref'
不要假設 PR number 等於 branch 名稱

### 衝突處理
遇到 conflict marker → 先完整閱讀三方內容
→ 用 git diff 確認差異
→ 確認合併方式
→ json.load() 驗證 JSON 有效性
→ git add + git rebase --continue
```

### 🆕 新功能開發任務

```markdown
## 新功能開發附加規則

### 先讀現有架構
- 先理解現有程式碼結構
- 先確認要修改的模組沒有其他人正在修改
- 用 git log --oneline -5 確認 recent commits

### 小步前進
- 每完成一個子功能就 commit
- 不要累積大量未 commit 的變更
- 避免 long-running branch（容易衝突）

### 重構優先順序
如果需要重構：
1. 先分離出測試案例
2. 確認測試通過
3. 做最小改動重構
4. 確認測試仍然通過
```

### 📋 Review 任務

```markdown
## Code Review 附加規則

### Review 前
- 先用 git diff origin/main...HEAD 確認 PR 範圍
- 確認 PR 的 intent（是修 bug？新功能？重構？）

### Review 時
- 標註 severity（blocking / non-blocking / nit）
- 區分「個人偏好」與「真實問題」
- 建議要有具體的替代方案

### Review 後
- 用 --body-file 送中文 comment（UTF-8）
```

---

## 常用參考指令速查

```bash
# 確認目前 branch
git branch --show-current

# 確認 PR head branch
gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.ref'

# 確認 upstream 是否有相同內容
git show upstream/master:{path} | grep {keyword}

# 確認 local 與 remote 是否同步
git rev-parse HEAD
gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.sha'

# 驗證 JSON 有效性
python -c "import json; json.load(open('file.json'))"

# 確認變更範圍
git status --short && git show HEAD --stat
```
