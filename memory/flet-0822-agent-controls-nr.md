# Flet Controls N-R 速查表

**版本標籤**：`flet:0.82.2`
**適用版本**：Flet 0.82.2（文件來源：docs.flet.dev）
**對照舊版**：專案使用 flet 0.28.3，原始碼為準，文件差異僅供參考
**語言**：繁體中文
**說明**：`Lottie` 與 `Map` 兩項返回 404，已跳過。

---

## 1. ListTile

定高列，典型用法為帶標題、副標題與前後圖示的列表項目。

### 屬性
`autofocus` | `bgcolor` | `content_padding` | `dense` | `enable_feedback` | `horizontal_spacing` | `hover_color` | `icon_color` | `is_three_line` | `leading` | `leading_and_trailing_text_style` | `min_height` | `min_leading_width` | `min_vertical_padding` | `mouse_cursor` | `selected` | `selected_color` | `selected_tile_color` | `shape` | `splash_color` | `style` | `subtitle` | `subtitle_text_style` | `text_color` | `title` | `title_alignment` | `title_text_style` | `toggle_inputs` | `trailing` | `url` | `visual_density`

### 事件
`on_click` | `on_long_press`

### 最小範例
```python
ft.ListTile(
    leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
    title="Jane Doe",
    subtitle="Product Manager",
    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
)
```

### 與 0.28.3 差異
0.28.3 尚未出現 `toggle_inputs`、`selected_tile_color`、`leading_and_trailing_text_style` 等屬性。新版 ListTile 強化了回饋與樣式控制。

---

## 2. ListView

可滾動的線性控制項列表，是最常用的滾動控制項。

### 屬性
`build_controls_on_demand`（預設 True）| `cache_extent` | `clip_behavior` | `controls` | `divider_thickness` | `first_item_prototype` | `horizontal` | `item_extent` | `padding` | `prototype_item` | `reverse` | `semantic_child_count` | `spacing`

### 事件
（繼承自 ScrollableControl：`on_scroll`）

### 最小範例
```python
ft.ListView(
    controls=[ft.Text(f"Item {i}") for i in range(1, 6)],
)
```

### 與 0.28.3 差異
`build_controls_on_demand`（lazy 建構）、`first_item_prototype`、`semantic_child_count` 為 0.82.x 新增。0.28.3 的 ListView 無這些優化屬性。

---

## 3. Lottie

**404，跳過。**

---

## 4. Map

**404，跳過。**

---

## 5. Markdown

將文字以 Markdown 格式渲染的控制項。

### 屬性
`auto_follow_links` | `auto_follow_links_target` | `code_style_sheet` | `code_theme` | `extension_set` | `fit_content` | `image_error_content` | `latex_scale_factor` | `latex_style` | `md_style_sheet` | `selectable` | `shrink_wrap` | `soft_line_break` | `value`

### 事件
`on_selection_change` | `on_tap_link` | `on_tap_text`

### 最小範例
```python
ft.Markdown(
    value="# Welcome\n\nThis is **Markdown** rendered in Flet.",
    width=260,
)
```

### 與 0.28.3 差異
`auto_follow_links_target`、`latex_scale_factor`、`latex_style`、`soft_line_break` 為 0.82.x 新增。0.28.3 Markdown 無 LaTeX 支援。

---

## 6. MenuBar

桌面平台的應用程式選單列，包含 SubmenuButton 與 MenuItemButton。

### 屬性
`controls`（SubmenuButton / MenuItemButton 列表）| `style`（MenuStyle：alignment、bgcolor、mouse_cursor）

### 事件
（SubmenuButton / MenuItemButton 各有 `on_click`、`on_open`、`on_close`、`on_hover`）

### 最小範例
```python
ft.MenuBar(
    expand=True,
    controls=[
        ft.SubmenuButton(
            content=ft.Text("File"),
            controls=[
                ft.MenuItemButton(content=ft.Text("Save"), on_click=handle_click),
            ],
        ),
    ],
)
```

### 與 0.28.3 差異
0.28.3 MenuBar 結構較簡單，0.82.x 強化了 `MenuStyle`（bgcolor、alignment、mouse_cursor state map）。

---

## 7. MultiView

BasePage 的容器，用於管理多視圖頁面。（文件內容大部分標記 TBD）

### 屬性
`initial_data`（dict）| `view_id`（int）

### 事件
（TBD）

### 最小範例
```python
# 文件僅提供框架，完整用法待實測
ft.MultiView(initial_data={...}, view_id=1)
```

### 與 0.28.3 差異
**MultiView 是 0.82.x 新增**，0.28.3 不存在此控制項。

---

## 8. NavigationBar

Material 3 底部導航列，在多個主要目的地之間切換。

### 屬性
`animation_duration` | `bgcolor` | `border` | `destinations`（NavigationBarDestination 列表）| `elevation` | `indicator_color` | `indicator_shape` | `label_behavior` | `label_padding` | `overlay_color` | `selected_index` | `shadow_color`

### 事件
`on_change`

### 最小範例
```python
ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explore"),
        ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label="Commute"),
        ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK_BORDER, selected_icon=ft.Icons.BOOKMARK, label="Favorites"),
    ]
)
```

### 與 0.28.3 差異
`overlay_color`、`border`、`shadow_color` 為 0.82.x 新增。0.28.3 NavigationBar 無 `label_padding`。

---

## 9. NavigationDrawer

從左側或右側邊緣滑入的面板，顯示應用程式主要導航目的地。

### 屬性
`bgcolor` | `controls`（含 NavigationDrawerDestination、Divider 等）| `elevation` | `indicator_color` | `indicator_shape` | `selected_index` | `shadow_color` | `tile_padding`

### 事件
`on_change` | `on_dismiss`

### 最小範例
```python
ft.NavigationDrawer(
    on_dismiss=handle_dismiss,
    on_change=handle_change,
    controls=[
        ft.NavigationDrawerDestination(label="Item 1"),
        ft.NavigationDrawerDestination(label="Item 2"),
    ],
)
```

### 與 0.28.3 差異
`shadow_color` 為 0.82.x 新增。`tile_padding` 預設行為在 0.28.3 與 0.82.x 間有細節差異。

---

## 10. NavigationRail

顯示在應用程式左側或右側的導航軌道，適用於 3-5 個視圖切換。

### 屬性
`bgcolor` | `destinations` | `elevation` | `extended` | `group_alignment` | `indicator_color` | `indicator_shape` | `label_type` | `leading` | `min_extended_width` | `min_width` | `selected_index` | `selected_label_text_style` | `trailing` | `unselected_label_text_style` | `use_indicator`

### 事件
`on_change`

### 最小範例
```python
ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=100,
    min_extended_width=400,
    leading=ft.FloatingActionButton(icon=ft.Icons.CREATE),
    destinations=[
        ft.NavigationRailDestination(icon=ft.Icons.FAVORITE_BORDER, selected_icon=ft.Icons.FAVORITE, label="First"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Settings"),
    ],
)
```

### 與 0.28.3 差異
`selected_label_text_style`、`unselected_label_text_style`、`use_indicator` 為 0.82.x 新增。

---

## 11. OutlinedButton

中等強調程度的按鈕，適合非主要但重要的操作。

### 屬性
`autofocus` | `clip_behavior` | `content` | `icon` | `icon_color` | `style` | `url`

### 事件
`on_blur` | `on_click` | `on_focus` | `on_hover` | `on_long_press`

### 方法
`focus()`

### 最小範例
```python
ft.OutlinedButton(content="Outlined button")
ft.OutlinedButton(content="With icon", icon=ft.Icons.CHAIR_OUTLINED)
```

### 與 0.28.3 差異
`clip_behavior` 為 0.82.x 新增。`url` 屬性在 0.28.3 可能以不同方式處理。

---

## 12. Pagelet

子頁面容器，攜帶自身的 AppBar、Drawer、FAB 等 UI 結構。

### 屬性
`appbar` | `bgcolor` | `bottom_appbar` | `content` | `drawer` | `end_drawer` | `floating_action_button` | `floating_action_button_location`

### 事件
（各子元件自有事件：drawer `on_dismiss` 等）

### 最小範例
```python
ft.Pagelet(
    width=500,
    height=500,
    appbar=ft.AppBar(title=ft.Text("Pagelet AppBar")),
    content=ft.Text("Pagelet Body"),
    drawer=ft.NavigationDrawer(
        controls=[ft.NavigationDrawerDestination(label="Item 1")],
    ),
)
```

### 與 0.28.3 差異
**Pagelet 是 0.82.x 新增**，0.28.3 不存在此控制項。

---

## 13. PageView

一次只顯示一個子控制項，支援左右滑動切換，類似輪播。

### 屬性
`clip_behavior` | `controls` | `horizontal` | `implicit_scrolling` | `keep_page` | `pad_ends` | `reverse` | `selected_index` | `snap` | `viewport_fraction`

### 事件
`on_change`

### 方法
`go_to_page()` | `jump_to()` | `jump_to_page()` | `next_page()` | `previous_page()`

### 最小範例
```python
ft.PageView(
    expand=True,
    viewport_fraction=0.9,
    selected_index=1,
    horizontal=True,
    controls=[
        ft.Container(bgcolor=ft.Colors.INDIGO_400, content=ft.Text("Page 1")),
        ft.Container(bgcolor=ft.Colors.PINK_300, content=ft.Text("Page 2")),
    ],
)
```

### 與 0.28.3 差異
`implicit_scrolling`、`pad_ends`、`viewport_fraction` 為 0.82.x 新增。

---

## 14. Placeholder

預留位置的方框，常用於開發階段版面配置。

### 屬性
`color` | `content` | `fallback_height`（預設 400）| `fallback_width`（預設 400）| `stroke_width`（預設 2）

### 事件
無

### 最小範例
```python
ft.Placeholder(
    expand=True,
    color=ft.Colors.GREEN_ACCENT,
    fallback_height=200,
    fallback_width=300,
    stroke_width=20,
)
```

### 與 0.28.3 差異
`content`、`fallback_height`、`fallback_width` 在 0.28.3 可能以不同型別呈現，差異輕微。

---

## 15. PopupMenuButton

點擊後顯示下拉選單的圖示按鈕。

### 屬性
`bgcolor` | `clip_behavior` | `content` | `elevation` | `enable_feedback` | `icon` | `icon_color` | `icon_size` | `items`（PopupMenuItem 列表）| `menu_padding` | `menu_position` | `padding` | `popup_animation_style` | `shadow_color` | `shape` | `size_constraints` | `splash_radius` | `style`

### 事件
`on_cancel` | `on_open` | `on_select`

### 最小範例
```python
ft.PopupMenuButton(
    items=[
        ft.PopupMenuItem(content=ft.Text("Item 1")),
        ft.PopupMenuItem(icon=ft.Icons.POWER_INPUT, content=ft.Text("Check power")),
        ft.PopupMenuItem(),  # divider
        ft.PopupMenuItem(content=ft.Text("Checked item"), checked=False),
    ],
    menu_position=ft.PopupMenuPosition.UNDER,
)
```

### 與 0.28.3 差異
`popup_animation_style`、`size_constraints` 為 0.82.x 新增。

---

## 16. ProgressBar

線性進度指示器（進度條）。

### 屬性
`bar_height` | `bgcolor` | `border_radius` | `color` | `semantics_label` | `semantics_value` | `stop_indicator_color` | `stop_indicator_radius` | `track_gap` | `value`（0.0-1.0，None 表示不明確）| `year_2023`

### 事件
無

### 最小範例
```python
ft.ProgressBar(width=400, value=0.8)  # 明確進度
ft.ProgressBar(width=400)               # 不明確（動畫）
```

### 與 0.28.3 差異
`stop_indicator_color`、`stop_indicator_radius`、`track_gap`、`year_2023` 為 0.82.x 新增（Material Design 3 造型相關）。

---

## 17. ProgressRing

圓形進度指示器（旋轉環）。

### 屬性
`bgcolor` | `color` | `padding` | `semantics_label` | `semantics_value` | `size_constraints` | `stroke_align` | `stroke_cap` | `stroke_width` | `track_gap` | `value` | `year_2023`

### 事件
無

### 最小範例
```python
ft.ProgressRing(value=0.4, padding=ft.Padding.all(10))  # 明確進度
ft.ProgressRing()  # 不明確（旋轉動畫）
```

### 與 0.28.3 差異
`size_constraints`、`stroke_align`、`stroke_cap`、`year_2023` 為 0.82.x 新增。

---

## 18. Radio

單選按鈕，需包在 RadioGroup 內使用。

### 屬性
`active_color` | `autofocus` | `fill_color`（含狀態映射）| `focus_color` | `hover_color` | `label` | `label_position`（預設 RIGHT）| `label_style` | `mouse_cursor` | `overlay_color` | `splash_radius` | `toggleable` | `value` | `visual_density`

### 事件
`on_blur` | `on_focus`

### 最小範例
```python
ft.RadioGroup(
    content=ft.Column([
        ft.Radio(value="red", label="Red"),
        ft.Radio(value="green", label="Green"),
        ft.Radio(value="blue", label="Blue"),
    ]),
)
```

### 與 0.28.3 差異
`fill_color`（狀態映射）、`overlay_color`、`visual_density` 為 0.82.x 新增。

---

## 版本差異摘要（0.28.3 vs 0.82.2）

| 控制項 | 狀態 |
|--------|------|
| ListTile | 0.82.x 新增 `toggle_inputs`、`selected_tile_color` 等 |
| ListView | 0.82.x 新增 lazy 建構與 `build_controls_on_demand` |
| Lottie | 404（文件路徑變更或移除）|
| Map | 404（文件路徑變更或移除）|
| Markdown | 0.82.x 新增 LaTeX 渲染 |
| MenuBar | 0.82.x 強化 `MenuStyle` |
| **MultiView** | **0.82.x 新增**，0.28.3 無 |
| NavigationBar | 0.82.x 新增 `overlay_color`、`border` |
| NavigationDrawer | 0.82.x 新增 `shadow_color` |
| NavigationRail | 0.82.x 新增 label style 相關屬性 |
| OutlinedButton | 0.82.x 新增 `clip_behavior` |
| **Pagelet** | **0.82.x 新增**，0.28.3 無 |
| PageView | 0.82.x 新增 `implicit_scrolling`、`pad_ends` |
| Placeholder | 差異輕微 |
| PopupMenuButton | 0.82.x 新增動畫與尺寸屬性 |
| ProgressBar | 0.82.x 新增 MD3 stop indicator |
| ProgressRing | 0.82.x 新增 stroke_align/cap |
| Radio | 0.82.x 新增狀態色彩映射 |
