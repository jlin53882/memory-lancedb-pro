# flet_desktop 桌面平台 — 學習筆記

> 來源：`flet_desktop` v0.82.2
> 完整路徑：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet_desktop\`

---

## flet_desktop 的角色

### 與 flet 主套件的差異

| 維度 | `flet` 主套件 | `flet_desktop` |
|------|--------------|---------------|
| 定位 | 通用跨平台（Web / Mobile / Desktop） | Desktop 專屬 runtime 管理 |
| 主要匯出 | 所有 UI 控制項（`Text`, `Column`, `Page` 等） | **桌面程序啟動 / 關閉管理** |
| 是否含 UI 元件 | ✅ 是 | ❌ 否 |
| 是否含 Flutter runtime | ❌ 否（依賴系統環境） | ✅ 是（自帶 Flutter desktop bundle） |
| 核心職責 | Python ↔ Flutter bridge、UI 宣告式 API | **啟動桌面視窗程序**、管理生命週期 |

### 核心結論

`flet_desktop` 的定位是「桌面客戶端 runtime 啟動器」：
- 它**不提供**任何 UI 控制項（`ft.Text`、`ft.Button` 等都在 `flet` 主套件裡）
- 它專門負責**啟動一個獨立的 Flutter 桌面程序**（`flet.exe` / `Flet.app` / `flet` binary）
- 透過 `subprocess` / `asyncio.subprocess` 啟動客戶端，並用 PID file 追蹤
- 桌面 client 可以是：
  1. **`flet build` 產出的 build artifact**（優先使用，`build/windows/*.exe` 等）
  2. 包裝在 `flet_desktop/app/` 目錄下的 Flutter runtime
  3. `FLET_VIEW_PATH` 環境變數指向的開發者自訂路徑

---

## desktop 專屬 API

### `ft.desktop` 命名空間

經查閱 `__init__.py`，**沒有**獨立的 `ft.desktop` 命名空間模組。
`flet_desktop` 直接在 module level 匯出以下函式（均為 module-level functions，無 class）：

| API | 簽名 | 說明 |
|-----|------|------|
| `open_flet_view()` | `(page_url, assets_dir, hidden) -> (Popen, pid_file)` | 同步啟動桌面 client 进程 |
| `open_flet_view_async()` | `(page_url, assets_dir, hidden) -> (asyncio.Process, pid_file)` | 非同步啟動桌面 client |
| `close_flet_view()` | `(pid_file) -> None` | 透過 PID file 終止 client 进程 |
| `get_package_bin_dir()` | `() -> str` | 回傳 `flet_desktop/app/` 路徑（內含 bundled runtime） |
| 內部輔助 | `__get_desktop_distribution_name()` | 查 metadata 取得 distribution 名稱 |
| 內部輔助 | `__get_client_storage_dir()` | 回傳 `~/.flet/client/<dist>-<version>`（解壓快取路徑） |
| 內部輔助 | `__locate_and_unpack_flet_view()` | 核心解析邏輯：找 exe / 解壓 tar.gz |

### 重要發現：無 `ft.desktop` 命名空間

這與 `flet` 主套件不同——`flet` 有完整的 `ft` 命名空間（所有 UI 控制項），
而 `flet_desktop` **沒有** `desktop` 子模組。它的函式是直接挂在 module root 的。
使用方式為：

```python
import flet_desktop
proc, pid_file = flet_desktop.open_flet_view(page_url, assets_dir, hidden)
```

---

## Window / System Tray 等桌面功能

### Window Management

`flet_desktop` 本身**不直接管理 window**（沒有 `Window` class）。
Window 管理是 Flutter 桌面 client 內部處理的，但以下机制與 window 有關：

#### 1. `hidden` 參數 — 啟動時隱藏視窗

```python
# 第 148-150 行：hidden 參數會設定環境變數
if hidden:
    flet_env["FLET_HIDE_WINDOW_ON_START"] = "true"
```

這個環境變數傳給 Flutter client 程序，client 據此決定是否在啟動時隱藏視窗。

#### 2. PID File — 追蹤與終止

每次 `open_flet_view()` 會產生一個隨機 20 字元的 PID file（L130）：
```python
pid_file = str(Path(tempfile.gettempdir()).joinpath(random_string(20)))
```

Flutter client 啟動後會把自己的 PID 寫入此檔案。`close_flet_view()` 讀取 PID 後
發送 `SIGKILL` 信號（L108-110）終止進程。

#### 3. 平台特定啟動方式

- **Windows**（L152-175）：直接執行 `.exe`，傳 `page_url` 和 `pid_file` 作為參數
- **macOS**（L176-210）：用 `open -n -W --args` 指令啟動 `.app` bundle
- **Linux**（L211-245）：直接執行 `flet` ELF binary

### System Tray

查閱 `__init__.py` 後，**`flet_desktop` 沒有任何 System Tray API**。
System Tray 功能應該是由 Flutter 層的 `Page.tray` 或其他 Desktop API 處理，
而非 Python 層的 `flet_desktop`。

---

## Flutter Assets 結構

### 目錄架構

```
flutter_assets/
├── fonts/
│   └── MaterialIcons-Regular.otf          # Material Icons 符號字體
├── packages/                               # Flutter 插件的 assets
│   ├── cupertino_icons/
│   │   └── assets/CupertinoIcons.ttf      # iOS 風格圖示
│   ├── flutter_map/
│   │   └── lib/...                        # 地圖相關（leaflet 等）
│   ├── flutter_math_fork/
│   │   └── lib/katex_fonts/fonts/         # KaTeX 數學字體（12+ 種 variant）
│   ├── media_kit/
│   │   └── assets/...                     # 影片/音頻播放
│   ├── record_web/
│   └── wakelock_plus/
├── shaders/
│   ├── ink_sparkle.frag                    # Ink 特效著色器
│   └── stretch_effect.frag                # 拉伸動畫著色器
├── AssetManifest.bin                      # Flutter asset 清單（二進位格式）
├── FontManifest.json                       # 字體宣告（含 MaterialIcons + KaTeX 全家族）
├── NativeAssetsManifest.json               # Native assets（目前空）
└── NOTICES.Z                               # 授權聲明（Zlib 壓縮）
```

### 關鍵發現

1. **`FontManifest.json`** 包含完整的內嵌字體家族：
   - `MaterialIcons-Regular.otf`
   - `KaTeX_Main` / `KaTeX_Math` / `KaTeX_AMS` / `KaTeX_Caligraphic` ... 等 **12 種 KaTeX 字體變體**
   - `CupertinoIcons.ttf`

2. **`NativeAssetsManifest.json`** 目前是空的（`{"native-assets":{}}`），
   代表此版本尚無 FFI native asset 需要註冊。

3. **`AssetManifest.bin`** 為二進位格式，Flutter 用來快速查詢 asset 路徑，無法直接解讀。

4. **`NOTICES.Z`** 是 Zlib 壓縮的授權文字檔，儲存各开源元件的版權/授權聲明。

5. **`shaders/`** 包含 2 個 GLSL fragment shader：
   - `ink_sparkle.frag`：用於 Material Ink 效果（按壓反饋）
   - `stretch_effect.frag`：用於滑動/拖曳的彈性動畫

6. **`packages/`** 下都是 Flutter 插件的 assets，不是直接被 `flet_desktop` 使用，
   而是由 Flutter client 在运行时加载。

---

## 重要發現與注意事項

### 1. `flet_desktop` ≠ UI 框架

新手常見誤解：以為 `import flet_desktop` 後就能用 `flet_desktop.Text()` 等控制項。
**實際上**：`Text`、`Button`、`Page` 等全部來自 `flet` 主套件；`flet_desktop` 只负责桌面程序啟動。

### 2. 客戶端查找優先順序

```
flet build 產出 (build/windows/*.exe)   ← 優先使用
  → FLET_VIEW_PATH 環境變數              ← 其次
  → f 包裝內嵌的 tar.gz / exe             ← 最後 fallback
```

### 3. macOS 用 `open` 指令的特殊性

macOS 上使用 `open -n -W --args`（L208）而非直接執行 binary，
这是因为需要由 macOS 系统启动 `.app` bundle 以正確處理 sandbox / code signing。

### 4. Linux 的架構偵測

Linux 解壓哪個 tar.gz 是由 `get_arch()` 動態判斷的（L227），常見值如
`x64`、`arm64` 等，確保不同 CPU 架構拿到對應的 Flutter runtime。

### 5. PID File 安全問題

`close_flet_view()` 對終止失敗**完全忽略**（L111 `except Exception: pass`），
且只支援 `SIGKILL`（L110）。對於需要優雅關閉的應用，訊號處理方式可能需要客製。

### 6. Storage Cache 位置

解壓後的 Flutter runtime 緩存在 `~/.flet/client/<distribution>-<version>/`，
可避免每次都重新解壓，但若版本升級會有新目錄，舊的會殘留。
