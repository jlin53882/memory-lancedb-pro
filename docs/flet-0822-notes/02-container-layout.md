# Flet 0.82.2 Container 與佈局 — 學習筆記

> 來源：Flet 0.82.2 原始碼
> 路徑：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\`

---

## Container 重要屬性（with line refs）

**類別位置**：`flet.core.container`（注意：不在 `flet.controls` 下，而是在獨立的 `flet.core`）

Container 繼承鏈：`Container → ConstrainedControl → LayoutControl → Control`

### 尺寸相關

| 屬性 | 型別 | 說明 |
|------|------|------|
| `width` | `OptionalNumber` | 容器寬度（虛擬像素） |
| `height` | `OptionalNumber` | 容器高度 |
| `expand` | `bool\|int` | 是否擴展填充父容器空間 |
| `expand_loose` | `bool` | 擴展時是否保持"鬆散"約束 |
| `aspect_ratio` | `OptionalNumber` | 寬高比（width/height） |

### 邊距與對齊

| 屬性 | 型別 | 說明 |
|------|------|------|
| `padding` | `PaddingValue` | 內邊距，content 與容器邊緣的距離（行 79） |
| `margin` | `MarginValue` | 外邊距，容器與父容器的距離（行 85） |
| `alignment` | `Alignment` | content 在容器內的對齊方式（行 77） |

### 背景與裝飾

| 屬性 | 型別 | 說明 |
|------|------|------|
| `bgcolor` | `ColorValue` | 背景顏色（行 80），可配合 `Colors.AMBER_100` 使用 |
| `gradient` | `Gradient` | 漸層背景（行 82） |
| `blend_mode` | `BlendMode` | 背景混合模式（需搭配 bgcolor 或 gradient） |
| `image` | `DecorationImage` | 背景圖片（行 97） |
| `foreground_decoration` | `BoxDecoration` | 前景裝飾（覆蓋在 content 上方） |
| `shape` | `BoxShape` | 形狀：`BoxShape.RECTANGLE`（預設）或 `BoxShape.CIRCLE`（行 91） |

### 邊框

| 屬性 | 型別 | 說明 |
|------|------|------|
| `border` | `Border` | 邊框設定（行 81），可用 `Border.all(color, width)` 建立 |
| `border_radius` | `BorderRadiusValue` | 圓角（行 92），不可與 `shape=BoxShape.CIRCLE` 共用 |

### 陰影

| 屬性 | 型別 | 說明 |
|------|------|------|
| `shadow` | `BoxShadow\|List[BoxShadow]` | 陰影（行 99），可設定 `spread_radius`、`blur_radius`、`color`、`offset`、`blur_style` |
| `blur` | `float\|int\|Tuple\|Blur` | 模糊效果（行 98） |

### 互動與特效

| 屬性 | 型別 | 說明 |
|------|------|------|
| `ink` | `bool` | 是否使用 Ink 墨水效果（行 93） |
| `ink_color` | `ColorValue` | Ink 效果的顏色 |
| `on_click` | 事件處理器 | 點擊事件 |
| `on_tap_down` | 事件處理器 | 手指/滑鼠按下事件，含座標 `local_x/y`、`global_x/y`（`ContainerTapEvent`） |
| `on_long_press` | 事件處理器 | 長按事件 |
| `on_hover` | 事件處理器 | 滑鼠懸停事件 |
| `animate` | `AnimationValue` | 動畫設定（行 96） |

### URL 與主題

| 屬性 | 型別 | 說明 |
|------|------|------|
| `url` | `str` | 點擊時開啟的連結 |
| `url_target` | `UrlTarget` | 連結開啟方式（`_blank`、`_self` 等） |
| `theme` | `Theme` | 主題覆寫 |
| `theme_mode` | `ThemeMode` | 主題模式 |

### 其他

| 屬性 | 型別 | 說明 |
|------|------|------|
| `content` | `Control` | 容器內的唯一子控制項（行 88） |
| `clip_behavior` | `ClipBehavior` | 內容裁剪行為 |
| `ignore_interactions` | `bool` | 是否忽略所有互動（禁用點擊、懸停等） |

---

## ScrollableControl 機制

**檔案**：`flet.controls.scrollable_control`（行 1 起）

### 誰繼承了 ScrollableControl？

根據原始碼，以下控制項同時繼承了 `LayoutControl` + `ScrollableControl` + `AdaptiveControl`：

| 控制項 | 檔案 | 佈局方向 |
|--------|------|---------|
| `Column` | `flet.controls.core.column` | 垂直（从上到下） |
| `Row` | `flet.controls.core.row` | 水平（从左到右） |
| `ListView` | `flet.controls.core.list_view` | 线性（可水平或垂直） |
| `GridView` | `flet.controls.core.grid_view` | 2D 網格（可水平或垂直） |

**Stack 沒有**繼承 `ScrollableControl`，因此本身不支援滾動。

### ScrollableControl 核心 API

```python
# 啟用滾動（行 107）
scroll: Optional[ScrollMode] = None
# ScrollMode 可選值：None, "none", "auto", "adaptive", "always", "none"

# 自動滾動到尾端（行 109）
auto_scroll: bool = False
# 重要：auto_scroll 為 True 時，scroll_to() 方法失效

# 滾動事件節流（行 111）
scroll_interval: Number = 10  # 毫秒

# 滾動事件處理（行 113）
on_scroll: Optional[EventHandler[OnScrollEvent]] = None
```

### scroll_to() 方法（行 118-147）

```python
async def scroll_to(
    self,
    offset: Optional[float] = None,   # 絕對位置（像素），負值相對於末端
    delta: Optional[float] = None,    # 相對滾動量
    scroll_key: Any = None,           # 滾動到指定 control 的 key
    duration: DurationValue = 0,      # 動畫時長（毫秒）
    curve: AnimationCurve = AnimationCurve.EASE,
)
```

**重要限制**：
- `auto_scroll` 必須為 `False` 否則無效
- 對動態建立項目的控制項（如 `ListView`、`GridView`）無效（行 144-146）

### OnScrollEvent 屬性（行 54-100）

| 屬性 | 說明 |
|------|------|
| `event_type` | `ScrollType`（START/UPDATE/END/USER/OVERSCROLL） |
| `pixels` | 目前滾動位置（像素） |
| `min_scroll_extent` | 最小滾動範圍 |
| `max_scroll_extent` | 最大滾動範圍 |
| `viewport_dimension` | 可見區域大小 |
| `scroll_delta` | 與上次變化量（`UPDATE` 時有值） |
| `direction` | 用戶滾動方向：`IDLE`/`FORWARD`/`REVERSE`（`USER` 時有值） |
| `overscroll` | 被阻止的滾動量（`OVERSCROLL` 時有值） |
| `velocity` | 滾動速度（`OVERSCROLL` 時有值） |
| `out_of_range` | 是否超出範圍 |
| `at_edge` | 是否正好在邊緣 |
| `extent_before` | 可視區域前方的內容量 |
| `extent_after` | 可視區域後方的內容量 |

---

## Row / Column / Stack / GridView / ListView 比較

### 繼承結構圖

```
Control
  └── LayoutControl
        ├── Stack (無 ScrollableControl)
        │     └── AdaptiveControl
        └── ConstrainedControl (@deprecated, alias of LayoutControl)

ScrollableControl
      ├── Column
      │     └── LayoutControl + ScrollableControl + AdaptiveControl
      ├── Row
      │     └── LayoutControl + ScrollableControl + AdaptiveControl
      ├── ListView
      │     └── LayoutControl + ScrollableControl + AdaptiveControl
      └── GridView
            └── LayoutControl + ScrollableControl + AdaptiveControl
```

### Column vs Row

| 特性 | Column | Row |
|------|--------|-----|
| 主軸 | 垂直（Y軸） | 水平（X軸） |
| 主軸對齊 | `alignment: MainAxisAlignment` | `alignment: MainAxisAlignment` |
| 交叉軸對齊 | `horizontal_alignment: CrossAxisAlignment` | `vertical_alignment: CrossAxisAlignment` |
| `tight` 預設 | `False`（會擴展填滿） | `False` |
| `wrap` | 支援，自動換列/行 | 支援 |
| 特殊屬性 | `intrinsic_width` | `intrinsic_height` |

```python
# Column 預設會擴展填滿可用空間（init() 中設定 _internals["host_expanded"] = True）
# 若要讓 Column 只有內容高度，設 tight=True
ft.Column(tight=True, controls=[...])
```

### Stack

| 特性 | 說明 |
|------|------|
| 定位方式 | 絕對定位（`left`, `top`, `right`, `bottom`） |
| 子項排序 | LIFO（最後加入的在最上層） |
| 非定位子項 | 由 `alignment` + `fit` 決定大小與位置 |
| `clip_behavior` | 預設 `HARD_EDGE` |

```python
ft.Stack(
    width=300, height=300,
    controls=[
        ft.Image(src="...", width=300, height=300),
        ft.Text("Overlay", top=10, left=10),  # 絕對定位
    ]
)
```

### GridView vs ListView

| 特性 | GridView | ListView |
|------|---------|---------|
| 佈局 | 2D 網格 | 1D 線性列表 |
| `runs_count` | 每行/列的 item 數量 | N/A |
| `child_aspect_ratio` | 寬高比 | N/A |
| `max_extent` | 每格最大尺寸 | N/A |
| `item_extent` | N/A | 每項固定高度（優化渲染） |
| `prototype_item` | N/A | 支援（以第一項為原型） |
| `divider_thickness` | N/A | 支援分隔線 |
| 預設 `spacing` | 10 | 0 |
| `cache_extent` | 支援 | 支援 |
| `build_controls_on_demand` | 預設 `True` | 預設 `True` |

```python
# GridView 範例
ft.GridView(
    runs_count=2,
    spacing=8,
    run_spacing=8,
    child_aspect_ratio=1.0,
    controls=[...]
)

# ListView 範例（適合大列表）
ft.ListView(
    spacing=0,
    item_extent=50,
    divider_thickness=1,
    controls=[...]
)
```

---

## 常用程式碼範例

### 1. Container 基本用法

```python
# 帶背景、圓角、陰影的容器
ft.Container(
    content=ft.Text("Hello"),
    bgcolor=ft.Colors.AMBER_100,
    border=ft.border.all(color=ft.Colors.AMBER_700, width=2),
    border_radius=ft.border_radius.all(10),
    padding=10,
    shadow=ft.BoxShadow(
        spread_radius=5,
        blur_radius=10,
        color=ft.Colors.with_values_opacity(ft.Colors.BLACK, 0.3),
        offset=ft.Offset(2, 2),
    )
)
```

### 2. Column 搭配 scroll=ft.ScrollMode.AUTO（最常用）

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Scroll Demo"

    # 當內容超出高度時自動啟用垂直滾動
    column = ft.Column(
        scroll=ft.ScrollMode.AUTO,  # 關鍵：自動判斷是否需要滾動
        height=400,
        spacing=10,
        controls=[
            ft.Container(
                content=ft.Text(f"Item {i}"),
                bgcolor=ft.Colors.AMBER_100,
                border_radius=5,
                padding=10,
            )
            for i in range(30)
        ]
    )
    page.add(column)

ft.app(target=main)
```

### 3. 滾動事件監聽

```python
async def on_scroll_handler(e: ft.OnScrollEvent):
    print(f"位置: {e.pixels:.0f}px")
    print(f"範圍: {e.min_scroll_extent:.0f} ~ {e.max_scroll_extent:.0f}")
    if e.at_edge:
        print("已滾動到邊緣")
    if e.event_type == ft.ScrollType.OVERSCROLL:
        print(f"過度滾動: {e.overscroll}px, 速度: {e.velocity}")

column = ft.Column(
    scroll=ft.ScrollMode.AUTO,
    auto_scroll=False,
    scroll_interval=50,  # 每 50ms 最多一次事件
    on_scroll=on_scroll_handler,
    controls=[...]
)
```

### 4. 程式化滾動到特定位置

```python
# 滾動到絕對位置（100px）
await column.scroll_to(offset=100, duration=500)

# 滾動到最尾端
await column.scroll_to(offset=-1, duration=500)

# 相對滾動（向下 50px）
await column.scroll_to(delta=50)
```

### 5. Stack 絕對定位

```python
ft.Stack(
    width=300, height=300,
    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    controls=[
        ft.Container(
            bgcolor=ft.Colors.BLUE_200,
            width=300, height=300,
        ),
        ft.Container(
            content=ft.Text("Floating", size=20),
            left=20, top=20,  # 絕對定位
            bgcolor=ft.Colors.WHITE,
            border_radius=5,
            padding=5,
        ),
    ]
)
```

### 6. Row / Column 自動換行（wrap）

```python
# Column 換行（多列）
ft.Column(
    wrap=True,
    run_spacing=10,
    spacing=5,
    controls=[
        ft.Container(ft.Text(f"Box {i}"), bgcolor=ft.Colors.AMBER_100)
        for i in range(20)
    ]
)

# Row 換行（多行）
ft.Row(
    wrap=True,
    run_spacing=10,
    spacing=5,
    controls=[
        ft.Container(ft.Text(f"Item {i}"), bgcolor=ft.Colors.BLUE_100)
        for i in range(20)
    ]
)
```

### 7. GridView 高效渲染大量項目

```python
ft.GridView(
    height=400,
    runs_count=3,
    spacing=10,
    run_spacing=10,
    child_aspect_ratio=1.0,
    cache_extent=200,  # 預渲染範圍（上下各 200px）
    controls=[
        ft.Container(
            content=ft.Text(f"{i}"),
            bgcolor=ft.Colors.random(),
            border_radius=8,
        )
        for i in range(1000)
    ]
)
```

---

## 重要發現與注意事項

### ⚠️ Container.scroll 屬性 — 0.82.2 特別說明

**在 Flet 0.82.2 中，`Container` 類本身沒有 `scroll` 屬性。**

- `Container` 繼承自 `ConstrainedControl`（即 `LayoutControl`），而 `LayoutControl` 不包含滾動功能
- `Container` 也**不**繼承 `ScrollableControl`
- 若要讓 `Container` 的內容可滾動，**必須**將 `Container` 包在具有滾動能力的容器中（如 `Column`、`ListView`、或 `Page`/`View`）

```python
# 錯誤示範：Container 本身沒有滾動
ft.Container(
    scroll=ft.ScrollMode.AUTO,  # 0.82.2 中 Container 根本沒有這個屬性
    content=ft.Text("...")
)

# 正確做法：用 Column 作為滾動容器
ft.Column(
    scroll=ft.ScrollMode.AUTO,
    controls=[ft.Container(content=ft.Text("..."))]
)
```

### ⚠️ ConstrainedControl 已廢棄

`ConstrainedControl` 在 0.80.0 被標記為廢棄（deprecated），建議改用 `LayoutControl`（兩者功能相同，只是名稱變更）。

### ⚠️ Column 的 host_expanded 設定

`Column` 和 `Row` 在 `init()` 中設定了 `_internals["host_expanded"] = True`，這意味著：
- 預設情況下，`Column`/ `Row` 會填滿可用空間（如果父容器允許）
- 若不希望擴展，需設定 `tight=True`

### ⚠️ scroll_to() 的限制

- `auto_scroll` 必須為 `False`
- 對 `ListView` 和 `GridView`（動態建構）無效

### ⚠️ Column vs ListView 選擇指南

| 情境 | 建議 |
|------|------|
| 少量項目（< 100） | `Column` 即可 |
| 大量項目（數百～數千） | `ListView`（虛擬化，建議 `item_extent`） |
| 需要換行（wrap） | `Column` 或 `Row` 的 `wrap=True` |
| 2D 網格佈局 | `GridView`（`runs_count` + `child_aspect_ratio`） |
| 需要絕對定位重疊 | `Stack` |

### 📌 blur 屬性新語法

`Container.blur` 接受多種型別（行 98）：
```python
blur: Union[None, float, int, Tuple[...], Blur] = None
# 可直接給數字（均勻模糊半徑）或 (水平, 垂直) 元組
container.blur = 10           # 均勻模糊
container.blur = (5, 10)      # 水平 5px，垂直 10px
```

### 📌 BoxDecoration vs 單一屬性

`Container` 同時支援：
- **單一屬性**：`bgcolor`、`border`、`border_radius`、`shadow`
- **BoxDecoration**：透過 `foreground_decoration: BoxDecoration` 設定

兩者區別：
- `bgcolor`/`border` 等是直接屬性，設定到底層 Dart 的 ` decoration` 屬性
- `foreground_decoration` 渲染在 `content` **上方**，用於需要與 `content` 分開裝飾的進階場景
