# Flet 0.82.2 Section 1：啟動與核心架構

> version: flet:0.82.2
> 來源：[docs.flet.dev](https://docs.flet.dev/)（官方文件，抓取日期：2026-03-22）
> 抓取 URL：controls/page、controls/basepage、controls/view、controls/multiview、getting-started/create-flet-app、getting-started/running-app、getting-started/navigation-and-routing

---

## 1. `ft.run()` vs `ft.app()` — 標準啟動方式

### ✅ 已驗證

| API | 地位 | 說明 |
|-----|------|------|
| `ft.run(main)` | **0.82.2 標準寫法** | 官方 `flet create` scaffold 產出的 `main.py` 末尾直接呼叫 `ft.run(main)`。文件明確說：「The application ends with a `ft.run()` function which initializes the Flet app and runs `main()`.」 |
| `ft.app(main)` | 仍可使用（舊寫法） | 舊版教學、tutorial 仍廣泛使用 `ft.app(main)`。搜尋結果顯示 older docs 仍以 `ft.app()` 為主。兩者功能相同，都是 blocking call，啟動後呼叫 `main(page: ft.Page)`。 |

### ❌ 待驗證
- `ft.run()` 與 `ft.app()` 是否有功能差異（例如 `ft.run()` 是否支援額外參數）。官方文件目前只展示 `ft.run(main)` 作為 entry point，未說明兩者底層是否完全等價。

### 差異對照（與 0.28.3）
- **0.28.3**：主要用 `ft.app(main)` 或 `flet.app()` 作為啟動點。
- **0.82.2**：`flet create` 預設 scaffold 改用 `ft.run(main)`，但 `ft.app()` 仍可正常運作。

---

## 2. BasePage / Page / MultiView 架構關係

### ✅ 已驗證

```
AdaptiveControl
    └── BasePage           (controls/basepage)
            ├── Page       (controls/page)
            └── MultiView  (controls/multiview)
```

- **`BasePage`**：abstract base class，不直接实例化。提供所有 page 層級的通用功能：appbar、bgcolor、controls（根視圖的 controls）、drawer、navigation_bar、overlay、padding、spacing、theme、title、views 等。
- **`Page`**：繼承 BasePage。每個使用者 session 自動建立一個 Page instance。多了 session 管理、route、auth、client_ip、window、pubsub 等 session-level 功能。
- **`MultiView`**：繼承 BasePage。文件幾乎全 TBD（initial_data、view_id）。用於多視圖支援，具體功能待官方完善文件。

### 與 0.28.3 差異
- 0.28.3 沒有獨立的 `BasePage` class，當時的 Page 直接具備這些屬性。0.82.2 把 page-level 功能抽到 BasePage，是為了支援 MultiView（多視圖）。
- 0.28.3 沒有 MultiView。

---

## 3. View 的角色（类似 Screen？）

### ✅ 已驗證

- **View 是最上層的容器 control**，用於容納所有其他 controls。文件說：「View is the top most container for all other controls. A root view is automatically created when a new user session started. From layout perspective the View represents a Column control, so it has a similar behavior.」
- View 有自己的 `route`、`appbar`、`drawer`、`end_drawer`、`bottom_appbar`、`navigation_bar`、`floating_action_button`、overlay 等，等同於一個獨立的「頁面/畫面（Screen）」。
- View 的 `route` 欄位：文件說「not currently used by Flet framework, but can be used in a user program to update `Page.route` when a view popped」。也就是說 framework 目前不自動用 View.route 做路由綁定，需手動在程式中處理。
- View 有 `can_pop` 和 `on_confirm_pop`：可用於返回前確認的對話框。

### 與 0.28.3 差異
- 0.28.3 的「畫面」概念比較模糊，通常直接在 `page.controls` 塞內容。0.82.2 的 View 更明確是「一個頁面/screen」的抽象。

---

## 4. `page.views` 與 navigation 的關係

### ✅ 已驗證

- `BasePage.views` 屬性：「A list of views managed by the page. Each View represents a distinct navigation state or screen in the application. The first view in the list is considered the active one by default.」
- `Page` 有 `multi_views` 屬性（`list[MultiView]`）：與 MultiView feature 相關。
- `Page.multi_view` 屬性（bool）：是否以 multi-view 模式運行。

### navigation 流程（根據文件重建）

```
page.go("/new-route")
  → 1. 更新 page.route
  → 2. 呼叫 page.on_route_change 事件處理器（讓開發者更新 page.views）
  → 3. 呼叫 page.update()
```

- `page.on_route_change` 是 navigation 的核心鉤子。開發者在其中根據 `page.route` 決定 `page.views` 的內容（替換或切換 views list）。
- `page.on_view_pop`：當使用者點擊 AppBar 的自動「返回」按鈕時觸發。

### ❌ 待驗證
- `page.views` 具體要怎麼操作（替換整個 list？還是 append/pop？）。文件只說「views 是 managed by the page」，實際操作方式需看更多 examples。

### 與 0.28.3 差異
- 0.28.3 的 navigation 是直接操作 `page.controls`（替換根視圖內容）。0.82.2 多了 `page.views` 機制和 `on_route_change`，是更結構化的 routing。

---

## 5. `page.on_route_change` 的用法

### ✅ 已驗證

- **事件觸發時機**：當 `page.route` 發生變化（程式呼叫 `page.go()`、編輯 URL、瀏覽器上一頁/下一頁）。
- **文件中的標準 pattern**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text(f"Initial route: {page.route}"))

    def route_change(e: ft.RouteChangeEvent):
        page.add(ft.Text(f"New route: {e.route}"))

    page.on_route_change = route_change
    page.update()
```

- `e` 是 `ft.RouteChangeEvent`，有 `.route` 屬性。
- 常見 pattern：在 `on_route_change` 中根據 `e.route` 決定要顯示哪個 View，並操作 `page.views`。
- `page.go(route)` 是一個 helper method，等同於：設定 `page.route` + 觸發 `on_route_change` + `page.update()`。

### 與 0.28.3 差異
- 0.28.3 沒有 `on_route_change`，navigation 靠直接替換 `page.controls`。0.82.2 引入了完整 routing 事件系統。

---

## 6. 錯誤處理機制（`page.on_error` 在 0.82.2 還在嗎？）

### ✅ 已驗證 — `page.on_error` 仍然存在！

- **位置**：`Page` events（`controls/page/`）
- **說明**：「Called when unhandled exception occurs.」
- 事件簽名：`on_error: ControlEventHandler[Page] | None`
- 還有 `page.error()` 方法：「Report an application error to the current session/client.」
- `page.on_close`：session 過期（預設 60 分鐘）時呼叫。

### 其他錯誤相關
- `BasePage` 沒有 `on_error`，這是 `Page` 特有的。
- Auto-update 機制（`ft.context.disable_auto_update()` / `ft.context.enable_auto_update()`）可以更細粒度控制更新時機，間接幫助錯誤隔離。

### 與 0.28.3 差異
- 0.28.3 的 `page.on_error` 是灰色區塊防呆清單中建議開啟的。0.82.2 依然存在，功能相同。
- 0.82.2 新增了 `ft.context` 機制控制 auto-update，是新的錯誤處理輔助工具。

---

## 7. Getting Started URL 索引（0.82.2）

| URL | 內容 |
|-----|------|
| https://docs.flet.dev/ | 官方首頁，有基本 Counter 範例 |
| https://docs.flet.dev/getting-started/installation/ | 安裝方式 |
| https://docs.flet.dev/getting-started/create-flet-app/ | `flet create` scaffold，ft.run() 標準寫法，auto-update 機制 |
| https://docs.flet.dev/getting-started/running-app/ | `flet run` / `flet run --web`，hot reload |
| https://docs.flet.dev/getting-started/navigation-and-routing/ | 路由與 on_route_change 標準範例 |

---

## 8. ✅ 已驗證 vs ❌ 待驗證 總清單

### ✅ 已驗證（來源：docs.flet.dev 官方文件）
- [x] `ft.run(main)` 是 0.82.2 官方 scaffold 的標準啟動 API
- [x] `ft.app(main)` 仍可使用，功能相同
- [x] BasePage → Page / MultiView 繼承結構
- [x] View 是最上層容器，等同於 Column，等同於一個 Screen/頁面
- [x] `BasePage.views` 是 `list[View]`，第一個 view 是預設 active view
- [x] `page.on_route_change` 存在，用於 routing，接收 `RouteChangeEvent`
- [x] `page.go(route)` = 更新 route + 觸發 on_route_change + update
- [x] `page.on_error` 仍然存在（Page level），用於全域錯誤處理
- [x] `page.error()` 方法可主動報告錯誤給 client
- [x] `page.on_view_pop` 存在，AppBar 返回按鈕觸發
- [x] Auto-update 預設開啟（0.82.2 新機制）
- [x] MultiView 存在但文件 TBD

### ❌ 待驗證
- [ ] `ft.run()` 與 `ft.app()` 是否有參數差異
- [ ] `page.views` 的具體操作方式（替換 vs append vs 整體賦值）
- [ ] MultiView 的完整功能（文件 TBD）
- [ ] View.route 在 framework 層面的實際應用場景
- [ ] `page.render()` vs `page.render_views()` 的使用情境
- [ ] `ft.context.disable_auto_update()` 的邊界與注意事項

---

## 9. 與 0.28.3 差異對照表

| 主題 | Flet 0.28.3 | Flet 0.82.2 |
|------|------------|------------|
| 啟動 API | `ft.app(main)` 或 `flet.app()` | `ft.run(main)`（官方 scaffold 標準），`ft.app()` 仍可 |
| 架構 | 只有 `Page`，無 BasePage/MultiView 分層 | BasePage → Page/MultiView 繼承結構 |
| View | 概念模糊，通常直接操作 page.controls | View 是獨立的 Screen 容器，有自己的 route/appbar/nav |
| Navigation | 直接替換 `page.controls` | `page.views` list + `on_route_change` 事件驅動 |
| page.on_error | 存在（灰色畫面防呆建議開啟） | 仍存在，功能相同 |
| Auto-update | 需手動 `page.update()` | 預設自動，需手動關閉要用 `ft.context.disable_auto_update()` |
| MultiView | 無 | 有，但文件 TBD |
| Routing 事件 | 無 | `on_route_change`、`on_view_pop` |
| page.go() | 無 | 有，routing helper |
| View.on_confirm_pop | 無 | 有，返回確認 |
