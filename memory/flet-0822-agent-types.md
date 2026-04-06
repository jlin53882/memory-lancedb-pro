# Flet Types 參考手冊

**版本標籤**：`flet:0.82.2`  
**來源**：https://docs.flet.dev/types/  
**最後更新**：2026-03-22  
**語言**：繁體中文

---

## ⚠️ 404 頁面（無法取得）

以下 URL 在 `docs.flet.dev` 上不存在（文件路徑可能已變更）：

| URL | 原因 |
|-----|------|
| `types/color/` | 404 - 可能已移至 `controls/page/` 或 `classes/page/` |
| `types/cursorkind/` | 404 - 可能已移除或改名 |
| `types/dragleteavevent/` | 404 - 拼寫錯誤？正確名稱可能是 `dragleaveevent` |
| `types/dragevent/` | 404 - 可能在 `controls/gesturedetector/` 說明 |
| `types/keyboardkey/` | 404 - 可能已移至 `controls/keyboardlistener/` |
| `types/pointerkind/` | 404 - 可能已移除 |

> 如需這些類型的具體資訊，建議直接查看 Flet 原始碼（`flet/py/flet/types.py`）。

---

## FontWeight

### 用途
控制文字的粗細（字重），影響字形的筆畫厚度。

### 類型定義
`enum.Enum` — 繼承自 Python 內建的列舉類型。

### 成員列表

| 成員 | 字串值 | 說明 |
|------|--------|------|
| `W_100` | `'w100'` | 極細（Thin） |
| `W_200` | `'w200'` | 超細（Extra-light） |
| `W_300` | `'w300'` | 細（Light） |
| `W_400` | `'w400'` | 正常（Normal / regular / plain），預設值 |
| `W_500` | `'w500'` | 中等（Medium） |
| `W_600` | `'w600'` | 半粗（Semi-bold） |
| `W_700` | `'w700'` | 粗（Bold） |
| `W_800` | `'w800'` | 超粗（Extra-bold） |
| `W_900` | `'w900'` | 最粗（Black） |
| `NORMAL` | `'normal'` | 等同 `w400`，預設值 |
| `BOLD` | `'bold'` | 等同 `w700` |

### 使用方式

```python
import flet as ft

# 直接指定字重值
ft.Text("粗體文字", weight=ft.FontWeight.BOLD)
ft.Text("細體文字", weight=ft.FontWeight.W_300)

# 或使用等價的字串值
ft.Text("粗體文字", weight="bold")
ft.Text("細體文字", weight="w300")

# 枚舉所有值
for weight in ft.FontWeight:
    ft.Text("Sample", weight=weight)
```

---

## Icons

### 用途
提供 Flet 可使用的所有 Material Design 圖示名稱，用於 `ft.Icon` 等控制項。

### 類型定義
`enum.Enum` — 完整的 Material Icons 圖示庫。

### 圖示命名規則
每個圖示都有 4 種變體：
- `<NAME>` — 預設填充版本
- `<NAME>_OUTLINED` — 線條版本
- `<NAME>_ROUNDED` — 圓角版本
- `<NAME>_SHARP` — 銳利版本

### 常見圖示範例（部分列表，完整列表約 7000+ 筆）

| 圖示名稱 | 說明 |
|----------|------|
| `ADD` | 加號（新增） |
| `ARROW_BACK` | 返回箭頭 |
| `SETTINGS` | 設定齒輪 |
| `HOME` | 首頁 |
| `SEARCH` | 搜尋 |
| `DELETE` | 刪除 |
| `EDIT` | 編輯 |
| `VISIBILITY` | 可見 |
| `VISIBILITY_OFF` | 隱藏 |
| `CHECK_CIRCLE` | 圓形打勾 |
| `ERROR` | 錯誤 |
| `WARNING` | 警告 |
| `INFO` | 資訊 |
| `PHONE` | 電話 |
| `EMAIL` | 電子郵件 |
| `PERSON` | 人物 |
| `LOCK` | 鎖頭 |
| `STAR` | 星號 |
| `FAVORITE` | 收藏 |
| `HOME` | 首頁 |
| `MENU` | 選單 |
| `CLOSE` | 關閉 |
| `REFRESH` | 重新整理 |

> **注意**：Icons 頁面內容極大（約 7000+ 個圖示），完整列表請見 https://docs.flet.dev/types/icons/

### 使用方式

```python
import flet as ft

# 基本用法
ft.Icon(ft.Icons.ADD)
ft.Icon(ft.Icons.SETTINGS)
ft.Icon(ft.Icons.HOME)

# 使用線條版本
ft.Icon(ft.Icons.SETTINGS_OUTLINED)

# 在按鈕中使用
ft.IconButton(icon=ft.Icons.DELETE)
ft.TextButton(icon=ft.Icons.EDIT)

# 在 ListTile 中使用
ft.ListTile(
    leading=ft.Icon(ft.Icons.HOME),
    title=ft.Text("首頁")
)
```

---

## MainAxisAlignment

### 用途
控制 Row / Column 中子元件在**主軸（Main Axis）**上的排列方式。

- Row 的主軸是**水平方向**
- Column 的主軸是**垂直方向**

### 類型定義
`enum.Enum`

### 成員列表

| 成員 | 字串值 | 說明 |
|------|--------|------|
| `START` | `'start'` | 從起始位置開始緊密排列（預設） |
| `END` | `'end'` | 從結尾位置開始排列 |
| `CENTER` | `'center'` | 全部集中在中央 |
| `SPACE_BETWEEN` | `'spaceBetween'` | 子元件之間均分剩餘空間，頭尾不留邊距 |
| `SPACE_AROUND` | `'spaceAround'` | 子元件之間均分空間，頭尾只留一半間距 |
| `SPACE_EVENLY` | `'spaceEvenly'` | 子元件之間及頭尾都留相同的間距 |

### 視覺對照

```
START:       [A] [B] [C]          |------容器------|
END:                   [A] [B] [C] |------容器------|
CENTER:           [A] [B] [C]       |------容器------|
SPACE_BETWEEN: [A]    [B]    [C]    |------容器------|
SPACE_AROUND:   [A]   [B]   [C]    |------容器------|
SPACE_EVENLY:  [A]   [B]   [C]     |------容器------|
```

### 使用方式

```python
import flet as ft

# Row 水平排列，調整水平對齊
ft.Row(
    controls=[...],
    alignment=ft.MainAxisAlignment.SPACE_EVENLY
)

# Column 垂直排列，調整垂直對齊
ft.Column(
    controls=[...],
    alignment=ft.MainAxisAlignment.CENTER
)
```

---

## Offset

### 用途
表示二維平面上的浮點數偏移量（x, y 座標），常用於圖片變換、圖形偏移等情境。

### 類型定義
資料類別（dataclass），非 enum。

### 屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `x` | `Number` | 水平偏移量（可為 int 或 float） |
| `y` | `Number` | 垂直偏移量（可為 int 或 float） |
| `distance` | `float`（唯讀） | 偏移向量的幅度（歐氏距離） |
| `transform_hit_tests` | `bool` | 是否在點擊測試時套用此變換，預設 `True` |
| `filter_quality` | `FilterQuality \| None` | 點陣圖變換時的濾鏡品質 |

### 方法

#### `copy(*, x=None, y=None, transform_hit_tests=None, filter_quality=None) -> Offset`
回傳一個修改了指定屬性的新 Offset 副本。

### 使用方式

```python
import flet as ft

# 基本用法
offset = ft.Offset(10, 20)
print(offset.x)   # 10
print(offset.y)   # 20

# 建立副本並修改
new_offset = offset.copy(x=50)
print(new_offset.x)  # 50
print(new_offset.y)  # 20（保留原始值）

# 在圖片變換中使用
ft.Image(
    src="...",
    offset=ft.Offset(5, 5)
)
```

### 常見 Offset 工廠

| 用法 | 說明 |
|------|------|
| `ft.Offset(x, y)` | 一般偏移 |
| `ft.Offset(0, 0)` | 原點（無偏移） |

---

## 其他無法取得的 Types（404）

以下頁面在 `docs.flet.dev/types/` 下返回 404，可能需要至其他位置查閱：

### Color
文件路徑可能已變更。在 Flet 0.82.2 中，顏色通常透過 `ft.Colors` 常數（如 `ft.Colors.RED`、`ft.Colors.BLUE_500`）或直接使用 HEX 字串（如 `"#FF5733"`）來指定。

### CursorKind
用於控制滑鼠游標形狀。可能已整合進 `ft.Cursor` 或在控制項的 `cursor` 屬性中使用。

### DragLeaveEvent / DragEvent
拖放事件相關型別。用於 `ft.DragTarget` 與 `ft.Draggable` 控制項。建議查閱：
- `https://docs.flet.dev/controls/dragtarget/`
- `https://docs.flet.dev/controls/draggable/`

### KeyboardKey
鍵盤按鍵對應表。用於 `ft.KeyboardListener` 控制項。建議查閱：
- `https://docs.flet.dev/controls/keyboardlistener/`

### PointerKind
指標類型（滑鼠、觸控、觸控筆等）。建議查閱原始碼 `flet/types.py` 中的定義。

---

## 補充說明

本筆記收錄了 Flet 0.82.2 文件網站（docs.flet.dev）中 `/types/` 路徑下的可用類型資訊。

**404 的類型**強烈建議直接查看 Flet 原始碼以確認最新 API：
- 原始碼：`https://github.com/flet-dev/flet/blob/main/sdk/python/packages/flet/src/flet/types.py`
- 或在 Python 環境中執行：`import flet as ft; print(dir(ft))` 列出所有可用類型
