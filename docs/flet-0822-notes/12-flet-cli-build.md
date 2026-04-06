# flet_cli 建置命令 — 學習筆記

> 來源：`flet_cli` v0.82.2  
> 目標檔案：`build.py`、`build_base.py`、`pack.py`  
> 學習日期：2026-03-23

---

## flet build 支援平台

`flet build` 的 `target_platform` 接受 8 種值（`build.py` L22-33）：

| CLI 命令 | 平台代號 | 封裝格式 | 支援主機 OS |
|---|---|---|---|
| `flet build windows` | `windows` | `.exe` / `.dll`（`build/windows/x64/runner/Release/*`） | Windows |
| `flet build macos` | `macos` | `.app` bundle（`build/macos/Build/Products/Release/*.app`） | macOS |
| `flet build linux` | `linux` | bundle 目錄（`build/linux/{arch}/release/bundle/*`） | Linux |
| `flet build web` | `web` | HTML/JS/WASM（`build/web/*`） | any |
| `flet build apk` | `apk` | `.apk`（`build/app/outputs/flutter-apk/*`） | any |
| `flet build aab` | `aab` | `.aab`（`build/app/outputs/bundle/release/*`） | any |
| `flet build ipa` | `ipa` | `.ipa`（`build/ios/archive/*`, `build/ios/ipa/*`） | macOS only |
| `flet build ios-simulator` | `ios-simulator` | `.app`（`build/ios/iphonesimulator/*`） | macOS only |

**平台矩陣表**（`build_base.py` L177-193）：系統會自動顯示一張表格，標示目前主機可建置哪些目標。

**交叉平台限制**（`build_base.py` L103-117 `can_be_run_on`）：
- Windows 只能建 Windows
- macOS 可建 macOS / web / apk / aab / ipa / ios-simulator
- Linux 可建 Linux / web / apk / aab

> **注意**：所有平台（8 種）都可以在 `flet build <platform>` 中指定，但主機不符時會在 `validate_target_platform()`（`build_base.py` L418）就直接中斷並顯示矩陣表。

---

## build_base.py 核心流程

`BaseBuildCommand` 是所有建置命令的基礎類別，核心 `handle()` 流程定義在 `build.py` L45-80：

### 完整建置 Pipeline（順序執行）

```
1. initialize_command()        # build_base.py L395
   - 解析選項、建立目錄結構（build/flutter、build/site-packages 等）
   - 設定 self.out_dir、self.flutter_dir、self.pubspec_path

2. validate_target_platform()  # build_base.py L418
   - 檢查目前主機是否可建 target_platform
   - 不支援時顯示平台矩陣表並 exit(1)

3. validate_entry_point()      # build_base.py L445
   - 解析 Python 入口模組（--module-name 或 pyproject 的 tool.flet.app.module）
   - 預設為 main.py，否則報錯

4. setup_template_data()       # build_base.py L477
   - 匯聚所有模板變數（專案名、artifact name、bundle id、權限、splash 設定等）
   - 結果存至 self.template_data（dict）

5. create_flutter_project()    # build_base.py L596
   - 使用 cookiecutter 從 `gh:flet-dev/flet-build-template`（預設）產生 Flutter bootstrap 專案
   - HashStamp 機制：比對 hash，只有變更過才重新產生（增量建置）
   - 支援 --template、--template-ref、--template-dir 自訂模板

6. package_python_app()         # build_base.py L737
   - 呼叫 `serious_python:main package` 將 Python app + 依賴封裝成 `app/app.zip`
   - 處理 requirements.txt、pyproject dependencies、平台特定依賴
   - 支援 --exclude、--compile-app、--compile-packages、--cleanup-* 等選項

7. register_flutter_extensions() # build_base.py L672
   - 掃描 `build/flutter-packages/` 目錄下的 Flutter 擴充套件
   - 將其寫入 pubspec.yaml dependencies

8. create_flutter_project(second_pass=True)  # build_base.py L596
   - 若 extension 有變更，觸發第二次 cookiecutter pass
   - 更新 pubspec.yaml dependencies

9. update_flutter_dependencies() # build_base.py L706
   - 將步驟 7 發現的 extension dependencies 合併進 pubspec.yaml

10. customize_icons()            # build_base.py L770
    - 複製 `assets/icon*.png/jpg` 等圖檔到 Flutter images 目錄
    - 呼叫 `flutter_launcher_icons`產生各平台圖示
    - HashStamp 機制：無變更時跳過

11. customize_splash_images()   # build_base.py L860
    - 只針對 web / ipa / ios-simulator / apk / aab
    - 複製 splash 圖檔，呼叫 `flutter_native_splash:create`
    - 支援 light/dark 模式、平台自適應背景色

12. run_flutter()               # build.py L120
    - 組裝完整 `flutter build <command>` 命令
    - 注入 --build-number、--build-name、平台特定參數

13. copy_build_output()          # build_base.py L1075
    - 將 Flutter build 產物複製到輸出目錄（預設 `build/<dist>/`）
    - Android APK/AAB 會自動Rename（移除 `-release`、替換 `app` 前綴為 artifact name）

14. cleanup()                    # BaseFlutterCommand（父類）
    - 顯示成功訊息、移除暫存
```

### 核心設計模式

- **HashStamp 增量建置**（`build_base.py` L606-610, L778-788 等）：每個步驟都有 hash 比對，無變更時跳過該步驟，避免重複工作。
- **三層設定合併**（`build_base.py` L477 的 `setup_template_data`）：CLI 參數 > `tool.flet.<platform>.*` > `tool.flet.*` > 預設值。
- **cookiecutter 模板**（`build_base.py` L619-646）：Bootstrap Flutter 專案，完全由 `flet-build-template` repo 定義。
- **serious_python 封裝**（`build_base.py` L737）：將 Python app + site-packages 封裝成 zip，供 Flutter runtime 使用。

### 重要輔助資料結構

**cross_platform_permissions**（`build_base.py` L130-177）：

```python
{
    "location": {
        "ios_info_plist": {...},
        "macos_entitlements": {...},
        "android_permissions": {...},
        "android_features": {...},
    },
    "camera": {...},
    "microphone": {...},
    "photo_library": {...},
}
```

使用 `--permissions location camera` 即可自動設定對應平台的所有權限。

---

## flet pack vs flet build

這是兩個完全不同的封裝機制：

| 維度 | `flet pack` | `flet build` |
|---|---|---|
| **封裝工具** | PyInstaller（直接） | Flutter + serious_python |
| **原理** | 把 Python 直譯器 + 程式碼 + 依賴包成單一執行檔 | 建立 Flutter 專案 → serious_python 封裝 Python → Flutter build |
| **適用平台** | **僅桌面**（Windows/macOS/Linux） | 全部 8 種平台（desktop + web + mobile） |
| **輸出格式** | 單一 `.exe`（Windows）或 `.app` bundle（macOS）| 各平台原生格式（`.exe`/`.app`/`.apk`/`.ipa`/HTML 等） |
| **Python 綁定** | 完整 Python 環境（可用任何 Python 套件） | serious_python（有限制的 Python 子集） |
| **不需要 Flutter SDK** | ❌ 需要 PyInstaller | ✅ 需要 Flutter SDK |
| **asar 打包** | PyInstaller bootloader | serious_python → `app/app.zip` |
| **dist 預設路徑** | `dist/<name>` | `build/<platform>/` |
| **-i / --icon** | ✅ | ❌（需用 `assets/icon.png`） |
| **--add-data** | ✅ | ❌ |
| **--hidden-import** | ✅ | ❌ |

### flet pack 流程（pack.py L108-228）

```
1. 確保 flet_desktop_package 已安裝
2. 清理 build/ 和 dist/ 目錄（互動或 -y 自動）
3. 複製 flet bin 目錄（fletd、flet.exe 等）
4. Windows: 更新 flet.exe 的 icon 與版本資訊（update_flet_view_*）
5. macOS: 解包 flet-macos-amd64.tar.gz → assemble_app_bundle
6. 呼叫 PyInstaller.__main__.run(pyi_args)
7. 清理暫存目錄
```

### 何時用哪個？

- **桌面簡單散發** → `flet pack`（單一檔案，無需 Flutter SDK）
- **需要 APK/AAB/Web/iOS** → 只能用 `flet build`
- **需要完整 Python 相容性** → `flet pack`（serious_python 有限制）

---

## 建置產物結構

### `flet build` 輸出目錄

**預設**：`build/<platform>/`（例：`build/windows/`）  
**自訂**：`--output <dir>`

| 平台 | 產物路徑（相對於 out_dir） |
|---|---|
| `windows` | `build/windows/x64/runner/Release/*.exe` → 複製到 `out_dir/` |
| `macos` | `build/macos/Build/Products/Release/<artifact>.app` → 複製到 `out_dir/` |
| `linux` | `build/linux/{arch}/release/bundle/*` → 複製到 `out_dir/` |
| `web` | `build/web/*`（index.html、assets、flutter_*.js 等） |
| `apk` | `build/app/outputs/flutter-apk/*.apk`（預設 `app-release.apk`） |
| `aab` | `build/app/outputs/bundle/release/*.aab` |
| `ipa` | `build/ios/archive/*.xcarchive` + `build/ios/ipa/*.ipa` |
| `ios-simulator` | `build/ios/iphonesimulator/*.app` |

### Android APK/AAB 的 Rename 邏輯（`build_base.py` L1104-1151）

Flutter 輸出的 release 檔名為 `app-release.apk` / `app-<abi>-release.apk`。  
`rename_android_build_outputs()` 會自動：

1. 移除 `-release` 後綴
2. 將前綴 `app`置換為 `--artifact` 指定的名稱（或 `tool.flet.artifact`）

```
app-release.apk     →  myapp.apk
app-armeabi-v7a-release.apk → myapp-armeabi-v7a.apk
```

### serious_python 封裝產物

在 Flutter 專案內部（`build/flutter/app/app.zip`）：
- 包含 Python 入口模組 + 所有 `--exclude` 後的檔案
- 配合 `build/flutter-packages/` 放置額外套件
- 再由 Flutter runtime 載入執行

---

## 常用命令範例

### 基本建置

```bash
# 預設入口：main.py，輸出至 build/<platform>/
flet build windows
flet build macos
flet build linux
flet build web
flet build apk

# 指定輸出目錄
flet build windows -o ./dist/win

# 指定專案目錄
flet build apk ./myapp

# 指定入口模組
flet build web --module-name app

# 指定 Python 程式碼目錄（預設為 .）
flet build windows ./path/to/myapp
```

### 元數據相關

```bash
# 基本資訊
flet build macos \
  --project "MyApp" \
  --product "My Application" \
  --description "A cool app" \
  --org "com.example" \
  --bundle-id "com.example.myapp" \
  --company "Example Inc" \
  --copyright "Copyright 2026"

# 版本與建置號
flet build apk --build-number 42 --build-version "1.2.3"

# iOS 簽署（需要 Provisioning Profile）
flet build ipa \
  --ios-team-id "XXXXXXXXXX" \
  --ios-provisioning-profile "My Profile Name" \
  --ios-export-method "app-store"
```

### Android 相關

```bash
# APK（可分割 ABI）
flet build apk --split-per-abi

# AAB（Google Play 上傳用）
flet build aab

# 自訂 APK/AAB 檔名
flet build apk --artifact "my-cool-app"

# Android 簽署
flet build apk \
  --android-signing-key-store "./upload-keystore.jks" \
  --android-signing-key-store-password "password" \
  --android-signing-key-password "keypassword" \
  --android-signing-key-alias "upload"
```

### Web 相關

```bash
# 基本 web 建置
flet build web

# 自訂 base URL（適用於子目錄部署）
flet build web --base-url "/myapp/"

# 指定 web renderer
flet build web --web-renderer canvaskit
flet build web --web-renderer skwasm

# 停用 WASM（只用 JS）
flet build web --no-wasm

# 停用 CDN（離線可用）
flet build web --no-cdn

# PWA 顏色設定
flet build web \
  --pwa-background-color "#1a1a2e" \
  --pwa-theme-color "#e94560"
```

### 圖示與 Splash

```bash
# 圖示放在 assets/ 目錄，命名規則：
# icon.png (default), icon_ios.png, icon_android.png,
# icon_web.png, icon_windows.png, icon_macos.png

# Splash 圖放在 assets/
# splash.png, splash_dark.png, splash_ios.png,
# splash_android.png, splash_web.png 等

flet build apk \
  --splash-color "#FFFFFF" \
  --splash-dark-color "#1a1a2e" \
  --android-adaptive-icon-background "#3d5afe"
```

### 權限與平台設定

```bash
# 跨平台預設權限
flet build apk --permissions location camera microphone

# Android 專屬權限
flet build apk \
  --android-permissions "android.permission.BLUETOOTH=True"

# Android 功能設定
flet build apk \
  --android-features "android.hardware.camera.autofocus=True"

# iOS/macOS Info.plist 自訂
flet build ipa --info-plist "ITSAppUsesNonExemptEncryption=False"

# macOS Entitlements
flet build macos --macos-entitlements "com.apple.security.app-sandbox=True"
```

### 清理與快取

```bash
# 清除快取（強制完整重建）
flet build windows --clear-cache

# 編譯選項（預設關閉）
flet build windows --compile-app
flet build windows --compile-packages

# 清理不需要的檔案
flet build windows --cleanup-app --cleanup-app-files "*.tmp,__pycache__"
flet build windows --cleanup-packages --cleanup-package-files "*.pyc,.git"
```

### 高級與模板

```bash
# 自訂 Flutter bootstrap 模板
flet build apk --template "gh:myorg/my-flet-template"
flet build apk --template-ref "v1.0.0"
flet build apk --template-dir "my-template-folder"

# 額外傳給 flutter build 的參數
flet build apk --flutter-build-args "--dart-define=MY_KEY=MY_VALUE"

# 從原始碼安裝特定套件
flet build apk --source-packages "numpy" "pandas"
```

### flet pack（PyInstaller，桌面專用）

```bash
# 基本打包
flet pack ./myapp.py

# 指定名稱與圖示
flet pack ./myapp.py -n "MyApp" -i ./icon.ico

# 建立 one-folder bundle（而非單一 exe）
flet pack ./myapp.py -D

# 指定輸出目錄
flet pack ./myapp.py --distpath ./output

# 加入額外資料或二進位
flet pack ./myapp.py --add-data "config.json:." --add-binary "./native.dll:."

# 隱藏 import（動態載入的模組）
flet pack ./myapp.py --hidden-import "pkg_resources" --hidden-import "cython"

# Windows UAC 提升權限
flet pack ./myapp.py --uac-admin

# 直接刪除 build/dist 目錄（不詢問）
flet pack ./myapp.py -y
```

---

## 重要發現與注意事項

### 1. `flet build` 本質是 Flutter 封裝器

`flet build` 的核心是：
- 用 **cookiecutter** + `flet-build-template` 建立 Flutter 專案
- 用 **serious_python** 將 Python app 包成 `app.zip`（放進 Flutter assets）
- 再用 **Flutter build** 編譯成各平台原生格式

所有平台最終都走 `flutter build <command>`（`build.py` L122-127）。

### 2. HashStamp 增量建置節省時間

`build_base.py` 中每個修改步驟（template、icons、splash、package）都有 `HashStamp` 比對。只有 hash 改變才會重跑對應步驟。這是為什麼第二次建置通常比第一次快很多。

### 3. `--output` 的實際行為

- CLI `--output`（`-o`）對應 `self.out_dir`（最終產物目錄）
- 內部的中間檔案（`build/flutter/` 等）永遠在 `python_app_path/build/` 下
- Flutter 產物透過 `copy_build_output()` 複製到 `--output` 指定目錄

### 4. `--module-name` vs 預設 `main`

`validate_entry_point()`（`build_base.py` L445）預設找 `main.py`。若入口為 `app.py`，必須加 `--module-name app`。

### 5. Web 建置的 `--no-cdn` / `--no-wasm`

- `--no-wasm`：停用 WebAssembly，只編譯 JS（用 `--wasm` 參數控制）
- `--no-cdn`：CDN 外的 CanvasKit/Pyodide，離線也能跑

### 6. iOS `ipa`  vs `ios-simulator`

- `ipa` 需要 Provisioning Profile 才能產生 `.ipa`，否則只產生 `.xcarchive`
- `ios-simulator` 直接產生 `.app`，可用 `xcrun simctl install` 安裝

### 7. Android AAB 產物會被 Rename

Flutter 原生輸出 `app-release.aab`，`rename_android_build_outputs()` 會改為 `<artifact-name>.aab`。

### 8. `flet pack` 的 `--onedir` 僅 Windows

`--onedir`（`pack.py` L52）在 macOS 上會被忽略並印出警告（`pack.py` L202-205）。

### 9. 模板版本綁定

`create_flutter_project()`（`build_base.py` L596）預設以當前 `flet` 版本當作 template ref：

```python
template_ref = version.Version(flet.version.flet_version).base_version
```

意味著升級 flet 版本後，第一次建置會自動使用新版本的模板。

### 10. `--permissions` 是捷徑

`--permissions location camera` 等同於同時設定 iOS Info.plist、macOS entitlements、Android permissions、Android features，不需要分開寫。

---

*行數對照：build.py L1-148、build_base.py L1-1200、pack.py L1-230（已濃縮解讀）*
