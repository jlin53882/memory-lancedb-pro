---
name: agent-self-review
description: "Agent 自我檢討與持續學習 Skill。支援四個層次：Level 1 單次對話檢討（/reflect）、Level 2 記憶學習（/learn-from-memory）、Level 3 深度稽核（/self-audit）、Level 4 即時行為修正（/fix-behavior）。適用時機：對話結束後、主題切換前、cron 定期執行、或失誤當下。目標頻道：#ai-程式修改助手（1476866394556465252）與 #ai-小助理（1476858065914695741）。"
metadata:
  openclaw:
    events:
      - command:reflect
      - command:learn-from-memory
      - command:self-audit
      - command:fix-behavior
      - cron
    channels:
      - discord:1476866394556465252
      - discord:1476858065914695741
---

# Agent Self-Review Skill — 多層次自我檢討與學習系統 v1.0

## 概述

此 Skill 賦予 Agent 自我檢討與持續學習的能力，分為四個層次：

| 等級 | 指令 | 觸發時機 | 執行者 |
|------|------|---------|--------|
| L1 | `/reflect` | 單次對話結束後 | Main agent |
| L2 | `/learn-from-memory` | 主題切換前、context > 60k | Main agent |
| L3 | `/self-audit` | Cron 每日/每週 | Main agent |
| L4 | `/fix-behavior` | 失誤當下 | Main agent |

**目標頻道（用於 L3 cron 輸出）：**
- `#ai-程式修改助手`：channel_id `1476866394556465252`
- `#ai-小助理`：channel_id `1476858065914695741`

---

## 共同原則

1. **只用事實說話**：所有觀察必須有 log/session 證據，不捏造
2. **區分已驗證 vs 推測**：標注 `✅ 已驗證` / `⚠️ 推測`
3. **產出導向**：每個 Level 都產出可直接採用的 action item
4. **優先級排序**：高 > 中 > 低，聚焦少數關鍵改進

---

## Level 1：單次對話自我檢討 `/reflect`

### 觸發條件
- 使用者輸入 `/reflect`
- 單次對話即將結束（偵測到結束語）
- Context 使用量 > 60k tokens

### 執行流程

**Step 1：抓取對話歷史**
使用 `sessions_history(sessionKey: "agent:main:discord:channel:1476866394556465252", limit: 50)` 或当前 session。

**Step 2：分析維度**

| 維度 | 檢查點 |
|------|--------|
| 回答品質 | 有無「應該」「可能」等不確定語氣？是否有假設未確認？ |
| 工具使用 | 有無 tool call 失敗或重試？原因？ |
| 指令遵守 | 有無違反 AGENTS.md / SOUL.md 的具體例子？ |
| Token 消耗 | 哪些步驟消耗最多？有無可壓縮處？ |
| 記憶遵從 | 有無跳過 LanceDB recall 直接輸出的情况？ |

**Step 3：產出格式**

```markdown
## 🪞 Level 1 自我檢討報告

**對話時間**：YYYY-MM-DD HH:MM ~ HH:MM
**Session**：{sessionKey}

### ✅ 做得好的地方
1. ...

### ⚠️ 問題清單

| # | 問題 | 根因 | 改善建議 |
|---|------|------|---------|
| 1 | ... | ... | ... |

### 📊 Token 消耗分析
- 最高消耗階段：...
- 壓縮空間：...

### 🎯 下次優先注意
1. ...
```

### 輸出目標
- 主要：直接回覆給使用者
- 次要：寫入 `memory/YYYY-MM-DD.md`（append）

---

## Level 2：從記憶中學習 `/learn-from-memory`

### 觸發條件
- 使用者輸入 `/learn-from-memory`
- 主題大幅切換前
- Context > 60k tokens

### 執行流程

**Step 1：LanceDB 查詢（4 個維度並行）**

```javascript
// 並行 recall
const [repeatedErrors, userCorrections, successPatterns, recentDecisions] = await Promise.all([
  memory_recall({ query: "錯誤 失敗 修正糾正", limit: 10, category: "fact" }),
  memory_recall({ query: "使用者糾正 糾正行為 修正偏好", limit: 10, category: "preference" }),
  memory_recall({ query: "成功 正面回饋 好的回應 指令格式", limit: 10, category: "decision" }),
  memory_recall({ query: "decision 近期 規則 變更", limit: 5, category: "decision" })
]);
```

**Step 2：模式分析**

| 模式 | 分析重點 |
|------|---------|
| 重複錯誤 | 同類問題出現次數、觸發根因 |
| 使用者糾正 | 哪些行為被糾正過多次？ |
| 成功模式 | 哪些回應格式得到正向結果？ |
| 待改進清單 | 具體行為改變建議 |

**Step 3：產出格式**

```markdown
## 📚 Level 2 記憶學習報告

**分析範圍**：近 14 天 LanceDB 記憶
**執行時間**：YYYY-MM-DD HH:MM

### 🔁 重複錯誤（高優先）

| 錯誤類型 | 發生次數 | 根因 | 建議 |
|---------|---------|------|------|
| ... | N次 | ... | ... |

### ✏️ 使用者糾正紀錄（中優先）

| 糾正內容 | 最近一次 | 頻率 |
|---------|---------|------|
| ... | YYYY-MM-DD | N次 |

### 🌟 成功模式

1. ...
2. ...

### 🎯 待改善清單（優先級排序）

| 優先級 | 項目 | 具體行為 |
|-------|------|---------|
| 🔴 高 | ... | ... |
| 🟡 中 | ... | ... |
| 🟢 低 | ... | ... |

### 📝 規則提案

若需更新 AGENTS.md / MEMORY.md，輸出：
```
LEARNED: [規則內容]
```
```

### 輸出目標
- 直接回覆使用者
- 建議寫入 LanceDB（高重要性 learning）

---

## Level 3：深度自我審計 `/self-audit`

### 觸發條件
- 使用者輸入 `/self-audit`
- Cron job 每日 02:00 或每週一 09:00 執行

### Cron 設定方式

```bash
# 每日 02:00 對 #ai-小助理 發送摘要
openclaw cron add \
  --name "Daily self-audit (L3)" \
  --schedule "0 2 * * *" \
  --timezone "Asia/Taipei" \
  --command "/self-audit --channels 1476858065914695741 --period daily"

# 每週一 09:00 對 #ai-程式修改助手 發送深度報告
openclaw cron add \
  --name "Weekly deep self-audit (L3)" \
  --schedule "0 9 * * 1" \
  --timezone "Asia/Taipei" \
  --command "/self-audit --channels 1476866394556465252 --period weekly"
```

### 執行流程

**Step 1：抓取目標頻道 session 歷史**

對每個目標頻道 channel_id：
```javascript
sessions_history({
  sessionKey: `agent:main:discord:channel:${channelId}`,
  limit: 100,
  includeTools: true
})
```

**Step 2：四區塊稽核**

#### 【區塊 A｜準確性稽核】

分析重點：
- 計數「我認為」「可能」「應該」「大概是」等不確定語氣出現次數
- 分類根因：資料不足 / 工具未呼叫 / 推理限制

```javascript
// 統計不確定語氣
const uncertainPhrases = ["我認為", "可能", "應該", "大概是", "也許"];
// 計數並分類
```

#### 【區塊 B｜工具效率稽核】

分析重點：
- 哪些工具呼叫失敗次數最多
- 是否有 3 步以上可壓縮為 1 步的情況
- 重複呼叫同一工具的 pattern

#### 【區塊 C｜原則遵守稽核】

對照 SOUL.md 逐條檢查：

| SOUL.md 原則 | 違反次數 | 具體案例 |
|-------------|---------|---------|
| 不假設，先確認 | N次 | ... |
| 不主動建議不相關的事 | N次 | ... |
| ... | ... | ... |

#### 【區塊 D｜學習提案】

產出格式：
```markdown
### 📋 應新增到 AGENTS.md 的規則
```
[具體規則文字]
```

### 📋 應新增到 MEMORY.md 的記憶條目
- [條目內容]

### 🎯 下週重點行為清單
1. ...
```

**Step 3：產出格式（完整報告）**

```markdown
# 🔍 Level 3 深度自我審計報告

**執行時間**：YYYY-MM-DD HH:MM
**審計範圍**：近 7 天 / 30 天
**目標頻道**：#ai-程式修改助手 / #ai-小助理

---

## 【區塊 A｜準確性稽核】

| 指標 | 數值 | 備註 |
|------|------|------|
| 不確定語氣出現次數 | N次 | |
| 其中：資料不足 | N次 | |
| 其中：工具未呼叫 | N次 | |
| 其中：推理限制 | N次 | |

**典型案例**：
1. ...

---

## 【區塊 B｜工具效率稽核】

| 工具 | 失敗次數 | 主要原因 |
|------|---------|---------|
| ... | N次 | ... |

**可優化項目**：
- ...

---

## 【區塊 C｜原則遵守稽核】

| 原則 | 違反次數 | 案例 |
|------|---------|------|
| 不假設，先確認 | N次 | ... |
| ... | ... | ... |

---

## 【區塊 D｜學習提案】

### 規則新增建議
```
LEARNED: [規則內容]
```

### 記憶條目建議
- [內容]

### 下週行動清單
- [ ] ...
```

### 輸出目標
- Discord 發送到對應頻道（使用 `message` tool）
- 存檔至 `memory/self-audit/YYYY-MM-DD.md`
- 高優先 learning 寫入 LanceDB

---

## Level 4：即時行為修正 `/fix-behavior`

### 觸發條件
- 使用者輸入 `/fix-behavior [問題描述]`
- Agent 自發偵測到錯誤（透過 hook 或自省）

### 執行流程（4 步）

**Step 1：承認錯誤**
- 明確、具體地說出哪個行為錯了
- 不迴避、不稀釋

**Step 2：分析根因**
- 指名是哪種錯誤類型：
  - `指令理解問題` / `記憶缺失` / `工具跳過` / `假設未驗證` / `流程跳步`

**Step 3：提出正確 SOP**
- 這個情境的正確處理流程

**Step 4：產出 LEARNED 規則**
```markdown
LEARNED: [規則內容]
```

### 產出格式

```markdown
## ⚡ Level 4 即時行為修正

**觸發時間**：YYYY-MM-DD HH:MM

### 1️⃣ 承認錯誤
[具體描述錯誤行為]

### 2️⃣ 根因分析
**類型**：[指令理解問題 / 記憶缺失 / 工具跳過 / 假設未驗證 / 流程跳步]
**分析**：[根因說明]

### 3️⃣ 正確 SOP
[這個情境的正確處理流程]

### 4️⃣ 學習規則
```
LEARNED: [規則內容]
```
```

### 輸出目標
- 直接回覆使用者
- 使用者可將 `LEARNED:` 規則手動加入 AGENTS.md

---

## 附件模板

### `assets/reflect_template.md`
（reflect 報告的 Markdown 模板）

### `assets/audit_template.md`
（self-audit 報告的 Markdown 模板）

---

## 與既有 self-improvement Skill 的分工

| 情境 | Skill |
|------|-------|
| 外部錯誤/例外捕獲 | `self-improving-agent` |
| 使用者即時糾正 | `self-improving-agent` |
| 自身行為檢討/稽核（L1-L3） | `agent-self-review`（本 Skill）|
| 即時失誤修正（L4） | `agent-self-review`（本 Skill）|

兩個 Skill 可同時啟用，互补不重疊。
