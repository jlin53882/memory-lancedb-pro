# Flet 0.82.2 App 生命週期、事件與類型系統 — 學習筆記

> 閱讀日期：2026-03-23｜來源：two_project .venv｜版本：0.82.2

---

## ft.app() / ft.run() 啟動方式

### 1. `ft.app()` — 已廢棄（0.80.0 起）

**檔案：** `app.py`，第 33–36 行

```python
@deprecated("Use run() instead.", version="0.80.0", show_parentheses=True)
def app(*args, **kwargs):
    new_args = list(args)
    if "target" in kwargs:
        new_args.insert(0, kwargs["target"])
    return run(*new_args, **kwargs)
```

`ft.app()` 是 `ft.run()` 的包裝器，只是把 `target` 參數挪到位置參數。**已從 0.80.0 廢棄**，請一律使用 `run()`。

---

### 2. `ft.run()` — 目前主要 API

**檔案：** `app.py`，第 48–125 行

```python
def run(
    main: AppCallable,                              # 必填：app 入口（同步或 async）
    before_main: Optional[AppCallable] = None,     # 選填：main 前的初始化 hook
    name: str = "",
    host: Optional[str] = None,                    # web server bind IP
    port: int = 0,                                 # 0 = 由 OS 自動選 port
    view: Optional[AppView] = AppView.FLET_APP,    # 顯示模式（預設桌面視窗）
    assets_dir: Optional[str] = "assets",
    upload_dir: Optional[str] = None,
    web_renderer: WebRenderer = WebRenderer.AUTO,
    route_url_strategy: RouteUrlStrategy = RouteUrlStrategy.PATH,
    no_cdn: Optional[bool] = False,
    export_asgi_app: Optional[bool] = False,       # True → 回傳 ASGI app 而不跑 event loop
    target=None,                                   # 已廢棄的 main 別名
)
```

**重點：**
- `port=0`：讓 OS 自動挑一個閒置 port。
- `view` 預設 `AppView.FLET_APP`（桌面應用程式視窗），可改 `AppView.WEB_BROWSER` 在瀏覽器開。
- `export_asgi_app=True` 時不回傳 None，而是回傳一個 FastAPI ASGI app，適用於嵌入現有 ASGI 框架（如 FastAPI/Starlette）。
- `main` 可為同步函式、async 函式、generator 或 async generator。
- 底層統一走 `asyncio.run(run_async(...))`（第 121 行）。

---

### 3. `ft.run_async()` — 非同步版本

**檔案：** `app.py`，第 128–228 行

不使用 `asyncio.run()` 包裝，適合已存在 event loop 的情境（如 Jupyter）。

---

### 4. 傳輸層選擇邏輯

**檔案：** `app.py`，第 202–205 行

```python
is_socket_server = (
    is_embedded() or view in [AppView.FLET_APP, AppView.FLET_APP_HIDDEN, None]
) and not force_web_server
```

- **Socket Server**（`__run_socket_server`）：桌面應用 (`FLET_APP`)、embedded 模式
- **Web Server**（`__run_web_server` → FastAPI/uvicorn）：`WEB_BROWSER` 或 Linux server 環境
- **Pyodide**（`__run_pyodide`）：瀏覽器環境

---

### 5. Signal 優雅關閉

**檔案：** `app.py`，第 183–197 行

```python
def exit_gracefully(signum, frame):
    logger.debug("Gracefully terminating Flet app...")
    loop.call_soon_threadsafe(terminate.set)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)
```

收到 `SIGINT`（Ctrl+C）或 `SIGTERM` 時，設定 `terminate` Event，使 server 進入關閉流程。

---

### 6. Session 入口處理（`__get_on_session_created`）

**檔案：** `app.py`，第 235–268 行

此工廠函式建立 session callback，支援四種 `main` 形式：

| `main` 型態 | 處理方式 |
|---|---|
| async function | `await main(session.page)` |
| async generator | `async for _ in main(...): await session.after_event(...)` |
| sync generator | `for _ in main(...): await session.after_event(...)` |
| sync function | 直接 `main(session.page)` |

這裡有 `before_main` hook 的呼叫時機：在 page 建立後、跑 `main` 前（由 `FletSocketServer` 實作）。

---

## 全域事件（events.py）

**檔案：** `controls/events.py`

所有事件皆為 `@dataclass(kw_only=True)`，各自定義了與 Flutter 端通訊時的 `data_field`（壓縮後的欄位名）。

### 觸控手勢事件

| 事件類別 | 說明 | 重要欄位 |
|---|---|---|
| `TapEvent` | 點擊按下/釋放 | `kind: PointerDeviceType`, `local_position`, `global_position` |
| `TapMoveEvent` | 點擊時指標移動 | 多了 `delta`（移動增量） |
| `MultiTapEvent` | 多指點擊 | `correct_touches: bool`（是否達到 multi_tap_touches 門檻） |
| `LongPressDownEvent` | 長按候選（手勢未確認前） | `kind`, `local_position`, `global_position` |
| `LongPressStartEvent` | 長按正式開始 | 與上面類似但已確認 |
| `LongPressMoveUpdateEvent` | 長按後移動 | 多了 `offset_from_origin`, `local_offset_from_origin` |
| `LongPressEndEvent` | 長按結束 | 多了 `velocity` 速度向量 |

### 拖曳事件

| 事件類別 | 說明 |
|---|---|
| `DragDownEvent` | 拖曳開始接觸 |
| `DragStartEvent` | 拖曳正式確認 | 含 `kind`, `local_position`, `global_position`, `timestamp` |
| `DragUpdateEvent` | 拖曳進行中 | 含 `local_delta`, `global_delta`, `primary_delta` |
| `DragEndEvent` | 拖曳結束 | 含 `velocity`, `primary_velocity` |

### 縮放/旋轉事件

| 事件類別 | 說明 |
|---|---|
| `ScaleStartEvent` | 雙指縮放開始 | 含 `local_focal_point`, `global_focal_point`, `pointer_count` |
| `ScaleUpdateEvent` | 縮放/旋轉進行中 | 含 `horizontal_scale`, `vertical_scale`, `scale`, `rotation`, `focal_point_delta` |
| `ScaleEndEvent` | 縮放結束 | 含 `pointer_count`, `velocity` |

### 指標/指標裝置事件

| 事件類別 | 說明 |
|---|---|
| `PointerEvent` | 低層級指標事件，詳細裝置資訊 | 含 `pressure`, `pressure_min/max`, `distance`, `distance_max`, `size`, `radius_major/min`, `orientation`, `tilt` 等 |
| `HoverEvent` | **即 `PointerEvent` 的別名**（第 580 行） | — |
| `ForcePressEvent` | 壓力感測 | 含 `pressure`（正規化 0.0–1.0+） |
| `ScrollEvent` | 滾輪事件 | 含 `scroll_delta`（滾動量） |

---

## ControlEvent 結構

**檔案：** `controls/control_event.py`

### `Event` 基礎類別（泛型）

```python
@dataclass
class Event(Generic[EventControlType]):
    name: str                          # 事件名稱，如 "click"
    data: Optional[Any] = field(kw_only=True)  # 事件附帶資料
    control: EventControlType = field(repr=False)  # 發出事件的 control 實例

    @property
    def page(self) -> Union["Page", "BasePage"]:
        if not self.control.page:
            raise RuntimeError("event control is not attached to a page")
        return self.control.page

    @property
    def target(self) -> int:
        return self.control._i   # 發出事件 control 的內部 ID
```

- `Event` 是所有事件的基底類別，屬於**泛型**（`Generic[EventControlType]`）。
- `name`：事件名稱字串（如 `"click"`, `"change"`）。
- `data`：可選的附帶資料。
- `control`：發出事件的 control 實例。
- `page` property：透過 `self.control.page` 取得所屬 Page（若 control 未掛載到 page 會 raise RuntimeError）。
- `target` property：回傳 control 的內部 ID（`_i`），等於 `control.id`（若有的話）。

### `ControlEvent` 類型別名

```python
ControlEvent = Event[_BaseControlType]
```

`ControlEvent` 是最廣泛的事件類型，適用於任何 `BaseControl` 發出的事件。

### `MultiTapEvent` 的例外

`MultiTapEvent` 直接繼承 `ControlEvent`（而非 `Event[EventControlType]`），是唯一例外。

### 事件欄位類型解析工具

```python
def get_event_field_type(control: Any, field_name: str)
```

用於在 runtime 解析某 control 的某事件處理欄位（如 `on_click`）的實際事件 payload 型別。
實作方式：走訪 control 的 MRO、解析 ForwardRef、從泛型參數取出事件型別。

### 型別別名

```python
ControlEventHandler = Union[Callable[[], Any], Callable[[Event[EventControlType]], Any]]
EventHandler = Union[Callable[[], Any], Callable[[EventType], Any]]
```

代表兩種 handler 簽名：不帶參數，或帶一個事件 payload 參數。

---

## 重要類型列舉（types.py）

**檔案：** `controls/types.py`

### AppView — 應用程式呈現模式

```python
class AppView(Enum):
    WEB_BROWSER = "web_browser"       # 在瀏覽器開啟
    FLET_APP = "flet_app"             # 桌面視窗（預設）
    FLET_APP_WEB = "flet_app_web"     # 桌面視窗但用 web 渲染
    FLET_APP_HIDDEN = "flet_app_hidden"  # 隱藏視圖（背景服務）
```

### WebRenderer

```python
class WebRenderer(Enum):
    AUTO = "auto"          # 自動選擇（預設）
    CANVAS_KIT = "canvaskit"  # 使用 CanvasKit（較大、較快）
    SKWASM = "skwasm"      # 使用 Wasm 版 Skia（最新）
```

### RouteUrlStrategy

```python
class RouteUrlStrategy(Enum):
    PATH = "path"  # /page_name（預設）
    HASH = "hash"  # /#/page_name（適用於 SPA 靜態托管）
```

### ThemeMode

```python
class ThemeMode(Enum):
    SYSTEM = "system"  # 跟隨系統
    LIGHT = "light"
    DARK = "dark"
```

### TextAlign

```python
class TextAlign(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    JUSTIFY = "justify"  # 左右對齊
    START = "start"       # 與 TextDirection 一致的 left
    END = "end"           # 與 TextDirection 一致的 right
```

### ScrollMode

```python
class ScrollMode(Enum):
    AUTO = "auto"        # 需要時才顯示滾動條（預設）
    ADAPTIVE = "adaptive"  # 根據平台：web/桌面固定顯示
    ALWAYS = "always"
    HIDDEN = "hidden"    # 可滾動但隱藏滾動條
```

### MainAxisAlignment

```python
class MainAxisAlignment(Enum):
    START = "start"
    END = "end"
    CENTER = "center"
    SPACE_BETWEEN = "spaceBetween"
    SPACE_AROUND = "spaceAround"
    SPACE_EVENLY = "spaceEvenly"
```

### CrossAxisAlignment

```python
class CrossAxisAlignment(Enum):
    START = "start"
    END = "end"
    CENTER = "center"
    STRETCH = "stretch"
    BASELINE = "baseline"
```

### VerticalAlignment

```python
class VerticalAlignment(Enum):
    START = -1.0   # 對齊頂部
    CENTER = 0.0   # 垂直居中
    END = 1.0      # 對齊底部
```

### PagePlatform

```python
class PagePlatform(Enum):
    IOS, ANDROID, ANDROID_TV, MACOS, WINDOWS, LINUX
    # 含輔助方法：is_apple(), is_mobile(), is_desktop()
```

### AppLifecycleState

```python
class AppLifecycleState(Enum):
    SHOW = "show"       # 應用程式顯示
    RESUME = "resume"   # 獲得輸入焦點
    HIDE = "hide"       # 應用程式隱藏
    INACTIVE = "inactive"  # 失去輸入焦點
    PAUSE = "pause"     # 暫停（僅 mobile）
    DETACH = "detach"   # 退出並卸載（僅 iOS/Android）
    RESTART = "restart" # 從暫停恢復（僅 mobile）
```

### MouseCursor

大量列舉值（44 種），涵蓋各種指標狀態：`ALIAS`, `ALL_SCROLL`, `BASIC`, `CELL`, `CLICK`, `CONTEXT_MENU`, `COPY`, `DISAPPEARING`, `FORBIDDEN`, `GRAB`, `GRABBING`, `HELP`, `MOVE`, `NO_DROP`, `NONE`, `PRECISE`, `PROGRESS`, `RESIZE_*` 系列（12 種）, `TEXT`, `VERTICAL_TEXT`, `WAIT`, `ZOOM_IN`, `ZOOM_OUT`。

### PointerDeviceType

```python
class PointerDeviceType(Enum):
    TOUCH = "touch"
    MOUSE = "mouse"
    STYLUS = "stylus"
    INVERTED_STYLUS = "invertedStylus"
    TRACKPAD = "trackpad"
    UNKNOWN = "unknown"
```

### FontWeight

11 級（`NORMAL`, `BOLD`, `W_100` ~ `W_900`）。

### ResponsiveRowBreakpoint

```python
class ResponsiveRowBreakpoint(Enum):
    XS = "xs"   # ≥0 px
    SM = "sm"   # ≥576 px
    MD = "md"   # ≥768 px
    LG = "lg"   # ≥992 px
    XL = "xl"   # ≥1200 px
    XXL = "xxl" # ≥1400 px
```

### 其他重要類別

- **`Url`**：含 `url: str` + `target: Optional[UrlTarget]`
- **`UrlTarget`**：`BLANK`, `SELF`, `PARENT`, `TOP`（等於 HTML `<a target>`）
- **`Locale`**：含 `language_code`（預設 `"und"`）、`country_code`、`script_code`
- **`LocaleConfiguration`**：含 `supported_locales` + `current_locale`
- **`BlendMode`**：28 種混色模式（Flutter BlendMode 對應）
- **`ImageRepeat`**：`NO_REPEAT`, `REPEAT`, `REPEAT_X`, `REPEAT_Y`
- **`ClipBehavior`**：`NONE`, `ANTI_ALIAS`, `ANTI_ALIAS_WITH_SAVE_LAYER`, `HARD_EDGE`
- **`DeviceOrientation`**：`PORTRAIT_UP/DOWN`, `LANDSCAPE_LEFT/RIGHT`
- **`VisualDensity`**：`STANDARD`, `COMPACT`, `COMFORTABLE`, `ADAPTIVE_PLATFORM_DENSITY`
- **`StrokeCap`**：`ROUND`, `SQUARE`, `BUTT`
- **`StrokeJoin`**：`MITER`, `ROUND`, `BEVEL`

---

## deprecated.py（已廢棄工具）

**檔案：** `utils/deprecated.py`

### 1. `@deprecated` 裝飾器工廠

```python
def deprecated(
    reason: str,
    version: Optional[str] = None,
    delete_version: Optional[str] = None,
    show_parentheses: bool = False,
):
```

- 用於標記函式/方法已廢棄。
- 發出 `DeprecationWarning`（stacklevel=2，指向 caller）。
- `show_parentheses=True`：警告訊息會顯示 `func_name()` 而非 `func_name`。

### 2. `@deprecated_class` 裝飾器工廠

```python
def deprecated_class(reason: str, version: str, delete_version: str):
```

- 只針對 class，包裝 `__init__` 和 `__post_init__` 各自發警告。
- 不包裝整個 class（所以 class 的屬性/方法仍可正常走訪）。

### 3. `deprecated_warning()` 輔助函式

```python
def deprecated_warning(
    name: str,
    reason: str,
    version: str,
    delete_version: Optional[str] = None,
    type: str = "property",
):
```

- 手動發出標準化廢棄警告訊息，適用於無法用裝飾器的場合（如 property、slot）。
- `type` 參數可指定被廢棄物件的類型（預設 `"property"`）。

---

## Version

**檔案：** `version.py`

```python
flet_version = "0.82.2"        # Flet SDK 版本（hardcoded，CI 替換）
flutter_version = "3.41.4"     # Flutter SDK 版本（CI 替換）
pyodide_version = "0.27.7"     # Pyodide 版本（flet build web 用）
```

`__version__ = flet_version`（對外暴露）。

版本解析優先順序：
1. CI 預設值（已設定在原始碼中的 `"0.82.2"`）
2. Git tag（若從 source 執行且無 CI 替換）
3. fallback `"0.1.0"`

---

## 常用程式碼範例

### 基本桌面應用

```python
import flet as ft

def main(page: ft.Page):
    page.title = "我的 Flet App"
    page.add(ft.Text("Hello, Flet!"))

ft.app(main)          # 廢棄寫法，請用 ft.run()
ft.run(main)          # ✅ 正確寫法
```

### Web 模式

```python
ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,   # 在瀏覽器開
    host="0.0.0.0",                # 對外暴露
    port=5000,
    web_renderer=ft.WebRenderer.CANVAS_KIT,
)
```

### 嵌入現有 FastAPI

```python
from fastapi import FastAPI
import flet as ft

app = FastAPI()
flet_app = ft.run(main, export_asgi_app=True)
app.mount("/flet", flet_app)
```

### 事件處理（按鈕點擊）

```python
def main(page: ft.Page):
    def on_click(e: ft.ControlEvent):
        print(f"點了！control={e.control}, target={e.target}")
    
    page.add(ft.ElevatedButton("按我", on_click=on_click))
```

### 觸控/拖曳事件

```python
def main(page: ft.Page):
    def on_drag_start(e: ft.DragStartEvent):
        print(f"拖曳開始：{e.local_position}")
    
    container = ft.Container(
        width=200, height=200, bgcolor="blue",
        on_drag_start=on_drag_start,
    )
    page.add(container)
```

### 生命週期鉤子

```python
async def before_my_app(page: ft.Page):
    page.title = "預先設定"
    print("Page 已建立，main 即將執行")

async def main(page: ft.Page):
    print("App 啟動完成")

ft.run(main, before_main=before_my_app)
```

### 響應式 Row 斷點

```python
row = ft.ResponsiveRow([
    ft.Container(col={"xs": 12, "md": 6}, bgcolor="red"),   # xs 全寬，md 一半
    ft.Container(col={"xs": 12, "md": 6}, bgcolor="green"),
])
```

### ThemeMode

```python
page.theme_mode = ft.ThemeMode.DARK   # 強制深色主題
```

---

## 重要發現與注意事項

1. **`ft.app()` 已廢棄**：從 0.80.0 起，`ft.app()` 只是 `run()` 的包裝器。新程式碼應直接使用 `ft.run()`。

2. **`target` 參數也是舊 API**：`run()` 仍接受 `target` 作為 `main` 的廢棄別名，建議統一使用 `main`。

3. **`app.py` 底部混入 events.py**：閱讀時注意 `app.py` 檔案結尾有 `from flet.controls.events import *` 及 `HoverEvent = PointerEvent` 別名定義（屬於另一個模組的內容）。

4. **`HoverEvent` 等於 `PointerEvent`**：兩者是同一個 class 的兩個名稱，用 `HoverEvent` 只是語義上的區分。

5. **`MultiTapEvent` 特殊繼承**：`MultiTapEvent` 直接繼承 `ControlEvent`，而非其他事件的泛型 `Event[EventControlType]`，這是唯一例外。

6. **`before_main` 是 session 級別的**：在 `on_session_created` 中，`before_main` 在每個 session 建立時被呼叫，適用於需要在 `main` 執行前預先設定 page 的情境。

7. **`main` 支援 sync/async/generator 四種形式**：`run()` 內部透過 `inspect` 模組自動判斷型態並用不同方式處理。

8. **`port=0` 的行為**：若同時設了 `FLET_SERVER_PORT` 環境變數，會被 `os.getenv()` 讀取並覆寫（app.py 第 168 行）。

9. **Linux Server 自動降級為 Web 模式**：若偵測到 `is_linux_server()` 或 `FLET_FORCE_WEB_SERVER=1`，會自動將 `view` 改為 `WEB_BROWSER` 並用 port 8000。

10. **Signal Handler 只在非 embedded 模式註冊**：`is_embedded()` 時不註冊 SIGINT/SIGTERM handler（桌面應用程式由其自己的框架處理關閉）。

11. **types.py 的 `VerticalAlignment` 是 float 值**：enum 成員的值是 `-1.0`、`0.0`、`1.0`，而非字串，這與 Flutter 的對應 enum 值一致。

12. **`AppLifecycleState` 的跨平台差異**：`PAUSE`、`DETACH`、`RESTART` 只在 mobile（iOS/Android）有效，desktop/web 不會觸發這些狀態。

13. **廢棄裝飾器 `show_parentheses` 參數**：設為 `True` 時警告訊息會把 `func_name` 顯示為 `func_name()`（模擬函式呼叫的視覺效果），適用於包裝類別的初始化器。
