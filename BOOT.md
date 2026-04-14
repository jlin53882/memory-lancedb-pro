# BOOT.md — 啟動檢查

## Gateway 重啟後必做

1. 檢查 `git status` — 確認 workspace 狀態
2. 確認 Discord bot 連線正常
3. 檢查 cron job 狀態

## 快速確認清單

- [ ] workspace 可讀寫
- [ ] shared/tasks/ 可存取
- [ ] 上次任務狀態

## 異常處理

若有異常，用 `sessions_send` 通知 main agent。
