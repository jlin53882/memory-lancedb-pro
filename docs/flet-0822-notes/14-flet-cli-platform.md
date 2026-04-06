# flet_cli 平台工具 — 學習筆記

> 來源：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet_cli\`  
> Flet 版本：0.82.2  
> 整理日期：2026-03-23

---

## flet create 專案建立

### 核心實作：`commands/create.py`

**支援的範本（`--template` 參數）：**

| 範本名稱 | 說明 |
|---------|------|
| `app`（預設） | 一般 Flet 應用程式 |
| `extension` | 瀏覽器延伸模組 |

**Cookiecutter 整合（第 75-85 行）：**
```python
cookiecutter(
    "gh:flet-dev/flet-app-templates",
    checkout=template_ref,        # 預設 = Flet 版本 base_version
    directory=options.template,   # "app" 或 "extension"
    output_dir=str(out_dir.parent),
    no_input=True,
    overwrite_if_exists=True,
    extra_context=template_data,
)
```
- 範本 repository：`flet-dev/flet-app-templates`（GitHub）
- 預設 checkout = Flet 的 semantic version base_version（如 `0.82.2` → `0.82`）
- `--template-ref` 可指定任意 git ref（branch / tag / commit）

**平台偵測（第 62-68 行）：**
```python
platform_name = {
    "windows": "windows",
    "darwin": "darwin",
    "linux": "linux",
}.get(system_name, system_name)
```
- 系統名稱統一轉小寫後比對，傳給 cookiecutter template context

**專案名稱處理（第 86-89 行）：**
- 若未指定 `--project-name`，預設使用輸出目錄名稱
- 透過 `flet.utils.slugify()` 轉換為合法的 slug（kebab-case）
- 寫入 `pyproject.toml` 的 `project.name` 欄位

**其他參數：**
- `--description`：專案描述，寫入 `pyproject.toml` 的 `project.description`

---

## flet doctor 環境檢查

### 核心實作：`commands/doctor.py`

**檢查項目（第 32-46 行）：**

| 檢查項目 | 輸出內容 |
|---------|---------|
| 作業系統 | 名稱（如 macOS）、版本、架構 |
| Flet 版本 | `flet.version.flet_version` |
| Python 版本 | `platform.python_version()` + 執行檔路徑 |

**已知限制：**
- 第 45 行有 `# TODO: output Flutter version, if installed` —  
  Flutter SDK 版本目前尚未實作（即使系統有安裝也不會顯示）

**程式碼結構（doctor.py 完整結構）：**
- 非常精簡，全部邏輯在 `handle()` 內一口氣完成
- 無法自訂檢查項目（無 subcommand / plugin 機制）

---

## flet emulators 模擬器管理

### 核心實作：`commands/emulators.py`

**支援的 action（第一個位置參數）：**

| action | 說明 | 所需參數 |
|--------|------|---------|
| `start` | 啟動模擬器 | `emulator`（ID 或名稱） |
| `create` | 建立新模擬器 | `emulator`（名稱） |
| `delete` | 刪除 Android 模擬器 | `emulator`（ID 或名稱） |
| （無 action） | 列出所有模擬器 | — |

**啟動模擬器（第 112-132 行 `_launch_emulator`）：**
```bash
flutter emulators --launch <emulator-id> --no-version-check --suppress-analytics [--cold]
```
- `--cold`：冷啟動（不使用快速啟動 snapshot）

**建立模擬器（第 156-185 行 `_create_emulator`）：**
```bash
flutter emulators --create --name <name> --no-version-check --suppress-analytics
```
- 名稱驗證（`_is_valid_emulator_name`，第 187-198 行）：只允許 `A-Za-z0-9._-`

**刪除模擬器（第 134-154 行 `_delete_emulator`）：**
- 透過 `AndroidSDK.delete_avd()` 呼叫 `avdmanager delete avd -n <name>`
- 需要先解析 ANDROID_HOME（從環境變數或 `AndroidSDK.android_home_dir()`）

**列舉模擬器（第 95-147 行 `_list_emulators`）：**
```bash
flutter emulators --no-version-check --suppress-analytics
```
- 解析 `flutter emulators` 輸出（第 218-260 行 `_parse_emulators_output`）
- 以 `•`（U+2022 bullet）作為欄位分隔符
- 解析後結構：`{id, name, platform, platform_label, manufacturer}`

---

## Android SDK 偵測

### 核心實作：`utils/android_sdk.py`

**路徑偵測順序（第 72-89 行 `android_home_dir`）：**

```
1. ANDROID_HOME  環境變數
2. ANDROID_SDK_ROOT 環境變數
3. Android Studio 安裝目錄：
   - Windows：~/AppData/Local/Android/Sdk
   - macOS：~/Library/Android/sdk
   - Linux：~/Android/Sdk
4. CLI 預設目錄：~/Android/sdk
```

**cmdline-tools 搜尋路徑（第 104-114 行 `cmdline_tools_bin`）：**
```python
home_dir / "cmdline-tools" / "latest" / "bin"
home_dir / "cmdline-tools" / "12.0" / "bin"
```

**最小安裝套件（第 18-22 行）：**
```python
MINIMAL_PACKAGES = [
    "cmdline-tools;latest",
    "platform-tools",
    "platforms;android-35",
    "build-tools;34.0.0",
]
```

**安裝時下載版本（第 12-13 行）：**
- `ANDROID_CMDLINE_TOOLS_DOWNLOAD_VERSION = "11076708"`
- `ANDROID_CMDLINE_TOOLS_VERSION = "12.0"`

**已安裝檢查（第 158-173 行 `has_minimal_packages_installed`）：**
- 透過 `home_dir.joinpath(*package.split(";"))` 檢查每個套件目錄是否存在
- 需同時滿足：cmdline-tools bin 存在 + 所有 MINIMAL_PACKAGES 目錄存在

---

## JDK / Flutter SDK 偵測

### JDK：`utils/jdk.py`

**版本要求（第 12-14 行）：**
```python
JDK_MAJOR_VER = 17       # 需要主版本 17
JDK_RELEASE = "17.0.13"
JDK_BUILD = "11"
```

**偵測順序（第 62-74 行 `install_jdk`）：**

```
1. JAVA_HOME 環境變數 → 檢查版本是否為 JDK 17
2. macOS：/usr/libexec/java_home → 檢查版本
3. 上述皆失敗：下載 Temurin JDK 17 安裝到 ~/java/<JDK_DIR_NAME>
```

**版本檢查（第 29-43 行 `check_jdk_version`）：**
```python
subprocess.run([<jdk_path>/bin/javac, "-version"])
# 解析 stdout 的第二個空白分隔區塊，取第一段（小數點前）為主版本號
```

**下載 URL（第 79-85 行）：**
```
https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13+11/
OpenJDK17U-jdk_{arch}_{platform}_hotspot_17.0.13_11.{ext}
```
- `ext`：macOS/Linux = `tar.gz`，Windows = `zip`

**macOS 安裝路徑修正（第 121 行）：**
```python
if platform.system() == "Darwin":
    install_dir = install_dir / "Contents" / "Home"
```

---

### Flutter SDK：`utils/flutter.py`

**版本基準（第 5 行）：**
```python
FLUTTER_VERSION = "3.24.3"  # 預設要安裝的版本
```

**偵測方式：**
- 目前 `flutter.py` 是純安裝导向，無偵測函式
- 需依賴外部 `flutter` CLI 在 PATH 中

**下載 URL 格式（第 10-25 行 `get_flutter_url`）：**

| 平台 | 架構 | URL pattern |
|------|------|-------------|
| Windows | 任意 | `.../windows/flutter_windows_{version}-stable.zip` |
| macOS | arm64 | `.../macos/flutter_macos_arm64_{version}-stable.zip` |
| macOS | x86_64 | `.../macos/flutter_macos_{version}-stable.zip` |
| Linux | 任意 | `.../linux/flutter_linux_{version}-stable.tar.xz` |

**安裝路徑（第 30-36 行 `get_flutter_dir`）：**
```python
# ~/flutter/<version>
home_dir = Path.home()
return os.path.join(home_dir, "flutter", version)
```

**安裝流程（第 44-74 行 `install_flutter`）：**
1. 若 `~/flutter/<version>` 已存在 → 直接返回（不重複下載）
2. 否則：下載 → 解壓到 `~/flutter/<version>_temp` → 移動 `flutter/` 到 `~/flutter/<version>` → 清理

---

## 重要發現與注意事項

### 1. `flet doctor` 目前不檢查 Flutter / Android SDK / JDK
- 只有作業系統、Python 版本、Flet 版本
- Flutter 版本輸出在 TODO 狀態（JDK 與 Android SDK 完全未檢查）
- 這表示 `flet doctor` 目前實用性有限，無法診斷平台工具鏈問題

### 2. `flet create` 的 template_ref 預設值等於 Flet version base_version
- 例如 Flet 0.82.2 → template checkout 為 `0.82`（第 75 行）
- 可透過 `--template-ref` 指定任意 branch/tag/commit

### 3. Android SDK 最小套件要求固定寫死
- `platforms;android-35` 和 `build-tools;34.0.0` 是寫死的（第 19-20 行）
- 未來 Flet 更新可能需要手動更新這些版本常數

### 4. JDK 偵測會繞過 JRE（只接受 JDK）
- `check_jdk_version` 只檢查 `bin/javac` 是否存在（第 35 行 `subprocess.run([.../javac, "-version"])`）
- 若 JAVA_HOME 指向 JRE（有 java 無 javac），會被當作無效並重新下載

### 5. Flutter SDK 需手動加入 PATH
- `flutter.py` 只做下載/安裝，沒有偵測現有 Flutter 的邏輯
- 若系統已安裝 Flutter 0.82.2，不會被利用，會重新下載到 `~/flutter/3.24.3`
- 目前 FLUTTER_VERSION 寫死為 `3.24.3`，與 Flet 0.82.2 無自動對應機制

### 6. `flet emulators delete` 只支援 Android
- 刪除路徑走 `avdmanager delete avd`，這是 Android AVD 專屬工具
- iOS 模擬器刪除未實作（`flet emulators delete` 對 iOS simulator ID 也會失敗）

### 7. `android_sdk.py` 的 `run()` 方法統一注入 JAVA_HOME
- 第 279-296 行：每次執行 SDK 命令前都會注入 `{"JAVA_HOME": self.java_home}`
- 若 `java_home` 為空字串，會導致 `JAVA_HOME=`（空值）傳入子程序，可能造成問題
