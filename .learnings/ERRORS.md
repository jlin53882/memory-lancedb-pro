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
