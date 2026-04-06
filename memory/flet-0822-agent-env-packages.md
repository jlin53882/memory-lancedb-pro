# Flet 0.82.2 環境變數與 Binary Packages

> **版本**：flet:0.82.2
> **來源**：
> - https://docs.flet.dev/reference/environment-variables/
> - https://docs.flet.dev/reference/binary-packages-android-ios/
> **日期**：2026-03-22

---

## 一、Environment Variables（環境變數）

> **設定方式**：在 `ft.run()` 之前 `import os; os.environ["VAR"] = "value"`

### 布林值設定規則
設定 `True` 可以使用：`"true"` / `"1"` / `"yes"`
其他值皆視為 `False`。

---

### 儲存路徑相關

| 變數名 | 用途 | 預設值 |
|---|---|---|
| `FLET_APP_CONSOLE` | 應用程式 console log 檔路徑（console.log） | 自動設定 |
| `FLET_APP_STORAGE_DATA` | 持久應用資料目錄 | 平台決定 |
| `FLET_APP_STORAGE_TEMP` | 暫存檔目錄（cache） | 平台決定 |

### 資源相關

| 變數名 | 用途 | 備註 |
|---|---|---|
| `FLET_ASSETS_DIR` | 應用程式 assets 目錄的絕對路徑 | 僅用於需要絕對路徑的場合（如 JSON config、資料庫） |

```python
import os
from pathlib import Path
import flet as ft

default_assets_dir = Path(__file__).parent / "assets"
assets_dir = Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()

ft.run(main, assets_dir="assets")
```

### Android 簽署相關

| 變數名 | 用途 |
|---|---|
| `FLET_ANDROID_SIGNING_KEY_ALIAS` |  keystore key alias |
| `FLET_ANDROID_SIGNING_KEY_PASSWORD` | key 密碼 |
| `FLET_ANDROID_SIGNING_KEY_STORE` | .jks keystore 檔路徑 |
| `FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD` | keystore 密碼 |

### 應用程式執行相關

| 變數名 | 預設值 | 用途 |
|---|---|---|
| `FLET_PLATFORM` | — | 目前執行平台：`android`/`ios`/`linux`/`macos`/`windows`/`fuchsia` |
| `FLET_HIDE_WINDOW_ON_START` | false | 啟動時隱藏主視窗 |
| `FLET_FORCE_WEB_SERVER` | false | 強制以 Web 應用執行 |
| `FLET_SERVER_IP` | `0.0.0.0` | Web 監聽 IP |
| `FLET_SERVER_PORT` | 8000（Linux） | TCP 連接埠 |
| `FLET_SERVER_UDS_PATH` | `flet_<pid>.sock` | Unix Domain Socket 路徑（Unix 系統） |
| `FLET_SESSION_TIMEOUT` | 3600 秒 | 工作階段生命週期 |

### 上傳相關

| 變數名 | 預設值 | 用途 |
|---|---|---|
| `FLET_MAX_UPLOAD_SIZE` | 無限制 | 上傳檔案最大位元組 |
| `FLET_UPLOAD_DIR` | — | 上傳目錄絕對路徑 |
| `FLET_UPLOAD_HANDLER_ENDPOINT` | `/upload` | 上傳 handler 路徑 |
| `FLET_SECRET_KEY` | — | 上傳 URL 簽署密鑰 |

### OAuth 相關

| 變數名 | 預設值 | 用途 |
|---|---|---|
| `FLET_OAUTH_CALLBACK_HANDLER_ENDPOINT` | `/oauth_callback` | OAuth callback 路徑 |
| `FLET_OAUTH_STATE_TIMEOUT` | 600 秒 | OAuth 完成最大時間 |

### Web 相關

| 變數名 | 預設值 | 用途 |
|---|---|---|
| `FLET_WEB_RENDERER` | `canvaskit` | Web 渲染引擎：`canvaskit`/`skwasm`/`auto` |
| `FLET_WEB_APP_PATH` | `/` | Web 應用 URL 路徑前綴 |
| `FLET_WEB_NO_CDN` | false | 避免從 CDN 載入 CanvasKit/Pyodide/fonts |
| `FLET_WEBSOCKET_HANDLER_ENDPOINT` | `/ws` | WebSocket handler 路徑 |
| `FLET_WEB_USE_COLOR_EMOJI` | false | 載入彩色 emoji Web 字體 |
| `FLET_WEB_ROUTE_URL_STRATEGY` | `path` | URL 策略：`path` 或 `hash` |

### CLI 相關

| 變數名 | 預設值 | 用途 |
|---|---|---|
| `FLET_CLI_NO_RICH_OUTPUT` | false | 停用 CLI 豐富輸出 |
| `FLET_CLI_SKIP_FLUTTER_DOCTOR` | false | 建置失敗時跳過 flutter doctor |

---

## 二、Binary Packages（Android / iOS）

### 說明
Flet 為 Android 和 iOS 預先封裝了特定的 binary Python 擴充功能，可透過 pip 安裝。

### 主要套件

| 套件名稱 | 用途 |
|---|---|
| `flet-desktop-light` | 輕量化桌面執行環境 |

### 安裝方式

```bash
pip install flet-desktop-light
```

> 詳見：https://pypi.flet.dev/flet-desktop-light/

### 與 two_project 的關係
two_project 是 Windows desktop 應用，不依賴 Android/iOS binary packages。此資訊僅供記錄。

---

## 三、實用對照表

| 場景 | 變數 |
|---|---|
| 隱藏視窗啟動 | `FLET_HIDE_WINDOW_ON_START=true` |
| 自訂連接埠 | `FLET_SERVER_PORT=9000` |
| Web 應用前綴 | `FLET_WEB_APP_PATH=/apps/myapp` |
| 上傳大小限制 | `FLET_MAX_UPLOAD_SIZE=10485760`（10MB） |
| 強制 Web 渲染引擎 | `FLET_WEB_RENDERER=skwasm` |
| 隱藏 window 標題列 | 需用 WindowDragArea + frameless 設定 |
