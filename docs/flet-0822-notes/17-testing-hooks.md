# Flet 測試工具與元件鉤子 — 學習筆記

> Flet 0.82.2 | 學習日期：2026-03-23 | 來源：`flet/testing/` + `flet/components/`

---

## testing 模組（FletApp / Tester / Finder）

### 架構概述

`flet.testing` 包含三個核心類：`FletTestApp`（L1）、`Tester`（L2）、`Finder`（L3）。

```
Flutter 整合測試流程
┌─────────────────────────────────────────────────┐
│  FletTestApp                                    │
│  ├─ 啟動 Python Flet App（asyncio）             │
│  ├─ 啟動 Flutter 整合測試進程                    │
│  │   └─ flutter test integration_test          │
│  └─ 協調兩者之間的通訊                           │
│       └─ Tester（透過 Dart IPC）                │
│            └─ Finder（搜尋結果封裝）             │
└─────────────────────────────────────────────────┘
```

### FletTestApp（flet_test_app.py 第 44–360 行）

**用途**：協調 Python Flet App 與 Flutter 整合測試框架的橋樑。

**初始化參數**（第 62–91 行）：

| 參數 | 說明 |
|------|------|
| `flutter_app_dir` | Flutter 專案路徑（含 `integration_test/`）|
| `flet_app_main` | Flet App 進入點（一個 `Callable[[Page], None]` 或 coroutine）|
| `assets_dir` | 靜態資源目錄，預設 `"assets"` |
| `test_path` | Python 測試檔路徑（用於 golden screenshot 比對）|
| `tcp_port` | Flet Server 監聽埠（自動選取自由埠）|
| `test_platform` | 目標平台（`windows`/`linux`/`macos`/`android`/`ios`）|
| `capture_golden_screenshots` | 是否 capture golden 截圖（等同 `FLET_TEST_GOLDEN=1`）|
| `screenshots_pixel_ratio` | 截圖解析度倍率，預設 `2.0` |
| `screenshots_similarity_threshold` | 截圖相似度閾值，預設 `99.0`（百分比）|
| `skip_pump_and_settle` | 略過初始 `pump_and_settle` |

**主要方法**：

- `start()`（第 152 行）：啟動 Flet App 與 Flutter 測試進程，兩者透過 TCP 或 HTTP 連接。
- `teardown()`（第 208 行）：關閉 Flutter 進程，优雅等待 10 秒後終止。
- `resize_page(width, height)`（第 237 行）：調整 page 視窗大小（僅桌面模式）。
- `assert_control_screenshot(name, control, ...)`（第 264 行）：對單一 Control 拍截圖並與 golden 比對。
- `take_page_controls_screenshot()`（第 259 行）：對整頁所有 controls 拍截圖。
- `assert_screenshot(name, screenshot, similarity_threshold)`（第 301 行）：比對截圖與 golden影像。
- `wrap_page_controls_in_screenshot(margin, pump_times)`（第 243 行）：將 page 所有 controls 包進 `Screenshot` Control 以便拍攝。
- `create_gif(image_names, output_name, duration)`（第 344 行）：從多張 golden PNG 生成動畫 GIF。

**Golden 截圖路徑規則**（第 313–316 行）：
```
{test_path}/golden/{test_platform}/{test_filename}/{name}.png
```

**環境變數支援**：
- `FLET_TEST_PLATFORM`、`FLET_TEST_DEVICE`、`FLET_TEST_GOLDEN=1`
- `FLET_TEST_SCREENSHOTS_PIXEL_RATIO`、`FLET_TEST_SCREENSHOTS_SIMILARITY_THRESHOLD`
- `FLET_TEST_USE_HTTP=1`、`FLET_TEST_DISABLE_FVM=1`

### Tester（tester.py 第 24–161 行）

**用途**：透過 Dart IPC 與 Flutter 測試環境互動，操控 UI 控制項。

**繼承關係**：`Tester` extends `Service` extends `BaseControl`，使用 `@control("Tester")` 裝飾器（第 24 行）。

**主要方法**：

| 方法 | 說明 |
|------|------|
| `pump(duration)` | 等待指定 duration 後觸發一個 frame |
| `pump_and_settle(duration, timeout)` | 重複 pump 直到所有動畫完成（預設 timeout 10s）|
| `find_by_text(text)` | 找含有精確文字的控制項 |
| `find_by_text_containing(pattern)` | 用正規表達式找文字 |
| `find_by_key(key)` | 用 `Key` 實例或 key 名稱找控制項 |
| `find_by_tooltip(value)` | 用 tooltip 找控制項 |
| `find_by_icon(icon)` | 用 Icon 找控制項 |
| `tap(finder)` | 點擊 Finder 找到的控制項中心 |
| `tap_at(offset)` | 點擊指定座標 |
| `long_press(finder)` | 長按 600ms |
| `enter_text(finder, text)` | 對文字輸入控制項填入文字 |
| `mouse_hover(finder)` | 模擬滑鼠懸停 |
| `take_screenshot(name)` | 對整個應用視窗截圖（僅 iOS/Android）|
| `teardown(timeout)` | 關閉 Flutter 整合測試 |

所有方法皆為 async，回傳 `await self._invoke_method(...)`。

### Finder（finder.py 第 13–50 行）

**用途**：封裝 `find_by_*` 搜尋結果，支援多結果索引。

**屬性**：

| 屬性 | 說明 |
|------|------|
| `id` | Dart side Finder 實例的內部 ID |
| `count` | 找到的控制項總數 |
| `index` | 要操作的控制項索引（預設 0）|

**實例方法**：

| 方法 | 說明 |
|------|------|
| `.first` | 取第一個（property）|
| `.last` | 取最後一個（property）|
| `.at(index)` | 取指定索引 |

```python
# 範例：找到所有 TextField，取第二個
finder = await tester.find_by_text_containing("name")
second = finder.at(1)
await tester.enter_text(second, "hello")
```

### ⚠️ 桌面模式支援

**重要發現**：`FletTestApp` 和 `Tester` 的設計是針對 **Flutter 整合測試框架**，而非桌面 Pytest 測試。

- `Tester` 的所有方法（`pump`、`tap`、`find_by_text` 等）需要 Flutter Dart runtime 支援。
- `take_screenshot()` 明確記載「僅 iOS 和 Android 可用」。
- `FletTestApp.start()` 內部啟動 `flutter test integration_test` 子進程（第 188 行）。
- 在純桌面模式下（Flet desktop app without Flutter test harness），**無法直接使用這些測試工具**。

若要在桌面環境做 UI 測試，需要另尋方案（如 `pytest-playwright`、`pytest-flet` 或手動截圖比對）。

---

## use_state

**檔案**：`flet/components/hooks/use_state.py`

### 核心概念

`use_state` 是 React-like 狀態鉤子，回傳 `(value, set_value)` tuple。

### API 簽名（L26–40 行）

```python
def use_state(
    initial: StateT | Callable[[], StateT],
) -> tuple[StateT, Callable[[StateT | Updater], None]]:
```

### StateHook 資料結構（L11–27 行）

```python
@dataclass
class StateHook(Hook):
    value: Any                    # 目前狀態值
    subscription: ObservableSubscription | None = None  # Observable 訂閱
    version: int = 0              # 遞增修訂計數器
```

### 重要行為

1. **延遲初始化**：若 `initial` 是 callable，會在首次 render 時才呼叫（`initial() if callable(initial) else initial`）。
2. **Observable 自動訂閱**：當 `value` 是 `Observable` 實例時，自動建立 `ObservableSubscription`（L43–51）。當 `value` 改變時，舊訂閱會 detach，新訂閱會 attach。
3. **Updater 函式模式**：`set_value` 接受兩種形式：
   - 直接值：`set_value(5)`
   - 函式：`set_value(lambda prev: prev + 1)`
4. **淺層相等比較**：只有當 `new_value != hook.value` 時才觸發更新（L61）。
5. **觸發更新方式**：透過 `hook.component._schedule_update()` 排程組件更新。

```python
# 基本用法
count, set_count = use_state(0)
set_count(count + 1)           # 直接更新
set_count(lambda c: c + 1)    # 函式更新

# Observable 搭配
obj = MyObservable()
val, set_val = use_state(obj)  # 自動訂閱 obj 的變化
```

---

## use_effect

**檔案**：`flet/components/hooks/use_effect.py`

### 核心概念

`use_effect` 執行副作用，支援 dependency tracking 與 cleanup 函式。

### EffectHook 資料結構（L17–29 行）

```python
@dataclass
class EffectHook(Hook):
    setup: Callable[[], Any | Awaitable[Any]]
    cleanup: Callable[[], Any | Awaitable[Any]] | None = None
    deps: list[Any] | None = None
    prev_deps: list[Any] | None = None
    _setup_task: asyncio.Task | None = None   # 執行 setup 的 task
    _cleanup_task: asyncio.Task | None = None # 執行 cleanup 的 task
```

### API 簽名（L49–67 行）

```python
def use_effect(
    setup: Callable[[], Any | Awaitable[Any]],
    dependencies: Sequence[Any] | None = None,
    cleanup: Callable[[], Any | Awaitable[Any]] | None = None,
):
```

### 執行階段（Component 到鉤子流程）

```
did_mount()
  └─ _run_mount_effects()
       └─ _schedule_effect(hook, is_cleanup=False)
            └─ session.schedule_effect(hook)
                 └─ 執行 setup()

before_update() / update()
  └─ _run_render_effects()
       └─ 比對 deps 是否改變
            ├─ 若改變且有 cleanup → schedule_effect(hook, is_cleanup=True)
            └─ → schedule_effect(hook, is_cleanup=False)

will_unmount()
  └─ _run_unmount_effects()
       └─ 若有 cleanup → schedule_effect(hook, is_cleanup=True)
```

### 便捷別名（L69–103 行）

```python
on_mounted(fn)          # use_effect(fn, dependencies=[])     → 只在 mount 時執行一次
on_unmounted(fn)        # use_effect(lambda: None, [], cleanup=fn) → unmount 時執行
on_updated(fn, deps)    # use_effect(fn, dependencies=deps)  → deps 改變或每次更新後執行
```

**注意**：`on_mounted`/`on_unmounted`/`on_updated` 內部直接 reassign 給 `use_effect`（L102–103），所以 `on_mounted is use_effect` 為 `True`。

```python
# 等價寫法
on_mounted(lambda: print("mounted"))
use_effect(lambda: print("mounted"), dependencies=[])
```

---

## use_memo

**檔案**：`flet/components/hooks/use_memo.py`

### 核心概念

`use_memo` 快取計算結果，只在 dependencies 改變時重新計算。

### MemoHook 資料結構（L20–27 行）

```python
@dataclass
class MemoHook(Hook, Generic[MemoValueT]):
    value: MemoValueT | None = None     # 快取值
    prev_deps: list[Any] | None = None   # 上次 dependencies 快照
```

### API 簽名（L29–48 行）

```python
def use_memo(
    calculate_value: Callable[[], MemoValueT],
    dependencies: Sequence[Any] | None = None,
) -> MemoValueT:
```

### 重要行為

1. **dependencies=None 時**：每次 render 都重新計算（第 41–42 行）。
2. **dependencies=[] 時**：只在首次 render 計算，之後永遠回傳快取值。
3. **依賴比較**：`shallow_compare_args(hook.prev_deps, dependencies)` 做淺層比較（L44）。
4. **立即播種**：當 `dependencies is None` 時，會在 `_create()` 內立即計算一次（第 35–36 行），確保 `hook.value` 有初始值。

```python
# 每次 render 都重新計算（無快取）
result = use_memo(lambda: expensive(), dependencies=None)

# 只在首次計算（終生快取）
result = use_memo(lambda: expensive(), dependencies=[])

# deps 改變才重新計算
result = use_memo(lambda: filter_data(data, query), dependencies=[query])
```

---

## use_callback / use_ref

### use_callback（use_callback.py）

**檔案**：`flet/components/hooks/use_callback.py`

**核心實現**（L21–30 行）：直接委託 `use_memo`，將函式本身當作值 memoize。

```python
def use_callback(
    fn: Callable[P, R],
    dependencies: Sequence[Any] | None = None,
) -> Callable[P, R]:
    return use_memo(lambda: fn, dependencies)
```

這保證了函式身份在 dependencies 不變時保持穩定，適用於作為其他 hooks 的穩定依賴。

### use_ref（use_ref.py）

**檔案**：`flet/components/hooks/use_ref.py`

**MutableRef 類**（L19–24 行）：
```python
class MutableRef(Generic[RefValueT]):
    __slots__ = ("current",)
    def __init__(self, initial_value: RefValueT | None = None):
        self.current = initial_value
```

**API 簽名**（L41–55 行）：
```python
def use_ref(
    initial_value: RefValueT | Callable[[], RefValueT] | None = None,
) -> MutableRef[RefValueT]:
```

### use_ref 與 use_state 的關鍵差異

| 特性 | `use_ref` | `use_state` |
|------|-----------|-------------|
| 改變是否觸發 re-render | **否** | 是 |
| `.current` 可否放任何值 | 是 | 是 |
| 適合存放計時器 ID、DOM 引用等 | ✅ | ❌（應用情境不同）|

```python
# 穩定身份，不觸發 re-render
timer_ref = use_ref(None)
timer_ref.current = setTimeout(lambda: ..., 1000)

# 觸發 re-render
count, set_count = use_state(0)
```

---

## observable / component 裝飾器

### @observable 裝飾器（observable.py 第 28–57 行）

**用途**：將任意類別（含 dataclass）混入 Observable 特性，自動追蹤屬性變更。

```python
@ft.observable
@dataclass
class MyDataClass:
    x: int
    y: int
```

**裝飾器實現邏輯**（第 28–48 行）：
1. 若 `Observable` 已在 MRO 中，直接返回原類別（防止重複混入）。
2. 否則，建立新類別 `Mixed = type(cls.__name__, (Observable, cls), ns)`。

### ObservableMixin 主要 API（observable.py 第 78–167 行）

| 方法 | 說明 |
|------|------|
| `subscribe(fn) → dispose` | 註冊監聽器，回傳取消訂閱函式 |
| `notify()` / `_notify(field)` | 手動通知或屬性 setter 自動通知 |
| `_wrap_if_collection(name, value)` | 自動將 `list`/`dict` 包裝為 ObservableList/ObservableDict |

**屬性攔截**（`__setattr__`，第 150–161 行）：
- 以 `_` 開頭的屬性不改動（不走通知流程）。
- 賦值時自動包裝 collection。
- 值改變（`not value_equal(old, value)`）時呼叫 `_notify(name)`。

### ObservableList / ObservableDict（observable.py 第 172–299 行）

這是兩個 `list`/`dict` 的子類，攔截所有變異操作並通知 owner：

```python
class ObservableList(list):
    # 會通知的變異方法：
    append, extend, insert, remove, clear, sort, reverse, pop, __setitem__, __delitem__
```

```python
class ObservableDict(dict):
    # 會通知的變異方法：
    __setitem__, __delitem__, clear, update, pop, popitem, setdefault
```

### ObservableSubscription（observable.py 第 65–103 行）

連接 Observable 與 Component生命週期的橋樑：

```python
class ObservableSubscription(ComponentOwned):
    def __post_init__(self, owner, observable):
        self.__disposer = observable.subscribe(self.__on_change)

    def dispose(self):
        # 取消訂閱
        if callable(self.__disposer):
            self.__disposer()
```

### @component 裝飾器（component_decorator.py）

**重要**：`@flet.route` 在 Flet 0.82.2 中**不存在**。正確的裝飾器是 `@component`。

```python
from flet.components import component

@component
def MyCard(title: str, content: str):
    return ft.Card(
        ft.Column([
            ft.Text(title),
            ft.Text(content),
        ])
    )
```

**裝飾器行為**（component_decorator.py 第 8–32 行）：
1. 標記 `fn.__is_component__ = True`。
2. 包裝為 `component_wrapper(...)`，自動呼叫 `current_renderer().render_component(fn, args, kwargs, key=key)`。

### Component 類（component.py 第 80–285 行）

`@control("C")` 裝飾的 function component 包裝器。

**核心職責**：
- 管理 hook 註冊表（`_state.hooks`）。
- 追蹤 observable 參數訂閱。
- 調度 re-render（`update()` / `before_update()`）。
- 執行 mount/unount effect。

**生命週期方法**：

```
did_mount()
  ├─ _state.mounted = True
  └─ _run_mount_effects()      → 所有 EffectHook 以 is_cleanup=False 執行

before_update()
  ├─ 比對 args/kwargs 是否改變
  │   └─ 若 memoized 且相同 → 跳過 render，回傳 last_b
  └─ _run_render_effects()    → deps 改變的 EffectHook 才執行

will_unmount()
  ├─ _state.mounted = False
  ├─ _detach_observable_subscriptions()
  ├─ _run_unmount_effects()   → 所有 cleanup 執行
  └─ 清除 hook state
```

**Renderer 類**（component.py 第 240–379 行）：管理 render stack 與 context，用 `contextvars.ContextVar` 實現執行期識別當前 renderer。

---

## 常用程式碼範例

### 1. 完整 Flutter 整合測試流程

```python
import flet as ft
from flet.testing import FletTestApp, Tester

# Flutter 專案必須有 integration_test/app_test.dart
fta = FletTestApp(
    flutter_app_dir="./my_flet_app",
    flet_app_main=lambda page: MyApp(page),
    test_path="integration_test/my_test.py",
    test_platform="windows",
    capture_golden_screenshots=False,
)

async def test_my_ui():
    await fta.start()
    page = fta.page
    tester = fta.tester

    # 等頁面 settle
    await tester.pump_and_settle()

    # 找控制項
    btn = await tester.find_by_text("Submit")
    await tester.tap(btn)
    await tester.pump_and_settle()

    # 截圖比對
    await fta.assert_control_screenshot("button_clicked", some_control)

    await fta.teardown()
```

### 2. function component + hooks

```python
from flet.components import component
from flet.components.hooks import use_state, use_effect, use_memo, use_ref

@component
def Counter(initial: int = 0):
    count, set_count = use_state(initial)
    label, set_label = use_state("zero")

    # mount 時執行一次
    on_mounted(lambda: print("Counter mounted"))

    # deps=[count] 改變時執行
    on_updated(lambda: set_label("one" if count == 1 else "many"), dependencies=[count])

    return ft.Column([
        ft.Text(f"Count: {count}"),
        ft.Text(label),
        ft.ElevatedButton("+1", on_click=lambda _: set_count(count + 1)),
    ])

@component
def ExpensiveList(items: list, query: str):
    # 只在 query 改變時重新過濾
    filtered = use_memo(
        lambda: [x for x in items if query.lower() in x.lower()],
        dependencies=[query],
    )
    return ft.ListView([
        ft.Text(item) for item in filtered
    ])
```

### 3. 自訂 Observable 搭配 use_state

```python
import flet as ft

@ft.observable
class CounterState:
    value: int = 0

@component
def ObservableCounter(state: CounterState):
    val, set_val = use_state(state)
    return ft.Text(f"Value: {val.value}")

# 使用時
state = CounterState(value=5)
page.add(ObservableCounter(state))
state.value = 10  # 自動觸發 re-render
```

### 4. Finder 多結果操作

```python
finder = await tester.find_by_text_containing("item")
print(f"Found {finder.count} items")
# 取倒數第二個
last_second = finder.at(finder.count - 2)
await tester.tap(last_second)
```

---

## 重要發現與注意事項

### 1. `@flet.route` 不存在
Flet 0.82.2 中沒有 `@flet.route` 裝飾器。路由功能是透過 `page.route` 和 `View` 控制項實現，並非裝飾器。function component 的正確裝飾器是 `@component`（來自 `flet.components`）。

### 2. desktop 模式下 testing 模組幾乎無法使用
`FletTestApp` 底層仰賴 `flutter test integration_test` 子進程，適用於 Flutter 整合測試（行動裝置為主）。純桌面 Pytest 情境需另尋 UI 測試方案。

### 3. hooks 呼叫順序嚴格
Hooks 內部使用位置索引（`hook_cursor`），必须在每次 render 的同順序呼叫，否則狀態會錯亂（與 React hooks 相同的限制）。

### 4. Observable 自動包裝行為
`Observable.__setattr__` 會自動將 `list`/`dict` 屬性包裝為 `ObservableList`/`ObservableDict`，所有 list/dict 變異操作（append/pop/update 等）都會觸發 `_notify`。

### 5. Observable 與 use_state 的互動
當 `use_state` 的 value 是 Observable 時，會自動建立/銷毀 ObservableSubscription，無需手動管理訂閱生命週期。

### 6. use_memo dependencies=None 每次都重算
`dependencies=None` 等同「不禁用快取」，每次 render 都會重新執行 `calculate_value()`。

### 7. use_callback 委託 use_memo
`use_callback` 並非直接緩存函式，而是透過 `use_memo(lambda: fn, deps)` 確保函式物件在 deps 不變時身份穩定。

### 8. Component 的 memoized 標記
由 `Renderer.set_memo()` 設定（透過 `with memo():` 語法），用於標記下游 component 是否應快取 render 結果。適用於子 component 的輸出在父母 render 不變時可跳過 re-render。
