# Flet 0.82.2 控制項筆記（Controls A-E）
版本標籤：`flet:0.82.2`  
資料來源：`https://docs.flet.dev/controls/`  
備註：使用繁體中文，濃縮每項 10-20 行

---

## AlertDialog

用於通知用戶需要確認的情況。可選標題與操作按鈕，標題在上、內容居中、按鈕在下。

**主要屬性**
- `title` (StrOrControl)：對話框頂部大標題
- `content` (Control)：中央顯示的內容
- `actions` (list[Control])：底部按鈕列表
- `modal` (bool)：是否為模態（點擊外部不可關閉）
- `actions_alignment` (MainAxisAlignment)：按鈕水平對齊
- `barrier_color` (ColorValue)：模態遮罩顏色
- `bgcolor`, `elevation`, `icon`, `icon_color`, `shape`, `scrollable`, `semantics_label`, `shadow_color`

**事件**
- `on_dismiss`：關閉對話框時觸發

**繼承**：DialogControl

**最小範例**
```python
ft.AlertDialog(
    title=ft.Text("Hello"),
    content=ft.Text("You are notified!"),
    actions=[ft.TextButton("Dismiss")],
    open=True,
)
```

---

## AnimatedSwitcher

帶動畫效果切換子控制項的容器。

**主要屬性**
- `content` (Control)：當前顯示的內容
- `duration` (DurationValue)：新內容淡入時間
- `reverse_duration` (DurationValue)：舊內容淡出時間
- `switch_in_curve`, `switch_out_curve` (AnimationCurve)：動畫曲線
- `transition` (AnimatedSwitcherTransition)：動畫類型（SCALE / FADE / ROTATION）

**最小範例**
```python
ft.AnimatedSwitcher(
    content=c1,
    transition=ft.AnimatedSwitcherTransition.SCALE,
    duration=500,
)
```

---

## AppBar

Material Design 頂部應用欄。

**主要屬性**
- `title` (StrOrControl)：主標題
- `leading` (Control)：標題前方控制項（如 Menu 圖標）
- `actions` (list[Control])：標題後方按鈕列表
- `bgcolor` (ColorValue)：背景色
- `center_title` (bool)：標題是否居中
- `elevation`, `elevation_on_scroll`：陰影相關
- `toolbar_height`, `toolbar_opacity`：工具列高度與透明度
- `shape`, `shadow_color`, `title_spacing`

**繼承**：AdaptiveControl

**最小範例**
```python
ft.AppBar(
    leading=ft.Icon(ft.Icons.MENU),
    title=ft.Text("Dashboard"),
    bgcolor=ft.Colors.SURFACE_CONTAINER,
    actions=[
        ft.IconButton(ft.Icons.SEARCH),
        ft.IconButton(ft.Icons.MORE_VERT),
    ],
)
```

---

## AutoComplete

輸入文字時從下拉列表選擇建議。

**主要屬性**
- `value` (str)：目前輸入框文字
- `suggestions` (list[AutoCompleteSuggestion])：建議選項列表
- `suggestions_max_height` (Number = 200)：下拉列表最大高度
- `selected_index` (int | None,唯讀)：已選建議的索引

**事件**
- `on_change`：輸入文字改變時
- `on_select`：選擇建議時（回傳 AutoCompleteSelectEvent）

**繼承**：LayoutControl

**最小範例**
```python
ft.AutoComplete(
    value="One",
    width=200,
    on_change=handle_change,
    on_select=handle_select,
    suggestions=[
        ft.AutoCompleteSuggestion(key="one 1", value="One"),
        ft.AutoCompleteSuggestion(key="two 2", value="Two"),
    ],
)
```

---

## AutofillGroup

將自動填充控制項分組（用於瀏覽器密碼/地址自動填充）。

**主要屬性**
- `content` (Control)：群組內的子控制項（通常包裝 TextField）
- `dispose_action` (AutofillGroupDisposeAction)：處置時的清理行為

**使用限制**
- content 必須可見，否則拋 ValueError

**繼承**：Control

**最小範例**
```python
ft.AutofillGroup(
    content=ft.Column(controls=[
        ft.TextField(label="Name", autofill_hints=ft.AutofillHint.NAME),
        ft.TextField(label="Email", autofill_hints=[ft.AutofillHint.EMAIL]),
    ])
)
```

---

## Badge

⚠️ **URL 404**：此控制項在 Flet 0.82.2 文件中尚無獨立頁面。

---

## Banner

位於頂部 AppBar 下方的重要訊息橫幅，非強制性、可忽略或操作。

**主要屬性**
- `leading` (IconDataOrControl)：左側圖標
- `content` (StrOrControl)：訊息內容
- `actions` (list[Control])：操作按鈕列表
- `bgcolor`, `elevation`, `force_actions_below`, `divider_color`, `shadow_color`
- `content_padding`, `content_text_style`, `leading_padding`

**事件**
- `on_visible`：首次顯示時觸發

**繼承**：DialogControl

**最小範例**
```python
ft.Banner(
    leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.PRIMARY),
    content=ft.Text("Backup completed successfully."),
    actions=[ft.TextButton("Dismiss")],
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
    open=True,
)
```

---

## BottomAppBar

Material Design 底部應用欄，可配合 FloatingActionButton 開缺口。

**主要屬性**
- `content` (Control)：欄位內容（通常為 Row 含 IconButton）
- `bgcolor`, `elevation`, `shape`, `padding`, `clip_behavior`
- `border_radius`：圓角
- `notch_margin`：FAB 缺口邊距
- `shadow_color`

**繼承**：LayoutControl

**最小範例**
```python
ft.BottomAppBar(
    bgcolor=ft.Colors.BLUE,
    shape=ft.CircularRectangleNotchShape(),
    content=ft.Row(controls=[
        ft.IconButton(icon=ft.Icons.MENU, icon_color=ft.Colors.WHITE),
        ft.Container(expand=True),
        ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE),
    ]),
)
```

---

## BottomSheet

從底部滑出的模態面板，覆蓋底部內容。

**主要屬性**
- `content` (Control)：面板內容
- `modal` (bool)：是否為模態（預設 True）
- `dismissible` (bool)：點擊遮罩是否關閉
- `draggable` (bool)：是否可上下拖曳滑動關閉
- `fullscreen` (bool)：是否全屏
- `scrollable` (bool)：移除半高限制，內容可自由延伸
- `show_drag_handle` (bool)：是否顯示頂部拖曳把手
- `shape`, `bgcolor`, `elevation`, `animation_style`, `barrier_color`
- `use_safe_area`, `maintain_bottom_view_insets_padding`, `size_constraints`

**繼承**：DialogControl

**最小範例**
```python
ft.BottomSheet(
    content=ft.Column(
        width=150,
        controls=[
            ft.Text("Choose an option"),
            ft.TextButton("Dismiss"),
        ],
    ),
)
```

---

## Button

Material Design 按鈕，支持文字、圖標、自訂內容。

**主要屬性**
- `content` (StrOrControl)：按鈕標籤
- `icon`, `icon_color`：圖標與顏色
- `bgcolor`, `color`：背景與前景色
- `style` (ButtonStyle)：按鈕樣式
- `elevation`：陰影高度
- `url`：點擊後開啟的 URL
- `autofocus`, `disabled`

**事件**
- `on_click`：點擊時
- `on_long_press`：長按時
- `on_hover`：懸停時
- `on_focus`, `on_blur`：獲取/失去焦點時

**方法**
- `focus()`：請求焦點

**繼承**：LayoutControl, AdaptiveControl

**最小範例**
```python
ft.Button(content="Enabled button")
ft.Button(content="Disabled button", disabled=True)
```

---

## Camera

⚠️ **URL 404**：此控制項在 Flet 0.82.2 文件中尚無獨立頁面。
（Flet 0.82 可能尚未實作 Camera 控制項，或路徑不同）

---

## Canvas

自由繪圖控制項，使用形狀原語（line, arc, path, text 等）繪製任意圖形。

**主要屬性**
- `shapes` (list[Shape])：要繪製的形狀列表
- `content` (Control)：覆蓋在 canvas 上的控制項（如透明 GestureDetector）
- `resize_interval` (Number)：on_resize 事件採樣間隔（毫秒）

**事件**
- `on_resize`：Canvas 尺寸改變時（回傳 CanvasResizeEvent）

**方法**
- `capture()`：擷取目前視覺狀態
- `clear_capture()`：清除已擷取圖像
- `get_capture()`：取得 PNG 位元組

**注意**：形狀使用 `flet.canvas` 模組（如 `cv.Rect`, `cv.Circle`, `cv.Arc`, `cv.Path`）

**繼承**：LayoutControl

**最小範例**
```python
import flet.canvas as cv

cv.Canvas(
    width=160, height=160,
    shapes=[
        cv.Rect(0, 0, 160, 160,
            paint=ft.Paint(color=ft.Colors.BLUE_100, style=ft.PaintingStyle.FILL)),
        cv.Circle(80, 80, 50,
            paint=ft.Paint(color=ft.Colors.BLUE_400, style=ft.PaintingStyle.FILL)),
    ],
)
```

---

## Card

帶圓角與陰影的 Material 卡片面板。

**主要屬性**
- `content` (Control)：卡片內部顯示的控制項
- `bgcolor`, `elevation`, `shadow_color`
- `shape` (OutlinedBorder)：卡片形狀
- `clip_behavior`：內容裁剪行為
- `variant` (CardVariant)：卡片變體
- `semantic_container` (bool)：是否為單一語義容器
- `show_border_on_foreground` (bool)：邊框是否繪製在內容前方

**繼承**：LayoutControl, AdaptiveControl

**最小範例**
```python
ft.Card(
    shadow_color=ft.Colors.ON_SURFACE_VARIANT,
    content=ft.Container(
        width=400, padding=10,
        content=ft.ListTile(
            bgcolor=ft.Colors.GREY_400,
            leading=ft.Icon(ft.Icons.FOREST),
            title=ft.Text("Card Name"),
        ),
    ),
)
```

---

## Checkbox

核取方塊，二選一或多選。

**主要屬性**
- `value` (bool | None)：核取狀態（True/False/None 三態）
- `label` (StrOrControl)：右側標籤文字
- `label_position` (LabelPosition)：標籤位置（LEFT/RIGHT）
- `tristate` (bool)：是否支援三態（預設 False）
- `active_color`, `check_color`, `fill_color`：顏色相關
- `border_side` (ControlStateValue[BorderSide])：邊框樣式
- `focus_color`, `hover_color`, `overlay_color`：狀態顏色
- `shape` (OutlinedBorder)：方塊形狀
- `semantics_label`：螢幕閱讀器標籤

**事件**
- `on_change`：狀態改變時
- `on_focus`, `on_blur`：獲取/失去焦點時

**繼承**：LayoutControl, AdaptiveControl

**最小範例**
```python
ft.Checkbox(label="Checked", value=True)
ft.Checkbox(label="Disabled", disabled=True)
```

---

## Chip

緊湊的元素，代表屬性、文字、實體或動作（如標籤、過濾器）。

**主要屬性**
- `label` (StrOrControl)：主要內容
- `selected` (bool)：是否選中
- `leading` (Control)：標籤左側控制項（如圖標）
- `delete_icon` (Control)：右側刪除圖標
- `bgcolor`, `selected_color`, `disabled_color`：背景色
- `check_color`：選中時打勾顏色
- `elevation`, `elevation_on_click`：陰影
- `border_side`：邊框樣式
- `delete_icon_tooltip`：刪除圖標提示文字
- 動畫相關：`delete_drawer_animation_style`, `enable_animation_style`, `select_animation_style`, `leading_drawer_animation_style`

**繼承**：LayoutControl

**最小範例**
```python
ft.Chip(
    label="Explore topics",
    leading=ft.Icon(ft.Icons.EXPLORE_OUTLINED),
)
```

---

## CircleAvatar

圓形使用者頭像，支援圖片/文字/圖標 fallback。

**主要屬性**
- `content` (StrOrControl)：頭像內容（文字或 Icon）
- `foreground_image_src`：前景圖片 URL（最優先）
- `background_image_src`：背景圖片 URL（foreground 失敗時使用）
- `bgcolor`：圖片皆失敗時的填充色
- `color`：文字預設顏色
- `radius` (Number)：半徑
- `min_radius`, `max_radius`：半徑範圍

**事件**
- `on_image_error`：圖片載入失敗時

**繼承**：LayoutControl

**最小範例**
```python
ft.CircleAvatar(
    content=ft.Text("AB"),
    bgcolor=ft.Colors.PRIMARY,
    color=ft.Colors.ON_PRIMARY,
)
# 或帶頭像圖片
ft.CircleAvatar(
    foreground_image_src="https://avatars.githubusercontent.com/u/5041459",
    content=ft.Text("FF"),
)
```

---

## 404 頁面記錄

以下控制項在 `docs.flet.dev/controls/` 中尚無獨立文件頁面：
- `badge`
- `camera`
