# Flet 0.82.2 部署與診斷手冊

> **version:** flet:0.82.2
> **來源：** https://docs.flet.dev/ （官方文件）
> **最後驗證：** 2026-03-22
> **狀態：** 🚧 部分待驗證（需要實際專案實測）

---

## 1. Desktop 模式啟動方式

### ✅ 已驗證

**CLI 模式（無 `ft.run()` platform 參數）**

| 命令 | 行為 |
|------|------|
| `flet run` | 原生 OS 視窗（Desktop） |
| `flet run [script]` | 指定 script 執行 |
| `flet run --web` / `-w` | Web 瀏覽器模式 |
| `flet run --port 8080` | 指定連接埠（僅 web） |
| `flet run --recursive` | 遞迴監看目錄變更（熱重載） |
| `flet run --directory` | 監看腳本目錄 |

**重要：`ft.run()` 本身沒有 platform 參數**。Platform 是由 CLI 命令切換，不是 `ft.run()` 的參數。

```python
# 0.82.2 標準寫法
import flet as ft

def main(page: ft.Page):
    page.title = "My App"
    page.add(ft.Text("Hello"))

ft.run(main)  # 無 platform 參數，預設啟動 desktop
```

### ❌ 待驗證
- `ft.run()` 是否仍支援 `view` 參數（如 `ft.View.WEB`）？文件未提及。
- 在 0.82.2 中從 Web 模式改回 Desktop 是否有穩定性差異？

---

## 2. SnackBar 寫法（0.82.2）

### ✅ 已驗證

**新 API（官方推薦）：`page.show_dialog(ft.SnackBar(...))`**

```python
import flet as ft

def main(page: ft.Page):
    def on_click(e):
        page.show_dialog(ft.SnackBar(ft.Text("Hello, world!")))
    
    page.add(ft.Button("Open SnackBar", on_click=on_click))

ft.run(main)
```

**帶動作的 SnackBar：**
```python
snack_bar = ft.SnackBar(
    content=ft.Text("You did it!"),
    action="Undo it!",
    on_action=lambda e: data.decrement(),
)

def handle_button_click(e):
    data.increment()
    snack_bar.content.value = f"You did it x {data.counter}"
    if not snack_bar.open:
        page.show_dialog(snack_bar)
    page.update()
```

### ❌ 待驗證（與 0.28.3 `page.overlay.append()` 的差異）

| 項目 | 0.28.3 | 0.82.2 |
|------|--------|--------|
| 顯示方式 | `page.overlay.append(snack_bar)` + `page.update()` | `page.show_dialog(snack_bar)` |
| `open` 屬性 | `snack_bar.open = True` | 文件範例未使用 `open`，直接呼叫 `show_dialog()` |
| `page.update()` | 需要 | 需要（在修改內容後） |
| 舊 API `page.snack_bar` | ✅ | ⚠️ Issue #376 指出文件有誤，正確應為 `page.show_dialog()` |

> **⚠️ 已知問題：** GitHub Issue #376 指出官方 SnackBar 文件使用錯誤寫法（`page.snack_bar.open = True`），正確做法是 `page.show_dialog(snack_bar)`。
> 
> GitHub Issue #3499 顯示 `page.snack_bar` 寫法在某些版本可運作，但趨勢是朝 `show_dialog()` 統一。

### SnackBar 主要屬性

| 屬性 | 說明 |
|------|------|
| `content` | 主要內容（接受 `ft.Text` 或其他 Control） |
| `action` | 動作按鈕文字 |
| `on_action` | 動作按鈕點擊事件 |
| `duration` | 顯示時間（預設自動 dismiss） |
| `persist` | 是否保持顯示（不自動 dismiss） |
| `bgcolor` | 背景顏色 |
| `show_close_icon` | 是否顯示關閉圖示 |

---

## 3. Dialog / BottomSheet 寫法（0.82.2）

### ✅ 已驗證

**所有 Dialog 家族統一使用 `page.show_dialog()`**

```python
# AlertDialog
page.show_dialog(ft.AlertDialog(
    title=ft.Text("Session expired"),
    content=ft.Text("Please sign in again."),
    actions=[ft.TextButton("Dismiss")],
    open=True,
))

# BottomSheet
sheet = ft.BottomSheet(
    content=ft.Column(
        width=150,
        controls=[
            ft.Text("Choose an option"),
            ft.TextButton("Dismiss"),
        ],
    )
)
page.show_dialog(sheet)
```

> **重要：** `page.dialog` 屬性仍可使用（舊 API），但官方新文件傾向 `page.show_dialog()`。

---

## 4. 錯誤處理機制

### ✅ 已驗證

**`page.on_error` — 只捕獲未處理的例外**

```python
def main(page: ft.Page):
    def handle_error(e):
        print(f"Error: {e}")
        page.add(ft.Text(f"Error: {e}"))
    
    page.on_error = handle_error
```

### ❌ 待驗證（對照 0.28.3 已知行為）

| 行為 | 0.28.3 | 0.82.2 |
|------|--------|--------|
| `page.on_error` 捕獲一般未處理例外 | ✅ | ✅（文件記載相同） |
| `page.on_error` 捕獲 UI handler 異常（按鈕點擊等） | ❌ 否（Future 機制，只輸出 console） | ❓ 推测相同，待驗證 |
| UI handler 例外輸出位置 | Console / stdout | Console / stdout（推测相同） |
| Desktop 模式下 console 輸出位置 | CMD/PowerShell 終端機 | ❓ 待確認 |

> **防呆原則（沿用 0.28.3 結論）：**
> - 所有按鈕/事件 handler 仍需在 `did_mount()` 層級包 `try/except`
> - 例外訊息仍需顯示 SnackBar（不可依賴 `page.on_error` 捕获 UI handler 例外）
> - SnackBar 顯示仍需 `page.update()`

### ❌ 待驗證
- 0.82.2 Desktop 模式下 Python 例外是否仍無法被 `page.on_error` 捕獲？
- `page.on_error` 的事件物件結構是否改變？
- 是否仍需在 `did_mount` 包 try/except？

---

## 5. Web vs Desktop 差異

### ✅ 已驗證

| 特性 | Desktop | Web（Static） | Web（Dynamic） |
|------|---------|---------------|----------------|
| 啟動命令 | `flet run` | `flet run --web` | `flet run --web` |
| Python 執行環境 | 本機原生 | 瀏覽器（Pyodide/WASM） | 伺服器 |
| 啟動速度 | 快 | 慢（需載入 Pyodide） | 中 |
| Python 套件限制 | 無（原生） | ⚠️ Pyodide 不支援所有套件 | 無 |
| UI 延遲 | 零延遲 | 零延遲 | 網路延遲 |
| 程式碼保護 | 高（原生執行檔） | 低（瀏覽器可看） | 高（伺服器端） |
| 託管成本 | — | 免費/便宜 | 需伺服器 |

**Static vs Dynamic 抉擇：**
- **Static**：`flet publish` → GitHub Pages / Cloudflare Pages / Vercel（純靜態）
- **Dynamic**：`flet run --web` + WebSocket 伺服器 → 需要 Python 環境的 VPS

---

## 6. 部署方式

### ✅ 已驗證

#### `flet build` — 包裝為獨立執行檔

```bash
# 支援平台
flet build macos
flet build linux
flet build windows
flet build web
flet build apk
flet build aab          # Android
flet build ipa
flet build ios-simulator
```

**常見參數：**
```bash
flet build windows --output-dir ./dist
flet build macos --app-name "My App"
flet build web --web-renderer canvaskit  # 或 skwasm / auto
flet build web --base-url /myapp         # 子目錄發布
```

**前置需求：**
- Flutter SDK（自動下載，如未安裝）
- Windows build：需 Visual Studio + C++ 工作負載
- macOS build：需在 macOS 上執行
- Linux build：需在 Linux 上執行

#### `flet publish` — 發布為靜態 Web 應用

```bash
flet publish [script]
  --distpath DISTPATH          # 輸出目錄（預設 dist）
  --app-name APP_NAME
  --base-url BASE_URL          # 子目錄
  --web-renderer {auto,canvaskit,skwasm}
  --route-url-strategy {path,hash}
  --no-cdn                     # 離線/封閉環境
```

#### `flet create` — 快速建立專案

```bash
flet create my_project
```

**標準專案結構：**
```
my_project/
├── README.md
├── pyproject.toml
└── src/
    ├── assets/
    │   └── icon.png
    └── main.py          # 入口點，包含 ft.run(main)
```

**pyproject.toml 範例：**
```toml
[project]
name = "example"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["flet"]

[tool.flet]
org = "com.mycompany"
product = "My App"

[tool.flet.app]
path = "src"
```

---

## 7. 與 0.28.3 差異對照

| 項目 | 0.28.3 | 0.82.2 |
|------|--------|--------|
| `ft.run()` platform 參數 | ❌ 無 | ❌ 無（仍由 CLI 控制） |
| SnackBar 顯示 | `page.overlay.append()` 或 `page.snack_bar.open = True` | **`page.show_dialog(ft.SnackBar(...))`** |
| Dialog 顯示 | `page.dialog = xxx` / `page.overlay.append()` | **`page.show_dialog()`** |
| `page.on_error` 捕獲範圍 | 只捕非 UI handler 例外 | ✅ 相同（推测） |
| UI handler 例外處理 | Future 機制 → console | ✅ 相同（推测） |
| `page.update()` 必要性 | SnackBar 需要 | SnackBar 需要 |
| 預設執行模式 | Desktop | Desktop |
| `flet build` | 支援 | ✅ 支援（完整） |
| `flet publish` | 可能是實驗性 | ✅ 正式支援 |
| 專案結構 | 任意 `.py` | 建議 `src/main.py` + `pyproject.toml` |
| Python 版本需求 | ? | `>=3.10` |

---

## 8. ✅ 已驗證 / ❌ 待驗證 總清單

### ✅ 已驗證（可安全使用）
- [x] Desktop 模式：`flet run`（無參數）
- [x] Web 模式：`flet run --web`
- [x] SnackBar 0.82.2 標準寫法：`page.show_dialog(ft.SnackBar(...))`
- [x] AlertDialog / BottomSheet 寫法：`page.show_dialog()`
- [x] `page.on_error` 用途（捕獲未處理例外）
- [x] `flet build` 指令與平台支援矩陣
- [x] `flet publish` 指令用途
- [x] `ft.run()` 無 platform 參數
- [x] Python 版本需求 `>=3.10`
- [x] 標準專案結構（`src/main.py` + `pyproject.toml`）

### ❌ 待驗證（需要實際專案測試）
- [ ] `page.on_error` 是否仍無法捕獲 UI handler 例外（按鈕點擊等）
- [ ] UI handler 例外在 Desktop 模式的 console 輸出位置
- [ ] 舊 API `page.snack_bar.open = True` 是否仍可運作
- [ ] `page.dialog` 舊 API 是否仍支援
- [ ] 0.82.2 Desktop 穩定性是否與 0.28.3 有差異
- [ ] `ft.View.WEB` 等視圖常數是否仍存在
- [ ] `page.overlay.append()` 是否仍可使用

---

## 9. 防呆檢查清單（沿用 0.28.3 原則）

> ⚠️ 以下原則推測適用於 0.82.2，需驗證：

1. **主要 View 佈局在 `__init__` 完成**，避免把核心掛載放到 `build()`
2. **各頁 `did_mount()` 必加 `try/except`**，錯誤要可見（SnackBar）
3. **SnackBar 顯示必須用 `page.update()`**，不能用 `self.update()`
4. **`page.on_error` 無法捕獲 UI handler 異常**，這些例外只輸出到 console
5. **例外交互時 SnackBar 須同步 `page.update()`**

---

## 10. 重要文件 URL

| 主題 | URL |
|------|-----|
| 文件首頁 | https://docs.flet.dev/ |
| 執行應用（Desktop/Web） | https://docs.flet.dev/getting-started/running-app/ |
| 發布總覽 | https://docs.flet.dev/publish/ |
| flet build CLI | https://docs.flet.dev/cli/flet-build/ |
| flet publish CLI | https://docs.flet.dev/cli/flet-publish/ |
| Windows 打包 | https://docs.flet.dev/publish/windows/ |
| Web 發布 | https://docs.flet.dev/publish/web/ |
| SnackBar | https://docs.flet.dev/controls/snackbar/ |
| AlertDialog | https://docs.flet.dev/controls/alertdialog/ |
| BottomSheet | https://docs.flet.dev/controls/bottomsheet/ |
| Page 控制項 | https://docs.flet.dev/controls/page/ |
