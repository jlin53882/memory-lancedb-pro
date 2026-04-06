# Discord / DC Agent Skill 使用 SOP

> 日期：2026-03-23
> 目的：避免「skill 已安裝但主流程從未使用」。
> 適用範圍：所有 Discord / DC agent（含 main、dc-channel-*、dc-ai、dc-codex、review 類 agent）

---

## 一、核心原則

### 1. skill ready ≠ 已進工作流
如果某個 skill 已是 `ready`，但沒有：
1. 明確觸發條件
2. 禁止條件
3. 輸出目的地
4. 升級門檻

則視為**未制度化**，不能算「已納入工作流」。

### 2. Discord agent 一律先判斷「是否該觸發 skill」
收到任務後，除了判斷要不要開 sub-agent，也要額外判斷：

```text
這個任務有沒有對應 skill？
這個 skill 是否屬於「應主動進工作流」？
如果有，先走 skill 再回答。
```

### 3. 不要為了用 skill 而用
如果直接 `read / exec / browser / sessions_spawn` 更短更準，則直接做。
SOP 的目的不是增加步驟，而是避免漏掉高價值 skill。

---

## 二、強制納入工作流的 skill（P1-C 類）

以下三個 skill，從 2026-03-23 起視為 **DC agent 強制檢查項**。

---

## 2.1 `self-improvement`

### 觸發條件（任一成立就要用）
- 使用者明確糾正：「不對 / 錯了 / 不是這樣 / 重來」
- 工具呼叫失敗，且失敗原因對未來有重複風險
- 發現先前認知過時 / 路徑記錯 / branch 看錯 / 流程用錯
- 找到更好的固定做法，可降低下次失誤

### 禁止條件
- 單次微小失誤且無 повтор 風險
- 純聊天內容、無流程價值
- 尚未驗證的猜測

### 輸出位置
- 第一層：`.learnings/`（事件原始學習）
- 第二層：若證明是 recurring pattern，再升級到 `AGENTS.md` / `TOOLS.md` / `SOUL.md`

### 升級門檻
- **1 次事件**：只記 `.learnings/`
- **2 次以上重複**：提出升級到 `AGENTS.md` 或 `TOOLS.md`
- **屬於人格/回話邊界**：升級到 `SOUL.md`

### DC agent 執行句型
- 「這次屬於可重複踩坑，我會把它記進 self-improvement。」
- 不要只說「下次注意」。

---

## 2.2 `agent-self-review`

### 觸發條件
- 一段任務結束後（特別是設計 / PR review / 大型除錯）
- 主題切換前
- 使用者對品質有疑慮時
- cron / 定期檢查時

### 禁止條件
- 每輪對話都跑（會變洗版）
- 任務尚未完成就插入 review
- 沒有新資訊、沒有可檢討點

### 輸出位置
- 以**摘要提醒**為主，不直接把長篇 review 灌進主對話
- 若有穩定新規則，再提案升級到 `AGENTS.md`

### 升級門檻
- 單次 review 結論：保留在當次輸出或 daily log
- 證明 recurring 的流程問題：升級 `AGENTS.md`
- 證明是長期偏好/語義邊界：升級 `MEMORY.md` / `SOUL.md`

### DC agent 執行原則
- 預設在「任務告一段落」時觸發，不在中途插話
- 輸出只留：問題 / 根因 / 下次規則

---

## 2.3 `proactive-agent`

### 觸發條件
- 使用者明顯卡住，不知道下一步
- 任務存在高機率後續步驟（例如：PR 修完後還要看 CI / merge / doc sync）
- 有明顯風險尚未處理（例如：只修 lint 還沒看 test）
- 任務可自然拆為下一個小步驟，且提議不會打擾

### 禁止條件
- 使用者已明確說「先這樣 / 不要再提 / 別主動建議」
- 每回合都主動加碼
- 提議內容沒有直接價值，只是展示能力

### 輸出位置
- 只做**下一步建議**，不直接落記憶
- 若使用者接受並證明好用，再考慮寫入 `.learnings/`

### 升級門檻
- 多次證明同一類主動建議能減少往返時，才提案升級到 `AGENTS.md`

### DC agent 執行句型
- 可用：「我建議下一步直接做 X，因為 Y。」
- 禁止：連續多輪主動派工、主動擴 scope

---

## 三、應優先評估觸發的技能（P1-A 類）

以下 skill 不一定每次都要用，但遇到對應任務時，**要先想一次**。

| Skill | 觸發情境 | 若不用，常見損失 |
|------|----------|----------------|
| `agentlens` | 新 repo / 大型 codebase 導航 | 手動 read 太慢、看不到結構 |
| `qmd` | 查 workspace 舊筆記 / SOP / 決策 | 重複問、重複找 |
| `session-logs` | 查歷史 session / 舊對話 | 靠記憶回答、答錯版本 |
| `healthcheck` | 安全健檢 / Gateway / 維運風險 | 漏掉安全 SOP |
| `batch-processor` | 批量文件 / 多檔任務 | 主線單筆處理過慢 |
| `find-skills` | 使用者問「有沒有 skill 可做」 | 錯過既有能力 |
| `skill-vetting` | 打算裝新 skill | 直接裝第三方，未先評估 |

### 執行規則
收到任務時，若符合上表，先在腦中做一次：

```text
這題是不是 agentlens / qmd / session-logs / find-skills / healthcheck / batch-processor / skill-vetting 的場景？
```

若是，就先讀該 skill 或直接使用。

---

## 四、低頻但保留的技能（P1-B 類）

| Skill | 保留原因 | 不主動強推原因 |
|------|----------|----------------|
| `codex-quota` | 查 Codex 配額很有用 | 只有 quota 類問題才用 |
| `node-connect` | 裝置配對問題很專用 | 平常任務不常遇到 |
| `opencode-controller` | 控 Opencode session 有價值 | 僅限特定工作流 |

規則：**保留可用，但不列入每次任務的必查清單。**

---

## 五、所有 DC agent 的最小 SOP

每次收到任務，依序做：

### Step 1：任務分類
- 是 coding / design / debug / memory / ops / skill-discovery 哪一類？

### Step 2：skill 觸發檢查
- 這題有沒有對應 skill？
- 若屬於 P1-C 類（self-improvement / agent-self-review / proactive-agent），要特別檢查是否該觸發
- 若屬於 P1-A 類，至少先想一次是否值得用

### Step 3：執行主任務
- 不為了用 skill 而繞路
- 以最短、最準、最可驗證的方式完成

### Step 4：任務結束檢查
- 這次是否產生可重複學習？→ `self-improvement`
- 這次是否值得做一次收尾檢討？→ `agent-self-review`
- 這次是否有自然的下一步應提醒？→ `proactive-agent`

---

## 六、禁止事項

- 不能因為 skill 已安裝，就在每輪都硬用
- 不能把主動建議變成洗版
- 不能把未驗證內容直接升級成長期規則
- 不能跳過主任務，只做 review / improvement / proactive 建議

---

## 七、收斂結論

從 2026-03-23 起，DC agent 對 skill 的要求改為：

1. **P1-C 類**：納入工作流硬檢查
2. **P1-A 類**：納入任務前心智檢查
3. **P1-B 類**：保留，但不主動強推

這樣可以避免：
- skill 裝了卻沒用
- 有能力但沒有觸發條件
- 主動性過高造成打擾
- 學習類 skill 寫太多、污染長期記憶
