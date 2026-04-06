# Flet 0.82.2 Page 與路由 — 學習筆記

> 學習日期：2026-03-23
> 原始檔案：
> - `page.py`（約 37KB）
> - `base_page.py`（約 22KB）

---

## 一、繼承架構

```
AdaptiveControl
    └── BasePage          # base_page.py（第 170 行）
            └── Page      # page.py（第 308 行）
```

**重要發現（0.82.2 新增）**：`BasePage` 已從 `Page` 中抽出成為獨立類別，使 `MultiView` 也能共用同一套底層機制。\
在 0.28.3 中，`Page` 直接繼承 `Control`，現在多了一層抽象。

---

## 二、Page 類的重要屬性

以下屬性**全部為唯讀**（read-only），由 Flet 框架在連線時自動設定：

| 屬性 | 型別 | 說明 | 行號 |
|------|------|------|------|
| `route` | `str` | 目前路由，預設 `"/"` | 320 |
| `web` | `bool` | 是否在瀏覽器中執行 | 323 |
| `pwa` | `bool` | 是否為 PWA 模式 | 326 |
| `debug` | `bool` | 是否為 debug 模式 | 329 |
| `wasm` | `bool` | 是否為 WebAssembly 模式 | 332 |
| `test` | `bool` | 是否為測試模式 | 335 |
| `multi_view` | `bool` | 是否支援多視圖（需驗證） | 338 |
| `pyodide` | `bool` | 是否為 Pyodide 模式 | 341 |
| `platform_brightness` | `Optional[Brightness]` | 主題亮度 | 347 |
| `client_ip` | `Optional[str]` | 客戶端 IP（僅 Web） | 350 |
| `client_user_agent` | `Optional[str]` | 瀏覽器 UA（僅 Web） | 353 |
| `platform` | `Optional[PagePlatform]` | 作業系統 | 356 |
| `fonts` | `Optional[dict[str, str]]` | 自訂字型對應表 | 359 |
| `window` | `Window` | OS 原生視窗控制（field default） | 314 |
| `multi_views` | `list[MultiView]` | 多視圖列表（0.82.2 新增） | 311 |
| `session` | `Session`（唯讀屬性） | 目前 session | 541 |
| `query` | `QueryString`（唯讀屬性） | URL query string 解析工具 | 551 |
| `url` | `Optional[str]`（唯讀屬性） | 完整 URL | 559 |
| `name` | `str`（唯讀屬性） | 頁面名稱 | 565 |
| `loop` | `asyncio.AbstractEventLoop`（唯讀屬性） | 事件循環 | 571 |
| `executor` | `Optional[ThreadPoolExecutor]`（唯讀屬性） | 執行緒池 | 577 |
| `auth` | `Optional[Authorization]`（唯讀屬性） | OAuth 授權狀態 | 583 |
| `pubsub` | `PubSubClient`（唯讀屬性） | 發布訂閱客戶端 | 590 |

---

## 三、Page 類的重要方法

### 3.1 生命週期相關

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `run_task(handler, *args, **kwargs)` | 在 page 事件循環中執行 coroutine | handler: coroutine 函式，其餘傳給 handler | `Future[RetT]` | 417 |
| `run_thread(handler, *args, **kwargs)` | 在執行緒池中執行同步函式 | handler: 同步函式，其餘傳給 handler | `None` | 450 |

> `did_mount` / `will_unmount`：**需驗證** — 在 `page.py` 與 `base_page.py` 中**未找到**這兩個方法。它們可能繼承自 `BaseControl`（0.28.3 的 `Control`），建議查閱 `base_control.py`。

### 3.2 路由導航

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `push_route(route, **kwargs)` | **async** — 推送新路由到瀏覽器歷史堆疊 | `route: str`, `**kwargs` 會拼接為 query string | `None` | 458 |
| `go(route, ...)` | **已廢棄（deprecated）**，使用 `push_route()` 取代 | 同上 | `None` | 440 |

**`push_route` 詳細說明**（行 458-510）：
- 用途：改變 URL 並觸發 `on_route_change` 事件
- `**kwargs`：會自動呼叫 `query.post(kwargs)` 附加到 URL
- 實作：透過 `_invoke_method("push_route", arguments={"route": new_route})` 呼叫客戶端

**`go` 已廢棄**（行 440-455）：
- `@deprecated(version="0.80.0", delete_version="0.90.0")`
- 內部實作已改為 `asyncio.create_task(self.push_route(route, **kwargs))`

### 3.3 元件渲染（0.82.2 新增 render API）

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `render(component, *args, **kwargs)` | 渲染元件樹，取代 `views[0].controls` | component: callable，回傳 View/Control | `None` | 382 |
| `render_views(component, *args, **kwargs)` | 渲染為整個 `page.views` 列表 | 同上 | `None` | 396 |

**重要發現（0.82.2）**：這是全新的渲染 API，用於「元件驅動」（component-driven）模式，取代舊的手動 `page.add()` 流程。

### 3.4 狀態同步

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `update(*controls)` | 推送變更到客戶端 | 可指定特定 controls，或留空更新整頁 | `None` | 406 |
| `schedule_update()` | 將 page 排入批次更新佇列 | 無 | `None` | 402 |
| `error(message)` | 報告錯誤訊息到客戶端 | `message: str` | `None` | 413 |

### 3.5 OAuth 認證

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `login(provider, ...)` | 發起 OAuth 流程 | `provider: OAuthProvider`, `fetch_user`, `fetch_groups`, `scope`, `saved_token`, etc. | `Authorization` | 496 |
| `logout()` | 清除授權狀態 | 無 | `None` | 575 |

### 3.6 檔案上傳

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `get_upload_url(file_name, expires)` | 產生預簽名上傳 URL | `file_name: str`, `expires: int`（秒） | `str` | 473 |

### 3.7 裝置控制

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `get_device_info()` | 取得裝置資訊 | 無 | `Optional[DeviceInfo]` | 610 |
| `set_allowed_device_orientations(orientations)` | 限制允許的螢幕方向（僅限手機） | `orientations: list[DeviceOrientation]` | `None` | 620 |

---

## 四、BasePage 類的重要屬性

### 4.1 檢視與佈局

| 屬性 | 型別 | 說明 | 行號 |
|------|------|------|------|
| `views` | `list[View]` | 視圖堆疊（預設 `[View()]`） | 189 |
| `controls` | `list[BaseControl]`（屬性代理到底層 view） | 根視圖的子控制項 | 370 |
| `overlay` | `list[BaseControl]` | 覆蓋層控制項（位於內容上方） | 363 |
| `appbar` | `Union[AppBar, CupertinoAppBar, None]` | 頂部 AppBar | 377 |
| `bottom_appbar` | `Optional[BottomAppBar]` | 底部 AppBar | 390 |
| `navigation_bar` | `Optional[Union[NavigationBar, CupertinoNavigationBar]]` | 底部導航列 | 400 |
| `drawer` / `end_drawer` | `Optional[NavigationDrawer]` | 左側/右側抽屜 | 415 / 429 |
| `floating_action_button` | `Optional[FloatingActionButton]` | FAB | 448 |
| `floating_action_button_location` | `Optional[Union[FloatingActionButtonLocation, OffsetValue]]` | FAB 位置 | 456 |

### 4.2 主題

| 屬性 | 型別 | 說明 | 行號 |
|------|------|------|------|
| `theme_mode` | `Optional[ThemeMode]` | 主題模式（預設 `SYSTEM`） | 193 |
| `theme` | `Optional[Theme]` | Light 主題 | 197 |
| `dark_theme` | `Optional[Theme]` | Dark 主題 | 201 |
| `locale_configuration` | `Optional[LocaleConfiguration]` | 地區設定 | 209 |

### 4.3 媒體與視窗

| 屬性 | 型別 | 說明 | 行號 |
|------|------|------|------|
| `title` | `Optional[str]` | 視窗標題 | 217 |
| `media` | `PageMediaData` | 環境度量（padding、view_insets、pixel_ratio 等） | 244 |
| `on_resize` | `EventHandler[PageResizeEvent]` | 視窗大小改變事件 | 229 |
| `on_media_change` | `EventHandler[PageMediaData]` | 媒體環境變更事件 | 238 |
| `width` / `height` | `Optional[Number]` | 頁面寬/高（唯讀） | 253 / 261 |
| `enable_screenshots` | `bool` | 是否啟用截圖功能 | 221 |

### 4.4 佈局輔助

| 屬性 | 型別 | 說明 | 行號 |
|------|------|------|------|
| `spacing` | `Number` | 子控制項間距 | 501 |
| `padding` | `Optional[PaddingValue]` | 內距 | 510 |
| `bgcolor` | `Optional[ColorValue]` | 背景色 | 518 |
| `scroll` | `Optional[ScrollMode]` | 滾動模式 | 525 |
| `auto_scroll` | `bool` | 自動滾動到底部 | 533 |
| `horizontal_alignment` | `CrossAxisAlignment` | 水平對齊 | 471 |
| `vertical_alignment` | `MainAxisAlignment` | 垂直對齊 | 480 |
| `decoration` / `foreground_decoration` | `Optional[BoxDecoration]` | 背景/前景裝飾 | 438 / 444 |

---

## 五、BasePage 類的重要方法

| 方法 | 用途 | 參數 | 回傳 | 行號 |
|------|------|------|------|------|
| `update(*controls)` | 推送變更到客戶端 | 可指定特定 controls | `None` | 272 |
| `add(*controls)` | 新增控制項到底層 view | `*controls: Control` | `None` | 283 |
| `insert(at, *controls)` | 插入控制項到指定索引 | `at: int`, `*controls` | `None` | 291 |
| `remove(*controls)` | 移除特定控制項 | `*controls` | `None` | 298 |
| `remove_at(index)` | 移除指定索引的控制項 | `index: int` | `None` | 305 |
| `clean()` | 清除所有根視圖控制項 | 無 | `None` | 313 |
| `scroll_to(...)` | 滾動到指定位置 | `offset`, `delta`, `scroll_key`, `duration`, `curve` | `None`（async） | 318 |
| `show_dialog(dialog)` | 顯示對話框 | `dialog: DialogControl` | `None` | 323 |
| `pop_dialog()` | 關閉最上層對話框 | 無 | `Optional[DialogControl]` | 356 |
| `show_drawer()` | 顯示左側抽屜 | 無 | `None`（async） | 371 |
| `close_drawer()` | 關閉左側抽屜 | 無 | `None`（async） | 376 |
| `show_end_drawer()` | 顯示右側抽屜 | 無 | `None`（async） | 381 |
| `close_end_drawer()` | 關閉右側抽屜 | 無 | `None`（async） | 386 |
| `take_screenshot(...)` | 截圖 | `pixel_ratio`, `delay` | `bytes`（async） | 392 |

---

## 六、生命週期鉤子（on_connect / did_mount / will_unmount / on_disconnect）

### 6.1 Page 層級事件（page.py）

| 事件 | 觸發時機 | 行號 |
|------|---------|------|
| `on_connect` | Web 使用者（重新）連線到 session（refresh、重新鎖定電腦後重新連線）。**不同於** app 首次開啟 | 334 |
| `on_disconnect` | Web 使用者關閉瀏覽器 tab/window | 340 |
| `on_close` | Session 過期（預設 60 分鐘無活動） | 346 |
| `on_error` | 未處理的例外發生 | 362 |

> ⚠️ **`did_mount` / `will_unmount`**：在 `page.py` 和 `base_page.py` 中**未找到**這兩個鉤子。它們可能定義在 `BaseControl`（原 `Control`）中。需驗證。

### 6.2 BasePage 層級事件（base_page.py）

| 事件 | 觸發時機 | 行號 |
|------|---------|------|
| `on_resize` | 使用者改變瀏覽器或原生 OS 視窗大小 | 229 |
| `on_media_change` | `media` 環境度量改變（旋轉、鍵盤彈出等） | 238 |

### 6.3 路由相關事件

| 事件 | Payload 類型 | 說明 | 行號 |
|------|------------|------|------|
| `on_route_change` | `RouteChangeEvent` | 路由改變（程式化、編輯 URL、瀏覽器按鈕） | 296 |
| `on_view_pop` | `ViewPopEvent` | 使用者點擊 AppBar 的「返回」按鈕 | 303 |

### 6.4 平台事件

| 事件 | Payload 類型 | 說明 | 行號 |
|------|------------|------|------|
| `on_platform_brightness_change` | `PlatformBrightnessChangeEvent` | 主題亮度改變 | 288 |
| `on_locale_change` | `LocaleChangeEvent` | 主機平台的地區設定改變 | 291 |
| `on_app_lifecycle_state_change` | `AppLifecycleStateChangeEvent` | App 生命週期狀態改變 | 294 |
| `on_keyboard_event` | `KeyboardEvent` | 鍵盤按鍵按下 | 306 |

### 6.5 OAuth 事件

| 事件 | Payload 類型 | 說明 | 行號 |
|------|------------|------|------|
| `on_login` | `LoginEvent` | OAuth 登入成功或失敗 | 355 |
| `on_logout` | `ControlEvent` | `page.logout()` 完成後 | 365 |

---

## 七、Dialog API（0.82.2）

### 7.1 `show_dialog(dialog)` — base_page.py 第 323 行

```python
def show_dialog(self, dialog: DialogControl) -> None:
```

- 用途：顯示一個 Dialog，並將其加入 dialog stack 管理
- 參數：`dialog: DialogControl`（必須尚未 open）
- 行為：
  1. 檢查 dialog 是否已存在於 stack，若已存在則拋 `RuntimeError`
  2. 暫時包裝 `dialog.on_dismiss` handler，確保關閉時從 stack 移除並觸發原 handler
  3. 設定 `dialog.open = True`
  4. 加入 `_dialogs.controls` 並呼叫 `update()`
- **重要**：0.82.2 以前可能無統一的 dialog stack 管理，現在是 first-class API

### 7.2 `pop_dialog()` — base_page.py 第 356 行

```python
def pop_dialog(self) -> Optional[DialogControl]:
```

- 用途：關閉最上層開啟中的 dialog
- 行為：從 stack 找到最後一個 `open == True` 的 dialog，設為 `open = False` 並 update
- 回傳：關閉的 dialog，若無則 `None`

### 7.3 內部機制

```python
# base_page.py 第 181-182
_dialogs: "Dialogs" = field(default_factory=lambda: Dialogs())
```

```python
# base_page.py 末段
@control("Dialogs")
class Dialogs(BaseControl):
    controls: list[DialogControl] = field(default_factory=list)
```

Dialog stack 是透過一個內部 `Dialogs` 控制項（實作與 `Overlay` 類似）來管理的，底層呼叫 `self._dialogs.update()` 推送變更。

---

## 八、路由與 Navigation

### 8.1 路由變更偵測 — `before_event`（page.py 第 424 行）

```python
def before_event(self, e: ControlEvent):
    if isinstance(e, RouteChangeEvent):
        if self.__last_route == e.route:
            return False  # 忽略相同路由
        self.__last_route = e.route
        self.query()  # 重新解析 query string
```

**重要發現**：`before_event` 會在事件觸發前被呼叫，用於過濾重複路由事件。

### 8.2 View Pop 偵測（page.py 第 431 行）

```python
elif isinstance(e, ViewPopEvent):
    for v in unwrap_component(self.views):
        if v.route == e.route:
            e.view = v  # 補全 view 參考
            break
```

### 8.3 Query String 工具

```python
# page.py 第 555
@property
def query(self) -> QueryString:
    return self.__query
```

`QueryString` 類用於解析和操作 URL query string（`?key=value`），在 `push_route` 中用 `query.post(kwargs)` 附加參數。

### 8.4 路由相關的事件 Data Class

| 類別 | 欄位 | 行號 |
|------|------|------|
| `RouteChangeEvent` | `route: str` | 95 |
| `ViewPopEvent` | `route: str`, `view: Optional[View]` | 141 |

---

## 九、常用程式碼範例

### 9.1 基本路由設定

```python
import flet as ft

def main(page: ft.Page):
    page.title = "路由範例"

    def route_change():
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(title=ft.Text("首頁")),
                    ft.Button("去商店", on_click=lambda _: page.push_route("/store"))
                ]
            )
        )
        if page.route == "/store":
            page.views.append(
                ft.View(
                    route="/store",
                    controls=[
                        ft.AppBar(title=ft.Text("商店")),
                        ft.Button("回首頁", on_click=lambda _: page.push_route("/"))
                    ]
                )
            )
        page.update()

    page.on_route_change = route_change
    route_change()  # 初始化

ft.run(main)
```

### 9.2 Dialog 使用（0.82.2）

```python
def main(page: ft.Page):
    dlg = ft.AlertDialog(title=ft.Text("嗨！"))

    def open_dialog(_):
        page.show_dialog(dlg)  # 取代舊版 page.dialog = dlg; page.update()

    page.add(ft.Button("開啟對話框", on_click=open_dialog))
    page.add(ft.Button("關閉對話框", on_click=lambda _: page.pop_dialog()))
```

### 9.3 Async Task 執行

```python
async def fetch_data(page: ft.Page):
    await asyncio.sleep(2)
    page.add(ft.Text("資料載入完成！"))

def main(page: ft.Page):
    page.add(ft.Button("執行背景任務", on_click=lambda _: page.run_task(fetch_data, page)))
```

### 9.4 元件驅動渲染（0.82.2 新功能）

```python
def app_content():
    return ft.View(
        "/",
        controls=[
            ft.Text("Hello from component!"),
            ft.Counter(),  # reactive component
        ]
    )

def main(page: ft.Page):
    page.render(app_content)  # 取代手動 page.add() + update()
```

### 9.5 OAuth 登入

```python
from flet.auth.oauth_provider import GoogleOAuthProvider

def main(page: ft.Page):
    page.on_login = lambda e: print(f"登入結果: error={e.error}")

    async def on_auth_url(url):
        print(f"請拜訪: {url}")

    provider = GoogleOAuthProvider(client_id="...", redirect_url="...")
    page.run_task(page.login, provider,
                   on_open_authorization_url=on_auth_url)
```

### 9.6 Query String + 路由

```python
# 推送 /store?category=electronics&id=42
await page.push_route("/store", category="electronics", id=42)
# 解析當前 query
print(page.query.get("category"))  # "electronics"
```

### 9.7 視窗大小監聽

```python
def on_resize(e):
    print(f"新大小: {e.width}x{e.height}")

page.on_resize = on_resize
```

---

## 十、0.82.2 新增/變更整理

| 項目 | 說明 | 驗證狀態 |
|------|------|---------|
| `BasePage` 獨立成類 | 從 Page 中抽出，`MultiView` 共用 | ✅ 已確認 |
| `ServiceRegistry` | 服務控制項容器 | ✅ 已確認 |
| `render()` / `render_views()` | 全新元件驅動渲染 API | ✅ 已確認 |
| `push_route()` async | 取代同步 `go()` | ✅ 已確認 |
| `go()` deprecated | 改用 `push_route()` | ✅ 已確認 |
| `show_dialog()` / `pop_dialog()` | 統一 dialog stack 管理 | ✅ 已確認 |
| `on_platform_brightness_change` | 新平台事件 | ✅ 已確認 |
| `on_locale_change` | 新平台事件 | ✅ 已確認 |
| `on_keyboard_event` | 新鍵盤事件 | ✅ 已確認 |
| `MultiView` 支援 | `multi_views` 屬性 | ✅ 已確認 |
| OAuth 完整重構 | `login()` / `logout()` 全面更新 | ✅ 已確認 |
| `set_allowed_device_orientations()` | 新方法，限制螢幕方向 | ✅ 已確認 |
| `get_device_info()` | 現已支援所有平台 | ✅ 已確認 |
| URL launcher deprecated | `page.url_launcher` 等屬性即將移除 | ✅ 已確認 |
| `did_mount` / `will_unmount` | **需驗證**：可能移至 `BaseControl` | ⚠️ 待驗證 |

---

## 十一、重要發現與注意事項

1. **`BasePage` 的_controls 代理到底層 view**：`page.controls` 讀寫的是 `views[0].controls`，並非獨立的列表。任何修改都直接作用在根視圖上。

2. **Dialog API 的重大改變**：舊版 Flet（0.28.3）使用 `page.dialog = dlg; page.update()`，新版（0.82.2）改為 `page.show_dialog(dlg)` / `page.pop_dialog()` 的 stack 管理模式，更接近 Flutter 的 API。

3. **`push_route()` 是 async**：必須使用 `await` 或包裝在 `run_task()` 中，不能直接同步呼叫。舊版 `go()` 的同步包裝已廢棄。

4. **`on_connect` vs app 啟動**：`on_connect` 只在 Web 重新連線時觸發，**不等同於** app 首次開啟。生命週期的完整對應需要驗證 `did_mount` / `will_unmount` 的實際定義位置。

5. **Query string 整合**：在 `push_route()` 中直接傳 `**kwargs` 會自動附加到 URL，這是 0.82.2 的便利設計。

6. **服務屬性即將移除**：`url_launcher`、`browser_context_menu`、`shared_preferences`、`clipboard`、`storage_paths` 全部 deprecated（`version="0.80.0"`, `delete_version="0.90.0"`），應改用對應的獨立類別（如 `UrlLauncher()`）。

7. **`BaseControl` 改名**：`Control` → `BaseControl`，`ControlEvent` 拆出更多專用 event 類別（如 `RouteChangeEvent`、`ViewPopEvent` 等），架構更模組化。

8. **Session 相關**：所有 page 層級的非同步操作都需要 session 存在，若 session 已過期（`on_close`），會拋 `RuntimeError`。

---

*本筆記由 Sub-Agent 產出，原始分析完整程式碼。未驗證項目已標註「需驗證」，請實際操作確認。*
