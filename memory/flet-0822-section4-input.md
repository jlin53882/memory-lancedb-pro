# Flet 0.82.2 — Section 4: Input 控制項

> version: flet:0.82.2
> 來源：docs.flet.dev（官方文件）
> 整理日期：2026-03-22

---

## ✅ 已驗證（文件已成功抓取）

| 控制項 | URL | 狀態 |
|--------|-----|------|
| TextField | docs.flet.dev/controls/textfield/ | ✅ 已抓取 |
| OutlinedButton | docs.flet.dev/controls/outlinedbutton/ | ✅ 已抓取 |
| IconButton | docs.flet.dev/controls/iconbutton/ | ✅ 已抓取 |
| Dropdown | docs.flet.dev/controls/dropdown/ | ✅ 已抓取（部分截斷） |
| DataTable | docs.flet.dev/controls/datatable/ | ✅ 已抓取 |

## ❌ 待驗證

| 控制項 | URL | 原因 |
|--------|-----|------|
| ElevatedButton | docs.flet.dev/controls/elevatedbutton/ | 404 Not Found |
| FilledButton | docs.flet.dev/controls/filledbutton/ | 頁面存在但屬性區塊未抓到（截斷） |

> 💡 ElevatedButton / FilledButton 可能是 0.82.x 新增的控制項，文件 URL 結構可能與預期不同。

---

## 1. TextField

**文件 URL：** https://docs.flet.dev/controls/textfield/
**繼承：** `FormFieldControl` → `AdaptiveControl`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `value` | `str` | 目前文字值 |
| `label` | `str` | 標籤文字（浮動標籤） |
| `hint_text` | `str` | 輸入前的佔位提示 |
| `password` | `bool` | 是否隱藏文字（如密碼） |
| `can_reveal_password` | `bool` | 是否顯示切換密碼可見性的眼睛按鈕 |
| `multiline` | `bool` | 是否支援多行文字 |
| `max_lines` | `int` | 最大行數（超出換行） |
| `min_lines` | `int` | 最小行數（自動高度） |
| `max_length` | `int` | 最大字元數限制 |
| `read_only` | `bool` | 唯讀模式 |
| `autofocus` | `bool` | 頁面載入時自動聚焦 |
| `autocorrect` | `bool` | 是否啟用自動校正 |
| `enable_suggestions` | `bool` | 是否顯示輸入建議 |
| `capitalization` | `TextCapitalization` | 自動大寫設定 |
| `keyboard_type` | `KeyboardType` | 鍵盤類型（數字、郵箱等） |
| `input_filter` | `InputFilter` | 即時過濾/驗證（0.82.x 新增） |
| `selection` | `TextSelection` | 目前選取範圍，可程式設定（0.82.x 新增） |
| `text_align` | `TextAlign` | 文字水平對齊 |
| `shift_enter` | `bool` | Shift+Enter 新行，Enter 發 `on_submit`（聊天模式） |
| `smart_dashes_type` | `bool` | 自動格式化破折號 |
| `smart_quotes_type` | `bool` | 自動格式化引號 |
| `cursor_color` | `ColorValue` | 游標顏色 |
| `cursor_width` | `Number` | 游標寬度 |
| `cursor_height` | `Number` | 游標高度（0.82.x 新增） |
| `cursor_radius` | `Number` | 游標圓角（0.82.x 新增） |
| `show_cursor` | `bool` | 是否顯示游標 |

### 事件

| 事件 | 說明 |
|------|------|
| `on_change` | 輸入內容改變時觸發 |
| `on_submit` | 按下 Enter 時觸發（密碼模式也能用） |
| `on_focus` | 獲得焦點時觸發 |
| `on_blur` | 失去焦點時觸發 |
| `on_selection_change` | 選取範圍或脫字符位置改變時（0.82.x 新增） |
| `on_click` | 點擊時（0.82.x 新增，TBD） |

---

## 2. ElevatedButton

**文件 URL：** https://docs.flet.dev/controls/elevatedbutton/ → ❌ **404**
**說明：** 文件路徑可能為 `/elevated-button/` 或已改名，需手動驗證。

> ⚠️ 0.82.2 預設有 `ft.ElevatedButton`，但官方文件路徑抓取失敗。

### 參考已知屬性（由 OutlinedButton / FilledButton 反推）

- `content`: 按鈕內容（文字或 Control）
- `icon`: 圖示
- `disabled`: 是否停用
- `on_click`: 點擊事件
- `style`: `ButtonStyle` 樣式

### ❌ 待驗證：請手動開啟瀏覽器確認 URL

---

## 3. FilledButton

**文件 URL：** https://docs.flet.dev/controls/filledbutton/
**說明：** 頁面有內容但屬性區塊截斷，以下為從代碼範例中逆推的屬性。

### 主要屬性（代碼逆推，未完整抓取）

| 屬性 | 說明 |
|------|------|
| `content` | 按鈕內容 |
| `icon` | 圖示（可用 `ft.Icons.ADD_OUTLINED`） |
| `disabled` | 是否停用 |

### ❌ 待驗證：屬性文件需重新抓取完整內容

---

## 4. OutlinedButton

**文件 URL：** https://docs.flet.dev/controls/outlinedbutton/
**繼承：** `LayoutControl` → `AdaptiveControl`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `content` | `StrOrControl` | 自訂按鈕內容（與 `icon` 二選一） |
| `icon` | `IconDataOrControl` | 按鈕圖示 |
| `icon_color` | `ColorValue` | 圖示顏色 |
| `autofocus` | `bool` | 自動聚焦 |
| `clip_behavior` | `ClipBehavior` | 裁剪行為 |
| `style` | `ButtonStyle` | 自訂外觀 |
| `url` | `str \| Url` | 點擊後開啟的 URL |

### 事件

| 事件 | 說明 |
|------|------|
| `on_click` | 點擊時 |
| `on_focus` | 獲得焦點時 |
| `on_blur` | 失去焦點時 |
| `on_hover` | 滑鼠進入/離開（event.data = "true"/"false"） |
| `on_long_press` | 長按時 |

### 方法

| 方法 | 說明 |
|------|------|
| `focus()` | 請求聚焦 |

---

## 5. IconButton

**文件 URL：** https://docs.flet.dev/controls/iconbutton/
**繼承：** `LayoutControl` → `AdaptiveControl`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `icon` | `IconDataOrControl` | 顯示的圖示 |
| `icon_color` | `ColorValue` | 圖示前景色 |
| `icon_size` | `Number` | 圖示大小（虛擬像素） |
| `selected` | `bool` | 選中狀態（可用於 Toggle 行為） |
| `selected_icon` | `IconDataOrControl` | 選中狀態顯示的圖示 |
| `selected_icon_color` | `ColorValue` | 選中狀態的圖示顏色 |
| `autofocus` | `bool` | 自動聚焦 |
| `bgcolor` | `ColorValue` | 按鈕背景色 |
| `hover_color` | `ColorValue` | 懸停時的顏色 |
| `focus_color` | `ColorValue` | 聚焦時的顏色 |
| `highlight_color` | `ColorValue` | 按下時的顏色（漣漪前的填充色） |
| `splash_color` | `ColorValue` | 按下時漣漪的顏色 |
| `splash_radius` | `Number` | 漣漪半徑 |
| `disabled_color` | `ColorValue` | 停用時的圖示顏色 |
| `enable_feedback` | `bool` | 點擊是否要有聲音/震動回饋 |
| `padding` | `PaddingValue` | 圖示周圍的內距（決定可點擊區域） |
| `alignment` | `Alignment` | 圖示在按鈕內的對齊（預設 `CENTER`） |
| `visual_density` | `VisualDensity` | 佈局密度（compact/comfortable/standard） |
| `size_constraints` | `BoxConstraints` | 按鈕尺寸限制 |
| `mouse_cursor` | `MouseCursor` | 滑鼠游標類型 |
| `style` | `ButtonStyle` | 自訂外觀 |
| `url` | `str \| Url` | 點擊後開啟的 URL |

### 事件

| 事件 | 說明 |
|------|------|
| `on_click` | 點擊時 |
| `on_focus` | 獲得焦點時 |
| `on_blur` | 失去焦點時 |
| `on_hover` | 懸停時 |
| `on_long_press` | 長按時 |

### 方法

| 方法 | 說明 |
|------|------|
| `focus()` | 移動焦點到此按鈕 |

---

## 6. Dropdown

**文件 URL：** https://docs.flet.dev/controls/dropdown/
**說明：** 屬性區塊有部分截斷，以下為已確認的屬性。

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `value` | `str` | 目前選中的 key 值 |
| `options` | `list[DropdownOption]` | 下拉選項列表 |
| `label` | `str` | 標籤文字 |
| `hint_text` | `str` | 佔位提示文字 |
| `hint_style` | `TextStyle` | 提示文字樣式 |
| `editable` | `bool` | 是否可編輯輸入框（0.82.x 新增） |
| `enable_filter` | `bool` | 是否啟用搜尋過濾（0.82.x 新增） |
| `filled` | `bool` | 是否顯示填充背景 |
| `fill_color` | `ColorValue` | 填充背景顏色 |
| `border` | `InputBorder` | 邊框樣式（OUTLINE / UNDERLINE / NONE） |
| `border_color` | `ColorValue` | 邊框顏色 |
| `border_radius` | `Number` | 邊框圓角 |
| `border_width` | `Number` | 邊框寬度 |
| `focused_border_color` | `ColorValue` | 聚焦時的邊框顏色 |
| `focused_border_width` | `Number` | 聚焦時的邊框寬度 |
| `color` | `ColorValue` | 文字顏色 |
| `text_size` | `Number` | 字體大小 |
| `content_padding` | `PaddingValue` | 內距 |
| `prefix` | `Control` | 前綴內容 |
| `prefix_icon` | `IconData` | 前綴圖示 |
| `suffix` | `Control` | 後綴內容 |
| `autofocus` | `bool` | 自動聚焦 |
| `dense` | `bool` | 是否使用緊湊高度 |
| `capitalization` | `TextCapitalization` | 文字大寫設定 |
| `keyboard_type` | `KeyboardType` | 鍵盤類型 |
| `visible` | `bool` | 可見性 |
| `selected_index` | `int` | 目前選中的索引 |
| `show_only_selected_if_muted` | `bool` | （待確認） |
| `overlay_color` | `ColorValue` | 下拉選單覆蓋層顏色 |

### 事件

| 事件 | 說明 |
|------|------|
| `on_change` | 選項改變時 |
| `on_focus` | 獲得焦點時 |
| `on_blur` | 失去焦點時 |

### DropdownOption 結構

```python
# 基本用法
ft.DropdownOption(key="a", text="Item A")

# 帶圖示
ft.DropdownOption(key="name", leading_icon=ft.Icons.ICON_NAME)

# 帶自訂內容
ft.DropdownOption(
    key=color.value,
    content=ft.Text(value=color.value, color=color)
)

# 帶樣式
ft.DropdownOption(
    key="a",
    text="Item A",
    style=ft.ButtonStyle(
        shape=ft.BeveledRectangleBorder(radius=15),
        color={ft.ControlState.HOVERED: ft.Colors.WHITE, ...}
    )
)
```

> 💡 還支援 `ft.dropdown.Option()`（小寫）作為別名。

---

## 7. DataTable

**文件 URL：** https://docs.flet.dev/controls/datatable/
**繼承：** `LayoutControl`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `columns` | `list[DataColumn]` | 欄位定義列表 |
| `rows` | `list[DataRow]` | 資料列列表 |
| `border` | `Border` | 整體邊框 |
| `border_radius` | `BorderRadiusValue` | 圓角 |
| `border_color` | `ColorValue` | 邊框顏色 |
| `bgcolor` | `ColorValue` | 背景色 |
| `gradient` | `Gradient` | 背景漸層 |
| `heading_row_color` | `ControlStateValue[ColorValue]` | 表頭行顏色（可依狀態變化） |
| `heading_row_height` | `Number` | 表頭行高度 |
| `heading_text_style` | `TextStyle` | 表頭文字樣式 |
| `data_row_min_height` | `Number` | 資料列最小高度 |
| `data_row_max_height` | `Number` | 資料列最大高度 |
| `data_row_color` | `ControlStateValue[ColorValue]` | 資料列顏色 |
| `data_text_style` | `TextStyle` | 資料文字樣式 |
| `horizontal_margin` | `Number` | 第一欄與最後一欄的外間距 |
| `column_spacing` | `Number` | 欄位間的水平間距 |
| `horizontal_lines` | `BorderSide` | 列之間的水平線（顏色+寬度） |
| `vertical_lines` | `BorderSide` | 欄之間的垂直線 |
| `divider_thickness` | `Number` | 分隔線寬度 |
| `show_bottom_border` | `bool` | 是否顯示底部邊框 |
| `show_checkbox_column` | `bool` | 是否顯示 checkbox 欄位 |
| `checkbox_horizontal_margin` | `Number` | checkbox 的水平外間距 |
| `sort_column_index` | `int` | 目前排序的欄位索引 |
| `sort_ascending` | `bool` | 排序是否為升序 |
| `clip_behavior` | `ClipBehavior` | 裁剪行為 |

### DataColumn 結構

```python
ft.DataColumn(
    label=ft.Text("Name"),        # 欄位標題
    numeric=False,                # 是否為數字欄位（靠右對齊）
    # on_sort=None,              # 排序回調（文件未列出但可能存在）
)
```

### DataRow 結構

```python
ft.DataRow(
    cells=[           # 每個儲存格
        ft.DataCell(ft.Text("John")),   # 純文字
        ft.DataCell(ft.Text("Smith")),
        ft.DataCell(ft.Text("43")),
    ],
    # on_select=None,   # 選中此列（當 show_checkbox_column=True）
)
```

### DataCell 結構

```python
ft.DataCell(
    content,           # 通常是 ft.Text() 或其他 Control
    # on_tap=None,     # 點擊事件
    # show_edit_icon=False,
)
```

### 事件

| 事件 | 說明 |
|------|------|
| `on_select_all` | 點擊全選 checkbox 時 |

---

## Input 與 0.28.3 差異摘要

> ⚠️ 以下差異基於文件對比。**重要提醒（來自歷史記憶）：文件 (docs.flet.dev) 為新版 API，專案使用 flet 0.28.3，文件與原始碼可能存在重大差異，務必以原始碼為準。**

### TextField 差異（0.28.3 vs 0.82.2）

| 差異項目 | 0.28.3 | 0.82.2 |
|----------|--------|--------|
| 繼承結構 | 直接繼承 `Control` | 改為 `FormFieldControl` → `AdaptiveControl` |
| 游標控制 | 無 | 新增 `cursor_color`, `cursor_width`, `cursor_height`, `cursor_radius` |
| 選取範圍 | 無 | 新增 `selection` 屬性（可程式設定選取）|
| 即時過濾 | 無 | 新增 `input_filter: InputFilter` |
| 選取變化事件 | 無 | 新增 `on_selection_change` 事件 |
| 智慧格式 | 無 | 新增 `smart_dashes_type`, `smart_quotes_type` |
| 聊天模式 | 無 | 新增 `shift_enter`（Enter 提交，Shift+Enter 新行）|
| 點擊事件 | 無 | 新增 `on_click`（文件標 TBD）|
| `hint_text` | `label` 引導佔位 | 0.82.x 明確有 `hint_text` 屬性 |

### Button 差異（0.28.3 vs 0.82.2）

| 差異項目 | 0.28.3 | 0.82.2 |
|----------|--------|--------|
| 按鈕類型 | 僅 `Button` | 新增 `ElevatedButton`, `FilledButton`, `OutlinedButton`, `IconButton` |
| `ElevatedButton` | 無 | 新增（文件 URL 待驗證）|
| `FilledButton` | 無 | 新增（文件 URL 待驗證）|
| `OutlinedButton` | 無 | 新增 |
| `IconButton` | 無 | 新增（含 selected 狀態、splash 等豐富屬性）|
| Focus/Blur 事件 | 按鈕通常無 | 新增 `on_focus`, `on_blur` |
| Long Press | 無 | 新增 `on_long_press` |
| URL 屬性 | 無 | 按鈕可設 `url` 直接開連結 |
| Hover 事件 | 無 | 新增 `on_hover`（IconButton / OutlinedButton）|

### Dropdown 差異（0.28.3 vs 0.82.2）

| 差異項目 | 0.28.3 | 0.82.2 |
|----------|--------|--------|
| 選項格式 | `options=["a","b","c"]` 或 `DropdownMenuItem` | 改為 `DropdownOption(key, text)` 結構 |
| 編輯輸入 | 無 | 新增 `editable=True` 屬性 |
| 搜尋過濾 | 無 | 新增 `enable_filter=True` 屬性 |
| 填充樣式 | 無 | 新增 `filled`, `fill_color` 屬性 |
| 自訂內容 | 無 | `DropdownOption.content` 支援任意 `Control` |
| Leading Icon | 無 | `DropdownOption` 支援 `leading_icon` |
| 樣式化選項 | 無 | `DropdownOption.style: ButtonStyle` 可個別設定樣式 |

### DataTable 差異（0.28.3 vs 0.82.2）

| 差異項目 | 0.28.3 | 0.82.2 |
|----------|--------|--------|
| 排序功能 | 無 | 新增 `sort_column_index`, `sort_ascending` |
| 漸層背景 | 無 | 新增 `gradient` 屬性 |
| 欄位間距 | 無 | 新增 `column_spacing` |
| 分隔線自訂 | 無 | 新增 `horizontal_lines`, `vertical_lines`, `divider_thickness` |
| 列高度控制 | 無 | 新增 `data_row_min_height`, `data_row_max_height` |
| 全選事件 | 無 | 新增 `on_select_all` |

---

## ⚠️ 重要警告

根據歷史分析（`flet_docs_vs_source_v0.28.3.md`），**文件 (docs.flet.dev) 為新版 API，專案使用的是 flet 0.28.3**。文件上的 API **不能直接使用**，必須以原始碼為準。

本文件內容來自文件抓取，**所有屬性/事件/功能在實際專案中使用前，必須以 `pip show flet` 確認版本，並查閱本地 flet 原始碼驗證**。
