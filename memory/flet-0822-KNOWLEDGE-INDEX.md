# Flet 0.82.2 知識庫索引

> **版本標籤**：`flet:0.82.2`
> **資料來源**：`https://docs.flet.dev`
> **建置日期**：2026-03-22
> **總計**：19 個檔案，約 229KB

---

## 快速定位

| 類別 | 檔案 | 大小 | 說明 |
|------|------|------|------|
| [📖 Cookbook](#cookbook) | `flet-0822-agent-cookbook.md` | 32.7KB | 21 個主題，含完整 PubSub |
| [🎛️ 控制項 A-E](#controls-ae) | `flet-0822-agent-controls-ae.md` | 11.4KB | AlertDialog～FilledIconButton |
| [🎛️ 控制項 F-M](#controls-fm) | `flet-0822-agent-controls-fm.md` | 11.6KB | FilledTonalButton～TextField |
| [🎛️ 控制項 N-R](#controls-nr) | `flet-0822-agent-controls-nr.md` | 13KB | NavigationBar～Row |
| [🎛️ 控制項 S-W](#controls-sw) | `flet-0822-agent-controls-sw.md` | 12.8KB | SafeArea～WindowDragArea |
| [🎛️ 控制項 Extra](#controls-extra) | `flet-0822-agent-controls-extra.md` | 15.2KB | Banner、BottomSheet、ListTile 等 17 個 |
| [⚙️ Services](#services) | `flet-0822-agent-services.md` | 15.7KB | 24 個服務（Accelerometer～Wakelock）|
| [💻 CLI](#cli) | `flet-0822-agent-cli.md` | 17.9KB | 10 個指令速查 |
| [🔤 Types](#types) | `flet-0822-agent-types.md` | 7.7KB | 類型系統速查 |
| [🌿 Env Variables](#env-vars) | `flet-0822-agent-env-vars.md` | 4.4KB | 環境變數完整列表 |
| [📦 Env Packages](#env-packages) | `flet-0822-agent-env-packages.md` | 4.3KB | 內建二元 Python 套件 |
| [🏗️ 宣告式 vs 命令式](#declarative) | `flet-0822-declarative-vs-imperative.md` | 8.6KB | 程式設計範式對照 |
| [📋 Logging](#logging) | `flet-0822-logging.md` | 2.9KB | 日誌策略 |
| [🚀 啟動與核心](#section1) | `flet-0822-section1-startup-core.md` | 9.6KB | Page/Theme/Window 設定 |
| [📐 版面配置](#section2) | `flet-0822-section2-layout.md` | 14.4KB | Container/Column/Row/Stack |
| [🔀 導航與狀態](#section3) | `flet-0822-section3-navigation.md` | 18.9KB | Tabs/NavigationBar/Drawer |
| [⌨️ 輸入與資料](#section4) | `flet-0822-section4-input.md` | 15.1KB | TextField/DataTable/Chart |
| [🚀 部署與除錯](#section5) | `flet-0822-section5-deploy-diagnostic.md` | 10.6KB | build/run/publish + 錯誤處理 |

---

## 詳細說明

### Cookbook
`flet-0822-agent-cookbook.md`（32.7KB）

涵蓋 21 個主題：
1. Accessibility（無障礙設計）
2. Adaptive Apps（自適應應用）
3. Animations（動畫）
4. Assets（資源檔案）
5. Async Apps（非同步應用）
6. Authentication（認證）
7. Client Storage（客戶端儲存）
8. Colors（顏色）
9. Control Refs（控制項引用）
10. Custom Controls（自訂控制項）
11. Drag and Drop（拖放）
12. Encrypting Sensitive Data（加密敏感資料）
13. Expanding Controls（展開控制項）
14. Fonts（字體）
15. Keyboard Shortcuts（鍵盤快捷鍵）
16. Large Lists（大型列表）
17. Pubsub（發布訂閱）✅
18. Read and Write Files（檔案讀寫）
19. Session Storage（工作階段儲存）
20. Subprocess（子程序）
21. Theming（主題）

---

### Controls A-E
`flet-0822-agent-controls-ae.md`（11.4KB）

涵蓋：AlertDialog、AnimatedSwitcher、AppBar、AutoComplete、AutofillGroup、Badge、Banner ✅、BottomAppBar ✅、BottomSheet ✅、Button、Card、Checkbox、Chip、CircleAvatar ✅、Column ✅、Container ✅、ContextMenu ✅、CupertinoActionSheet、CupertinoActivityIndicator、CupertinoAlertDialog、CupertinoButton、CupertinoCheckbox、CupertinoFilledButton、CupertinoListTile、CupertinoNavigationBar、CupertinoTextField、DatePicker、DateRangePicker、Divider、Dropdown ✅

---

### Controls F-M
`flet-0822-agent-controls-fm.md`（11.6KB）

涵蓋：FilledButton ✅、FilledIconButton、FilledTonalButton、FilledTonalIconButton、FloatingActionButton、GestureDetector ✅、Icon、IconButton ✅、Image、InteractiveViewer、ListTile ✅、ListView ✅、Map ⚠️ 404、Markdown ✅、MenuBar、MenuItemButton、OutlinedButton、OutlinedIconButton、PageView、Pagelet、Placeholder、ProgressBar、ProgressRing、Radio、RadioGroup、RangeSlider、ReorderableListView、ReorderableDragHandle、ResponsiveRow ✅、RotatedBox

---

### Controls N-R
`flet-0822-agent-controls-nr.md`（13KB）

涵蓋：NavigationBar、NavigationDrawer、NavigationRail、OutlinedButton、OutlinedIconButton、PageView、Pagelet、Placeholder、ProgressBar、ProgressRing、Radio、RadioGroup、RangeSlider、ReorderableListView、RotatedBox、Row ✅

---

### Controls S-W
`flet-0822-agent-controls-sw.md`（12.8KB）

涵蓋：SafeArea ✅、SearchBar ✅、SegmentedButton ✅、ShaderMask ✅、Shimmer ✅、Slider ✅、SnackBar ✅、Stack ✅、SubmenuButton、Switch ✅、Tabs ✅、Text ✅、TextButton ✅、TextField ✅、TimePicker ✅、Video ✅、View ✅、WebView、WindowDragArea ✅

---

### Controls Extra
`flet-0822-agent-controls-extra.md`（15.2KB）

涵蓋：Banner ✅、BottomAppBar ✅、BottomSheet ✅、Charts ⚠️ 404、CircleAvatar ✅、CupertinoActionButton ⚠️ 404、CupertinoContextMenu ✅、CupertinoPicker ✅、CupertinoSegmentedButton ✅、CupertinoSwitch ✅、ExpansionPanel ✅、ExpansionPanelList ✅、FilledButton ✅、GestureDetector ✅、Hero ✅、IconButton ✅、ListTile ✅、ListView ✅、Map ⚠️ 404、Markdown ✅、Responsive ⚠️ 404

---

### Services
`flet-0822-agent-services.md`（15.7KB）

涵蓋 24 個服務：
Accelerometer、Audio、AudioRecorder、Barometer、Battery、BrowserContextMenu、Clipboard、Connectivity、FilePicker、Flashlight、Geolocator、Gyroscope、HapticFeedback、Magnetometer、PermissionHandler、ScreenBrightness、SemanticsService、ShakeDetector、Share、SecureStorage、SharedPreferences、StoragePaths、UrlLauncher、UserAccelerometer、Wakelock

---

### CLI
`flet-0822-agent-cli.md`（17.9KB）

涵蓋：flet create、flet run、flet build、flet debug、flet pack、flet publish、flet serve、flet emulators、flet devices、flet doctor

---

### Types
`flet-0822-agent-types.md`（7.7KB）

涵蓋：ColorValue、PaddingValue、MarginValue、Number、StrOrControl、IconDataOrControl、Control 層級體系（Control→Widget→Container→LayoutControl→特定控制項）、AnimationStyle、Alignment、CrossAxisAlignment、MainAxisAlignment、BorderRadius、ClipboardContent、DragAnchor、FilePickerFileType、FilePickerMode、HrefTemplate、ObservedColorChange、OverlayColor、RefreshIndicationStyle、ScrollMode、TextAlign、TextDirection、TextStyle、VerticalAlignment、VisualDensity 等

---

### Env Variables
`flet-0822-agent-env-vars.md`（4.4KB）

涵蓋所有 Flet 環境變數：FLET_APP_STORAGE_DATA、FLET_APP_STORAGE_TEMP、FLET_ASSETS_DIR、FLET_PLATFORM、FLET_SERVER_IP/PORT、FLET_WEB_RENDERER、FLET_WEB_ROUTE_URL_STRATEGY、FLET_HIDE_WINDOW_ON_START、FLET_SECRET_KEY、FLET_SESSION_TIMEOUT、FLET_MAX_UPLOAD_SIZE、OAuth 相關變數、Android 簽名變數等

---

### Env Packages
`flet-0822-agent-env-packages.md`（4.3KB）

涵蓋：flet-desktop-light（pypi.flet.dev）、flet-desktop（舊版）、預設包含的二元 Python 套件說明

---

### Section 1-5 學習手冊章節

| 檔案 | 大小 | 主題 |
|------|------|------|
| `flet-0822-section1-startup-core.md` | 9.6KB | Page 初始化、Theme 設定、Window 屬性、View 架構 |
| `flet-0822-section2-layout.md` | 14.4KB | Container、Column、Row、Stack、GridView、ListView、ScrollableControl |
| `flet-0822-section3-navigation.md` | 18.9KB | Tabs、NavigationBar、NavigationRail、NavigationDrawer、PageView、View |
| `flet-0822-section4-input.md` | 15.1KB | TextField、TextField/TextFormField、Dropdown、Checkbox、Radio、Slider、Switch、DatePicker、TimePicker、DataTable |
| `flet-0822-section5-deploy-diagnostic.md` | 10.6KB | flet build、flet run、flet publish、flet debug、SnackBar 錯誤處理、桌面模式差異 |

---

### 附加參考

| 檔案 | 大小 | 說明 |
|------|------|------|
| `flet-0822-declarative-vs-imperative.md` | 8.6KB | 宣告式 vs 命令式程式設計範式 |
| `flet-0822-logging.md` | 2.9KB | 日誌策略與實作 |
| **`flet-0822-API.md`** | **51.6KB** | **⭐ 完整 API 掃描（親測）含所有類別方法簽名 + Breaking Changes 對照表 + Event 模擬方式** |

---

## ⚠️ 404 記錄（已跳過）

以下 URL 在 2026-03-22 抓取時返回 404：
- `https://docs.flet.dev/controls/codeeditor/` → 舊版路徑
- `https://docs.flet.dev/controls/colorpickers/` → 路徑已改
- `https://docs.flet.dev/controls/charts/` → 章節已移除或重構
- `https://docs.flet.dev/controls/cupertinoactionbutton/` → 路徑不符
- `https://docs.flet.dev/controls/map/` → 可能需要單獨設定
- `https://docs.flet.dev/controls/responsive/` → 可能已重構
- `https://docs.flet.dev/cookbook/pub-sub/` → 初次抓取 404，後已手動補完

---

## 與 0.28.3 版差異重點摘要

| 主題 | 0.28.3 | 0.82.2 |
|------|--------|--------|
| Page API | 大部分相同 | 擴充 View/TemeMode 選項 |
| Controls | 基礎覆蓋完整 | 更多 Flutter 原生控制項 |
| Services | 大部分相同 | 新增更多平台服務 |
| PubSub | `page.pubsub` | 相同 API |
| Theme | `Theme(color_scheme_seed)` | 相同 + 更多 nested theme 選項 |
| Navigation | Tabs/NavigationBar | 新增 NavigationRail/NavigationDrawer |
| Deployment | `flet build` | 完整重寫 build 系統，支援更多平台 |

---

*最後更新：2026-03-22*
