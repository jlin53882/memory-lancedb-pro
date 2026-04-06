# Flet 0.82.2 環境變數參考（繁體中文）

> **版本標籤**：`flet:0.82.2`
> **資料來源**：https://docs.flet.dev/reference/environment-variables/
> **翻譯語言**：繁體中文
> **最後更新**：2026-03-22

---

## 布林值設定方式

設定布林值為 True，可使用以下字串之一：`"true"`、`"1"` 或 `"yes"`。其他值皆視為 False。

---

## 應用程式環境變數

### FLET_APP_CONSOLE

應用程式主控台日誌檔（console.log）的路徑，位於暫存儲存目錄。**僅在發布模式設定。**

### FLET_APP_STORAGE_DATA

用於存放應用程式持久資料的目錄。位置依平台而異，**在更新後會保留**。已預先建立。

### FLET_APP_STORAGE_TEMP

用於存放暫存檔案（快取）的目錄。位置依平台而異。已預先建立。

### FLET_ASSETS_DIR

應用程式 assets 目錄的絕對路徑。

**發布模式**（`flet build`）：指向打包後 assets 的實際位置，適用於需要檔案系統路徑的場景（如 JSON 設定檔、資料庫、模型檔案）。

```python
import os
from pathlib import Path
import flet as ft

default_assets_dir = Path(__file__).parent / "assets"
assets_dir = Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()

def main(page: ft.Page):
    ...

ft.run(main, assets_dir="assets")
```

**本地開發模式**：此變數可能未設定，建議加上 fallback（如上例）。

**注意**：對於 `Image.src` 等控制項屬性，仍應使用相對於 `ft.run(assets_dir=...)` 的相對路徑。

---

## Android 簽署變數

### FLET_ANDROID_SIGNING_KEY_ALIAS

Android 簽署金鑰別名。用於 `flet build` Android 簽署，僅在設定 keystore 時使用。

### FLET_ANDROID_SIGNING_KEY_PASSWORD

Android 簽署金鑰密碼。若未設定但有設定 keystore 密碼，則 keystore 密碼會被重複使用。

### FLET_ANDROID_SIGNING_KEY_STORE

Android 上傳 keystore（.jks）的路徑。用於 `flet build` Android 簽署。

### FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD

Android keystore 密碼。若未設定則使用金鑰密碼。

---

## CLI 環境變數

### FLET_CLI_NO_RICH_OUTPUT

停用 CLI 主控台的 rich 輸出格式。預設 `"false"`。

### FLET_CLI_SKIP_FLUTTER_DOCTOR

建置失敗時略過執行 `flutter doctor`。預設 False。

---

## 平台與顯示

### FLET_PLATFORM

應用程式執行所在的平台。值可能為：`"android"`、`"ios"`、`"linux"`、`"macos"`、`"windows"` 或 `"fuchsia"`。

### FLET_HIDE_WINDOW_ON_START

設為 `true` 可讓應用程式啟動時隱藏主視窗。預設 False。

---

## 網頁伺服器

### FLET_FORCE_WEB_SERVER

設為 `true` 可強制以網頁應用模式執行。在無頭 Linux 主機上會自動設定。

### FLET_SERVER_IP

Web 應用程式監聽的 IP 位址，例如 `"127.0.0.1"`。預設 `0.0.0.0`（監聽所有 IP）。

### FLET_SERVER_PORT

TCP 連接埠。Linux 伺服器或設定了 `FLET_FORCE_WEB_SERVER` 時預設 `8000`，否則為隨機連接埠。

### FLET_SERVER_UDS_PATH

Unix Domain Socket（UDS）路徑。啟用 Unix 系統上的程序間通訊，格式為 `flet_<pid>.sock`。

### FLET_WEB_APP_PATH

網域後的 URL 路徑，例如 `"/apps/myapp"`。預設 `"/"`（根目錄）。

### FLET_WEB_NO_CDN

設為 `true` 可避免從 CDN 載入 CanvasKit、Pyodide 和字體。

### FLET_WEB_RENDERER

網頁渲染模式：`"canvaskit"`（預設）、`"skwasm"` 或 `"auto"`。

### FLET_WEB_USE_COLOR_EMOJI

設為 `True`/`true`/`1` 以載入彩色emoji網頁字體。

### FLET_WEB_ROUTE_URL_STRATEGY

URL 策略：`"path"`（預設）或 `"hash"`。

### FLET_WEBSOCKET_HANDLER_ENDPOINT

WebSocket 處理程式路徑。預設 `"/ws"`。

---

## OAuth

### FLET_OAUTH_CALLBACK_HANDLER_ENDPOINT

OAuth 處理程式自訂路徑。預設 `"/oauth_callback"`。

### FLET_OAUTH_STATE_TIMEOUT

OAuth 網頁流程完成的最長時間（秒）。預設 600。

---

## 上傳與工作階段

### FLET_MAX_UPLOAD_SIZE

上傳檔案的最大大小（位元組）。預設無限制。

### FLET_SECRET_KEY

用於簽署暫存上傳 URL 的密鑰。

### FLET_SESSION_TIMEOUT

工作階段生命週期（秒）。預設 3600。

### FLET_UPLOAD_DIR

應用程式「上傳」目錄的絕對路徑。

### FLET_UPLOAD_HANDLER_ENDPOINT

上傳處理程式自訂路徑。預設 `"/upload"`。
