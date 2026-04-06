# Flet 0.82.2 Button 全家 — 學習筆記

> 學習日期：2026-03-23｜來源：Flet 0.82.2 原始碼

---

## 按鈕繼承結構

```
ButtonStyle (dataclass)          ← buttons.py，全域样式定義
    │
    ├─── Button (base)          ← material/button.py，@control("Button")
    │       ├─── ElevatedButton ← material/elevated_button.py，⚠️ deprecated wrapper
    │       └─── FilledButton   ← material/filled_button.py，@control("FilledButton")
    │
    ├─── OutlinedButton         ← material/outlined_button.py，@control("OutlinedButton")
    ├─── TextButton             ← material/text_button.py，@control("TextButton")
    │
    └─── IconButton             ← material/icon_button.py，@control("IconButton")
            ├─── FilledIconButton
            ├─── FilledTonalIconButton
            └─── OutlinedIconButton
```

### 重要發現：ElevatedButton 只是 proxy class

`elevated_button.py`（L1-L15）：

```python
from flet.controls.material.button import Button
from flet.utils.deprecated import deprecated_class

@deprecated_class(reason="Use Button instead.", version="0.80.0", delete_version="1.0")
class ElevatedButton(Button):
    pass
```

`ElevatedButton` 在 0.80.0 被標記 deprecated，1.0 將刪除。**目前 `ft.Button` 就是標準寫法**，不必再寫 `ft.ElevatedButton`。

### IconButton 家族同一個檔案

`icon_button.py` 同一個檔案同時定義了 `IconButton`、`FilledIconButton`、`FilledTonalIconButton`、`OutlinedIconButton`，皆繼承自 `IconButton`。

---

## ft.Button（標準按鈕）

**檔案**：`flet/controls/material/button.py`（L1 起）

### 類別定義

```python
@control("Button")
class Button(LayoutControl, AdaptiveControl):
```

繼承自 `LayoutControl`（佈局能力）和 `AdaptiveControl`（自適應平臺）。

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `content` | `StrOrControl` | 按鈕文字標籤，可傳字串或 `Text` 控制項 |
| `icon` | `IconDataOrControl` | 按鈕內的圖示，可傳 `Icons.XXX` 或 `Icon` 控制項 |
| `icon_color` | `ColorValue` | 圖示顏色 |
| `color` | `ColorValue` | 前景色（文字顏色），預設使用主題 primary 色 |
| `bgcolor` | `ColorValue` | 背景顏色 |
| `elevation` | `Number` | 陰影高度，預設 `1` |
| `style` | `ButtonStyle` | 全域樣式（可針對不同狀態設置） |
| `autofocus` | `bool` | 是否自動聚焦 |
| `clip_behavior` | `ClipBehavior` | 裁剪行為 |
| `url` | `str \| Url` | 點擊時開啟的 URL |

### 事件

```python
on_click: Optional[ControlEventHandler["Button"]]
on_long_press: Optional[ControlEventHandler["Button"]]
on_hover: Optional[ControlEventHandler["Button"]]
on_focus: Optional[ControlEventHandler["Button"]]
on_blur: Optional[ControlEventHandler["Button"]]
```

### before_update 邏輯（L126-L142）

```python
def before_update(self):
    super().before_update()
    # 驗證：icon 或 content（字串或可見控制項）至少要有一個
    if not (self.icon or isinstance(self.content, str)
            or (isinstance(self.content, Control) and self.content.visible)):
        raise ValueError("At least icon or content ...")

    # 如果有設 style/color/bgcolor/elevation，就合併進 _internals["style"]
    if (self.style is not None or self.color is not None
            or self.bgcolor is not None or self.elevation != 1):
        self._internals["style"] = (self.style or ButtonStyle()).copy(
            color=self.color, bgcolor=self.bgcolor, elevation=self.elevation)
    else:
        self._internals.pop("style", None)
```

---

## ft.ElevatedButton（⚠️ deprecated）

**檔案**：`flet/controls/material/elevated_button.py`

```python
@deprecated_class(reason="Use Button instead.", version="0.80.0", delete_version="1.0")
class ElevatedButton(Button):
    pass
```

從 0.80.0 起 deprecated（廢棄），將在 1.0 刪除。**請統一使用 `ft.Button`**，不要再用 `ft.ElevatedButton`。

---

## ft.OutlinedButton

**檔案**：`flet/controls/material/outlined_button.py`

```python
@control("OutlinedButton")
class OutlinedButton(LayoutControl, AdaptiveControl):
```

### 主要屬性

| 屬性 | 說明 |
|------|------|
| `content` | 按鈕內容（字串或控制項） |
| `icon` | 圖示 |
| `icon_color` | 圖示顏色 |
| `style` | `ButtonStyle` |
| `autofocus` | 預設 `False` |
| `clip_behavior` | 預設 `ClipBehavior.NONE` |
| `url` | 點擊開啟的 URL |

### 事件

`on_click`、`on_long_press`、`on_hover`、`on_focus`、`on_blur`（同 Button）。

### 特色

外框按鈕，帶有外框線條但無填充背景，屬於中等強調程度。

---

## ft.TextButton

**檔案**：`flet/controls/material/text_button.py`

```python
@control("TextButton")
class TextButton(LayoutControl, AdaptiveControl):
```

純文字按鈕，**預設沒有可見的容器外框**，只用於最低優先順序的操作。

### 主要屬性

| 屬性 | 說明 |
|------|------|
| `content` | 按鈕內容 |
| `icon` | 圖示 |
| `icon_color` | 圖示顏色 |
| `style` | `ButtonStyle` |
| `autofocus` | 預設 `False` |
| `url` | 點擊開啟的 URL |
| `clip_behavior` | 預設 `ClipBehavior.NONE` |

### 事件

`on_click`、`on_long_press`、`on_hover`、`on_focus`、`on_blur`。

---

## ft.IconButton

**檔案**：`flet/controls/material/icon_button.py`

### 類別階層

```
IconButton
    ├─── FilledIconButton
    ├─── FilledTonalIconButton
    └─── OutlinedIconButton
```

### IconButton 專有屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `icon` | `IconDataOrControl` | 要顯示的圖示 |
| `icon_color` | `ColorValue` | 圖示前景色 |
| `icon_size` | `Number` | 圖示大小，預設 `24` |
| `selected` | `bool` | 選中狀態（切換模式） |
| `selected_icon` | `IconDataOrControl` | 選中時顯示的圖示 |
| `selected_icon_color` | `ColorValue` | 選中圖示顏色 |
| `bgcolor` | `ColorValue` | 按鈕背景色 |
| `highlight_color` | `ColorValue` | 按下時的強調色 |
| `hover_color` | `ColorValue` | 懸停時的顏色 |
| `focus_color` | `ColorValue` | 聚焦時的顏色 |
| `splash_color` | `ColorValue` | 漣漪點擊效果的主要顏色 |
| `splash_radius` | `Number` | 漣漪半徑（僅 M2 有效） |
| `disabled_color` | `ColorValue` | disabled 時的圖示顏色 |
| `alignment` | `Alignment` | 圖示對齊，預設 `Alignment.CENTER` |
| `padding` | `PaddingValue` | 內距，預設 `Padding.all(8)` |
| `enable_feedback` | `bool` | 是否提供聲音/觸覺回饋 |
| `visual_density` | `VisualDensity` | 佈局緊湊程度 |
| `size_constraints` | `BoxConstraints` | 尺寸約束 |
| `mouse_cursor` | `MouseCursor` | 滑鼠游標樣式 |

### IconButton 特色：selected 切換模式

```python
# selected=False → 顯示 icon
# selected=True  → 顯示 selected_icon
```

### before_update（L147-L160）

```python
def before_update(self):
    super().before_update()
    if self.splash_radius is not None and self.splash_radius <= 0:
        raise ValueError("splash_radius must be greater than 0 ...")
    if (self.style is not None or self.bgcolor is not None
            or self.visual_density is not None or self.mouse_cursor is not None):
        self._internals["style"] = (self.style or ButtonStyle()).copy(
            bgcolor=self.bgcolor, visual_density=self.visual_density,
            mouse_cursor=self.mouse_cursor)
    else:
        self._internals.pop("style", None)
```

---

## ft.FilledButton

**檔案**：`flet/controls/material/filled_button.py`

```python
@control("FilledButton")
class FilledButton(Button):
    pass
```

完全繼承 `Button`，無額外屬性。用於高強調程度的動作（如「Save」「Confirm」）。

---

## ButtonStyle dataclass

**檔案**：`flet/controls/buttons.py`（L85 起）

`ButtonStyle` 是所有按鈕樣式的中央定義，所有狀態相關屬性都支援 `ControlStateValue`（可為不同狀態設不同值）：

| 屬性 | 說明 |
|------|------|
| `color` | 文字和圖示的顏色 |
| `bgcolor` | 背景填充色 |
| `overlay_color` | 聚焦/懸停/按下時的強調色 |
| `shadow_color` | 陰影顏色 |
| `elevation` | 陰影高度（`None` = 無陰影） |
| `animation_duration` | 動畫持續時間（毫秒） |
| `padding` | 按鈕邊界與內容的間距 |
| `side` | 按鈕外框線條 |
| `shape` | 按鈕形狀（`StadiumBorder`、`RoundedRectangleBorder` 等） |
| `alignment` | 內容對齊方式 |
| `enable_feedback` | 是否提供聲音/觸覺回饋 |
| `text_style` | 文字樣式 |
| `icon_size` | 圖示大小 |
| `icon_color` | 圖示顏色（預設使用 `color`） |
| `visual_density` | 佈局緊湊程度 |
| `mouse_cursor` | 滑鼠游標 |

### 形狀子類別（`buttons.py` L31 起）

```
OutlinedBorder (abstract)
    ├─── StadiumBorder        ← 膠囊/藥丸形
    ├─── RoundedRectangleBorder ← 圓角矩形
    ├─── CircleBorder         ← 圓形（可調 eccentricity）
    ├─── BeveledRectangleBorder ← 斜角矩形
    └─── ContinuousRectangleBorder ← 連續曲線圓角
```

---

## 常用程式碼範例

### 基本用法

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Button(content="按我", on_click=lambda e: print("clicked!")),
        ft.Button(icon=ft.Icons.STAR, icon_color=ft.Colors.YELLOW, content="收藏"),
        ft.Button("disabled", disabled=True),
    )
```

### 使用 style 客製化

```python
ft.Button(
    content="圓角按鈕",
    style=ft.ButtonStyle(
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=20),
        elevation=4,
    ),
    on_click=lambda e: print("OK"),
)
```

### 狀態別樣式

```python
from flet.controls.control_state import ControlState

ft.Button(
    content="狀態按鈕",
    style=ft.ButtonStyle(
        color={ControlState.HOVERED: ft.Colors.RED},
        bgcolor={ControlState.DISABLED: ft.Colors.GREY_300},
    ),
)
```

### OutlinedButton / TextButton

```python
ft.OutlinedButton(
    content="Outlined",
    icon=ft.Icons.SETTINGS,
    on_click=lambda e: print("settings"),
)

ft.TextButton(
    content="Text Button",
    icon=ft.Icons.STAR_BORDER,
    icon_color=ft.Colors.BLUE_300,
)
```

### IconButton（及其變體）

```python
# 基本 IconButton
ft.IconButton(
    icon=ft.Icons.FAVORITE,
    icon_color=ft.Colors.PRIMARY,
    on_click=lambda e: print("liked"),
)

# 選中切換模式
ft.IconButton(
    icon=ft.Icons.FAVORITE_BORDER,
    selected_icon=ft.Icons.FAVORITE,
    selected=False,
    on_click=lambda e: print("toggled"),
)

# FilledIconButton
ft.FilledIconButton(icon=ft.Icons.CHECK)

# FilledTonalIconButton
ft.FilledTonalIconButton(icon=ft.Icons.CHECK)

# OutlinedIconButton
ft.OutlinedIconButton(icon=ft.Icons.CHECK)
```

### FilledButton

```python
ft.FilledButton(
    content="Tap me",
    on_click=lambda e: print("tapped!"),
)
```

---

## 重要發現與注意事項

1. **`ft.Button` 是標準按鈕，`ft.ElevatedButton` 已 deprecated**
   - `ElevatedButton` 在 0.80.0 標記廢棄，1.0 刪除
   - 統一使用 `ft.Button`，不要用 `ft.ElevatedButton`

2. **所有按鈕都有 `on_click` 事件**
   - 簽名：`on_click: Optional[ControlEventHandler["XXXButton"]]`
   - 只要傳入函式作為 `on_click` 回調即可

3. **按鈕 content/icon 至少要有一個**
   - `before_update` 會檢查：`icon` 或 `content`（字串或可見控制項）至少要有一個
   - 都不給會拋 `ValueError`

4. **IconButton 有 `selected` 模式**
   - `selected=False` → 顯示 `icon`
   - `selected=True` → 顯示 `selected_icon`
   - 適合做切換按鈕（如喜歡/不喜歡）

5. **`style` 屬性採用「合併」策略**
   - 在 `Button.before_update` 中，如果設了 `style`、`color`、`bgcolor` 或 `elevation`，會和既有 `ButtonStyle` 合併
   - 直接設 `color`/`bgcolor` 會自動封裝進 `ButtonStyle`

6. **`IconButton` 的 `splash_radius` 僅在 M2 有效**
   - M3 模式下此參數被忽略

7. **按鈕家族分兩大類**
   - **繼承 `Button` 的**：Button（base）、ElevatedButton（deprecated）、FilledButton
   - **直接繼承 `LayoutControl, AdaptiveControl` 的**：OutlinedButton、TextButton、IconButton 及其變體
   - 這兩類的內部實作有差異（主要是 `_internals["style"]` 的處理時機），但 public API 相似
