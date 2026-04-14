# SUBAGENT_ERRORS.md — Sub-agent 常犯錯誤深度檢討

> 建立日期：2026-04-07
> 目的：系统性分析 sub-agent 犯錯根因，建立預防機制

---

## 一、錯誤分類總表

| 錯誤類型 | 範例 | 嚴重性 | 發生頻率 |
|----------|------|--------|----------|
| **意圖解讀錯誤** | 把「準備合併」當成「可以合併」直接執行 | 高 | 高 |
| **驗證不足** | push 失敗沒發現就送 review、沒有讀檔案實際內容 | 高 | 高 |
| **假設未確認** | 假設 remote 包含正確內容、假設「沒反對=可以做」 | 中 | 中 |
| **編碼/工具問題** | PowerShell `>` 搞砸 UTF-8、CRLF 問題 | 中 | 中 |
| **架構跳步** | 重要功能沒有先確認方向就實作 | 中 | 低 |
| **目錄操作錯誤** | 在不同目錄操作，沒有驗證 cwd | 中 | 中 |

---

## 二、根因分析

### 根因 1：Context 傳遞不完整

**現象**：Sub-agent 拿到 task 後，不知道 James 的偏好（比如「不要合併」「要先問再動」），只收到冰冷的指令文字。

**解讀**：Main session 知道 James 的風格，但 sub-agent 從零開始，沒有拿到這層 context。

**預防**：
- Spawn sub-agent 時，在 task 描述明確附上「底線」
- 包含「暖但有重點，所有變更需 James 明確授權」提醒

---

### 根因 2：Main session 跳過驗證

**現象**：Sub-agent 說完成了，Main session 直接送 review 或 amend+push，沒有驗證。

**預防**：
- 強制執行「Sub-agent 完成後檢查清單」（見第三章）
- 不要懶惰，不要太信任 sub-agent 的回報

---

### 根因 3：Task 描述缺少「目的」和「底線」

**現象**：Sub-agent 被告知「做 X」，但不知道為什麼要做 X、有沒有底線，只能靠猜測意圖。

**預防**：
- 每個 sub-agent task 都必須包含：目標 + 底線 + 驗收方式
- 禁止只給一句話指令就 spawn

---

### 根因 4：不熟悉 Windows/PowerShell 環境

**現象**：PowerShell `>` 重新導向導致 CRLF 錯誤、cmd quoting 問題。

**預防**：
- 含中文 UTF-8 檔案操作強制用 Python subprocess
- PowerShell 只做：git checkout, git status, mkdir, 簡單系統指令

---

### 根因 5：模糊指令時沒有先問

**現象**：收到的指令有兩種可能的解讀，sub-agent 自己選一個方向蠻幹。

**預防**：
- 模糊 → 先停在原地問清楚
- 不要自己假設意圖

---

## 三、Sub-agent 監督強制檢查清單

> Main session 在 sub-agent 完成後必須執行

```
✅ git show HEAD --stat（看變更範圍）
✅ 抽查關鍵檔案的實際內容（不能只看 git log）
✅ 確認變更範圍符合預期
✅ 才能送 review 或 push
✅ push 完成後驗證 remote 包含正確內容（git ls-remote 或 gh pr diff）
✅ push 失敗時立即告知 James，不要假設 remote 已經更新
```

---

## 四、Sub-agent Task 標準模板

每個 sub-agent spawn 時，task 描述必須包含：

```
【任務目標】XXX
【底線限制】
  - 禁止：merge / push --force / delete / gateway restart / config 變更
  - 嚴格遵守：含中文 UTF-8 用 Python subprocess，PowerShell 只做 git/status/mkdir
  - 所有變更需要 James 明確授權才能執行
【驗收方式】
  - 完成後執行 git show HEAD --stat，彙報變更範圍
  - 抽查關鍵檔案內容
  - 確認符合預期後再回報完成
【編碼提醒】Windows PowerShell 環境，慎用 > 重新導向
```

---

## 五、蒸餾成 AGENTS.md 的規則

以下規則已寫入 `AGENTS.md`：

| 規則 | 內容 |
|------|------|
| R-S1 | Sub-agent 完成後強制執行「監督檢查清單」 |
| R-S2 | Sub-agent task 必須包含：目標 + 底線 + 驗收方式 |
| R-S3 | 模糊指令先問清楚，不要自己假設 |
| R-S4 | 含中文 UTF-8 強制 Python subprocess，PowerShell 只做簡單指令 |
| R-S5 | push 完成後驗證 remote 內容，失敗立即告知 James |

---

*本檔案為 2026-04-07 深度檢討產物，隨著新錯誤持續更新。*
