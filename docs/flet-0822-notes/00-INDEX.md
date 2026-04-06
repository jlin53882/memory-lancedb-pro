# Flet 0.82.2 學習筆記 Index（完整版）

> 來源：`two_project\.venv\Lib\site-packages\flet` 完整原始碼
> 學習日期：2026-03-23｜Agent：10× M2.7 并發 × 2 批次（共 20 顆）

---

## 📚 全部筆記（20 份）

| # | 檔案 | 主題 | 核心檔案 |
|---|------|------|---------|
| 1 | `01-page-routing.md` | Page 與路由、生命週期鉤子、Dialog stack | `controls/page.py`, `controls/base_page.py` |
| 2 | `02-container-layout.md` | Container、Row/Column/Stack/GridView/ListView、ScrollableControl | `box.py`, `core/column.py`, ... |
| 3 | `03-buttons.md` | Button 家族（Button/ElevatedButton/OutlinedButton/TextButton/IconButton） | `buttons.py`, `material/button.py`, ... |
| 4 | `04-input-controls.md` | TextField/Dropdown/Slider/DatePicker/FilePicker | `textfield.py`, `dropdown.py`, `file_picker.py`, ... |
| 5 | `05-display-controls.md` | Text/TextSpan/Icon/Image/TextStyle | `core/text.py`, `core/icon.py`, `core/image.py`, ... |
| 6 | `06-dialogs-overlay.md` | AlertDialog/SnackBar/Banner/BottomSheet | `alert_dialog.py`, `snack_bar.py`, `bottom_sheet.py` |
| 7 | `07-navigation.md` | AppBar/NavigationBar/Tabs/NavigationDrawer/View | `app_bar.py`, `navigation_bar.py`, `tabs.py`, ... |
| 8 | `08-selection-controls.md` | Chip/Badge/Checkbox/Switch/Radio/SegmentedButton | `chip.py`, `badge.py`, `checkbox.py`, ... |
| 9 | `09-theme-decorations.md` | Theme/Border/BorderRadius/Padding/DataTable/ProgressBar | `theme.py`, `border.py`, `border_radius.py`, ... |
| 10 | `10-app-lifecycle.md` | ft.app/ft.run、ControlEvent、types.py 全域 Enum | `app.py`, `events.py`, `control_event.py`, `types.py` |
| 11 | `11-flet-web-fastapi.md` | FastAPI 整合、Session 管理、Static Files、上傳機制 | `flet_web/fastapi/app.py`, `flet_app.py`, ... |
| 12 | `12-flet-cli-build.md` | flet build 流程（8 平台）、build_base.py（1200 行核心） | `build.py`, `build_base.py`, `pack.py` |
| 13 | `13-flet-cli-run-publish.md` | flet run 熱重載、flet debug、flet publish | `run.py`, `debug.py`, `publish.py` |
| 14 | `14-flet-cli-platform.md` | flet create/doctor/emulators、Android SDK/JDK 偵測 | `create.py`, `doctor.py`, `emulators.py` |
| 15 | `15-flet-desktop.md` | flet_desktop 角色、桌面 runtime 啟動器 | `flet_desktop/__init__.py` |
| 16 | `16-messaging-pubsub.md` | PubSub 雙向索引、Session 生命週期、WebSocket msgpack 協議 | `messaging/`, `pubsub/` |
| 17 | `17-testing-hooks.md` | FletTestApp/Tester、React-like Hooks（use_state/use_effect/use_memo/@observable） | `testing/`, `components/hooks/` |
| 18 | `18-auth-services.md` | OAuth PKCE、URL Launcher/Share/Clipboard/Battery Service | `auth/`, `services/` |
| 19 | `19-desktop-controls.md` | Cupertino iOS 風格控制項、ListTile/Card/ExpansionTile | `cupertino/*.py`, `list_tile.py`, `card.py`, ... |
| 20 | `20-window-decorations.md` | Window/WindowDragArea/Badge/CircleAvatar/Tooltip/ProgressRing | `core/window.py`, `badge.py`, `tooltip.py`, ... |

---

## 🔑 重要必記差異（對照 0.28.3）

| 項目 | 舊版（0.28.3） | 0.82.2 |
|------|---------------|--------|
| 開對話框 | `page.open(dlg)` | `page.show_dialog(dlg)` |
| 關對話框 | `page.close()` | `page.pop_dialog()` |
| Container 滾動 | `Container(scroll=...)` | Container 無 scroll，移到內層 Column |
| ElevatedButton | `ft.ElevatedButton` | `ft.Button`（deprecated proxy） |
| Border.all | `ft.border.all()` | `ft.Border.all()`（deprecated warning） |
| Padding.symmetric | `ft.padding.symmetric()` | `ft.Padding.symmetric()`（deprecated warning） |
| TextField prefix | `prefix_text` | 移除，改用 Row 包裝 |
| Dropdown 事件 | `on_change` | `on_select` |
| FilePicker | `FilePicker(on_result=...)` | 屬性賦值：`picker.on_result = fn` |
| DatePicker 開啟 | `pick_date()` | `open()` 或 `show_dialog()` |
| Slider 事件 | `on_change`（拖動中） | `on_change` + `on_change_end` |
| 啟動 API | `ft.app()` | `ft.app()` deprecated → `ft.run()` |
| go() 路由 | `page.go(url)` | `page.go()` deprecated → `page.push_route()` |
| flet doctor | 實用 | 空殼，無法診斷平台工具鏈 |
| flet_desktop | 有 UI API | 只是啟動器，無桌面 UI API |
| Hooks | 無 | use_state / use_effect / use_memo / use_callback / use_ref |

---

## 📂 相關文件

- `docs/flet-0822-vs-0283.md` — 0.82.2 vs 0.28.3 完整版本差異速查表
- `docs/flet-ui-0283-design-audit.md` — Flet 0.28.3 設計稽核（含已知坑）
- `memory/flet-0822-KNOWLEDGE-INDEX.md` — flet 0.82.2 知識索引（two_project 用）

---

## 📊 學習統計

- 閱讀原始檔案：**120+ 個**
- 總產出：**21 份文件（共 ~318KB）**
- Runtime：20 agents 并發，總計約 **25 分鐘**
