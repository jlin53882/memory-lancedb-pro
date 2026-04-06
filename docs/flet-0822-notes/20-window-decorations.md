# Flet 視窗與裝飾控制項 — 學習筆記

> 來源：Flet 0.82.2 原始碼  
> 路徑：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\controls\`  
> 涵蓋：window.py、window_drag_area.py、snack_bar.py、badge.py、divider.py、progress_ring.py、circle_avatar.py、tooltip.py

---

## Window 桌面視窗控制

**類別**：`flet.controls.core.window.Window`（繼承自 `BaseControl`，decorator `@control("Window")`）  
**平台限制**：僅限 Desktop（macOS、Windows、Linux）。在網頁或 mobile 上無效。

### 主要屬性一覽

| 屬性 | 型別 | 說明 |
|------|------|------|
| `title` | — | （文件未列出，但標準 Window 會有） |
| `bgcolor` | `ColorValue` | 視窗背景色。可搭配 `Page.bgcolor` 做透明效果 |
| `width` / `height` | `Number` | 視窗尺寸 |
| `top` / `left` | `Number` | 視窗在螢幕上的位置（虛擬像素） |
| `max_width` / `max_height` | `Number` | 最大尺寸限制 |
| `min_width` / `min_height` | `Number` | 最小尺寸限制 |
| `opacity` | `Number`（預設 1.0） | 視窗透明度，範圍 0.0～1.0 |
| `aspect_ratio` | `Number` | 視窗寬高比 |
| `full_screen` | `bool`（預設 False） | 是否全螢幕模式 |
| `maximized` | `bool`（預設 False） | 是否最大化；設 True 可程式化最大化 |
| `minimized` | `bool`（預設 False） | 是否最小化 |
| `minimizable` | `bool`（預設 True） | 是否允許使用者點擊最小化按鈕 |
| `maximizable` | `bool`（預設 True） | 是否顯示/啟用最大化按鈕 |
| `resizable` | `bool`（預設 True） | 是否允許調整視窗大小 |
| `movable` | `bool`（預設 True） | 是否允許拖曳移動（僅 macOS） |
| `always_on_top` | `bool`（預設 False） | 視窗永遠在最上層 |
| `always_on_bottom` | `bool`（預設 False） | 視窗永遠在最下層（Linux、Windows） |
| `prevent_close` | `bool`（預設 False） | 攔截原生關閉訊號，可用於 exit 確認對話框 |
| `skip_task_bar` | `bool`（預設 False） | 是否隱藏 Task Bar / Dock 圖示 |
| `title_bar_hidden` | `bool`（預設 False） | 隱藏標題列（frameless 效果） |
| `title_bar_buttons_hidden` | `bool`（預設 False） | 隱藏標題列按鈕（僅 macOS） |
| `frameless` | `bool`（預設 False） | 無框視窗 |
| `progress_bar` | `Number`（0.0～1.0） | 在 Task Bar / Dock 上顯示進度條 |
| `focused` | `bool`（預設 True） | 是否取得焦點 |
| `visible` | `bool`（預設 True） | 是否可見（可做為啟動隱藏） |
| `shadow` | `bool`（預設 True） | 是否顯示陰影 |
| `alignment` | `Alignment` | 視窗內容對齊方式 |
| `badge_label` | `str` | 在 Dock 上顯示 badge（僅 macOS） |
| `icon` | `str` | 視窗圖示，副檔名需為 `.ico`（僅 Windows） |
| `ignore_mouse_events` | `bool` | 是否忽略滑鼠事件，透传到下層視窗 |
| `on_event` | `EventHandler[WindowEvent]` | 視窗狀態變化回調 |

### 重要枚舉

**`WindowEventType`**（行 19-57）：涵蓋所有視窗事件
- `CLOSE` / `BLUR` / `FOCUS` / `HIDE` / `SHOW`
- `MAXIMIZE` / `UNMAXIMIZE` / `MINIMIZE` / `RESTORE`
- `RESIZE` / `RESIZED` / `MOVE` / `MOVED`
- `ENTER_FULL_SCREEN` / `LEAVE_FULL_SCREEN`

**`WindowResizeEdge`**（行 63-90）：用於 `start_resizing()` 程式化調整大小
- `TOP` / `LEFT` / `RIGHT` / `BOTTOM`
- `TOP_LEFT` / `BOTTOM_LEFT` / `TOP_RIGHT` / `BOTTOM_RIGHT`

### 主要方法

| 方法 | 說明 |
|------|------|
| `wait_until_ready_to_show()` | 等到視窗準備好顯示（async） |
| `destroy()` | 摧毀視窗（async） |
| `center()` | 將視窗置中（async） |
| `close()` | 請求優雅的關閉，若 `prevent_close=True` 會被攔截 |
| `to_front()` | 將視窗帶到最上層（async） |
| `start_dragging()` | 開始拖曳視窗（用於自訂標題列） |
| `start_resizing(edge)` | 開始程式化調整大小，需傳入 `WindowResizeEdge` |

### 實作細節

- 行 102-104：`opacity` 在 `__post_init__` 中做範圍驗證（0.0～1.0），超出範圍拋 `ValueError`
- 行 99：`_i = 2`，代表視窗控制項的內部索引（多用於 Page 控制項列表）
- `bgcolor` + `Page.bgcolor` 皆設透明色時可做透明視窗效果

---

## WindowDragArea 自訂標題列

**類別**：`flet.controls.core.window_drag_area.WindowDragArea`（繼承 `LayoutControl`）  
**用途**：在任意 `Control` 上模擬原生 OS 視窗標題列行為（拖曳移動、雙擊最大化/还原）。

### 主要屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `content` | `Control` | 拖曳區域的內容，**必須可見**，否則拋 `ValueError` |
| `maximizable` | `bool`（預設 True） | 雙擊是否最大化/还原視窗 |
| `on_double_tap` | `EventHandler[WindowEvent]` | 雙擊回調；`event.type` 只會是 `MAXIMIZE` 或 `UNMAXIMIZE` |
| `on_drag_start` | `EventHandler[DragStartEvent]` | 指標接觸並開始拖曳時觸發 |
| `on_drag_end` | `EventHandler[DragEndEvent]` | 指標離開結束拖曳時觸發 |

### 實作細節

- 行 41：`before_update()` 中強制檢查 `content.visible`，若不可見拋 `ValueError`
- 雙擊時，`on_double_tap` 的事件類型限制為 `MAXIMIZE` / `UNMAXIMIZE`（由 OS 決定哪個）
- 內部呼叫 `Window.start_dragging()` 實現拖曳

### 使用模式

常見於自訂標題列（`title_bar_hidden=True` 時）：
```python
# 自訂標題列：隱藏系統標題列，用自訂 UI 取代
page.window.title_bar_hidden = True

# 自訂拖曳區域包住標題列內容
header = ft.WindowDragArea(
    content=ft.Row([
        ft.Text("我的應用"),
        ft.IconButton(icon=ft.Icons.MINIMIZE, on_click=minimize),
        ft.IconButton(icon=ft.Icons.CLOSE, on_click=close),
    ])
)
```

---

## SnackBar（實作細節）

**類別**：`flet.controls.material.snack_bar.SnackBar`（繼承 `DialogControl`）  
**顯示方式**：`page.show_dialog(snack_bar)`（非 `page.add`）

### SnackBarBehavior（行 27-44）

| 值 | 說明 |
|----|------|
| `FIXED`（預設） | 固定在頁面底部，若有 `NavigationBar` 會顯示在其上方 |
| `FLOATING` | 為浮動表面，可覆蓋底部的 `NavigationBar` / `FloatingActionButton`；可用 `width` + `margin` 控制寬度 |

### DismissDirection（行 50-88）

| 值 | 說明 |
|----|------|
| `NONE` | 禁用滑動關閉 |
| `VERTICAL` | 上下滑動皆可關閉 |
| `HORIZONTAL` | 左右滑動皆可關閉 |
| `END_TO_START` | 依閱讀方向關閉（LTR: 右→左） |
| `START_TO_END` | 依閱讀方向關閉（LTR: 左→右） |
| `UP` / `DOWN` | 僅允許單一方向 |

### SnackBar 屬性

| 屬性 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `content` | `StrOrControl` | — | 主要內容，通常是 `Text`；字串或可見 Control |
| `action` | `str \| SnackBarAction \| None` | — | 可選動作按鈕（如 "Undo"） |
| `behavior` | `SnackBarBehavior` | `FIXED`（或 theme） | 定位行為 |
| `dismiss_direction` | `DismissDirection` | `DOWN`（或 theme） | 滑動關閉方向 |
| `show_close_icon` | `bool` | `False` | 是否顯示關閉圖示 |
| `bgcolor` | `ColorValue` | — | 背景顏色 |
| `duration` | `DurationValue` | `4000ms` | 自動關閉時間 |
| `margin` | `MarginValue` | — | FLOATING 模式的外邊距（`width` 優先於 `margin`） |
| `padding` | `PaddingValue` | — | 內邊距 |
| `width` | `Number` | — | FLOATING 模式下的寬度（`width` 優先於 `margin`） |
| `elevation` | `Number` | — | 陰影高度，負值拋 `ValueError` |
| `shape` | `OutlinedBorder` | — | 形狀 |
| `clip_behavior` | `ClipBehavior` | `HARD_EDGE` | 內容裁剪行為 |
| `action_overflow_threshold` | `Number` | `0.25` | action 寬度閾值（0.0～1.0） |
| `persist` | `bool \| None` | — | 是否持續顯示（不自動消失） |
| `on_action` | `EventHandler` | — | action 按鈕點擊回調 |
| `on_visible` | `EventHandler` | — | 第一次可見時回調 |

### SnackBarAction（行 91-136）

| 屬性 | 型別 | 說明 |
|------|------|------|
| `label` | `str` | 按鈕標籤 |
| `text_color` / `disabled_text_color` | `ColorValue` | 文字顏色 |
| `bgcolor` / `disabled_bgcolor` | `ColorValue` | 背景顏色 |
| `on_click` | `EventHandler` | 點擊回調；**只響應第一次點擊**，後續忽略 |

### 實作細節

- 行 155-159：`before_update()` 驗證 `content` 必須是字串或可見的 `Control`，否則拋 `ValueError`
- 行 160-164：驗證 `action_overflow_threshold` 必須在 0.0～1.0 範圍內
- 行 165-167：驗證 `elevation` 不能為負數
- 行 159：`SnackBarAction` 只響應第一次點擊，第二次後忽略
- 行 140-142：`persist` 若為 `None`，但有設 `action`，則預設也會持續顯示（不自動消失）
- 行 143-148：`width` 和 `margin` 只在 `FLOATING` 模式有效，且 `width` 優先於 `margin`

### persist 邏輯補充

- `persist=True`：持續顯示直到使用者點擊 action 或 close icon
- `persist=False`：timeout 後自動消失
- `persist=None` + 有 `action`：`persist=True`（自動套用）
- `persist=None` + 無 `action`：使用 `duration` 的預設值（4000ms）

---

## Badge / CircleAvatar

### Badge

**類別**：`flet.controls.material.badge.Badge`（繼承 `BaseControl`，decorator `@control("Badge")`）  
**用途**：在 NavigationBar、NavigationRail、Button 等元件上顯示通知計數或狀態標記。

#### Badge 屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `label` | `StrOrControl` | 標記文字（通常 1-4 字）；若為 `None` 則顯示實心圓點 |
| `offset` | `OffsetValue` | 配合 `alignment` 調整位置 |
| `alignment` | `Alignment` | 對齊方式（預設：右上角外側） |
| `bgcolor` | `ColorValue` | 背景顏色 |
| `label_visible` | `bool`（預設 True） | 控制是否顯示標籤 |
| `large_size` | `Number` | 有 `label` 時的高度；預設 16 |
| `small_size` | `Number` | 無 `label` 時的圓點直徑；預設 6 |
| `padding` | `PaddingValue` | label 內邊距（左右預設 4px） |
| `text_color` | `ColorValue` | 文字顏色 |
| `text_style` | `TextStyle` | 文字樣式 |

#### Badge 使用方式

```python
# 方式一：直接賦值字串（最常見）
ft.FilledIconButton(icon=ft.Icons.PHONE, badge="3")

# 方式二：完整 Badge 物件（可自訂外觀）
ft.FilledIconButton(
    icon=ft.Icons.PHONE,
    badge=ft.Badge(label="99+", bgcolor=ft.Colors.RED)
)
```

#### 重要發現

- 行 43：無 `label` 時顯示為 `small_size` 直徑的實心圓（可用於「有未讀訊息」狀態）
- 行 46-53：有 `label` 時為 `StadiumBorder`（膠囊形）形狀，高度為 `large_size`
- 行 59：`label_visible=False` 可控制條件式顯示

### CircleAvatar

**類別**：`flet.controls.material.circle_avatar.CircleAvatar`（繼承 `LayoutControl`）  
**用途**：代表用戶的圓形元件，支援文字（如 initials）、圖片、背景色。

#### 主要屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `content` | `StrOrControl` | 圓形內容，通常是 `Text`（顯示 initials） |
| `foreground_image_src` | `str \| bytes` | 前景圖片（ profile 圖）；失敗時 fallback 到 `background_image_src` |
| `background_image_src` | `str \| bytes` | 背景圖片（fallback 圖） |
| `color` | `ColorValue` | 文字預設顏色 |
| `bgcolor` | `ColorValue` | 填充顏色 |
| `radius` | `Number` | 半徑（直徑 = radius × 2），與 `min_radius`/`max_radius` 互斥 |
| `min_radius` | `Number` | 最小半徑 |
| `max_radius` | `Number` | 最大半徑（預設無窮大） |
| `on_image_error` | `EventHandler` | 圖片載入失敗時回調；`event.data` 為 `"background"` 或 `"foreground"` |

#### 圖片 fallback 順序

1. `foreground_image_src` → 若失敗
2. `background_image_src` → 若也失敗
3. `bgcolor`

#### 實作細節

- 行 82-98：`before_update()` 做半徑驗證
  - `radius < 0` 拋 `ValueError`
  - `min_radius < 0` 拋 `ValueError`
  - `max_radius < 0` 拋 `ValueError`
  - `radius` 與 `min_radius`/`max_radius` 互斥（不可同時設定）

```python
# 典型用法：顯示 initials
ft.CircleAvatar(
    content=ft.Text("AB"),
    bgcolor=ft.Colors.PRIMARY,
    color=ft.Colors.ON_PRIMARY,
)

# 加上 badge 顯示線上狀態
ft.Stack([
    ft.CircleAvatar(content=ft.Text("AB"), bgcolor=ft.Colors.PRIMARY),
    ft.Badge(offset=(-5, -5), bgcolor=ft.Colors.GREEN),  # 右上角綠點
])
```

---

## Divider / ProgressRing / Tooltip

### Divider

**類別**：`flet.controls.material.divider.Divider`（繼承 `Control`）  
**用途**：水平分隔線。

| 屬性 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `color` | `ColorValue` | theme | 線的顏色 |
| `height` | `Number` | 16（theme 為 None 時） | 整個 Divider 的高度範圍（視覺線居中） |
| `leading_indent` | `Number` | 0.0 | 左側縮排 |
| `thickness` | `Number` | 0.0 | 線的粗細；0.0 = 1 device pixel |
| `trailing_indent` | `Number` | 0.0 | 右側縮排 |
| `radius` | `BorderRadiusValue` | — | 邊框圓角 |

- 行 52-67：`before_update()` 驗證所有數值不可為負

### ProgressRing

**類別**：`flet.controls.material.progress_ring.ProgressRing`（繼承 `LayoutControl`）  
**用途**：圓形進度指示器，旋轉表示忙碌状態。

| 屬性 | 型別 | 說明 |
|------|------|------|
| `value` | `Number`（0.0～1.0）| 進度值；`None` = 不確定（旋轉動畫） |
| `stroke_width` | `Number` | 線條寬度 |
| `color` | `ColorValue` | 進度顏色 |
| `bgcolor` | `ColorValue` | 圓環軌道背景色 |
| `stroke_align` | `Number`（-1.0～1.0）| 線條相對位置：-1.0=內側，0=居中，1.0=外側；預設根據 `year_2023` |
| `stroke_cap` | `StrokeCap` | 線條末端樣式 |
| `track_gap` | `Number` | 進度與軌道的間隙；`None` 預設 4.0 |
| `size_constraints` | `BoxConstraints` | 最小/最大尺寸；預設 min 36×36 |
| `padding` | `PaddingValue` | 軌道內邊距 |
| `year_2023` | `bool` | `False` = Material Design 3（2023版），`True` = 舊版 |

- 行 81-83：`stroke_align` 預設值取決於 `year_2023`：舊版預設 `-1`（內側），新版預設 `0`（居中）

### Tooltip

**類別**：`flet.controls.material.tooltip.Tooltip`（不是 `Control`，是 dataclass）  
**用途**：為其他控制項提供說明文字標籤。

#### Tooltip 屬性

| 屬性 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `message` | `str` | — | 提示文字內容（必填） |
| `decoration` | `BoxDecoration` | `BorderRadius.all(4.0)` | 背景裝飾 |
| `enable_feedback` | `bool` | `True` | 是否提供觸控/點擊回饋 |
| `vertical_offset` | `Number` | — | 與控制項的垂直間距 |
| `margin` | `MarginValue` | 0.0 | 外邊距 |
| `padding` | `PaddingValue` | 平臺預設 | 內邊距（desktop: 8×4, mobile: 16×4） |
| `bgcolor` | `ColorValue` | — | 背景色 |
| `text_style` | `TextStyle` | — | 文字樣式 |
| `text_align` | `TextAlign` | `START` | 文字水平對齊 |
| `prefer_below` | `bool` | `True` | 預設顯示在控制項下方 |
| `show_duration` | `DurationValue` | 1.5s | 顯示持續時間（long_press/tap 後） |
| `wait_duration` | `DurationValue` | 100ms | 指標懸停多久後顯示 |
| `exit_duration` | `DurationValue` | 0ms | 指標離開後多久消失 |
| `tap_to_dismiss` | `bool` | `True` | 點擊 tooltip 是否關閉 |
| `exclude_from_semantics` | `bool` | `False` | 是否排除於 semantics 樹 |
| `trigger_mode` | `TooltipTriggerMode` | `LONG_PRESS` | 觸發模式 |
| `mouse_cursor` | `MouseCursor` | — | 指標進入時的鼠標樣式 |
| `size_constraints` | `BoxConstraints` | 平臺預設 | 尺寸約束 |

#### TooltipTriggerMode

| 值 | 說明 |
|----|------|
| `MANUAL` | 手動控制 |
| `TAP` | 單次點擊後顯示 |
| `LONG_PRESS`（預設） | 長按後顯示 |

#### 使用方式

```python
# 方式一：直接給字串
ft.TextButton("儲存", tooltip="點擊儲存目前的進度")

# 方式二：完整 Tooltip 物件
ft.TextButton(
    "上傳",
    tooltip=ft.Tooltip(
        message="將檔案上傳至雲端",
        prefer_below=False,
        show_duration=3000,
        trigger_mode=ft.TooltipTriggerMode.TAP,
    )
)
```

#### 重要發現

- 行 106-119：`padding` 有平臺特定預設值（desktop: 8×4, mobile: 16×4）
- 行 130-134：`wait_duration` 預設 100ms（滑鼠懸停延遲）
- 行 115-120：`size_constraints` 有平臺預設（desktop: min_height=24, mobile: min_height=32）
- Tooltip 是 **dataclass**（非 Control），所以沒有繼承 `Control`，是一個純資料容器

---

## 常用程式碼範例

### 自訂視窗標題列（Frameless Window）

```python
import flet as ft

def main(page: ft.Page):
    page.window.title_bar_hidden = True          # 隱藏系統標題列
    page.window.frameless = True                 # 無框視窗
    page.add = ft.Column([                       # 使用 expand 填滿
        ft.WindowDragArea(                        # 自訂拖曳區
            content=ft.Container(
                ft.Row([
                    ft.Text("我的應用", expand=True),
                    ft.IconButton(icon=ft.Icons.MINIMIZE, on_click=lambda _: page.window.minimized),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: page.window.close()),
                ]),
                bgcolor=ft.Colors.SURFACE_VARIANT,
            ),
            height=40,
        ),
        ft.Text("應用程式內容"),
    ])

ft.app(main)
```

### SnackBar（完整功能）

```python
def show_snack(page: ft.Page):
    sb = ft.SnackBar(
        content=ft.Text("檔案已儲存"),
        action="復原",
        action_handler=lambda e: print("Undo!"),
        behavior=ft.SnackBarBehavior.FLOATING,
        dismiss_direction=ft.DismissDirection.UP,
        duration=5000,
        show_close_icon=True,
    )
    page.show_dialog(sb)
```

### Badge 疊加在 CircleAvatar 上

```python
# 使用 Stack 實現頭像 + 線上狀態 badge
ft.Stack([
    ft.CircleAvatar(
        content=ft.Text("JH"),
        bgcolor=ft.Colors.PRIMARY,
        radius=30,
    ),
    ft.Badge(
        offset=(-8, -8),
        bgcolor=ft.Colors.GREEN,
    ),  # 右上角顯示線上綠點
])
```

### ProgressRing（普通 + 不確定狀態）

```python
# 進度 40%
ft.ProgressRing(value=0.4, stroke_width=4)

# 不確定狀態（旋轉動畫）
ft.ProgressRing()  # value=None 即為旋轉
```

### Divider 搭配 Subtitle 分組

```python
ft.Column(
    spacing=0,
    controls=[
        ft.Text("章節 A", weight=ft.FontWeight.W_600),
        ft.Divider(height=1, thickness=0.5),
        ft.Text("項目 1"),
        ft.Text("項目 2"),
        ft.Divider(height=1, thickness=0.5),
        ft.Text("章節 B", weight=ft.FontWeight.W_600),
        ft.Divider(height=1, thickness=0.5),
    ]
)
```

---

## 重要發現與注意事項

### Window

1. **平臺限制**：`Window` 僅在 Desktop 有效，網頁/mobile 會被忽略，不會拋錯。
2. **透明度效果**：設 `bgcolor` + `Page.bgcolor` 皆透明，可做透明視窗。
3. **`opacity` 驗證**：`__post_init__` 中主動檢查 0.0～1.0 範圍，超出拋 `ValueError`。
4. **`prevent_close`**：可攔截 OS 關閉訊號，但需搭配 `on_event` 監聽 `CLOSE` 事件。
5. **macOS 專屬**：`badge_label`（Dock badge）、`title_bar_buttons_hidden`（隱藏標題列按鈕）、`movable`（移動限制）僅 macOS 有效。
6. **Windows 專屬**：`icon` 需 `.ico` 副檔名。
7. **`progress_bar`**：在 Task Bar / Dock 上顯示 0.0～1.0 的進度，可用於長時間任務。

### WindowDragArea

1. **`content` 必須可見**：`before_update()` 會主動檢查，否則拋 `ValueError`。
2. **雙擊行為由 OS 決定**：`on_double_tap` 的事件類型由平臺決定（`MAXIMIZE` 或 `UNMAXIMIZE`）。
3. **無需手動呼叫 `Window.start_dragging()`**：內部自動處理。

### SnackBar

1. **顯示方式**：不是 `page.add`，而是 `page.show_dialog()`。
2. **`persist` 與 `action` 連動**：有 `action` 時即使 `persist=None` 也會持續顯示。
3. **`action_overflow_threshold`**：當內容寬度超過 snackbar 減 action 寬度的 25% 時，action 會換行到新行。
4. **圖示關閉**：可獨立於 `action` 使用。
5. **驗證嚴格**：`before_update()` 對 `elevation`、`action_overflow_threshold`、`content` 皆有檢查。

### Badge

1. **無 `label`**：顯示 `small_size`（預設 6px）實心圓點，常用於「有未讀」狀態。
2. **有 `label`**：顯示 `StadiumBorder` 膠囊形，高度 `large_size`（預設 16）。
3. **`label_visible`**：可用於條件式顯示（如優惠券數量為 0 時不顯示）。
4. **`BadgeValue` 別名**：接受 `str` 或 `Badge` 物件。

### CircleAvatar

1. **圖片 fallback**：優先 `foreground_image_src` → `background_image_src` → `bgcolor`。
2. **`on_image_error`**：`event.data` 可區分 `"foreground"` 或 `"background"` 失敗。
3. **半徑互斥**：`radius` 與 `min_radius`/`max_radius` 不可同時設定。

### Tooltip

1. **dataclass 而非 Control**：不能直接加到 `page`，需作為其他控制項的 `tooltip` 屬性值。
2. **平臺差異大**：`padding`、`wait_duration`、`size_constraints` 皆有平臺特定預設。
3. **Desktop 滑鼠行為**：指標 hover 時會立即顯示（不受 `trigger_mode` 影響）。
4. **`trigger_mode`**：行動裝置用 `LONG_PRESS`（預設），桌面滑鼠不受此限制。
5. **`enable_feedback`**：可關閉觸控/點擊時的視覺/聽覺/震動回饋。

### Divider

1. **`height` 是整體高度，不是線的粗細**：視覺線在此高度範圍內居中。
2. **`thickness=0.0`**：等於 1 device pixel（始終繪製一像素線）。
3. **`radius`**：可設定圓角，塑造現代風格分隔線。

### ProgressRing

1. **`value=None` = 不確定狀態**：顯示旋轉動畫，不表示實際進度。
2. **`year_2023`**：預設 `False` 為最新 Material Design 3 外觀，設 `True` 可回退到 2023 前版本。
3. **`stroke_align`**：新版（M3）預設居中（0），舊版預設內側（-1）。
4. **`track_gap`**：新版 M3 預設不繪製間隙；設定 `track_gap=0` 可強制隱藏。
