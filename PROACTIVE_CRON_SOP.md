# Proactive Cron SOP — 主動式 Agent 機制

## 目標
讓 agent 不只是被動回應指令，而是能主動：
1. 每天定時整理進度
2. 主動預判需求
3. 在 context 即將爆滿前主動壓縮

---

## Cron 工作流程

### 每日 Cron（早上 9:00）
- 讀取 `memory/active_state_discord.md`
- 檢查是否有待追蹤的事項
- 主動在 #ai-程式修改助手 回報進度摘要
- 預判當天可能需要處理的事

### 睡前 Cron（晚上 11:00）
- 如果今天有新決策，寫入 `memory/YYYY-MM-DD.md`
- 檢查 context 使用量
- 若 > 70%，主動執行 /compress 提示

### Context 警戒線
- 50%：開始注意，盡量壓縮回覆
- 60%：進入 Working Buffer 模式，每個 exchange 都記錄
- 75%：主動詢問是否要 /compress 或 /reset

---

## 主動預判清單

### 每次收到 coding 任務時，主動檢查：
- [ ] 上次這個專案的進度在哪裡？（讀 active_state）
- [ ] 有沒有類似的歷史任務？（QMD 搜尋）
- [ ] 這個任務需要開 sub-agent 嗎？

### 每次收到 complex 任務時，主動：
- [ ] 先建立工作清單
- [ ] 預估 token 消耗
- [ ] 主動分段處理，不要一次做完

---

## HEARTBEAT.md 更新

更新 `C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\HEARTBEAT.md`：

```markdown
# HEARTBEAT.md

## 每次 Heartbeat 檢查清單

### 🟢 上下文檢查
- [ ] Context 使用量是否 > 50%？
- [ ] 是否進入 Working Buffer 模式（> 60%）？

### 🟢 主動整理
- [ ] `memory/active_state_discord.md` 是否為最新？
- [ ] 今天有新決策需要寫入嗎？

### 🟢 待辦追蹤
- [ ] 有沒有pending的任務還沒處理？
- [ ] 有沒有超時未回應的問題？

### 🟢 Proactive 預判
- [ ] James 今天可能需要什麼？（根據最近對話）
- [ ] 有沒有可以主動做的事？（建立 Proactive 清單）
```

---

## Cron 設定方式

在 OpenClaw 中設定 cron：
```bash
# 每日早上 9:00 主動整理進度
openclaw cron add \
  --name "Daily proactive check" \
  --schedule "0 9 * * *" \
  --timezone "Asia/Taipei" \
  --command "/proactive-check"
```

---

*最後更新：2026-03-25*
