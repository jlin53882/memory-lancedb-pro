# OpenClaw 設定 知識索引
> 蒸餾日期：2026-03-25
> 來源：memory/decisions.v2.md、memory/openclaw-*.md 等

---

## 核心知識點

1. **Gateway 重啟必先通知家豪** - 任何導致 restart 的操作，都必須先通知並告知「重啟後 agent 會暫時離線」，等確認後才執行（嚴禁默默重啟）。- 來源：P-2026-02-25-GATEWAY-RESTART-REQUIRE-CONFIRM

2. **更新指令統一用 npm** - `npm install -g openclaw@latest`，不用 `openclaw update`（只適用 git source 開發模式）。pnpm global 移除後 restart 會失效，統一 npm 確保路徑一致。- 來源：D-2026-03-23-UPDATE-MECHANISM

3. **Cron B 方案（兩個 job）** - Job 1（12:00）只做 update + restart 不回報；Job 2（12:02）驗證後 announce 結果到 Telegram 監控群。避免重啟導致通知被切斷。- 來源：D-2026-02-25-DAILY-UPDATE-CRON-B

4. **Gateway 服務重啟後 RPC probe failed：統一 npm 路徑** - 根因是 Scheduled Task 指向 pnpm shim，移除 pnpm 後失效。修法：確保 openclaw 由 npm 安裝，gateway.cmd 固定呼叫 `C:\Users\admin\AppData\Roaming\npm\openclaw.cmd`。- 來源：D-2026-03-23-GATEWAY-RESTART-FIX

5. **memory-lancedb-pro 設定三坑** - (1) plugins.load.paths 要用絕對路徑 (2) embedding.apiKey 仍需非空（可填 dummy）(3) Windows/PowerShell 寫 JSON 注意反斜線雙重轉義。- 來源：D-2026-03-23-MEMORY-LANCEDB-PRO-CONFIG

6. **Codex OAuth token 複製補救** - `openclaw onboard` 只會寫入 default profile，無法指定 active/plus/third。解法：把 default 的 token 複製到目標 profile，auth-profiles.json 位於 `~\.openclaw\agents\main\agent\`。- 來源：D-2026-03-23-CODEX-OAUTH-PROFILES

7. **Gateway restart 由家豪手動執行** - Agent 只負責寫入設定 + 通知家豪，不自行執行 restart。- 來源：AGENTS.md 安全硬規則

---

## 常見踩坑

1. **pnpm global 移除後 gateway restart 失效** - `gateway.cmd` 綁 pnpm shim，移除 pnpm 後 restart 就失效了。解法：重新用 npm 安裝。- 來源：D-2026-03-23-GATEWAY-RESTART-FIX

2. **Codex onboard 只寫 default profile** - 重新登入後 token 只在 default，無法指定其他 profile。補救：手動複製 token。- 來源：D-2026-03-23-CODEX-OAUTH-PROFILES

3. **Discord 檔案上傳上限 10MB** - 單一檔案超過 10MB 需改用雲端分享連結。- 來源：TOOLS.md
