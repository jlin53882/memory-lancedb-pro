# Flet 0.82.2 主題與裝飾 — 學習筆記

> 來源：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\controls\`  
> 記錄日期：2026-03-23

---

## Theme

**檔案：`theme.py`（行 1 起）**

### ColorScheme（行 116–322）

`ColorScheme` 是一個基於 Material 3 規範的 dataclass，包含 **40+ 顏色屬性**。核心屬性：

| 屬性 | 說明 |
|------|------|
| `primary` / `on_primary` | 主色及其對比文字色 |
| `primary_container` / `on_primary_container` | 主色容器（較淺） |
| `secondary` / `on_secondary` | 次要色 |
| `surface` / `on_surface` | 表面色（卡片背景） |
| `error` / `error_container` | 錯誤色 |
| `outline` / `outline_variant` | 邊界線顏色 |
| `surface_container_*` | Material 3 的分層表面色（行 295–318） |
| `inverse_surface` / `inverse_primary` | 反転表面色（用於 SnackBar 這類元件） |

```python
# 建立自訂 ColorScheme（行 116）
cs = ColorScheme(
    primary="#6750A4",
    on_primary="#FFFFFF",
    surface="#FFFBFE",
)
```

### TextTheme（行 325–392）

定義 Material 3 的 5 組文字樣式，每組 3 種尺寸：

| 群組 | 尺寸 |
|------|------|
| **Display** | `display_large`, `display_medium`, `display_small` |
| **Headline** | `headline_large`, `headline_medium`, `headline_small` |
| **Title** | `title_large`, `title_medium`, `title_small` |
| **Label** | `label_large`, `label_medium`, `label_small` |
| **Body** | `body_large`, `body_medium`, `body_small` |

所有屬性型別為 `Optional[TextStyle]`（行 348–392）。

### Theme 主類別（行 ~1900+）

全域主題透過 `page.theme = Theme(...)` 設定，支援：

```python
# 設定全域主題（行 ~1900）
page.theme = Theme(
    color_scheme_seed="#6750A4",        # 用單一顏色自動生成 ColorScheme
    use_material3=True,                 # 啟用 Material 3
    font_family="Noto Sans TC",
    text_theme=TextTheme(
        body_large=TextStyle(size=16, color="#333333"),
    ),
)
```

**重要子主題類別**（全部定義在 `theme.py`）：

| 類別 | 用途 |
|------|------|
| `AppBarTheme`（行 ~1300） | AppBar 樣式 |
| `CardTheme`（行 ~1200） | Card 卡片樣式 |
| `DialogTheme`（行 ~1100） | AlertDialog 對話框 |
| `DividerTheme`（行 ~1480） | Divider / VerticalDivider |
| `DataTableTheme`（行 ~1780） | DataTable 表格 |
| `ProgressIndicatorTheme`（行 ~1680） | ProgressBar / ProgressRing |
| `ChipTheme`（行 ~1220） | Chip 元件 |
| `SnackBarTheme`（行 ~1500） | SnackBar 提示條 |
| `BottomSheetTheme`（行 ~1170） | 底部彈出面板 |
| `NavigationBarTheme`（行 ~1860） | 底部導航列 |
| `TabBarTheme`（行 ~620） | TabBar 分頁 |

---

## Border（重要：Border.all() vs ft.border.all()）

**檔案：`border.py`（行 1 起）**

### BorderSide（行 ~60–160）

單一邊的邊框設定：

```python
@dataclass
class BorderSide:
    width: Number = 1.0          # 線寬，設 0 為頭髮線（1px）
    color: ColorValue = Colors.BLACK
    stroke_align: BorderSideStrokeAlignValue = BorderSideStrokeAlign.INSIDE
    style: BorderStyle = BorderStyle.SOLID   # SOLID 或 NONE
```

`BorderSideStrokeAlign`（行 15–30）是 Enum：
- `INSIDE = -1.0`（預設）：邊框全繪製在路徑內側
- `CENTER = 0.0`：對齊中心
- `OUTSIDE = 1.0`：繪製在外側

```python
# 透明邊框（不繪製但佔空間）
BorderSide(width=0.0, style=BorderStyle.NONE)

# 頭髮線（hairline border，width=0 但顯示 1px）
BorderSide(width=0.0)

# 外側對齊的粗邊框
BorderSide(width=2.0, color="#FF0000", stroke_align=BorderSideStrokeAlign.OUTSIDE)
```

### Border（行 ~165–280）

四邊邊框容器：

```python
@dataclass
class Border:
    top: BorderSide = field(default_factory=lambda: BorderSide.none())
    right: BorderSide
    bottom: BorderSide
    left: BorderSide
```

**工廠方法（classmethod）— 正確寫法：**

```python
# 所有邊相同（行 ~195）
Border.all(width=1.0, color="#000000", side=None)
# 若傳入 side=BorderSide(...)，width 和 color 會被忽略

# 對稱邊框：上下一組、左右一組（行 ~225）
Border.symmetric(vertical=BorderSide(...), horizontal=BorderSide(...))

# 只指定某些邊（行 ~255）
Border.only(left=BorderSide(...), top=BorderSide(...))
```

### ⚠️ Deprecated 模組級函式（行 ~290–330）

> 這些是在模組層直接呼叫的 `ft.border.all()` 寫法，**已廢棄**，將在 0.83.0 刪除：

```python
# ❌ 舊寫法（deprecated since 0.80.0，刪除於 0.83.0）
ft.border.all(width=1.0, color="#000")
ft.border.symmetric(vertical=..., horizontal=...)
ft.border.only(left=..., top=...)

# ✅ 新寫法（直接用 Border classmethod）
Border.all(width=1.0, color="#000")
Border.symmetric(vertical=..., horizontal=...)
Border.only(left=..., top=...)
```

---

## BorderRadius（重要：BorderRadius.all() vs ft.border_radius.only()）

**檔案：`border_radius.py`（行 1 起）**

### BorderRadius dataclass（行 ~25–130）

```python
@dataclasses.dataclass
class BorderRadius:
    top_left: Number
    top_right: Number
    bottom_left: Number
    bottom_right: Number
```

### 工廠方法（classmethod）— 正確寫法：

```python
# 所有角相同（行 ~35）
BorderRadius.all(10)                    # 四角皆為 10

# 水平對稱：左右相同、上下各自（行 ~42）
BorderRadius.horizontal(left=5, right=5) # top_left=left, top_right=right, bottom_left=left, bottom_right=right

# 垂直對稱：上下相同、左右各自（行 ~55）
BorderRadius.vertical(top=8, bottom=2)   # top_left=top, top_right=top, bottom_left=bottom, bottom_right=bottom

# 只設定某些角（行 ~67）
BorderRadius.only(top_left=10, bottom_right=5)
```

### ⚠️ Deprecated 模組級函式（行 ~135–175）

> 直接呼叫 `ft.border_radius.all()` 等，已廢棄，0.83.0 刪除：

```python
# ❌ 舊寫法
ft.border_radius.all(10)
ft.border_radius.only(top_left=10)
ft.border_radius.horizontal(left=5)
ft.border_radius.vertical(top=8)

# ✅ 新寫法
BorderRadius.all(10)
BorderRadius.only(top_left=10)
BorderRadius.horizontal(left=5)
BorderRadius.vertical(top=8)
```

### 算術運算（行 ~100–130）

`BorderRadius` 支援四則運算：

```python
r1 = BorderRadius.all(10)
r2 = BorderRadius.only(top_left=5)
r3 = r1 + r2      # 各角相加
r4 = r1 * 2       # 每角乘以 2
r5 = r1 // 2      # 每角整除 2（不能除以 0）
```

---

## Padding

**檔案：`padding.py`（行 1 起）**

```python
@dataclass
class Padding:
    left: Number = 0
    top: Number = 0
    right: Number = 0
    bottom: Number = 0
```

### 工廠方法：

```python
# 所有方向相同（行 ~35）
Padding.all(8)                          # 等同 Padding(8, 8, 8, 8)

# 對稱：上下一組、左右一組（行 ~41）
Padding.symmetric(vertical=10, horizontal=5)  # top/bottom=10, left/right=5

# 只設定某些邊（行 ~50）
Padding.only(left=8, top=4)

# 零padding（行 ~60）
Padding.zero()                          # 等同 Padding.only()
```

### ⚠️ Deprecated（行 ~70–90）

```python
# ❌ 舊寫法
ft.padding.all(8)
ft.padding.symmetric(vertical=10, horizontal=5)
ft.padding.only(left=8)

# ✅ 新寫法
Padding.all(8)
Padding.symmetric(vertical=10, horizontal=5)
Padding.only(left=8)
```

`PaddingValue = Union[Number, Padding]`（行 ~100）：可直接傳數字或 Padding 實例。

---

## DataTable

**檔案：`datatable.py`（行 1 起）**

### 組成結構

DataTable 由三層子控制項組成：

```
DataTable
 ├── columns: list[DataColumn]       # 欄位定義
 └── rows: list[DataRow]             # 資料列
      └── cells: list[DataCell]      # 每列的儲存格
```

### DataColumn（行 ~45–95）

```python
class DataColumn(Control):
    label: StrOrControl              # 欄位抬頭（Text 或 Icon）
    numeric: bool = False            # 數值欄位靠右對齊
    tooltip: Optional[str] = None
    heading_row_alignment: Optional[MainAxisAlignment] = None
    on_sort: Optional[EventHandler[DataColumnSortEvent]] = None  # 排序事件
```

### DataCell（行 ~100–160）

```python
class DataCell(Control):
    content: StrOrControl            # 儲存格內容（Text、Dropdown 或容器）
    placeholder: bool = False         # 是否為預設文字
    show_edit_icon: bool = False      # 顯示編輯圖示
    # 事件：on_tap, on_double_tap, on_long_press, on_tap_cancel, on_tap_down
```

### DataRow（行 ~165–230）

```python
class DataRow(Control):
    cells: list[DataCell]            # 必須與 columns 數量完全一致
    color: Optional[ControlStateValue[ColorValue]] = None  # 背景色（可響應狀態）
    selected: bool = False
    on_select_change: Optional[ControlEventHandler["DataRow"]] = None
    on_long_press: Optional[ControlEventHandler["DataRow"]] = None
```

### DataTable 主類別（行 ~235–380）

```python
class DataTable(LayoutControl):
    columns: list[DataColumn]
    rows: list[DataRow] = field(default_factory=list)

    # 排序
    sort_column_index: Optional[int] = None     # 目前排序的欄位索引
    sort_ascending: bool = False                # True=遞增，False=遞減

    # 勾選框
    show_checkbox_column: bool = False          # 顯示列勾選框

    # 邊框與線條
    border: Optional[Border] = None             # 表格外框
    border_radius: Optional[BorderRadiusValue] = None
    horizontal_lines: Optional[BorderSide] = None  # 列之間的水平線
    vertical_lines: Optional[BorderSide] = None    # 欄之間的垂直線

    # 間距
    column_spacing: Optional[Number] = None      # 欄與欄之間的間距
    horizontal_margin: Optional[Number] = None   # 左右外邊距

    # 列高
    data_row_min_height: Optional[Number] = None   # 預設 48.0
    data_row_max_height: Optional[Number] = None   # 預設 48.0
    heading_row_height: Optional[Number] = None

    # 顏色
    data_row_color: Optional[ControlStateValue[ColorValue]] = None
    heading_row_color: Optional[ControlStateValue[ColorValue]] = None
    bgcolor: Optional[ColorValue] = None
    gradient: Optional[Gradient] = None

    # 文字樣式
    data_text_style: Optional[TextStyle] = None
    heading_text_style: Optional[TextStyle] = None

    # 分隔線
    divider_thickness: Number = 1.0              # 列之間分隔線粗細

    # 全選
    on_select_all: Optional[ControlEventHandler["DataTable"]] = None
```

### DataTable 驗證邏輯（行 ~355–380）

```python
# 驗證每列的 DataCell 數量必須與 DataColumn 數量完全一致
# 驗證 data_row_min_height <= data_row_max_height
# 驗證 divider_thickness >= 0
# 驗證 sort_column_index 在有效範圍內
```

### data_table_style（無獨立屬性）

`DataTable` 沒有 `data_table_style` 屬性。全域樣式應透過 `Theme.data_table_theme: Optional[DataTableTheme]` 設定，`DataTableTheme` 定義於 `theme.py` 行 ~1780：

```python
@dataclass
class DataTableTheme:
    checkbox_horizontal_margin: Optional[Number] = None
    column_spacing: Optional[Number] = None
    data_row_max_height: Optional[Number] = None
    data_row_min_height: Optional[Number] = None
    data_row_color: Optional[ControlStateValue[ColorValue]] = None
    data_text_style: Optional[TextStyle] = None
    divider_thickness: Optional[Number] = None
    heading_text_style: Optional[TextStyle] = None
    heading_row_color: Optional[ControlStateValue[ColorValue]] = None
    heading_row_height: Optional[Number] = None
    decoration: Optional[BoxDecoration] = None
    heading_row_alignment: Optional[MainAxisAlignment] = None
```

---

## ProgressBar

**檔案：`progress_bar.py`（行 1 起）**

```python
class ProgressBar(LayoutControl):
    value: Optional[Number] = None   # 0.0~1.0，None=indeterminate（不確定模式）
    bar_height: Optional[Number] = None  # 進度條高度

    color: Optional[ColorValue] = None   # 進度條顏色
    bgcolor: Optional[ColorValue] = None # 軌道背景色

    border_radius: Optional[BorderRadiusValue] = None  # 預設 BorderRadius.all(0)

    # 停止指示器（Material 3 2023+ 功能）
    stop_indicator_color: Optional[ColorValue] = None
    stop_indicator_radius: Optional[Number] = None
    track_gap: Optional[Number] = None   # 進度條與軌道的間隙

    # 外觀版本
    year_2023: Optional[bool] = None    # True=2023外觀，False=最新MD3外觀

    # 無障礙
    semantics_label: Optional[str] = None
    semantics_value: Optional[Number] = None
```

### 使用範例

```python
# 確定進度（80%）
ft.ProgressBar(width=400, value=0.8)

# 不確定模式（動畫）
ft.ProgressBar(width=400, value=None)

# 自訂高度與圓角
ft.ProgressBar(width=400, value=0.5, bar_height=8, border_radius=10)

# 隱藏 stop indicator（year_2023=True 或非 Material 3）
ft.ProgressBar(width=400, value=0.5, stop_indicator_radius=0)
```

---

## Divider

**檔案：`divider.py`（行 1 起）**

```python
class Divider(Control):
    color: Optional[ColorValue] = None        # 線的顏色（預設用 DividerTheme）
    height: Optional[Number] = None           # 佔位高度（預設 16.0）
    leading_indent: Optional[Number] = None  # 左側縮排（預設 0.0）
    trailing_indent: Optional[Number] = None  # 右側縮排（預設 0.0）
    thickness: Optional[Number] = None        # 線的粗細（預設 0.0=1px）
    radius: Optional[BorderRadiusValue] = None  # 圓角
```

### 行為細節

- `height`：整個 Divider 控制項的垂直空間，線在其中間
- `thickness=0.0`：始終繪製為 1 物理像素的線
- 若 `color=None`：使用 `DividerTheme.color`
- 若 `height=None`：使用 `DividerTheme.space`（預設 16.0）
- 若 `thickness=None`：使用 `DividerTheme.thickness`（預設 0.0）

### 使用範例

```python
ft.Column(
    width=240,
    spacing=10,
    controls=[
        ft.Text("Section A", weight=ft.FontWeight.w_600),
        ft.Divider(),                          # 預設 Divider
        ft.Text("Section B"),
        ft.Divider(color="#FF0000", thickness=2),  # 紅色粗線
        ft.Divider(leading_indent=20, trailing_indent=20),  # 縮排線
        ft.Divider(border_radius=5),          # 圓角線
    ],
)
```

---

## 常用程式碼範例

### 設定全域深色主題

```python
import flet as ft

def main(page: ft.Page):
    page.theme = Theme(
        color_scheme_seed="#1F1F1F",
        use_material3=True,
        brightness=Brightness.DARK,
    )
    page.add(ft.Text("Hello Dark Theme"))
```

### Card 組合應用（結合所有裝飾）

```python
ft.Card(
    elevation=4,
    shape=BorderRadius.all(12),          # ✅ 新寫法
    # shape=ft.border_radius.all(12),     # ❌ 舊寫法，已廢棄
    content=ft.Container(
        padding=Padding.all(16),          # ✅ 新寫法
        # padding=ft.padding.all(16),      # ❌ 舊寫法，已廢棄
        border=Border.all(1, "#E0E0E0"),  # ✅ 新寫法
        # border=ft.border.all(1, "#E0E0E0"),  # ❌ 舊寫法，已廢棄
        border_radius=BorderRadius.all(12),
        content=ft.Text("Card 內容"),
    ),
)
```

### DataTable 完整範例

```python
dt = ft.DataTable(
    columns=[
        ft.DataColumn(
            label=ft.Text("Name"),
            on_sort=lambda e: print(f"Sort by column {e.column_index}, asc={e.ascending}"),
        ),
        ft.DataColumn(label=ft.Text("Age"), numeric=True),
        ft.DataColumn(label=ft.Text("Role")),
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Alice")),
                ft.DataCell(ft.Text("28"), placeholder=True),  # 數值通常設 numeric=True 靠右
                ft.DataCell(ft.Text("Engineer")),
            ],
            selected=False,
            on_select_change=lambda e: print(f"Row selected: {e.control.selected}"),
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Bob")),
                ft.DataCell(ft.Text("35")),
                ft.DataCell(ft.Text("Designer")),
            ],
        ),
    ],
    sort_column_index=0,
    sort_ascending=True,
    show_checkbox_column=True,
    heading_row_height=56,
    data_row_min_height=48,
    data_row_max_height=64,
    divider_thickness=1,
    border=Border.all(1, "#E0E0E0"),
    border_radius=BorderRadius.all(8),
)
```

---

## 重要發現與注意事項

### 1. Deprecated 迁移（0.80.0 → 0.83.0）

所有模組層級工廠函式（`ft.border.*`、`ft.border_radius.*`、`ft.padding.*`）已從 0.80.0 標記為 deprecated，**將在 0.83.0 刪除**。現在就應該使用 classmethod 寫法：

| 舊寫法（deprecated） | 新寫法（正確） |
|------|------|
| `ft.border.all()` | `Border.all()` |
| `ft.border.symmetric()` | `Border.symmetric()` |
| `ft.border.only()` | `Border.only()` |
| `ft.border_radius.all()` | `BorderRadius.all()` |
| `ft.border_radius.only()` | `BorderRadius.only()` |
| `ft.border_radius.horizontal()` | `BorderRadius.horizontal()` |
| `ft.border_radius.vertical()` | `BorderRadius.vertical()` |
| `ft.padding.all()` | `Padding.all()` |
| `ft.padding.symmetric()` | `Padding.symmetric()` |
| `ft.padding.only()` | `Padding.only()` |

### 2. Border.all() 的 side 參數優先級

`Border.all(width=, color=, side=)` 中，若傳入 `side=BorderSide(...)`，則 `width` 和 `color` 參數會被忽略（行 ~207）：

```python
# width 和 color 會被忽略
Border.all(width=10, color="red", side=BorderSide(width=1, color="blue"))
# 實際效果等同 Border.all(side=BorderSide(width=1, color="blue"))
```

### 3. BorderRadius 的數值型別

`BorderRadius` 是 `@dataclasses.dataclass`（非 `@dataclass`），且 `top_left` 等為 `Number`（浮點），可用算術運算（`+`, `-`, `*`, `//`），但需注意 floor division 不能除以 0（行 ~130）。

### 4. DataTable 數量驗證

`DataTable.before_update()`（行 ~355–380）會嚴格驗證：
- 每列的 `DataCell` 數量 **必須與** `DataColumn` 數量完全一致
- `data_row_min_height <= data_row_max_height`
- `sort_column_index` 必須在有效範圍內

### 5. ProgressBar indeterminate 模式

當 `value=None` 時，ProgressBar 顯示「不確定模式」（predetermined animation），不是進度 0%。

### 6. Divider 佔位高度行為

`Divider.height` 是「佔位總高度」，線本身在其中間垂直置中；`thickness` 才是實際繪製的線寬。

### 7. Theme 繼承結構

Flet 的 Theme 系統非常龐大，`Theme` 類別包含 40+ 個子主題成員，所有子主題（`CardTheme`、`DialogTheme`、`DividerTheme` 等）都是獨立的 dataclass，定義在 `theme.py` 中各自對應的位置。

### 8. BorderRadiusValue / PaddingValue 型別

```python
BorderRadiusValue = Union[Number, BorderRadius]   # 行 ~180 border_radius.py
PaddingValue = Union[Number, Padding]               # 行 ~100 padding.py
```

這表示可以直接傳數字（如 `10`）給需要 `BorderRadiusValue` 的屬性，框架會自動轉換為 `BorderRadius.all(10)`。
