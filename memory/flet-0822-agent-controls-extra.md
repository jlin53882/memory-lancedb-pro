# Flet 0.82.2 控制項筆記（Controls B-I 續）
版本標籤：`flet:0.82.2`  
資料來源：`https://docs.flet.dev/controls/`  
備註：使用繁體中文，濃縮每項 10-20 行  
⚠️ 表示該 URL 404 文件不存在

---

## Banner

在頂部應用欄下方顯示簡潔重要訊息，並提供使用者操作按鈕。非強制性，使用者可直接忽略或隨時互動。

**主要屬性**
- `leading` (IconDataOrControl)：左側圖示
- `content` (StrOrControl)：訊息內容
- `actions` (list[Control])：底部操作按鈕列表
- `bgcolor`, `elevation`, `shadow_color`：外觀設定
- `force_actions_below` (bool)：強制將 actions 置於 content 下方
- `content_padding`, `leading_padding`：內距調整
- `divider_color` (ColorValue)：分隔線顏色

**事件**
- `on_visible`：Banner 首次顯示時觸發

**繼承**：DialogControl

**最小範例**
```python
banner = ft.Banner(
    leading=ft.Icon(ft.Icons.INFO_OUTLINED),
    content=ft.Text("Backup completed successfully."),
    actions=[ft.TextButton("Dismiss")],
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
)
page.show_dialog(banner)
```

---

## BottomAppBar

Material Design 底部應用欄，可嵌入 FAB 並自動產生缺口。

**主要屬性**
- `bgcolor` (ColorValue)：背景顏色
- `content` (Control)：欄位內的控制項，通常為 Row 排列 IconButton
- `shape` (NotchShape)：FAB 缺口形狀（CircularRectangleNotchShape / CircleBorder）
- `elevation` (Number)：陰影高度
- `notch_margin` (Number)：缺口邊距
- `clip_behavior` (ClipBehavior)：裁剪行為
- `padding`, `shadow_color`, `border_radius`

**搭配 FAB 使用**
```python
page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, shape=ft.CircleBorder())
page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED
page.bottom_appbar = ft.BottomAppBar(
    bgcolor=ft.Colors.BLUE,
    shape=ft.CircularRectangleNotchShape(),
    content=ft.Row(controls=[...]),
)
```

---

## BottomSheet

從螢幕底部滑出的臨時覆蓋層，顯示補充內容或操作選項。顯示時阻擋背景互動（modal）。

**主要屬性**
- `content` (Control)：Sheet 內顯示的內容
- `dismissible` (bool)：點擊遮罩是否可關閉（預設 True）
- `draggable` (bool)：是否可拖曳上下滑動關閉
- `fullscreen` (bool)：是否占滿整個視窗高度
- `show_drag_handle` (bool)：是否顯示頂部拖曳把手
- `scrollable` (bool)：移除半高限制，允許內容滾動
- `bgcolor`, `elevation`, `shape`, `use_safe_area`, `maintain_bottom_view_insets_padding`
- `barrier_color` (ColorValue)：遮罩顏色

**事件**
- `on_dismiss`：Sheet 關閉時觸發

**最小範例**
```python
sheet = ft.BottomSheet(
    content=ft.Column(
        width=150,
        controls=[ft.Text("Choose an option"), ft.TextButton("Dismiss")],
    )
)
page.show_dialog(sheet)
```

---

## CircleAvatar ⚠️ URL 404（文件不存在）

（A 文件已不存在，僅保留此標記供參考）

---

## CupertinoActionButton ⚠️ URL 404（文件不存在）

（A 文件已不存在，僅保留此標記供參考）

---

## CupertinoContextMenu

iOS 風格長按上下文選單，長按時以全螢幕模態路由開啟選單。

**主要屬性**
- `content` (Control)：長按目標的內容（如 Image）
- `actions` (list[Control])：選單動作列表，通常為 CupertinoContextMenuAction
- `enable_haptic_feedback` (bool)：點擊動作是否產生觸覺回饋（預設 True）

**CupertinoContextMenuAction 屬性**
- `content`：動作顯示文字
- `default` (bool)：是否為預設動作
- `destructive` (bool)：是否為破壞性動作（紅色）
- `trailing_icon`：右側圖示

**最小範例**
```python
ft.CupertinoContextMenu(
    enable_haptic_feedback=True,
    content=ft.Image("https://picsum.photos/200/200"),
    actions=[
        ft.CupertinoContextMenuAction(content="Action 1", default=True, trailing_icon=ft.Icons.CHECK),
        ft.CupertinoContextMenuAction(content="Action 2", trailing_icon=ft.Icons.MORE),
        ft.CupertinoContextMenuAction(content="Action 3", destructive=True, trailing_icon=ft.Icons.CANCEL),
    ],
)
```

---

## CupertinoPicker

iOS 滾輪式選擇器，適用於時間、日期、列表選項等場景。

**主要屬性**
- `controls` (list[Control])：選擇器內的項目（通常為 Text）
- `selected_index` (int)：目前選中項目的索引（從 0 開始）
- `looping` (bool)：滾動是否可循環
- `item_extent` (Number)：每個項目的統一高度
- `magnification` (Number)：中間項目的放大倍率
- `squeeze` (Number)：滾輪緊湊程度
- `use_magnifier` (bool)：是否使用放大鏡效果
- `off_axis_fraction` (Number)：滾輪水平偏離程度
- `diameter_ratio` (Number)：高度與圓柱直徑的比例
- `bgcolor`, `selection_overlay` (Control)：選擇框疊加層

**事件**
- `on_change`：選中項目改變時觸發（`e.data` 為新索引）

**最小範例**
```python
picker = ft.CupertinoPicker(
    selected_index=3,
    magnification=1.22,
    squeeze=1.2,
    use_magnifier=True,
    on_change=handle_selection_change,
    controls=[ft.Text(value=f) for f in FRUITS],
)
```

---

## CupertinoSegmentedButton

iOS 風格的分段按鈕，單選群組，一次只能選擇一個區段。

**主要屬性**
- `controls` (list[Control])：區段列表（通常為 Text 或 Container 包裝 Text）
- `selected_index` (int)：目前選中的區段索引
- `selected_color`, `unselected_color`, `disabled_color`：狀態顏色
- `border_color`：邊框顏色
- `click_color`：長按/拖曳時的背景顏色
- `padding`：內距調整

**事件**
- `on_change`：選中狀態改變時觸發（`e.data` 為新索引字串）

**最小範例**
```python
ft.CupertinoSegmentedButton(
    selected_index=1,
    selected_color=ft.Colors.RED_400,
    on_change=lambda e: print(f"selected_index: {e.data}"),
    controls=[
        ft.Text("All"),
        ft.Text("None"),
        ft.Text("Selected"),
    ],
)
```

---

## CupertinoSwitch

iOS 風格開關，用於切換單一設定的開/關狀態。

**主要屬性**
- `value` (bool)：目前開關狀態
- `label` (str)：開關右側的說明文字
- `label_position` (LabelPosition)：標籤位置（LEFT / RIGHT）
- `active_track_color`, `inactive_track_color`：軌道顏色
- `thumb_color` (ColorValue)：滑塊顏色
- `active_thumb_image_src`, `inactive_thumb_image_src`：滑塊圖片
- `track_outline_color`, `track_outline_width`：軌道邊緣設定
- `off_label_color`, `on_label_color`：無障礙標籤顏色

**事件**
- `on_change`：狀態改變時觸發
- `on_focus`, `on_blur`：焦點事件
- `on_image_error`：圖片載入失敗時

**最小範例**
```python
ft.CupertinoSwitch(label="Cupertino Switch", value=True)
```

---

## ExpansionPanel

可展開/收合的 Material 面板，平時只顯示 header，展開後才顯示內容區塊。

**主要屬性**
- `header` (Control)：面板標題，始終可見
- `content` (Control)：展開後才顯示的內容
- `expanded` (bool)：目前是否展開
- `can_tap_header` (bool)：點擊 header 是否可展開/收合
- `bgcolor` (ColorValue)：面板背景色
- `highlight_color`, `splash_color`：點擊回饋顏色

**注意**：ExpansionPanel 通常與 ExpansionPanelList 搭配使用，而非單獨使用。

**最小範例**
```python
ft.ExpansionPanel(
    header=ft.Text("Shipping address"),
    content=ft.Text("123 Market Street, Springfield"),
    expanded=True,
)
```

---

## ExpansionPanelList

ExpansionPanel 的容器，管理多個面板的展開動畫與狀態。

**主要屬性**
- `controls` (list[ExpansionPanel])：面板列表
- `elevation` (Number)：展開面板的陰影高度（需 >= 0）
- `expand_icon_color` (ColorValue)：展開/收合圖示顏色
- `divider_color` (ColorValue)：面板分隔線顏色
- `spacing` (Number)：面板間距
- `on_change`：面板展開狀態改變時觸發（`e.data` 為面板索引）

**支援滾動**：可透過 `scroll=ft.ScrollMode.ALWAYS` 讓內容可滾動

**最小範例**
```python
ft.ExpansionPanelList(
    expand_icon_color=ft.Colors.AMBER,
    elevation=8,
    divider_color=ft.Colors.AMBER,
    on_change=handle_change,
    controls=[
        ft.ExpansionPanel(header=ft.Text("Details"), content=ft.Text("Info"), expanded=True),
        ft.ExpansionPanel(header=ft.Text("History"), content=ft.Text("History")),
    ],
)
```

---

## FilledButton

填充樣式按鈕，視覺效果最強烈的按鈕類型，通常用於主要操作（如「儲存」「確認」）。

**主要屬性**
- 繼承自 `Button`（含 `content`, `on_click`, `disabled`, `icon`, `url` 等）
- `style` (ButtonStyle)：自訂外觀樣式

**最小範例**
```python
ft.FilledButton(content="Tap me")
ft.FilledButton(content="Disabled button", disabled=True)
ft.FilledButton(content="With icon", icon=ft.Icons.ADD_OUTLINED)
```

---

## GestureDetector

包裝其他控制項以偵測各類手勢（點擊、拖曳、縮放、滾動等）的容器。

**主要屬性**
- `content` (Control)：被偵測手勢的子控制項，若無則自適應父容器大小
- `allowed_devices` (list[PointerDeviceType])：允許的指標裝置類型
- `drag_interval` (int)：水平/垂直拖曳事件節流（毫秒）
- `hover_interval` (int)：hover 事件節流（毫秒）
- `multi_tap_touches` (int)：多擊所需的最少指標數
- `mouse_cursor` (MouseCursor)：滑鼠進入時的游標類型

**主要事件**
- `on_tap`：點擊
- `on_double_tap`, `on_double_tap_down`, `on_double_tap_cancel`：雙擊
- `on_long_press`：長按
- `on_horizontal_drag_start/end/update/cancel`：水平拖曳
- `on_vertical_drag_start/end/update/cancel`：垂直拖曳
- `on_hover`, `on_enter`, `on_exit`：滑鼠懸停
- `on_scale_start/update/end`：縮放手勢
- `on_pan_start/update/end`：平移
- `on_focus`, `on_blur`：焦點

**最小範例**
```python
ft.GestureDetector(
    content=ft.Container(width=100, height=100, bgcolor=ft.Colors.BLUE),
    on_tap=lambda e: print("Tapped!"),
    on_horizontal_drag_end=lambda e: print(f"Dragged: {e.velocity_x}"),
)
```

---

## Hero

跨路由的 Hero 動畫控制項，讓元件在兩個頁面之間飛行轉場。

**主要屬性**
- `tag` (str)：Hero 動畫的標識符，兩個頁面的相同 tag 會形成配對
- `content` (Control)：參與動畫的內容
- `transition_on_user_gestures` (bool)：是否允許使用者手勢中斷動畫

**使用方式**：在 `page.route` 切換時，相同 `tag` 的 Hero 內容會自動產生縮放飛行動畫。需搭配 `page.on_route_change` 和 `page.on_view_pop` 事件。

**最小範例**
```python
# 頁面 1
ft.Hero(tag="avatar", content=ft.Image(src))

# 頁面 2（route="/details"）
ft.Hero(tag="avatar", content=ft.Image(src))
```

---

## IconButton

圓形圖示按鈕，點擊時以墨水擴散效果反饋，常用於工具列。

**主要屬性**
- `icon` (IconDataOrControl)：顯示的圖示
- `icon_color`, `icon_size`：圖示顏色與大小
- `selected` (bool)：選中狀態
- `selected_icon`, `selected_icon_color`：選中時的圖示與顏色
- `bgcolor`, `hover_color`, `highlight_color`, `splash_color`：各種狀態顏色
- `disabled_color`：禁用時的顏色
- `padding`, `splash_radius`：按鈕內距與漣漪半徑
- `autofocus`, `enable_feedback`：焦點與觸覺回饋
- `url`：點擊後開啟的連結
- `style` (ButtonStyle)：自訂樣式
- `mouse_cursor` (MouseCursor)：游標類型

**事件**
- `on_click`, `on_long_press`, `on_hover`, `on_focus`, `on_blur`

**最小範例**
```python
ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.PRIMARY)
```

---

## ListTile

固定高度的列表項目列，典型用於設定頁面或訊息列表，包含前導圖示、標題、副標題與後綴圖示。

**主要屬性**
- `title` (StrOrControl)：主標題
- `subtitle` (StrOrControl)：副標題（可放第二行文字）
- `leading` (IconDataOrControl)：左側前導控制項（通常為 Icon 或 CircleAvatar）
- `trailing` (IconDataOrControl)：右側後綴控制項（通常為 Icon 或 Switch）
- `bgcolor`, `selected_tile_color`：背景與選中時背景色
- `selected` (bool)：是否為選中狀態
- `is_three_line` (bool)：是否為三行模式
- `dense` (bool)：是否為緊湊模式
- `content_padding` (PaddingValue)：內距
- `shape` (OutlinedBorder)：邊框形狀
- `hover_color`, `splash_color`：懸停與點擊效果
- `mouse_cursor` (MouseCursor)：游標

**事件**
- `on_click`：點擊時觸發

**最小範例**
```python
ft.ListTile(
    leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
    title="Jane Doe",
    subtitle="Product Manager",
    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
)
```

---

## ListView

可滾動的線性列表控制項，是最常用的滾動容器，適用於長列表場景。

**主要屬性**
- `controls` (list[Control])：列表項目
- `horizontal` (bool)：是否水平排列（預設垂直）
- `spacing` (Number)：項目間距
- `divider_thickness` (Number)：分隔線厚度（設 >0 啟用）
- `padding` (PaddingValue)：列表內距
- `item_extent` (Number)：固定項目尺寸（用於效能優化）
- `prototype_item` (Control)：作為所有項目尺寸原型的控制項
- `first_item_prototype` (bool)：是否以第一項為原型
- `auto_scroll` (bool)：是否自動滾動到底部
- `reverse` (bool)：是否反向滾動
- `build_controls_on_demand` (bool)：是否延遲建立控制項（懒加载）
- `cache_extent` (Number)：預載入範圍
- `clip_behavior` (ClipBehavior)：裁剪行為

**繼承**：ScrollableControl、AdaptiveControl

**最小範例**
```python
ft.ListView(
    spacing=10,
    padding=20,
    controls=[ft.Text(f"Item {i}") for i in range(1, 6)],
)
```

---

## Map ⚠️ URL 404（文件不存在）

（A 文件已不存在，僅保留此標記供參考）

---

## Markdown

將 Markdown 文字渲染為富文本的控制項，支援標題、連結、圖片、程式碼區塊、表格、LaTeX 等語法。

**主要屬性**
- `value` (str)：Markdown 內容字串
- `selectable` (bool)：渲染後文字是否可選取
- `fit_content` (bool)：是否自適應內容高度
- `shrink_wrap` (bool)：scroll view 是否收縮到內容大小
- `soft_line_break` (bool)：是否保留行尾空格與行首縮排
- `extension_set` (MarkdownExtensionSet)：解析的語法擴展集
- `code_theme` (MarkdownCodeTheme)：程式碼區塊語法高亮主題
- `code_style_sheet` (MarkdownStyleSheet)：程式碼樣式表
- `md_style_sheet` (MarkdownStyleSheet)：Markdown 整體樣式表
- `auto_follow_links` (bool)：是否自動開啟連結
- `image_error_content` (Control)：圖片載入失敗時顯示的內容

**事件**
- `on_selection_change`：文字選取範圍改變時
- `on_tap_link`：點擊連結時
- `on_tap_text`：點擊文字時

**最小範例**
```python
ft.Markdown(
    value="# Welcome\n\nThis is **Markdown** rendered in Flet.",
    width=260,
)
```

---

## Responsive ⚠️ URL 404（文件不存在）

（A 文件已不存在，僅保留此標記供參考）
