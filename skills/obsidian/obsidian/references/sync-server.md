# Obsidian Sync Server — 完整設定指南

## 架構

```
Obsidian Vault ←→ obsidian-openclaw 插件 ←→ Sync Server ←→ AI Workspace
                              (HTTP)              (localhost)
```

## 前置需求

1. `obsidian-openclaw` Obsidian 社群插件（透過 BRAT 安裝）
2. Node.js 運行環境
3. Sync server 腳本（從 `obsidian-sync` skill 取得）

## 安裝步驟

### 1. 安裝 sync server 腳本

```bash
# 從 obsidian-sync skill 安裝
clawhub install obsidian-sync --workdir /path/to/workspace --dir skills
```

### 2. 設定環境變數

```bash
export SYNC_TOKEN="your-gateway-token"           # 必填，Gateway token
export SYNC_WORKSPACE="/path/to/workspace"       # AI workspace 根目錄
export SYNC_PORT="18790"                         # 預設 18790
export SYNC_BIND="localhost"                      # 預設 localhost
export SYNC_ALLOWED_PATHS="notes,memory"          # 允許的子目錄
```

### 3. 啟動 sync server

```bash
SYNC_TOKEN="xxx" SYNC_WORKSPACE="/data/agent" node scripts/sync-server.mjs
```

## API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/sync/status` | 健康檢查 |
| GET | `/sync/list?path=notes` | 列出資料夾中的 Markdown 檔案 |
| GET | `/sync/read?path=notes/x.md` | 讀取檔案 + metadata |
| POST | `/sync/write?path=notes/x.md` | 寫入檔案（附衝突偵測） |

### 請求格式

所有請求需帶 Header：
```
Authorization: Bearer <SYNC_TOKEN>
```

### 寫入請求
```
POST /sync/write?path=notes/my-note.md
Content-Type: text/plain

# My Note

Content here.
```

## Obsidian 插件設定

### 透過 BRAT 安裝

1. 安裝 **BRAT** 社群插件（`TfTHacker/obsidian42-brat`）
2. BRAT → Add a beta plugin → 輸入：`AndyBold/obsidian-openclaw`
3. 啟用插件
4. 設定 Sync Server URL（如 `http://localhost:18790`）
5. 輸入 SYNC_TOKEN

### 插件功能

- 💬 **聊天側邊欄** — 在 Obsidian 內與 AI 對話
- 📁 **檔案操作** — 透過對話建立、編輯、刪除筆記
- 🔄 **雙向同步** — 保持 vault 和 AI workspace 同步
- 🔒 **安全儲存** — OS keychain 整合儲存 token
- 📋 **稽核日誌** — 追蹤所有檔案操作

## systemd 服務（Linux/macOS）

```ini
[Unit]
Description=OpenClaw Sync Server
After=network.target

[Service]
Type=simple
Environment=SYNC_TOKEN=your-token-here
Environment=SYNC_WORKSPACE=/data/clawdbot
Environment=SYNC_ALLOWED_PATHS=notes,memory
ExecStart=/usr/bin/node /path/to/skills/obsidian-sync/scripts/sync-server.mjs
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now openclaw-sync
loginctl enable-linger $USER  # 開機啟動
```

## Tailscale 暴露（遠端存取）

```bash
tailscale serve --bg --https=18790 http://localhost:18790
```

## 安全考量

- 只允許設定的子目錄存取
- 防止路徑穿越（`../`）
- 所有請求需 Authorization header
- 綁定 localhost；透過 Tailscale 暴露
