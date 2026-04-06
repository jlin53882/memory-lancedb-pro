# Flet 0.82.2 選擇控制項 — 學習筆記

> 來源：Flet 0.82.2 原始碼 (`site-packages/flet/controls/material/`)
> 檔案：chip.py、badge.py、checkbox.py、switch.py、radio.py、segmented_button.py

---

## Chip

**類別**：`Chip`（繼承 `LayoutControl`），decorator `@control("Chip")`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `StrOrControl` | 晶片的主要文字內容（第 36 行） |
| `leading` | `Optional[Control]` | 晶片左側的控制項，通常是 Icon 或 CircleAvatar（第 43 行） |
| `selected` | `bool = False` | 是否為選中狀態；需搭配 `on_select` 使用才有實際切換效果（第 53 行） |
| `selected_color` | `Optional[ColorValue]` | 選中時的背景顏色（第 58 行） |
| `show_checkmark` | `bool = True` | 選中時是否顯示打勾符號（第 69 行） |
| `check_color` | `Optional[ColorValue]` | 打勾符號的顏色（第 74 行） |
| `bgcolor` | `Optional[ColorValue]` | 未選中時的背景顏色（第 63 行） |
| `elevation` | `Optional[Number]` | 陰影大小，預設 0（第 58 行起）；不可為負值 |
| `delete_icon` | `Optional[Control]` | 右側刪除圖示，須搭配 `on_delete` 事件（第 113 行） |
| `shape` | `Optional[OutlinedBorder]` | 邊框形狀，預設 `RoundedRectangleBorder(radius=8)`（第 91 行） |
| `disabled_color` | `Optional[ColorValue]` | 禁用狀態的背景顏色（第 126 行） |
| `label_padding` | `Optional[PaddingValue]` | label 內距，預設左右 4px、上下 0（第 131 行） |
| `color` | `Optional[ControlStateValue[ColorValue]]` | 依狀態填滿的顏色（第 152 行） |
| `elevation_on_click` | `Optional[Number]` | 點擊時的陰影高度，預設 8.0（第 159 行） |

### 事件

| 事件 | 說明 |
|------|------|
| `on_select` | 點擊晶片時觸發，內部自動翻轉 `selected` 狀態（第 175 行） |
| `on_click` | 點擊時觸發；**不可與 `on_select` 同時使用**（第 167 行） |
| `on_delete` | 點擊刪除圖示時觸發（第 171 行） |
| `on_focus` / `on_blur` | 取得／失去焦點時觸發（第 183–188 行） |

### `before_update` 驗證（第 190–200 行）
- `on_select` 與 `on_click` 不可同時指定，否則拋 `ValueError`
- `elevation` 或 `elevation_on_click` 若為負數，拋 `ValueError`

### 重要發現
- `selected` 屬性**只有設定初值作用**；點擊後狀態翻轉是由 `on_select` 內部機制處理
- `show_checkmark=True` 搭配 `on_select` 時，選中才會出現打勾
- `selected_color` 控制選中背景，`bgcolor` 控制未選中背景，兩者獨立

---

## Badge

**類別**：`Badge`（繼承 `BaseControl`），decorator `@control("Badge")`
**型別別名**：`BadgeValue = Union[str, Badge]`（可直接傳字串或 Badge 物件）

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `Optional[StrOrControl]` | 徽章文字（1-4 字）；無則顯示為實心圓形（第 33 行） |
| `offset` | `Optional[OffsetValue]` | 配合 `alignment` 調整位置偏移（第 44 行） |
| `alignment` | `Optional[Alignment]` | 對齊方式，類似 Container.alignment 的語意（第 54 行） |
| `bgcolor` | `Optional[ColorValue]` | 背景顏色（第 66 行） |
| `label_visible` | `bool = True` | 是否顯示徽章；可用来条件隐藏（第 71 行） |
| `large_size` | `Optional[Number]` | 有 label 時的高度，預設 16（第 76 行） |
| `small_size` | `Optional[Number]` | 無 label 時的圓形直徑，預設 6（第 87 行） |
| `padding` | `Optional[PaddingValue]` | label 的內距，預設左右 4px（第 82 行） |
| `text_color` | `Optional[ColorValue]` | 文字顏色，會覆蓋 `text_style`（第 93 行） |
| `text_style` | `Optional[TextStyle]` | 文字樣式（第 98 行） |

### Position 定位說明
Badge 的位置由兩個控制項決定：
1. **`alignment`**：決定 label（原點）的對齊位置，類似 `Container.alignment`
2. **`offset`**：在 alignment 結果基礎上再加上偏移

> 這裡沒有獨立的 `position` 屬性；位置是透過 `alignment + offset` 兩個屬性組合控制。

### 使用方式
Badge 本質上是一個裝飾性元件，常見用法是當作其他控制項的 `badge=` 參數傳入：

```python
ft.FilledIconButton(
    icon=ft.Icons.PHONE,
    badge=ft.Badge(label="3"),  # 直接傳 Badge 物件
)
# 或
ft.FilledIconButton(
    icon=ft.Icons.PHONE,
    badge="99+",  # 直接傳字串，會自動轉成 BadgeValue
)
```

---

## Checkbox

**類別**：`Checkbox`（繼承 `LayoutControl, AdaptiveControl`），decorator `@control("Checkbox")`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `Optional[StrOrControl]` | 核取方塊右側的說明文字（第 36 行） |
| `value` | `Optional[bool] = False` | 選中狀態；可為 `None`（indeterminate）若 `tristate=True`（第 42 行） |
| `label_position` | `LabelPosition = LabelPosition.RIGHT` | label 在左側或右側（第 47 行） |
| `tristate` | `bool = False` | 為 `True` 時 value 可為 `True/False/None`（第 56 行） |
| `fill_color` | `Optional[ControlStateValue[ColorValue]]` | 依狀態填滿的顏色（第 63 行） |
| `active_color` | `Optional[ColorValue]` | 勾選時的顏色（第 77 行） |
| `check_color` | `Optional[ColorValue]` | 打勾符號的顏色（第 72 行） |
| `overlay_color` | `Optional[ControlStateValue[ColorValue]]` | 覆蓋層顏色（依狀態）（第 68 行） |
| `hover_color` | `Optional[ColorValue]` | 滑鼠懸停顏色（第 80 行） |
| `focus_color` | `Optional[ColorValue]` | 聚焦時的顏色（第 84 行） |
| `border_side` | `Optional[ControlStateValue[BorderSide]]` | 邊框樣式（依狀態）（第 104 行） |
| `shape` | `Optional[OutlinedBorder]` | 形狀，預設 `RoundedRectangleBorder(radius=2)`（第 98 行） |
| `splash_radius` | `Optional[Number]` | 漣漪效果半徑，預設 20.0（第 109 行） |
| `error` | `bool = False` | 是否顯示錯誤狀態（第 116 行） |

### 事件

| 事件 | 說明 |
|------|------|
| `on_change` | 狀態改變時觸發（第 127 行） |

### 三態（tristate）行為
- `tristate=False`（預設）：`value` 只接受 `True` / `False`
- `tristate=True`：`value` 可為 `None`，此時方塊顯示為破折號「—」表示 indeterminate 狀態

---

## Switch

**類別**：`Switch`（繼承 `LayoutControl, AdaptiveControl`），decorator `@control("Switch")`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `Optional[StrOrControl]` | 開關右側的說明文字（第 34 行） |
| `value` | `bool = False` | 目前開關狀態（第 50 行） |
| `label_position` | `LabelPosition = LabelPosition.RIGHT` | label 位置（第 39 行） |
| `active_color` | `Optional[ColorValue]` | 開啟時的thumb顏色（第 56 行） |
| `active_track_color` | `Optional[ColorValue]` | 開啟時的軌道顏色（第 60 行） |
| `inactive_thumb_color` | `Optional[ColorValue]` | 關閉時的thumb顏色（第 67 行） |
| `inactive_track_color` | `Optional[ColorValue]` | 關閉時的軌道顏色（第 73 行） |
| `thumb_color` | `Optional[ControlStateValue[ColorValue]]` | thumb顏色（依狀態）（第 82 行） |
| `thumb_icon` | `Optional[ControlStateValue[IconData]]` | thumb上的圖示（依狀態）（第 88 行） |
| `track_color` | `Optional[ControlStateValue[ColorValue]]` | 軌道顏色（依狀態）（第 94 行） |
| `adaptive` | `Optional[bool] = None` | 為 `True` 時，iOS/macOS 自動用 `CupertinoSwitch`（第 103 行） |
| `splash_radius` | `Optional[Number]` | 點擊時漣漪半徑；不可為負數（第 119 行） |
| `overlay_color` | `Optional[ControlStateValue[ColorValue]]` | 覆蓋層顏色（依狀態）（第 123 行） |
| `track_outline_color` | `Optional[ControlStateValue[ColorValue]]` | 軌道邊線顏色（依狀態）（第 128 行） |
| `padding` | `Optional[PaddingValue]` | 內距，預設水平 4px（第 143 行） |

### 事件

| 事件 | 說明 |
|------|------|
| `on_change` | 狀態改變時觸發（第 149 行） |
| `on_focus` / `on_blur` | 焦點事件（第 153–159 行） |

### 重要發現
- Switch **沒有** `tristate` 屬性，只能在 `True/False` 之間切換
- `adaptive=True` 時，在 iOS/macOS 會渲染成 `CupertinoSwitch`，其他平台則是 Material Switch
- `thumb_icon` 可以讓 thumb 顯示圖示（支援 ControlState）

---

## Radio

**類別**：`Radio`（繼承 `LayoutControl, AdaptiveControl`），decorator `@control("Radio")`

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `str = ""` | 單選按鈕右側的說明文字（第 33 行） |
| `value` | `Optional[str] = None` | 此選項的值，選中時會設給所屬 `RadioGroup`（第 42 行） |
| `label_position` | `LabelPosition = LabelPosition.RIGHT` | label 位置（第 36 行） |
| `fill_color` | `Optional[ControlStateValue[ColorValue]]` | 填滿顏色（依狀態）（第 49 行） |
| `active_color` | `Optional[ColorValue]` | 選中時的填滿顏色（第 53 行） |
| `overlay_color` | `Optional[ControlStateValue[ColorValue]]` | 覆蓋層顏色（依狀態）（第 57 行） |
| `hover_color` | `Optional[ColorValue]` | 懸停顏色（第 60 行） |
| `focus_color` | `Optional[ColorValue]` | 聚焦顏色（第 63 行） |
| `splash_radius` | `Optional[Number]` | 漣漪半徑（第 66 行） |
| `toggleable` | `bool = False` | 為 `True` 時，再次點擊已選中的項目可回到 indeterminate（第 69 行） |

### 重要發現
- `Radio` 本身**沒有 `on_change` 事件**；它的狀態變化由所屬 `RadioGroup` 的 `on_change` 統一處理
- 使用時必須包在 `RadioGroup` 內，否則 `value` 無意義
- `toggleable=True` 允許選中→點擊→取消選中（回到 indeterminate）的行為

---

## SegmentedButton

**類別**：`SegmentedButton`（繼承 `LayoutControl`），decorator `@control("SegmentedButton")`
**子類**：`Segment`（每個分段），decorator `@control("Segment")`

### Segment 類別

| 屬性 | 類型 | 說明 |
|------|------|------|
| `value` | `str`（必填） | 用於識別這個分段（第 28 行） |
| `icon` | `Optional[IconDataOrControl]` | 分段內的圖示（第 34 行） |
| `label` | `Optional[StrOrControl]` | 分段內的文字；`icon` 和 `label` 至少要有一個（第 39 行） |

### SegmentedButton 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `segments` | `list[Segment]` | 所有分段列表（第 19 行） |
| `selected` | `list[str]` | 目前選中的 Segment value 列表（第 43 行） |
| `allow_empty_selection` | `bool = False` | 允許一個都沒選中（第 27 行） |
| `allow_multiple_selection` | `bool = False` | 允許多選（第 35 行） |
| `selected_icon` | `Optional[IconDataOrControl]` | 選中分段顯示的圖示，預設 `Icons.CHECK`（第 49 行） |
| `show_selected_icon` | `bool = True` | 是否顯示選中圖示（第 55 行） |
| `direction` | `Optional[Axis]` | 分段排列方向，預設 `Axis.HORIZONTAL`（第 60 行） |
| `style` | `Optional[ButtonStyle]` | 自訂外觀樣式（第 23 行） |
| `on_change` | `Optional[ControlEventHandler]` | 選中改變時觸發；`event.data` 是 `list[str]`（第 66 行） |

### 重要發現
- `selected` 是 `list[str]`（非單一值），表示可以同時追蹤多個選中分段
- `allow_multiple_selection=False`（預設）時，`selected` 最多只會有一個元素
- `on_change` 的 `event.data` 是 **字串列表**（JSON array 格式），需注意類型是 `list[str]`
- `Segment` 的 `value` 是辨識 ID，`label`/`icon` 是顯示內容

---

## Chip vs SegmentedButton 核心差異

| 維度 | Chip | SegmentedButton |
|------|------|----------------|
| 用途 | 獨立可選的標籤元件 | 成組的分段按鈕 |
| 選中管理 | 自身管理 `selected` 狀態 | 由父元件 `SegmentedButton.selected` 統一管理 |
| 多選 | 需自行實作群組邏輯 | 內建 `allow_multiple_selection` 支援 |
| 刪除功能 | 有 `delete_icon` + `on_delete` | 無內建刪除 |
| 點擊回調 | `on_select`（內部翻轉 selected） | `on_change`（由父元件觸發） |
| 空選擇 | 任意 | `allow_empty_selection=False` 強制至少選一 |

---

## 常用程式碼範例

```python
import flet as ft

# --- Chip ---
chip = ft.Chip(
    label="已選中晶片",
    leading=ft.Icon(ft.Icons.CHECK_CIRCLE),
    selected=True,
    selected_color=ft.colors.PRIMARY_CONTAINER,
    show_checkmark=True,
    on_select=lambda e: print(f"Chip selected: {e.control.selected}"),
)

# --- Badge ---
btn_with_badge = ft.FilledIconButton(
    icon=ft.Icons.MESSAGES,
    badge=ft.Badge(label="8"),  # 方式一：Badge 物件
)
btn_dot_badge = ft.FilledIconButton(
    icon=ft.Icons.MESSAGES,
    badge="99+",  # 方式二：字串自動轉 BadgeValue
)

# --- Checkbox ---
cb = ft.Checkbox(
    label="同意條款",
    value=False,
    tristate=True,  # 支援 True/False/None 三態
    on_change=lambda e: print(f"Checkbox value: {e.control.value}"),
)

# --- Switch ---
sw = ft.Switch(
    label="深色模式",
    value=False,
    active_color=ft.colors.PRIMARY,
    on_change=lambda e: print(f"Switch value: {e.control.value}"),
)

# --- Radio + RadioGroup ---
# Radio 沒有自己的 on_change，由 RadioGroup 統一管理
rg = ft.RadioGroup(
    content=ft.Column([
        ft.Radio(value="a", label="選項 A"),
        ft.Radio(value="b", label="選項 B"),
        ft.Radio(value="c", label="選項 C"),
    ]),
    on_change=lambda e: print(f"RadioGroup value: {e.value}"),
)

# --- SegmentedButton（單選）---
seg1 = ft.Segment(value="week", label=ft.Text("週"))
seg2 = ft.Segment(value="month", label=ft.Text("月"))
seg3 = ft.Segment(value="year", label=ft.Text("年"))

sb = ft.SegmentedButton(
    segments=[seg1, seg2, seg3],
    selected=["month"],  # 初始選中（list[str]）
    allow_empty_selection=False,
    allow_multiple_selection=False,
    on_change=lambda e: print(f"Selected: {e.data}"),  # e.data 是 JSON array 字串
)

# --- SegmentedButton（多選）---
seg_multi = ft.SegmentedButton(
    segments=[
        ft.Segment(value="bold", icon=ft.Icons.BOLD, label=ft.Text("粗體")),
        ft.Segment(value="italic", icon=ft.Icons.ITALIC, label=ft.Text("斜體")),
        ft.Segment(value="underline", icon=ft.Icons.UNDERLINE, label=ft.Text("底線")),
    ],
    selected=["bold"],
    allow_multiple_selection=True,
    on_change=lambda e: print(f"Multi selected: {e.data}"),
)
```

---

## 重要發現與注意事項

1. **Chip 的 `on_select` 與 `on_click` 互斥**：`before_update` 會驗證兩者不可同時設定，強行同時使用會拋 `ValueError`

2. **Checkbox 的 `value` 可為 `None`**：只有 `tristate=True` 時才支援；`None` 顯示為 indeterminate（破折號）狀態

3. **Switch 的 `adaptive` 特性**：設定 `adaptive=True` 後，iOS/macOS 會自動變成 `CupertinoSwitch`，行為相同但視覺樣式不同

4. **RadioGroup 的事件集中化**：`Radio` 本身無 `on_change`；所有選項的狀態變化都經由 `RadioGroup.on_change` 統一處理，`e.value` 拿到的是被選中 Radio 的 `value` 屬性值

5. **SegmentedButton `selected` 是 list**：`selected` 類型是 `list[str]`，即使單選時也是列表；`on_change` 的 `event.data` 是 JSON 字串（例如 `"[\"month\"]"`），需用 `json.loads()` 解析

6. **SegmentedButton 強制至少一選**：`allow_empty_selection=False`（預設）時，若 `selected` 為空會在 `before_update` 拋 `ValueError`

7. **Badge `position` 的實作方式**：沒有獨立的 `position` 屬性，而是透過 `alignment`（對齊原點）+ `offset`（偏移）兩個屬性組合達成定位效果

8. **Chip 的 `selected_color` vs `bgcolor`**：`selected_color` 只在選中時生效；未選中時的背景由 `bgcolor` 控制；兩者可同時設定，互不干擾

9. **Chip `delete_icon` 需要 `on_delete`**：只有設定了 `on_delete` 事件處理常式，刪除圖示才會出現並可互動
