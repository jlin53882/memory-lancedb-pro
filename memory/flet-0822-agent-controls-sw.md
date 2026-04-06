# Flet 0.82.2 Controls S-W（繁體中文）

> **版本標籤**：`flet:0.82.2`
> **資料來源**：https://docs.flet.dev/controls/（依類別分組）
> **翻譯語言**：繁體中文
> **最後更新**：2026-03-22

---

## Row（水平列）

**控制項說明**：將多個子控制項以水平方向排列。與 `Column` 互為垂直/水平對應。

**關鍵屬性**：
- `controls` — 子控制項列表
- `alignment`（`MainAxisAlignment`）— 水平對齊：START/CENTER/END/SPACE_BETWEEN/SPACE_AROUND/SPACE_EVENLY
- `vertical_alignment`（`CrossAxisAlignment`）— 垂直對齊：START/CENTER/END/BASELINE/STRETCH
- `spacing` — 子控制項間距（像素）
- `wrap`（bool）— 超出時是否自動換行
- `run_spacing` — 換行後行間距
- `tight`（bool）— 是否緊密貼合子項目（False = 佔滿可用寬度）
- `intrinsic_height`（bool）— 是否以最高子項目高度為高度
- `scroll`（`ScrollMode`）— 滾動模式

**與 Column 對比**：
| 屬性 | Row | Column |
|---|---|---|
| 主軸 | 水平 | 垂直 |
| 對齊 | `alignment`（水平）| `alignment`（垂直）|
| 交叉軸對齊 | `vertical_alignment` | `horizontal_alignment` |
| 間距 | `spacing` | `spacing` |

---

## Rive

**控制項說明**：嵌入 Rive 動畫。Rive 是一個用於創建互動式動畫的工具。

**關鍵屬性**：
- `src` — Rive 動畫檔案路徑或 URL
- `artboard` — 使用的 artboard 名稱
- `state_machine` — 狀態機名稱
- `fit`（`ImageFit`）— 動畫在容器中的貼合方式
- `size` — 控制項尺寸

---

## SafeArea（安全區域）

**控制項說明**：將內容包在安全區域內，避免被系統 UI（如瀏覽器網址列、瀏覽器底部工具列）遮擋。

**關鍵屬性**：
- `content` — 子控制項
- `top` / `bottom` / `left` / `right`（bool）— 是否在各方向保留安全區域
- `maintain_bottom_view_insets` — 是否處理底部視圖插距

**最小範例**：

```python
ft.SafeArea(
    content=ft.Text("Content here"),
    maintain_bottom_view_insets=True,
)
```

---

## SearchBar（搜尋列）

**控制項說明**：Material 3 風格的搜尋輸入框元件。

**關鍵屬性**：
- `value` — 目前輸入的文字
- `hint_text` — 提示文字
- `bar_hint_text` — 搜尋列提示
- `view_hint_text` — 展開視圖提示
- `controls` — 展開後顯示的建議列表

**事件**：
- `on_change` — 當輸入內容改變時
- `on_submit` — 當提交搜尋時

---

## SegmentedButton（分段按鈕）

**控制項說明**：將多個選項以分段按鈕群組呈現，類似 Material 3 的 SegmentedButton。

**關鍵屬性**：
- `segments` — 分段列表（`Segment` 物件）
- `selected` — 目前選中的值集合
- `show_selected_on_check`（bool）— 是否在選中項目上顯示勾選標記

**最小範例**：

```python
ft.SegmentedButton(
    segments=[
        ft.Segment(value="A", label=ft.Text("Option A")),
        ft.Segment(value="B", label=ft.Text("Option B")),
    ],
    on_change=lambda e: print(f"Selected: {e.control.selected}"),
)
```

---

## ShaderMask（著色器遮罩）

**控制項說明**：使用著色器（梯度或其他）對內容進行遮罩處理。

**關鍵屬性**：
- `content` — 要套用遮罩的內容
- `shader` — 著色器（如 `Gradient`）
- `blend_mode` — 混合模式

---

## Shimmer（閃爍效果）

**控制項說明**：在內容上方顯示閃爍動畫效果，常用於載入佔位。

**關鍵屬性**：
- `content` — 要顯示的內容（會被閃爍覆蓋）
- `shimmer_color` — 閃爍顏色
- `base_color` — 基礎顏色
- `direction` — 閃爍方向

---

## Slider（滑桿）

**控制項說明**：讓使用者在一個數值範圍內選擇。支持水平和垂直模式。

**關鍵屬性**：
- `value` — 目前數值
- `min` / `max` — 最小/最大值
- `divisions` — 離散分段數
- `label`（bool/str）— 是否顯示目前數值標籤（`"{value}"` 格式字串）
- `thumb_color` / `track_color` — 顏色設定
- `active_color` / `inactive_color` — 主/副軌道顏色

**事件**：
- `on_change` — 當數值改變時
- `on_change_end` — 當拖曳結束時

**最小範例**：

```python
ft.Slider(
    min=0, max=100,
    divisions=20,
    label="{value}",
    on_change=lambda e: print(f"Value: {e.control.value}"),
)
```

---

## SnackBar（提示列）

**控制項說明**：短暫顯示的訊息列，用於向使用者提供操作回饋。**注意：在 Flet 0.28.3 中 SnackBar 顯示後必須呼叫 `page.update()`，不能只呼叫元件的 `update()`。**

**關鍵屬性**：
- `content` — 訊息內容（`Control` 或文字）
- `action` — 可選的操作按鈕（`TextButton`）
- `duration` — 顯示時間（毫秒），預設 4 秒
- `bgcolor` — 背景顏色
- `close_button_color` — 關閉按鈕顏色

**顯示方式**：`page.show_snack_bar(snack_bar)` 或 `page.snack_bar = ...`

**最小範例**：

```python
page.show_snack_bar(
    ft.SnackBar(
        content=ft.Text("Operation completed!"),
        action=ft.TextButton("UNDO", on_click=lambda _: print("Undo")),
    )
)
```

---

## Stack（疊加層）

**控制項說明**：將多個子控制項以絕對位置疊加在一起。適合實現絕對定位佈局。

**關鍵屬性**：
- `controls` — 子控制項列表
- `alignment`（`Alignment`）— 對齊方式（適用於未指定 `top`/`left` 的子項目）
- `fit`（`StackFit`）— 如何填滿可用空間：LOOSE/EXPAND/PASSTHROUGH

**定位子項目**：在 `Container` 包裝，並設定 `top`、`left`、`right`、`bottom` 屬性。

**最小範例**：

```python
ft.Stack(
    controls=[
        ft.Container(
            content=ft.Text("Background"),
            bgcolor=ft.Colors.BLUE_200,
            width=200, height=200,
        ),
        ft.Container(
            content=ft.Text("Foreground"),
            top=30, left=30,
        ),
    ]
)
```

---

## Switch（開關）

**控制項說明**：Material 風格的開關控制項，用於布林值切換。

**關鍵屬性**：
- `value`（bool）— 目前開關狀態
- `label` — 標籤文字
- `active_color` — 開啟時的顏色
- `inactive_thumb_color` / `inactive_track_color` — 關閉時的顏色

**事件**：
- `on_change` — 當狀態改變時

**最小範例**：

```python
ft.Switch(
    value=False,
    label="Dark Mode",
    on_change=lambda e: print(f"Switched: {e.control.value}"),
)
```

---

## Tabs（標籤頁）

**控制項說明**：提供多頁籤切換介面。每個標籤頁包含一個 tab 本身和對應的 content 控制項。

**關鍵屬性**：
- `tabs` — `Tab` 物件列表
- `selected_index` — 目前選中的標籤索引
- `height` — tab 的高度
- `is_secondary`（bool）— 是否使用次要样式
- `divider_color` — 分隔線顏色

**Tab 關鍵屬性**：
- `text` / `icon` — 標籤顯示文字和圖示
- `content` — 該標籤頁的內容
- `disabled`（bool）— 是否停用該標籤

**事件**：
- `on_change` — 當選中標籤改變時

**最小範例**：

```python
ft.Tabs(
    selected_index=0,
    tabs=[
        ft.Tab(text="Tab 1", content=ft.Text("Content 1")),
        ft.Tab(text="Tab 2", content=ft.Text("Content 2")),
    ],
    on_change=lambda e: print(f"Selected: {e.control.selected_index}"),
)
```

---

## Text（文字）

**控制項說明**：顯示文字內容的最基本控制項。支援樣式、字體、顏色、對齊等豐富屬性。

**關鍵屬性**：
- `value` / `spans` — 文字內容或富文字片段
- `size` — 字體大小
- `color` — 文字顏色
- `font_family` — 字體家族
- `weight`（`FontWeight`）— 字重：NORMAL/BOLD 等，或 100-900 數值
- `italic` / `strike_through` / `underline` — 樣式修飾
- `text_align`（`TextAlign`）— 對齊：LEFT/CENTER/RIGHT/JUSTIFY
- `max_lines` — 最大行數（超出截斷）
- `overflow`（`TextOverflow`）— 超出處理：CLIP/FADE/ELLIPSIS/VISIBLE
- `selectable`（bool）— 是否可選取
- `semantics_label` — 無障礙標籤

**TextSpan（富文字）**：

```python
ft.Text(
    spans=[
        ft.TextSpan("Hello ", weight=ft.FontWeight.BOLD),
        ft.TextSpan("World", color=ft.Colors.BLUE),
    ]
)
```

---

## TextButton（文字按鈕）

**控制項說明**：純文字樣式的按鈕，無背景填充。適用於工具列、對話框等場景。

**關鍵屬性**：
- `text` — 按鈕文字
- `icon` — 圖示（可選）
- `url` — 點擊後開啟的 URL（與 `on_click` 互斥）
- `url_target` — URL 開啟目標：_blank/_self 等

**事件**：
- `on_click` — 點擊時觸發

**與 OutlinedButton 的區別**：OutlinedButton 有邊框，TextButton 完全無邊框。

---

## TextField（文字輸入框）

**控制項說明**：單行或多行文字輸入框，是 Flet 表單輸入的核心控制項。

**關鍵屬性**：
- `value` — 目前輸入文字
- `label` — 浮動標籤
- `hint_text` — 提示文字
- `helper_text` — 輔助說明文字
- `error_text` — 錯誤訊息
- `multiline`（bool）— 是否多行模式
- `max_lines` — 最大行數
- `max_length` — 最大字數
- `password`（bool）— 密碼模式
- `can_reveal_password`（bool）— 是否顯示密碼切換按鈕
- `keyboard_type`（`KeyboardType`）— 鍵盤類型：TEXT/URL/EMAIL/NUMBER 等
- `input_filter` — 輸入過濾器（如 `ft.InputFilter.allow(RegExp(r"[0-9]"))`）
- `autofocus`（bool）— 是否自動聚焦
- `read_only`（bool）— 是否唯讀
- `enabled`（bool）— 是否啟用
- `prefix_icon` / `suffix_icon` — 前/後圖示
- `prefix_text` / `suffix_text` — 前/後文字

**事件**：
- `on_change` — 當內容改變時（每次輸入）
- `on_submit` — 當按下 Enter 提交時
- `on_focus` / `on_blur` — 聚焦/失焦事件

**最小範例**：

```python
ft.TextField(
    label="Email",
    hint_text="Enter your email",
    keyboard_type=ft.KeyboardType.EMAIL,
    prefix_icon=ft.Icons.EMAIL,
    on_submit=lambda _: print("Submitted!"),
)
```

---

## TimePicker（時間選擇器）

**控制項說明**：Material 風格的時間選擇對話框。

**關鍵屬性**：
- `value` — 目前選中的時間（`Time` 物件）
- `hour_cap` / `minute_cap` — 小時/分鐘上限
- `confirm_text` / `cancel_text` — 確認/取消按鈕文字
- `error_invalid_text` — 無效輸入時的錯誤文字

**事件**：
- `on_change` — 當時間確認時

**使用方式**：`page.dialog = time_picker; page.open_dialog()`

---

## Video（影片）

**控制項說明**：嵌入並播放影片。

**關鍵屬性**：
- `src` — 影片檔案路徑或 URL
- `paused`（bool）— 是否暫停
- `volume` — 音量（0.0-1.0）
- `playback_rate` — 播放速度
- `aspect` — 顯示比例
- `filter_quality`（`VideoFilterQuality`）— 濾鏡品質：AUTO/LOW/MEDIUM/HIGH

**事件**：
- `on_page_started` — 頁面開始時
- `on_page_ended` — 播放結束時

---

## View（視圖）

**控制項說明**：頁面內容的容器，作為 `Page` 的主要內容區域。繼承自 `Container`。

**關鍵屬性**：
- `controls` — 子控制項列表
- `route` — 路由路徑
- `app_bar` — 頂部應用程式列
- `drawer` / `end_drawer` — 側邊抽屜選單
- `bottom_app_bar` — 底部應用程式列
- `floating_action_button` — 浮動動作按鈕
- `navigation_rail` / `navigation_bar` — 導航元件
- `padding` — 內距

**路由使用範例**：

```python
ft.View(
    route="/home",
    controls=[ft.Text("Home Page")],
    app_bar=ft.AppBar(title=ft.Text("Home")),
)
```

---

## WebView（網頁檢視）

**控制項說明**：在應用程式內嵌瀏覽器，可用於顯示網頁內容。

**關鍵屬性**：
- `src` — 網頁 URL
- `javascript_enabled`（bool）— 是否啟用 JavaScript
- `zoom_enabled`（bool）— 是否允許縮放

**事件**：
- `on_page_started` — 頁面開始載入時
- `on_page_ended` — 頁面載入完成時
- `on_web_resource_error` — 資源載入錯誤時

**平台限制**：WebView 並非所有平台都支援，請參考官方文件。

---

## WindowDragArea（視窗拖曳區）

**控制項說明**：在桌面應用程式中，定義可拖曳以移動視窗的區域。通常放在 `AppBar` 內。

**關鍵屬性**：
- `image_src` — 拖曳區域內的圖示
- `intecept_standard_key_events`（bool）— 是否攔截標準按鍵事件
- `child` — 區域內的子控制項

**最小範例**：

```python
ft.WindowDragArea(
    content=ft.Container(
        content=ft.Text("Drag to move window"),
        padding=10,
    )
)
```

**使用時機**：建立無邊框視窗的桌面應用程式時，用於自訂標題列的拖曳行為。
