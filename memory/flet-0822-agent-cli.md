# Flet CLI 指令手冊（v0.82.2）

> **版本標籤**：`flet:0.82.2`  
> **文件來源**：[https://docs.flet.dev/cli/](https://docs.flet.dev/cli/)  
> **維護日期**：2026-03-22  
> **語言**：繁體中文

---

## 目錄

1. [flet create](#1-flet-create) — 建立新專案
2. [flet run](#2-flet-run) — 熱重載執行
3. [flet build](#3-flet-build) — 跨平台打包
4. [flet debug](#4-flet-debug) — 偵錯模式執行
5. [flet pack](#5-flet-pack) — PyInstaller 打包
6. [flet publish](#6-flet-publish) — 發布為靜態 Web 應用
7. [flet serve](#7-flet-serve) — 靜態檔案服務器
8. [flet emulators](#8-flet-emulators) — 模擬器管理
9. [flet devices](#9-flet-devices) — 連接裝置列表
10. [flet doctor](#10-flet-doctor) — 環境檢測

---

## 1. `flet create`

### 用途
使用預先定義的範本建立一個新的 Flet 專案，包含初始目錄結構、中繼資料與必要檔案，快速啟動新專案。

### 語法
```
flet create [-h] [-v] [--project-name PROJECT_NAME]
            [--description DESCRIPTION]
            [--template {app,extension}]
            [--template-ref TEMPLATE_REF]
            [output_directory]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `output_directory` | 專案建立目錄，省略則在目前目錄建立 |
| `--project-name` | 專案名稱（寫入 pyproject.toml 等中繼資料） |
| `--description` | 專案簡短描述（中繼資料用） |
| `--template` | 範本類型：`app`（預設）或 `extension` |
| `--template-ref` | 指定 Git 分支/tag/commit 來使用自訂或開發版範本 |
| `-v, --verbose` | 詳細輸出（`-v` 一般，`-vv` 更詳細） |

### 使用範例
```bash
# 在目前目錄建立 app 範本專案
flet create .

# 在 myapp 目錄建立，並指定專案名稱
flet create --project-name "My App" --description "我的 Flet 應用" myapp

# 使用 extension 範本建立擴充套件專案
flet create --template extension my-extension

# 使用自訂範本分支
flet create --template-ref develop myapp
```

---

## 2. `flet run`

### 用途
以熱重載（hot reload）模式執行 Flet 應用程式。開發階段使用，修改程式碼後自動重載。

### 語法
```
flet run [-h] [-v] [-p PORT] [--host HOST] [--name APP_NAME]
         [-m] [-d] [-r] [-n] [-w] [--ios] [--android]
         [-a ASSETS_DIR] [--ignore-dirs IGNORE_DIRS]
         [script]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `script` | Python 程式進入點（預設：`.`） |
| `-p, --port` | 指定 TCP 或 HTTP 連接埠（隨機選擇預設值） |
| `--host` | Web 應用綁定的主機，`*` 表示所有 IP |
| `--name` | 應用程式唯一名稱（多應用同 port 時區分） |
| `-m, --module` | 將 script 視為 Python 模組路徑，如 `my_app.main` |
| `-d, --directory` | 監視 script 所在目錄並熱重載 |
| `-r, --recursive` | 遞迴監視所有子目錄的變更 |
| `-n, --hidden` | 啟動時隱藏視窗 |
| `-w, --web` | 以動態網站模式啟動，並自動開啟瀏覽器 |
| `--ios` | 在 iOS 裝置啟動 |
| `--android` | 在 Android 裝置啟動 |
| `-a, --assets` | 靜態資源目錄路徑（預設：`assets`） |
| `--ignore-dirs` | 監視時忽略的目錄（逗號分隔） |

### 使用範例
```bash
# 熱重載執行目前目錄的 app.py
flet run app.py

# 以模組方式執行
flet run -m my_app.main

# 監視目錄變更並熱重載
flet run -d app.py

# 遞迴監視，指定連接埠
flet run -d -r -p 8555 app.py

# 作為 Web 應用並隱藏視窗
flet run -w -n app.py

# 在 Android 裝置執行
flet run --android app.py

# 指定 assets 目錄
flet run -a ./public_assets app.py
```

---

## 3. `flet build`

### 用途
將 Flet Python 應用程式編譯打包為平台專屬的可執行檔或安裝包。支援 macOS、Linux、Windows 桌面平台，以及 Android（APK/AAB）、iOS（IPA/simulator .app）和 Web。

### 語法
```
flet build [-h] [-v] [-o OUTPUT_DIR]
           [--arch TARGET_ARCH [TARGET_ARCH ...]]
           [--exclude EXCLUDE [EXCLUDE ...]]
           [--clear-cache]
           [--project PROJECT_NAME] [--artifact ARTIFACT_NAME]
           [--description DESCRIPTION] [--product PRODUCT_NAME]
           [--org ORG_NAME] [--bundle-id BUNDLE_ID]
           [--company COMPANY_NAME] [--copyright COPYRIGHT]
           [--android-adaptive-icon-background COLOR]
           [--splash-color COLOR] [--splash-dark-color COLOR]
           [--no-web-splash] [--no-ios-splash] [--no-android-splash]
           [--ios-team-id ID] [--ios-export-method METHOD]
           [--ios-provisioning-profile PROFILE]
           [--ios-signing-certificate CERT]
           [--base-url URL]
           [--web-renderer {auto,canvaskit,skwasm}]
           [--route-url-strategy {path,hash}]
           [--pwa-background-color COLOR] [--pwa-theme-color COLOR]
           [--no-wasm] [--no-cdn]
           [--split-per-abi] [--compile-app] [--compile-packages]
           [--cleanup-app] [--cleanup-packages]
           [--flutter-build-args [ARGS ...]]
           [--android-permissions [PERMS ...]]
           [--permissions {location,camera,microphone,photo_library} ...]
           [--deep-linking-scheme SCHEME] [--deep-linking-host HOST]
           [--android-signing-key-store FILE]
           [--build-number NUM] [--build-version VER]
           [--template TEMPLATE] [--show-platform-matrix]
           [--yes] [--skip-flutter-doctor]
           {macos,linux,windows,web,apk,aab,ipa,ios-simulator}
           [python_app_path]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `target_platform`（位置引數） | 目標平台：`macos`、`linux`、`windows`、`web`、`apk`、`aab`、`ipa`、`ios-simulator` |
| `python_app_path` | Flet Python 程式目錄（預設：`.`） |
| `-o, --output-dir` | 輸出目錄 |
| `--arch` | 目標 CPU 架構（macOS/Android 多架構時使用，如 `--arch arm64 x64`） |
| `--bundle-id` | 應用程式 Bundle ID（如 `com.mycompany.app-name`） |
| `--project` | 專案名稱 |
| `--product` | 產品顯示名稱 |
| `--company` | 公司名稱（關於對話框用） |
| `--copyright` | 版權宣告 |
| `--build-number` | 內部版本號 |
| `--build-version` | 使用者看到的 x.y.z 版本字串 |
| `--web-renderer` | Web 渲染引擎：`auto`（預設）、`canvaskit`、`skwasm` |
| `--route-url-strategy` | 路由策略：`path`（預設）或 `hash` |
| `--base-url` | Web 應用的基礎 URL（用於子目錄部署） |
| `--permissions` | 權限：`location`、`camera`、`microphone`、`photo_library` |
| `--deep-linking-scheme` | Deep linking URL scheme（如 `https` 或 `myapp`） |
| `--android-signing-key-store` | Android 簽名 keystore `.jks` 檔路徑 |
| `--compile-app` | 預編譯 app 的 `.py` 為 `.pyc` |
| `--compile-packages` | 預編譯 site-packages 的 `.py` 為 `.pyc` |
| `--clear-cache` | 清除现有快取後開始建置 |
| `--split-per-abi` | 依 ABI 分割 APK（Android） |
| `--yes` | 跳過所有提示 |
| `--show-platform-matrix` | 顯示支援的平台矩陣 |

### 使用範例
```bash
# 建置 Windows 執行檔
flet build windows .

# 建置 macOS app（指定架構）
flet build macos --arch arm64 x64 .

# 建置 Android APK
flet build apk .

# 建置 Android AAB（發布用）
flet build aab --bundle-id "com.mycompany.myapp" .

# 建置 Web 應用
flet build web .

# 建置 Web 並指定基礎 URL
flet build web --base-url /myapp .

# 建置 macOS app 並設定簽名
flet build macos --ios-team-id TEAM123 --ios-signing-certificate "Apple Development" .

# 建置並清除快取
flet build windows --clear-cache .

# 顯示支援平台矩陣
flet build --show-platform-matrix
```

---

## 4. `flet debug`

### 用途
在指定平台（桌面、網頁、手機）上以偵錯模式執行 Flet Python 應用。支援 `--show-devices` 檢視可用裝置，以及 `--release` 執行正式版。

### 語法
```
flet debug [-h] [-v] [--device-id DEVICE_ID] [--show-devices]
           [--release] [--route ROUTE]
           [--arch TARGET_ARCH [TARGET_ARCH ...]]
           [--exclude EXCLUDE [EXCLUDE ...]] [--clear-cache]
           [--project PROJECT_NAME] [--artifact ARTIFACT_NAME]
           [--description DESCRIPTION] [--product PRODUCT_NAME]
           [--org ORG_NAME] [--bundle-id BUNDLE_ID]
           [--company COMPANY_NAME] [--copyright COPYRIGHT]
           [--base-url URL]
           [--web-renderer {auto,canvaskit,skwasm}]
           [--route-url-strategy {path,hash}]
           [--permissions {location,camera,microphone,photo_library} ...]
           [--build-number NUM] [--build-version VER]
           [--yes] [--skip-flutter-doctor]
           [{macos,linux,windows,web,ios,android}]
           [python_app_path]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `platform`（位置引數） | 目標平台：`android`、`ios`、`linux`、`macos`、`web`、`windows` |
| `python_app_path` | Flet Python 程式目錄（預設：`.`） |
| `--device-id` | 指定裝置 ID |
| `--show-devices` | 列出所有可用裝置並結束 |
| `--release` | 以 Release 模式執行（預設為 Debug） |
| `--route` | 指定初始路由 |
| `--arch` | 目標 CPU 架構 |
| 其他平台參數 | 與 `flet build` 共享（見第 3 節） |

### 使用範例
```bash
# 在目前平台的桌面環境偵錯執行
flet debug .

# 列出所有可用裝置
flet debug --show-devices

# 在 Android 裝置偵錯執行
flet debug android

# 在 iOS 裝置執行（Release 模式）
flet debug ios --release

# 在 macOS 執行並指定裝置 ID
flet debug macos --device-id 00001234-00123456789ABC
```

---

## 5. `flet pack`

### 用途
使用 PyInstaller 將 Flet 應用程式封裝為獨立的桌面可執行檔或 App Bundle。

### 語法
```
flet pack [-h] [-v] [-i ICON] [-n NAME] [-D]
          [--distpath DISTPATH]
          [--add-data [ADD_DATA ...]] [--add-binary [ADD_BINARY ...]]
          [--hidden-import [HIDDEN_IMPORT ...]]
          [--product-name PRODUCT_NAME] [--file-description DESC]
          [--product-version VER] [--file-version VER]
          [--company-name COMPANY] [--copyright COPYRIGHT]
          [--codesign-identity CODESIGN_IDENTITY]
          [--bundle-id BUNDLE_ID]
          [--debug-console]
          [--uac-admin]
          [--pyinstaller-build-args [ARGS ...]]
          [-y]
          script
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `script`（位置引數） | Python 程式進入點（**必要**） |
| `-i, --icon` | 圖示檔案路徑（`.ico`/Windows、`.icns`/macOS、`.png`/Linux） |
| `-n, --name` | 產生的可執行檔或 Bundle 名稱 |
| `-D, --onedir` | 建立一個資料夾 bundle 而非單一檔案（Windows） |
| `--distpath` | 輸出目錄（預設：`dist`） |
| `--add-data` |額外加入的非二進位檔案，格式：`source:destination` |
| `--add-binary` | 額外加入的二進位檔案，格式：`source:destination[:platform]` |
| `--hidden-import` | 手動新增動態匯入但靜態分析未偵測到的模組 |
| `--product-name` | 產品名稱（中繼資料） |
| `--company-name` | 公司名稱（Windows 中繼資料） |
| `--copyright` | 版權字串 |
| `--codesign-identity` | Code signing 身份（macOS） |
| `--bundle-id` | Bundle 識別符（macOS） |
| `--debug-console` | 顯示 Python debug 主控台（用於排錯） |
| `--uac-admin` | 要求系統管理員權限啟動（Windows UAC） |
| `-y, --yes` | 非互動模式，跳過所有提示 |

### 使用範例
```bash
# 基本封裝
flet pack app.py

# 指定名稱和圖示
flet pack -i icon.ico -n MyApp app.py

# 建立 one-folder bundle（Windows）
flet pack -D -n MyApp app.py

# 輸出到自訂目錄
flet pack --distpath ./output app.py

# 新增隱藏匯入模組
flet pack --hidden-import pkg_resources app.py

# 新增額外資料檔案
flet pack --add-data ./assets:assets app.py

# macOS 簽名並指定 Bundle ID
flet pack --codesign-identity "Apple Development" --bundle-id "com.myco.myapp" app.py

# Windows 要求系統管理員權限
flet pack --uac-admin -i icon.ico -n AdminApp app.py
```

---

## 6. `flet publish`

### 用途
將 Flet 應用程式編譯並封裝為獨立的靜態 Web 應用程式。

### 語法
```
flet publish [-h] [-v] [--pre]
             [-a ASSETS_DIR] [--distpath DISTPATH]
             [--app-name APP_NAME] [--app-short-name APP_SHORT_NAME]
             [--app-description APP_DESCRIPTION]
             [--base-url BASE_URL]
             [--web-renderer {auto,canvaskit,skwasm}]
             [--route-url-strategy {path,hash}]
             [--pwa-background-color COLOR]
             [--pwa-theme-color COLOR]
             [--no-cdn]
             [script]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `script` | Python 程式進入點（預設：`.`） |
| `-a, --assets` | 靜態資源目錄 |
| `--distpath` | 輸出目錄（預設：`dist`） |
| `--app-name` | 完整應用程式名稱（PWA 中繼資料用） |
| `--app-short-name` | 簡短名稱（主畫面捷徑/安裝提示用） |
| `--app-description` | 應用程式簡短描述（PWA manifest） |
| `--base-url` | 應用程式服務的基礎 URL（子目錄部署） |
| `--web-renderer` | Web 渲染引擎：`auto`（預設）、`canvaskit`、`skwasm` |
| `--route-url-strategy` | 路由策略：`path`（預設）或 `hash` |
| `--pwa-background-color` | 載入階段背景顏色（splash screen） |
| `--pwa-theme-color` | 安裝為 PWA 時瀏覽器 UI 預設顏色 |
| `--no-cdn` | 停用 CanvasKit、Pyodide、Fonts 的 CDN 載入（全離線部署） |
| `--pre` | 允許 micropip 安裝預發布版 Python 套件 |

### 使用範例
```bash
# 基本發布
flet publish app.py

# 指定 PWA 名稱和顏色
flet publish --app-name "我的應用" --pwa-theme-color "#2196F3" app.py

# 子目錄部署
flet publish --base-url /myapp app.py

# 全離線部署（不使用 CDN）
flet publish --no-cdn app.py

# 指定 assets 目錄
flet publish -a ./static app.py
```

---

## 7. `flet serve`

### 用途
以輕量級 Web 伺服器託管靜態檔案，並可選擇性地為 Flet Web 應用程式新增 WebAssembly 相關 Header。

### 語法
```
flet serve [-h] [-v] [-p PORT] [web_root]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `web_root` | 要服務的目錄（預設：`./build/web`） |
| `-p, --port` | 連接埠號（預設：`8000`） |
| `-v, --verbose` | 詳細輸出 |

### 使用範例
```bash
# 服務預設目錄（./build/web），使用預設連接埠 8000
flet serve

# 服務自訂目錄，指定連接埠
flet serve -p 8080 ./dist

# 詳細輸出
flet serve -v ./my-app-build
```

---

## 8. `flet emulators`

### 用途
列出、建立與啟動可用的模擬器（依賴 Flutter SDK 的模擬器功能）。

### 語法
```
flet emulators [-h] [-v] [--cold] [--no-rich-output]
               [--yes] [--skip-flutter-doctor]
               [{start,create,delete}] [emulator]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `action` | 執行動作：`start`、`create`、`delete` |
| `emulator` | 模擬器 ID 或名稱（start/create/delete 需要） |
| `--cold` | 以冷開機方式啟動模擬器 |
| `--no-rich-output` | 停用豐富輸出，改用純文字（Windows） |
| `--yes` | 所有提示自動回答 yes（不安裝依賴時跳過確認） |
| `--skip-flutter-doctor` | 建置失敗時跳過 Flutter doctor 檢查 |

### 使用範例
```bash
# 列出所有可用模擬器
flet emulators

# 啟動指定的模擬器
flet emulators start my-emulator

# 冷開機啟動
flet emulators start --cold my-emulator

# 建立新模擬器
flet emulators create new-emulator

# 刪除模擬器
flet emulators delete old-emulator
```

---

## 9. `flet devices`

### 用途
列出所有已連接的 iOS 和 Android 裝置（實體裝置或模擬器）。

### 語法
```
flet devices [-h] [-v] [--device-timeout SECONDS]
             [--device-connection {both,attached,wireless}]
             [--no-rich-output] [--yes] [--skip-flutter-doctor]
             [{ios,android}]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `platform`（位置引數） | 限定平台：`ios` 或 `android`，省略則列出所有 |
| `--device-timeout` | 等待裝置連接的超時秒數（預設：`10`） |
| `--device-connection` | 連線類型過濾：`both`（預設）、`attached`（USB）、`wireless` |
| `--no-rich-output` | 停用豐富輸出（Windows） |
| `--yes` | 所有提示自動回答 yes |
| `--skip-flutter-doctor` | 建置失敗時跳過 Flutter doctor 檢查 |

### 使用範例
```bash
# 列出所有已連接裝置
flet devices

# 只列出 Android 裝置
flet devices android

# 只列出 iOS 裝置
flet devices ios

# 只看 USB 有線連接的裝置
flet devices --device-connection attached

# 增加等待超時
flet devices --device-timeout 30
```

---

## 10. `flet doctor`

### 用途
檢查系統與環境設定，回報 Flet 開發所需的各項工具與依賴是否就緒。

### 語法
```
flet doctor [-h] [-v]
```

### 主要參數

| 參數 | 說明 |
|------|------|
| `-h, --help` | 顯示說明訊息 |
| `-v, --verbose` | 詳細輸出（`-v` 一般，`-vv` 更詳細） |

### 使用範例
```bash
# 基本環境檢測
flet doctor

# 詳細輸出
flet doctor -v
```

---

## 附錄：指令速查表

| 指令 | 主要用途 |
|------|---------|
| `flet create` | 從範本建立新專案 |
| `flet run` | 熱重載開發執行 |
| `flet build` | 打包為平台執行檔（桌面/行動/Web） |
| `flet debug` | 偵錯模式執行（支援多平台） |
| `flet pack` | PyInstaller 桌面打包 |
| `flet publish` | 發布為靜態 Web 應用 |
| `flet serve` | 靜態檔案 HTTP 服務 |
| `flet emulators` | 模擬器管理（清單/建立/刪除/啟動） |
| `flet devices` | 列出已連接的 iOS/Android 裝置 |
| `flet doctor` | 環境檢測（Flutter/Python 等） |
