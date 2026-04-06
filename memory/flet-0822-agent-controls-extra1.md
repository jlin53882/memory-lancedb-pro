# Flet 0.82.2 控制項速查表（第二批）

版本標籤：`flet:0.82.2`
建置日期：2026-03-22
說明：摘錄自 [docs.flet.dev](https://docs.flet.dev)，繁體中文，每控制項 10-20 行。

---

## ExpansionPanel

Material Design 折疊面板，可展開或收合，body 只在展開時可見。

**主要屬性：**
- `header`：面板標題，始終可見
- `content`：展開後顯示的內容
- `expanded`：布林，展開（True）或收合（False）
- `can_tap_header`：點擊 header 是否可切換展開狀態
- `bgcolor`：面板背景色
- `highlight_color`、`splash_color`：按壓與否的強調色

繼承自 `LayoutControl`、`AdaptiveControl`。

```python
ft.ExpansionPanel(
    header=ft.Text("Shipping address"),
    content=ft.Text("123 Market Street, Springfield"),
    expanded=True,
)
```

---

## ExpansionPanelList

包裝多個 `ExpansionPanel` 的清單容器，支援展開動畫。

**主要屬性：**
- `controls`：面板列表
- `elevation`：展開時的面板陰影高度
- `expand_icon_color`：展開箭頭顏色
- `divider_color`：面板間分隔線顏色
- `spacing`：面板間距
- `on_change`：展開狀態改變時觸發（ callback 接收面板索引 `e.data`）

支援滑動（`scroll=ft.ScrollMode.ALWAYS`），可用於大量面板情境。

```python
ft.ExpansionPanelList(
    expand_icon_color=ft.Colors.AMBER,
    elevation=8,
    divider_color=ft.Colors.AMBER,
    on_change=handle_change,
    controls=[...],
)
```

---

## FloatingActionButton（FAB）

懸浮操作按鈕，圓形圖示按鈕，用於推廣應用程式的「主要動作」。

**主要屬性：**
- `icon`：按鈕圖示（`ft.Icons.ADD` 等）
- `mini`：是否為迷你尺寸
- `bgcolor`、`foreground_color`：背景與前景色
- `elevation`、`disabled_elevation`、`hover_elevation`：各狀態陰影
- `focus_color`、`hover_color`、`splash_color`：各狀態強調色
- `shape`：按鈕形狀（預設為圓形）
- `url`：點擊時開啟的 URL
- `on_click`：點擊事件處理常式

通常設為 `page.floating_action_button`，也可作為一般控制項放在任意位置。

```python
ft.FloatingActionButton(icon=ft.Icons.ADD)
```

---

## GestureDetector

手勢偵測控制項，偵測觸控/滑鼠互動後觸發對應事件。

**主要屬性：**
- `content`：包覆的子控制項（可為 None，會自適應父容器大小）
- `allowed_devices`：限制可偵測的指標裝置類型
- `drag_interval`、`hover_interval`：拖曳/懸停事件的節流間距（毫秒）

**常用事件：**
- `on_tap`、`on_double_tap`：點擊與雙擊
- `on_horizontal_drag_start/end/update`：水平拖曳
- `on_vertical_drag_start/end/update`：垂直拖曳
- `on_scale_start/end/update`：縮放手勢
- `on_hover`、`on_enter`、`on_exit`：指標懸停
- `on_long_press`：長按

```python
ft.GestureDetector(
    mouse_cursor=ft.MouseCursor.CLICK,
    on_tap=handle_tap,
    content=ft.Container(...),
)
```

---

## GridView

二維可滾動控制項陣列，專為大量資料（數千筆）設計，滑動效能優於 Column/Row 巢狀組合。

**主要屬性：**
- `runs_count`：交叉軸（橫向）的子項數量（相當於欄數）
- `max_extent`：子項最大寬度或高度
- `child_aspect_ratio`：子項寬高比（橫向模式為 height/width）
- `spacing`、`run_spacing`：主軸與交叉軸間距
- `horizontal`：是否為橫向佈局（改變主軸方向）
- `cache_extent`：預載入範圍
- `build_controls_on_demand`：按需建構（預設 True）
- `controls`：控制項列表

```python
ft.GridView(
    expand=1,
    runs_count=5,
    max_extent=150,
    child_aspect_ratio=1.0,
    spacing=5,
    run_spacing=5,
    controls=[...],
)
```

---

## Hero

頁面路由動畫控制項，在兩個頁面之間以相同 `tag` 建立「英雄飛入」過渡動畫。

**主要屬性：**
- `tag`：動畫標識，兩端 `Hero` 控制項需使用相同 tag
- `content`：要進行動畫的內容（通常為 Container）
- `transition_on_user_gestures`：是否在使用者手勢時也可觸發過渡

需要配合 `page.push_route()` / `page.views` 機制使用，適用於從列表頁到詳情頁的場景。

```python
ft.Hero(
    tag="demo-hero-card",
    content=build_card(130, "Open details"),
)
```

---

## Icon

圖示控制項，支援 Material Icons、Cupertino Icons，可自訂顏色、尺寸、填充度、陰影等。

**主要屬性：**
- `icon`：圖示資料（`ft.Icons.XXX` 或 `ft.CupertinoIcons.XXX`）
- `size`：圖示尺寸
- `color`：圖示顏色
- `fill`：填充程度（0.0=線框，1.0=實心），需字體支援
- `weight`：線條粗細（ stroke weight ）
- `grade`、`optical_size`：微調圖示在不同尺寸下的視覺表現
- `blend_mode`：與背景的混合模式
- `shadows`：套用陰影
- `apply_text_scaling`：是否隨系統文字大小縮放

```python
ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK, size=40)
```

---

## IconButton

圓形圖示按鈕，帶按壓填充（墨水）效果，常用於工具列。

**主要屬性：**
- `icon`、`icon_color`、`icon_size`：圖示相關設定
- `bgcolor`、`disabled_color`：背景與禁用時顏色
- `hover_color`、`focus_color`、`highlight_color`、`splash_color`：各狀態顏色
- `selected`/`selected_icon`/`selected_icon_color`：選中狀態（可切換圖示）
- `style`：自訂外觀的 `ButtonStyle`
- `padding`、`splash_radius`：內距與水波半徑
- `visual_density`、`size_constraints`：密度與尺寸約束
- `url`：點擊開啟 URL

**事件：** `on_click`、`on_blur`、`on_focus`、`on_hover`、`on_long_press`

**方法：** `focus()` 移動焦點

```python
ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.PRIMARY)
```

---

## Image

顯示圖片的控制項，支援 JPEG、PNG、SVG、GIF（靜/動）、WebP（靜/動）、BMP、WBMP 等格式。

**主要屬性：**
- `src`：圖片來源（URL、檔案路徑或 `bytes`）
- `width`、`height`：尺寸
- `fit`：`BoxFit` 模式，定義如何填充空間
- `border_radius`：圓角
- `repeat`：超出範圍時的重複模式
- `color`/`color_blend_mode`：與圖片混合的顏色
- `cache_width`/`cache_height`：解碼尺寸（控制記憶體）
- `anti_alias`：是否啟用抗鋸齒
- `filter_quality`：渲染品質（`low`、`medium`、`high`）
- `placeholder_src`：載入中顯示的佔位圖
- `fade_in_animation`/`placeholder_fade_out_animation`：淡入淡出動畫
- `gapless_playback`：更換圖源時是否無縫繼續顯示舊圖

```python
ft.Image(
    src="https://flet.dev/img/logo.svg",
    width=100,
    height=100,
)
```

---

## InteractiveViewer

支援平移（pan）、縮放（zoom）、旋轉（rotate）的檢視器容器，適合地圖、圖片長圖、圖表等場景。

**主要屬性：**
- `content`：要變換的目標控制項（必填）
- `min_scale`/`max_scale`：縮放範圍（預設 0.25~4.0）
- `pan_enabled`/`scale_enabled`：是否啟用平移/縮放手勢
- `boundary_margin`：內容可視邊界的外邊距
- `constrained`：是否套用父容器尺寸約束
- `trackpad_scroll_causes_scale`：觸控板滾輪是否改為縮放
- `scale_factor`：每次滾輪的縮放倍率
- `interaction_update_interval`：互動更新事件的觸發間隔（毫秒）

**事件：** `on_interaction_start/end/update`

**方法：** `pan()`、`zoom()`、`reset()`、`save_state()`、`restore_state()`

```python
ft.InteractiveViewer(
    min_scale=0.1,
    max_scale=15,
    boundary_margin=ft.Margin.all(20),
    on_interaction_start=lambda e: print(e),
    content=ft.Image(src="https://picsum.photos/500/500"),
)
```
