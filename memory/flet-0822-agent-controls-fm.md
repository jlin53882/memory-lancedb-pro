# Flet 0.82.2 Controls F-M（繁體中文）

> **版本標籤**：`flet:0.82.2`
> **資料來源**：https://docs.flet.dev/controls/（依類別分組）
> **翻譯語言**：繁體中文
> **最後更新**：2026-03-22

---

## CodeEditor

**控制項說明**：提供程式碼編輯功能，支援語法高亮。為桌面應用程式提供專業的程式碼輸入體驗。

**版本注意**：CodeEditor 在某些平台可能需要額外依賴。

---

## ColorPickers（色彩選擇器）

**控制項說明**：提供色彩選擇對話框，讓使用者從调色盤中選擇顏色。

**關鍵屬性**：
- `value` — 目前選中的顏色（Hex 字串）
- `gallery_padding` — 調色盤內距
- `gallery_item_size` — 調色盤項目大小
- `opacity` — 是否顯示透明度滑桿

**事件**：
- `on_change` — 當使用者選擇新顏色時觸發

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    def color_changed(e):
        result.value = f"Selected: {picker.value}"
        page.update()

    picker = ft.ColorPicker(on_change=color_changed)
    result = ft.Text()
    page.add(picker, result)

ft.run(main)
```

---

## Column（垂直列表）

**控制項說明**：將多個子控制項以垂直方向排列。是 Flet 最基本也是最常用的版面配置控制項之一。

**關鍵屬性**：
- `controls` — 子控制項列表
- `alignment`（`MainAxisAlignment`）— 水平對齊：START/CENTER/END/SPACE_BETWEEN/SPACE_AROUND/SPACE_EVENLY
- `horizontal_alignment`（`CrossAxisAlignment`）— 垂直對齊：START/CENTER/END/BASELINE/STRETCH
- `spacing` — 子控制項間距（像素）
- `scroll`（`ScrollMode`）— 滾動模式：AUTO/HIDDEN/ADAPTIVE/HOLD/DISABLED
- `clip_behavior` — 超出範圍時的裁切行為

**重要**：當 Column 在 `Container` 或有高度限制的父層內使用 `scroll=True` 時，**父層必須有明確高度**，否則 Column 會無法正確計算滾動範圍。

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Column(
            controls=[
                ft.Text("Item 1"),
                ft.Text("Item 2"),
                ft.Text("Item 3"),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
    )

ft.run(main)
```

---

## Container（容器）

**控制項說明**：單一子控制項的容器，支援背景、邊框、圓角、內距、陰影等視覺樣式設定。是 Flet UI 設計的核心元件。

**關鍵屬性**：
- `content` — 容器內的子控制項
- `padding` — 內距
- `margin` — 外距
- `bgcolor` / `bg_blend_mode` — 背景顏色
- `border` / `border_radius` — 邊框與圓角
- `shadow` — 陰影（`BoxShadow` 列表）
- `alignment`（`Alignment`）— 內部內容對齊
- `width` / `height` / `expand` — 尺寸控制
- `opacity` — 透明度

**最小範例**：

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=20,
    bgcolor=ft.Colors.BLUE_100,
    border_radius=12,
    shadow=ft.BoxShadow(
        spread_radius=2,
        blur_radius=8,
        color=ft.Colors.BLACK38,
    ),
)
```

---

## ContextMenu（上下文選單）

**控制項說明**：為控制項添加右鍵或長按選單。

**關鍵屬性**：
- `controls` — 附加了右鍵選單的控制項
- `items` — 選單項目（`MenuItemButton` 列表）

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Container(
            content=ft.Text("Right-click me"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
            border_radius=8,
            context_menu=ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Copy"),
                    ft.PopupMenuItem(text="Paste"),
                ]
            ),
        )
    )

ft.run(main)
```

---

## CupertinoActivityIndicator

**控制項說明**：iOS 風格的圓形載入指示器。適用於需要表示程式忙碌中的場景。

**關鍵屬性**：
- `color` — 顏色
- `radius` — 半徑大小

---

## CupertinoAlertDialog

**控制項說明**：iOS 風格的彈出警告對話框。

**關鍵屬性**：
- `title` — 標題
- `content` — 內容
- `actions` — 操作按鈕列表

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    def show_dlg(e):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Warning"),
            content=ft.Text("Are you sure?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: page.close_dialog()),
                ft.TextButton("OK", on_click=lambda _: page.close_dialog()),
            ],
        )
        page.open_dialog()

    page.add(ft.ElevatedButton("Show Dialog", on_click=show_dlg))

ft.run(main)
```

---

## CupertinoNavigationBar

**控制項說明**：iOS 風格的頂部導航列。

**關鍵屬性**：
- `leading` / `trailing` — 左右兩側的控制項
- `middle` — 中間標題
- `background_color` — 背景顏色

---

## DataTable（資料表格）

**控制項說明**：以表格形式展示結構化資料。支援排序、欄位標題、水平/垂直捲動。

**關鍵屬性**：
- `columns` — 欄位定義（`DataColumn` 列表）
- `rows` — 資料列（`DataRow` 列表）
- `heading_row_height` — 標題列高度
- `data_row_height` — 資料列高度
- `column_spacing` — 欄位間距
- `horizontal_lines` — 水平分隔線樣式
- `show_checkbox_column` — 是否顯示核取方塊欄位
- `sort_column_index` — 當前排序欄位索引
- `sort_ascending` — 排序方向

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Age"), numeric=True),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("John")),
                        ft.DataCell(ft.Text("30")),
                        ft.DataCell(ft.Text("Active")),
                    ]
                ),
            ],
        )
    )

ft.run(main)
```

---

## DatePicker（日期選擇器）

**控制項說明**：Material 風格的日期選擇對話框，支援日曆視圖和文字輸入兩種模式。

**關鍵屬性**：
- `value` — 目前選中的日期
- `current_date` — 今天日期（會在日曆上高亮）
- `first_date` / `last_date` — 可選範圍
- `entry_mode`（`DatePickerEntryMode`）— 初始輸入模式：CALENDAR/INPUT/ONLY_CALENDAR
- `date_picker_mode`（`DatePickerMode`）— 初始顯示模式
- `modal` — 是否為強制-modal 對話框

**事件**：
- `on_change` — 當使用者確認選擇時觸發
- `on_entry_mode_change` — 當輸入模式改變時觸發

**最小範例**：

```python
import datetime
import flet as ft

def main(page: ft.Page):
    picker = ft.DatePicker()

    def confirm(e):
        page.add(ft.Text(f"Selected: {picker.value.strftime('%m/%d/%Y')}"))
        page.update()

    picker.on_change = confirm
    page.dialog = picker
    page.add(ft.ElevatedButton("Pick Date", on_click=lambda _: page.open_dialog()))

ft.run(main)
```

---

## DateRangePicker（日期範圍選擇器）

**控制項說明**：選擇一個日期範圍的對話框。

**關鍵屬性**：
- `value` — 目前選中的日期範圍（`DateRange`）
- `start_field_label` / `end_field_label` — 開始/結束欄位的標籤文字

**事件**：
- `on_change` — 當範圍確認時觸發

---

## Dismissible（滑動刪除）

**控制項說明**：支援水平或垂直滑動來執行操作（如刪除）的元件。

**關鍵屬性**：
- `content` — 滑動時顯示的內容
- `direction`（`DismissDirection`）— 滑動方向：HORIZONTAL/UP/DOWN/START_TO_END/END_TO_START
- `dismiss_thresholds` — 各方向解除閾值
- `background` — 滑動時顯示的背景

**事件**：
- `on_dismiss` — 當滑動完成時觸發
- `on_update` — 當滑動進度更新時觜發

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Dismissible(
            content=ft.ListTile(title=ft.Text("Swipe me")),
            background=ft.Container(bgcolor=ft.Colors.RED),
            direction=ft.DismissDirection.END_TO_START,
            on_dismiss=lambda _: print("Dismissed!"),
        )
    )

ft.run(main)
```

---

## Divider（分隔線）

**控制項說明**：水平或垂直分隔線，用於區隔內容區塊。

**關鍵屬性**：
- `height` — 分隔線高度（水平時）
- `width` — 分隔線寬度（垂直時）
- `thickness` — 線條粗細
- `color` — 線條顏色

---

## Draggable / DragTarget（拖放）

**控制項說明**：Draggable 讓元件可被拖曳；DragTarget 是拖放目的地。兩者結合實現拖放功能。

**Draggable 關鍵屬性**：
- `content` — 拖曳時顯示的內容
- `data` — 攜帶的資料

**DragTarget 關鍵屬性**：
- `on_accept` — 當收到 Draggable 時的回呼

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    def accept(e):
        print(f"Accepted: {e.control.data}")

    page.add(
        ft.DragTarget(
            content=ft.Container(bgcolor=ft.Colors.BLUE_100, width=100, height=100),
            on_accept=accept,
        ),
        ft.Draggable(
            content=ft.Container(bgcolor=ft.Colors.GREEN, width=50, height=50),
            data="drag_data",
        ),
    )

ft.run(main)
```

---

## Dropdown（下拉選單）

**控制項說明**：下拉式選單，讓使用者從選項列表中選擇。

**關鍵屬性**：
- `options` — 選項列表（`Option` 物件）
- `value` — 目前選中的值
- `hint` — 未選中時顯示的提示文字
- `label` — 標籤文字
- `border` / `border_radius` — 邊框樣式
- `disabled` — 是否停用

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    def changed(e):
        print(f"Selected: {dropdown.value}")

    dropdown = ft.Dropdown(
        label="Choose option",
        options=[
            ft.dropdown.Option("A", "Option A"),
            ft.dropdown.Option("B", "Option B"),
            ft.dropdown.Option("C", "Option C"),
        ],
        on_change=changed,
    )
    page.add(dropdown)

ft.run(main)
```

---

## ExpansionTile（擴展瓷磚）

**控制項說明**：單行 ListTile，點擊可展開或收合以顯示或隱藏內部控制項。

**關鍵屬性**：
- `title` — 主要標題
- `subtitle` — 副標題
- `leading` / `trailing` — 左右兩側的控制項
- `expanded` — 目前是否展開
- `controls` — 展開後顯示的控制項列表
- `maintain_state` — 展開/收合時是否維持內部控制項狀態
- `affinity`（`TileAffinity`）— 展開箭頭圖示位置：LEADING/TRAILING
- `collapsed_bgcolor` / `bgcolor` — 收合/展開時的背景顏色

**事件**：
- `on_change` — 當展開狀態改變時觸發

**最小範例**：

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.ExpansionTile(
            width=400,
            title=ft.Text("Account"),
            subtitle="Manage profile and security",
            expanded=True,
            controls=[
                ft.ListTile(title=ft.Text("Profile")),
                ft.ListTile(title=ft.Text("Security")),
            ],
        )
    )

ft.run(main)
```
