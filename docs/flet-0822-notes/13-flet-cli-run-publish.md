# flet_cli 執行與發布 — 學習筆記

> 來源：flet_cli 0.82.2  
> 路径：`flet_cli\commands\run.py`、`debug.py`、`publish.py`、`serve.py`

---

## flet run 開發模式

### 核心流程（run.py）

`flet run` 是 Flet 開發的核心命令，啟動熱重載（hot reload）模式。

**流程架構：**

```
Handler (FileSystemEventHandler)
    ├── 啟動 Python 子程序（subprocess.Popen）
    ├── 用 watchdog/Observer 監控檔案變更
    └── on_any_event() → 檢測變更 → restart_program()
```

**重要行為：**

- **路徑解析**（第 108-118 行）：`script` 參數可以是檔案或目錄。若是目錄，預設找 `main.py`。
- **Module 模式**（第 105-107 行）：`-m` 參數將 script 視為 Python 模組路徑（如 `flet run -m my_app.main`）。
- **pyproject.toml 整合**（第 120-125 行）：讀取 `[tool.flet.app.path]` 決定實際腳本目錄。
- **自動安裝依賴**（第 97-100 行）：web 模式自動安裝 `flet_web`，其餘模式安裝 `flet_desktop`。

### 子程序環境變數

`start_process()`（第 193-220 行）設定以下環境變數傳給子程序：

| 環境變數 | 用途 |
|---------|------|
| `FLET_FORCE_WEB_SERVER` | 設為 `"true"` 時，強制使用 web server 模式 |
| `FLET_SERVER_PORT` | 指定 TCP 連接埠 |
| `FLET_SERVER_IP` | 指定主機 IP |
| `FLET_WEB_APP_PATH` | 網頁路徑或 app 名稱 |
| `FLET_SERVER_UDS_PATH` | Unix Domain Socket 路徑（非 Windows） |
| `FLET_ASSETS_DIR` | 靜態資源目錄 |
| `FLET_APP_STORAGE_DATA` | App 資料儲存目錄（`storage/data`） |
| `FLET_APP_STORAGE_TEMP` | App 暫存目錄（`storage/temp`） |
| `PYTHONIOENCODING` | 固定為 `utf-8` |

### 平台支援

- **Desktop**：啟動 `flet_desktop` 視窗，透過 `open_flet_view()` 開啟。
- **Web** (`-w`)：自動開啟瀏覽器，設定 `FLET_FORCE_WEB_SERVER=true`。
- **iOS / Android**：輸出 QR code，透過 `android.flet.dev` 或 `flet-host` 協定發布。
- **隱藏模式** (`-n`)：視窗啟動時隱藏。

### 熱重載 debounce

`on_any_event()`（第 235-248 行）：檔案變更後等待 0.5 秒（`> 0.5`）才重啟，防止短時間內連續觸發。

### --asar

**本檔案中未使用 `--asar` 參數。**`--asar` 應屬於 `flet build` 命令（包裝 desktop app）而非 `run`。

---

## flet debug 除錯功能

### 核心定位（debug.py）

`flet debug` 是對標 `flet run` 的 Flutter 模式，專為需要原生包裝（如 iOS/Android APK/IPA）的除錯場景設計。與 `run` 的本質差異：

- `run`：純 Python 熱重載，直接執行 Python 腳本。
- `debug`：透過 Flutter 工具鏈包裝 Python app，再部署到目標平台。

### 支援平台矩陣

```python
debug_platforms = {
    "windows": {"target_platform": "windows", "device_id": "windows"},
    "macos":   {"target_platform": "macos",   "device_id": "macos"},
    "linux":   {"target_platform": "linux",   "device_id": "linux"},
    "web":     {"target_platform": "web",     "device_id": "chrome"},
    "ios":     {"target_platform": "ipa",     "device_id": None},  # 需 --device-id
    "android": {"target_platform": "apk",     "device_id": None},  # 需 --device-id
}
```

### 執行流程（handle()，第 68-102 行）

1. `check_device_id()` — iOS/Android 必須指定 `--device-id`，否則中止。
2. `run_flutter_devices()` — 若有 `--show-devices`，僅列出可用設備。
3. `validate_target_platform()` — 驗證平台支援。
4. `validate_entry_point()` — 驗證入口腳本。
5. `setup_template_data()` — 設定 Flutter 專案模板資料。
6. `create_flutter_project()` — 建立 Flutter 專案。
7. `package_python_app()` — 將 Python app 包裝進 Flutter。
8. `register_flutter_extensions()` — 註冊 Flutter 擴充。
9. `update_flutter_dependencies()` — 更新依賴（第二階段）。
10. `customize_icons()`、`customize_splash_images()` — 自訂圖示與 Splash。
11. `run_flutter()` — 執行 `flutter run`（`--release` 可選）。

### 重要參數

- `--device-id / -d`：指定 iOS/Android 設備 ID。
- `--show-devices`：列出已連接的 iOS/Android 設備。
- `--release`：以 Release 模式編譯執行（預設為 Debug）。
- `--route`：指定 Web/iOS/Android 的初始路由。

---

## flet publish 發布目標

### 核心定位（publish.py）

`flet publish` 將 Flet app 編譯為**靜態網頁應用（Static Web App）**，包含完整的 Pyodide 運行時，讓 Python 程式直接在瀏覽器中執行。

### 輸出結構

```
dist/
├── index.html          # 主 HTML（含 Pyodide 加載腳本）
├── manifest.json       # PWA 資訊清單
├── app.tar.gz         # Python 程式碼 + requirements.txt
├── assets/            # 靜態資源
└── FontManifest.json  # 字型資訊清單
```

### 封裝邏輯（第 180-215 行）

`app.tar.gz` 排除：
- `.` 開頭的檔案（隱藏檔）
- `__pycache__`
- `requirements.txt`（單獨以根目錄形式加入）
- `assets/` 目錄（已单独拷貝到 dist/assets）
- `dist/` 目錄本身

### 依賴解析順序（第 145-164 行）

```
1. [tool.poetry.dependencies]（pyproject.toml）
2. [project.dependencies]（pyproject.toml）
3. requirements.txt
4. fallback: flet=={current_version}
```

### 重要參數

| 參數 | 說明 |
|------|------|
| `--distpath` | 輸出目錄，預設 `dist` |
| `--app-name` | PWA 全名（影響 manifest.json） |
| `--app-short-name` | PWA 簡稱 |
| `--app-description` | PWA 描述 |
| `--base-url` | 部署子目錄路徑（如 `/myapp`） |
| `--web-renderer` | `auto` / `canvaskit` / `skwasm` |
| `--route-url-strategy` | `path`（預設）或 `hash` |
| `--pwa-background-color` | 載入畫面背景色 |
| `--pwa-theme-color` | PWA 主題色 |
| `--no-cdn` | 離線部署（自行 hosting CanvasKit/Pyodide/字體） |
| `--pre` | 允許 micropip 安裝預發布版本套件 |
| `--assets` | 資源目錄，預設 `assets` |

### 發布目標（不含 GitHub Pages）

**本檔案未實作任何 GitHub Pages 上傳功能。** `flet publish` 只負責產生靜態檔案到 `dist/` 目錄，部署到 GitHub Pages 是使用者的責任（可手動上傳或用 GitHub Action）。

### --no-cdn 行為（第 220-223 行）

當 `--no-cdn` 啟用時：
1. 不從 CDN 載入 CanvasKit、Pyodide、字體。
2. 需自行在 `dist/` 中提供這些資源。
3. 同時修補 `FontManifest.json` 以使用本機字體。

---

## flet serve

### 用途（serve.py）

`flet serve` 是一個輕量級靜態檔案伺服器，預設監聽 `8000` 埠，用於本地預覽 `flet publish` 輸出的靜態網頁。

### 與 `flet run -w` 的差異

- `flet run -w`：啟動 Flet Python app 的動態 web 伺服器（帶熱重載）。
- `flet serve`：純靜態檔案服務，無 Python 程式執行能力。

### COOP/COEP 跨域隔離（CustomHandler，第 28-43 行）

```python
self.send_header("Cross-Origin-Opener-Policy", "same-origin")
self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
self.send_header("Access-Control-Allow-Origin", "*")
```

這三個 header 對於 **SharedArrayBuffer** 和高解析度計時器是必要的，也是 Flet Web（Pyodide/WASM）正常運作的基礎。

### 重要參數

- `web_root`：服務目錄，預設 `./build/web`。
- `-p / --port`：連接埠，預設 `8000`。

---

## 常用命令範例

```bash
# 開發模式（桌面視窗）
flet run my_app.py

# 模組模式熱重載
flet run -m my_app.main

# 指定連接埠與主機
flet run my_app.py -p 5000 --host "0.0.0.0"

# Web 模式（瀏覽器）
flet run my_app.py -w

# 隱藏視窗啟動
flet run my_app.py -n

# Android 設備（需先 --show-devices 確認 ID）
flet run my_app.py --android --port 8551

# 發布為靜態網頁
flet publish my_app.py --app-name "My App" --distpath ./dist

# 自訂 base URL（部署到子目錄）
flet publish my_app.py --base-url "/myapp"

# 離線部署（不依賴 CDN）
flet publish my_app.py --no-cdn

# 本地預覽靜態網頁
flet serve ./dist --port 8080

# Flutter debug 模式（macOS）
flet debug macos

# Flutter debug 模式（Android，指定設備）
flet debug android --device-id <device-id> --show-devices
```

---

## 重要發現與注意事項

### 1. `flet run` vs `flet debug` 的選擇

| 場景 | 推薦命令 |
|------|---------|
| 純 Python 熱重載開發 | `flet run` |
| 需要 iOS/Android 原生包裝除錯 | `flet debug` |
| 網頁靜態部署 | `flet publish` |
| 預覽靜態網頁 | `flet serve` |

### 2. `--asar` 不存在於 run/publish/serve/debug

`--asar` 是 `flet build` 命令（Desktop App 包裝）的參數，用於將 Python 程式封裝成 ASAR 壓縮格式。**`run`/`publish`/`serve` 均無此參數。**

### 3. iOS/Android 行動裝置模式的特殊處理（run.py 第 131-135 行）

- `port` 預設為 `8551`（iOS/Android）。
- iOS/Android 使用 QR code 掃描，URL 透過 `android.flet.dev` 或 `flet-host` 協定封裝。
- 預設會隱藏主控台輸出（因無瀏覽器可直接觀看）。

### 4. `flet publish` 的 Python 執行方式

Python 程式碼並非編譯成 JavaScript，而是**包進 `app.tar.gz`，由 Pyodide  runtime 在瀏覽器中執行**。這意味著發布的 app 仍依赖 Python 環境（Pyodide）。

### 5. `flet serve` 的跨域隔離 header

使用 `flet serve` 預覽時，這三個 header（COOP/COEP/ACAO）是正確渲染 Flet Web 的必要條件。本地開發時不應移除。

### 6. 熱重載 debounce 陷阱

`flet run` 的 debounce 為 0.5 秒（`current_time - self.last_time > 0.5`）。快速連續存檔可能只觸發一次重載，這是預期行為。

### 7. Windows 上的 UDS 限制

`flet run` 在非 Windows 平台使用 Unix Domain Socket（`FLET_SERVER_UDS_PATH`），Windows 則強制使用 TCP port（run.py 第 137-139 行）。
