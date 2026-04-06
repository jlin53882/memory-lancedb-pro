# Flet 0.82.2 顯示控制項 — 學習筆記

> 學習日期：2026-03-23
> 來源：flet 0.82.2 原始碼 (`site-packages/flet/controls/core/` + `text_style.py`)

---

## ft.Text（屬性、方法、spans 用法）

**類別位置：** `flet/controls/core/text.py`，第 144 行 (`@control("Text")`)

### 核心屬性

| 屬性 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `value` | `str` | `""` | 要顯示的文字內容 |
| `spans` | `Optional[list[TextSpan]]` | `None` | 用於组合多段不同樣式的富文字 |
| `text_align` | `TextAlign` | `TextAlign.START` | 水平對齊（START/CENTER/END/JUSTIFY） |
| `weight` | `Optional[FontWeight]` | `None` | 字重（預設 NORMAL） |
| `size` | `Optional[Number]` | `None` | 字體大小，預設 14 |
| `color` | `Optional[ColorValue]` | `None` | 文字前景色 |
| `bgcolor` | `Optional[ColorValue]` | `None` | 文字背景色 |
| `style` | `Optional[TextStyle]` | `None` | TextStyle 物件，定義完整樣式 |
| `theme_style` | `Optional[TextThemeStyle]` | `None` | 預設 Material 主題樣式（DISPLAY_LARGE~BODY_SMALL） |
| `max_lines` | `Optional[int]` | `None` | 最大行數，超出則依 `overflow` 截斷 |
| `overflow` | `TextOverflow` | `TextOverflow.CLIP` | 溢出處理：CLIP/ELLIPSIS/FADE/VISIBLE |
| `selectable` | `Optional[bool]` | `None` | 是否可選取文字（預設 False） |
| `no_wrap` | `Optional[bool]` | `None` | True=不換行，False=在軟換行點斷行（預設 False） |
| `font_family` | `Optional[str]` | `None` | 字體名稱（可自訂） |
| `font_family_fallback` | `Optional[list[str]]` | `None` | 字體 fallback 列表 |
| `italic` | `bool` | `False` | 是否斜體 |
| `semantics_label` | `Optional[str]` | `None` | 無障礙替代文字標籤 |
| `show_selection_cursor` | `bool` | `False` | 選取時是否顯示閃爍游標（需 selectable=True） |
| `enable_interactive_selection` | `bool` | `True` | 是否啟用長按選取、複製/貼上功能 |
| `selection_cursor_width` | `Number` | `2.0` | 游標寬度 |
| `selection_cursor_height` | `Optional[Number]` | `None` | 游標高度 |
| `selection_cursor_color` | `Optional[ColorValue]` | `None` | 游標顏色 |

### Text 與 spans 的組合邏輯

Text 由 `value` 和 `spans` 兩個來源共同構成最終文字。兩者可以同時使用：
- `value`：純文字字串
- `spans`：一個 `TextSpan` 列表，用於對同一段落內不同範圍套用不同樣式

### 重要事件

| 事件 | 說明 |
|------|------|
| `on_tap` | 使用者點擊可選取文字時觸發 |
| `on_selection_change` | 選取範圍改變時觸發（回傳 `TextSelectionChangeEvent`） |

### TextSelection 相關類別

- **`TextAffinity`**（Enum，第 31 行）：`UPSTREAM` / `DOWNSTREAM`
- **`TextSelection`**（dataclass，第 43 行）：
  - 屬性：`base_offset`、`extent_offset`、`affinity`、`directional`
  -唯讀屬性：`start`、`end`、`is_valid`、`is_collapsed`、`is_normalized`
  - 方法：`get_selected_text(source_text)`
- **`TextSelectionChangeCause`**（Enum）：`TAP`/`DOUBLE_TAP`/`LONG_PRESS`/`FORCE_PRESS`/`KEYBOARD`/`TOOLBAR`/`DRAG`/`SCRIBBLE`
- **`TextSelectionChangeEvent`**（dataclass）：`selected_text`、`selection`、`cause`

---

## ft.TextSpan

**類別位置：** `flet/controls/core/text_span.py`，第 26 行 (`@control("TextSpan")`)

TextSpan 是 `Control` 的子類別（不同於 Text 繼承 `LayoutControl`）。

### 核心屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `text` | `Optional[str]` | 此段的文字內容 |
| `style` | `Optional[TextStyle]` | 套用到此段的樣式 |
| `spans` | `Optional[list["TextSpan"]]` | 巢狀子 TextSpan |
| `url` | `Optional[str]` | 點擊時開啟的 URL（與 on_click 可同時使用） |
| `semantics_label` | `Optional[str]` | 無障礙替代標籤 |
| `spell_out` | `Optional[bool]` | 是否逐字朗讀（對密碼很有用） |

### 重要行為

- **`text` 優先於 `spans`**：若兩者同時設定，`text` 會生效，`spans` 被忽略（第 52-53 行 docstring）
- 若設定 `semantics_label`，則 `text` 不可為 `None`，否則拋出 `ValueError`（第 81 行 `before_update`）
- 支援點擊相關事件：`on_click`、`on_enter`（滑鼠進入）、`on_exit`（滑鼠離開）

### 巢狀結構範例

```python
ft.Text(
    spans=[
        ft.TextSpan("Hello ", style=ft.TextStyle(color=ft.Colors.BLUE)),
        ft.TextSpan("World", style=ft.TextStyle(color=ft.Colors.RED)),
    ]
)
```

---

## ft.Icon

**類別位置：** `flet/controls/core/icon.py`，第 22 行 (`@control("Icon")`)

### 核心屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `icon` | `IconData` | 要顯示的圖示（必填），使用 `ft.Icons.XXX` |
| `color` | `Optional[ColorValue]` | 圖示顏色 |
| `size` | `Optional[Number]` | 圖示尺寸（寬高相同，正方形區域） |
| `fill` | `Optional[Number]` | 填滿程度 0.0~1.0（0=線條，1=實心）需字體支援 |
| `weight` | `Optional[Number]` | 線條粗細（需大於 0） |
| `grade` | `Optional[Number]` | 細微調整筆畫厚度（可正可負） |
| `optical_size` | `Optional[Number]` | 視覺尺寸調整（需大於 0） |
| `shadows` | `Optional[BoxShadowValue]` | 陰影效果 |
| `apply_text_scaling` | `Optional[bool]` | 是否跟隨系統文字大小縮放 |
| `semantics_label` | `Optional[str]` | 無障礙標籤 |
| `blend_mode` | `BlendMode` | 顏色混合模式，預設 `SRC_OVER` |

### Icons 常數列表

Icons 並非 Enum，而是透過 `_IconsProxy`（第 59 行）動態代理至 `icons.json`（Material Icons 圖示集）。

**總數量：8825 個圖示**（含各變體）

命名規則（以 `ACCESS_ALARM` 為例）：
- `ACCESS_ALARM` — 預設（filled）
- `ACCESS_ALARM_OUTLINED`
- `ACCESS_ALARM_ROUNDED`
- `ACCESS_ALARM_SHARP`

**部分圖示範例：**

```
ABC, ABC_OUTLINED, ABC_ROUNDED, ABC_SHARP
ACCESSIBILITY, ACCESSIBILITY_NEW, ACCESSIBLE
ACCESS_ALARM, ACCESS_ALARMS, ACCESS_TIME
ACCOUNT_BALANCE, ACCOUNT_BOX, ACCOUNT_CIRCLE
FAVORITE, FAVORITE_OUTLINED, FAVORITE_ROUNDED
HOME, HOME_OUTLINED, HOME_ROUNDED, HOME_SHARP
SETTINGS, SETTINGS_OUTLINED, SETTINGS_ROUNDED
ARROW_BACK, ARROW_FORWARD, ARROW_DROP_DOWN
```

取得完整列表：`print(dir(ft.Icons))`

### 驗證規則（before_update）

- `fill` 必須在 0.0~1.0 範圍內，否則拋 `ValueError`
- `weight` 必須大於 0，否則拋 `ValueError`
- `optical_size` 必須大於 0，否則拋 `ValueError`

---

## ft.Image

**類別位置：** `flet/controls/core/image.py`，第 27 行 (`@control("Image")`)

### 支援格式

JPEG, PNG, SVG, GIF（靜態/動態）, WebP（靜態/動態）, BMP, WBMP

### 核心屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `src` | `Union[str, bytes]` | 圖片來源：URL、asset 路徑、base64 字串、或原始 bytes |
| `fit` | `Optional[BoxFit]` | 如何適配空間：NONE/FILL/FIT_WIDTH/FIT_HEIGHT/COVER/CONTAIN/SCALE_DOWN |
| `width` |  inherited | 寬度（由 LayoutControl 繼承） |
| `height` | inherited | 高度（由 LayoutControl 繼承） |
| `border_radius` | `Optional[BorderRadiusValue]` | 圓角 |
| `color` | `Optional[ColorValue]` | 與圖片像素混合的顏色 |
| `color_blend_mode` | `Optional[BlendMode]` | 顏色混合模式 |
| `repeat` | `ImageRepeat` | 空間不足時如何重複：NO_REPEAT/REPEAT/REPEAT_X/REPEAT_Y |
| `gapless_playback` | `bool` | 圖片更換時是否先隱藏再顯示（對 SVG 無效） |
| `filter_quality` | `FilterQuality` | 渲染品質：LOW/MEDIUM/HIGH（預設 MEDIUM） |
| `anti_alias` | `bool` | 是否消除鋸齒（預設 False，旋轉時有用） |
| `error_content` | `Optional[Control]` | 圖片載入失敗時顯示的替代控制項 |
| `semantics_label` | `Optional[str]` | 無障礙描述 |
| `exclude_from_semantics` | `bool` | 是否從無障礙樹排除 |
| `placeholder_src` | `Optional[Union[str, bytes]]` | 載入中的替代圖片（SVG 不支援） |
| `placeholder_fit` | `Optional[BoxFit]` | placeholder 的 fit 方式（None 時預設同 `fit`） |
| `fade_in_animation` | `Optional[Animation]` | 圖片淡入動畫 |
| `placeholder_fade_out_animation` | `Optional[Animation]` | placeholder 淡出動畫 |
| `cache_width` | `Optional[int]` | 解碼時的寬度（影響記憶體，非實際顯示大小） |
| `cache_height` | `Optional[int]` | 解碼時的高度 |

### init() 特殊處理

```python
# 第 119 行
def init(self):
    super().init()
    self._internals["skip_properties"] = ["width", "height"]
```

Image 的 `width` 和 `height` 會被跳過，不傳給 Flutter 層，這是因為 Image 的尺寸直接由 `src` 和 `fit` 決定。

---

## TextStyle 用法

**類別位置：** `flet/controls/text_style.py`，第 135 行 (`@dataclass TextStyle`)

### TextStyle 屬性一覽

| 屬性 | 型別 | 說明 |
|------|------|------|
| `size` | `Optional[Number]` | 字體大小，預設 14 |
| `height` | `Optional[Number]` | 行高（font size 的倍數） |
| `weight` | `Optional[FontWeight]` | 字重 |
| `italic` | `bool` | 是否斜體（預設 False） |
| `color` | `Optional[ColorValue]` | 文字前景色 |
| `bgcolor` | `Optional[ColorValue]` | 文字背景色 |
| `font_family` | `Optional[str]` | 字體名稱 |
| `font_family_fallback` | `Optional[list[str]]` | Fallback 字體列表 |
| `decoration` | `Optional[TextDecoration]` | 裝飾線（underline/overline/line-through） |
| `decoration_color` | `Optional[ColorValue]` | 裝飾線顏色 |
| `decoration_thickness` | `Optional[Number]` | 裝飾線粗細（字體粗細的倍數） |
| `decoration_style` | `Optional[TextDecorationStyle]` | SOLID/DOUBLE/DOTTED/DASHED/WAVY |
| `shadow` | `Optional[BoxShadowValue]` | 文字陰影 |
| `foreground` | `Optional[Paint]` | 前景繪製 Paint |
| `letter_spacing` | `Optional[Number]` | 字間距（可為負） |
| `word_spacing` | `Optional[Number]` | 字組間距（可為負） |
| `overflow` | `Optional[TextOverflow]` | 溢出處理 |
| `baseline` | `Optional[TextBaseline]` | 基線對齊（ALPHABETIC/IDEOGRAPHIC） |

### TextDecoration（IntFlag）

```python
# 可用 | 組合多個裝飾
ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE | ft.TextDecoration.LINE_THROUGH)
```

- `NONE = 0`
- `UNDERLINE = 1`
- `OVERLINE = 2`
- `LINE_THROUGH = 4`

### TextDecorationStyle（Enum）

`SOLID` / `DOUBLE` / `DOTTED` / `DASHED` / `WAVY`

### TextOverflow（Enum）

- `CLIP` — 直接裁切（預設）
- `ELLIPSIS` — 用省略號截斷
- `FADE` — 漸層淡出
- `VISIBLE` — 超出範圍仍顯示

### TextThemeStyle（Enum）

Material Design 主題文字樣式，14 種角色：

| 等級 | 大 | 中 | 小 |
|------|-----|-----|-----|
| Display | DISPLAY_LARGE | DISPLAY_MEDIUM | DISPLAY_SMALL |
| Headline | HEADLINE_LARGE | HEADLINE_MEDIUM | HEADLINE_SMALL |
| Title | TITLE_LARGE | TITLE_MEDIUM | TITLE_SMALL |
| Label | LABEL_LARGE | LABEL_MEDIUM | LABEL_SMALL |
| Body | BODY_LARGE | BODY_MEDIUM | BODY_SMALL |

### copy() 方法

`TextStyle` 支援鏈式複製，所有屬性都可以用 keyword-only 參數覆寫：

```python
base_style = ft.TextStyle(size=14, color=ft.Colors.GREY_700)
copy1 = base_style.copy(weight=ft.FontWeight.BOLD)
copy2 = base_style.copy(color=ft.Colors.RED, size=24)
```

### StrutStyle

獨立的 strut（支架）樣式，用於控制最小行高：
- `size`、`height`、`weight`、`italic`、`font_family`、`leading`（額外行距）、`force_strut_height`

---

## 常用程式碼範例

### 1. 基本 Text

```python
ft.Text("Hello Flet!", size=24, weight=ft.FontWeight.W_600)
```

### 2. 富文字（Text + TextSpan）

```python
ft.Text(
    spans=[
        ft.TextSpan("紅色粗體 ", ft.TextStyle(color=ft.Colors.RED, weight=ft.FontWeight.BOLD)),
        ft.TextSpan("普通文字 ", ft.TextStyle()),
        ft.TextSpan("藍色底線", ft.TextStyle(
            color=ft.Colors.BLUE,
            decoration=ft.TextDecoration.UNDERLINE,
            decoration_style=ft.TextDecorationStyle.DASHED
        )),
    ]
)
```

### 3. Text 搭配 theme_style

```python
ft.Text("標題文字", theme_style=ft.TextThemeStyle.TITLE_LARGE)
```

### 4. 可選取文字（支援複製）

```python
ft.Text(
    "這段文字可以被選取複製",
    selectable=True,
    show_selection_cursor=True,
    selection_cursor_color=ft.Colors.PRIMARY,
)
```

### 5. 溢出截斷

```python
ft.Text(
    "很長的文字內容..." * 50,
    max_lines=2,
    overflow=ft.TextOverflow.ELLIPSIS,
)
```

### 6. Icon 基本用法

```python
ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.RED, size=32)
```

### 7. Icon 填滿程度（outline → filled）

```python
ft.Icon(ft.Icons.FAVORITE, fill=0.5)  # 半填滿
```

### 8. Image 載入網路圖片

```python
ft.Image(
    src="https://flet.dev/img/logo.svg",
    width=100,
    height=100,
    fit=ft.ImageFit.COVER,
    border_radius=ft.border_radius.all(10),
)
```

### 9. Image 加上漸入動畫

```python
ft.Image(
    src="https://example.com/image.png",
    placeholder_src="assets/loading.png",
    fade_in_animation=ft.Animation(500, ft.AnimationCurve.EASE_IN),
)
```

### 10. Image 載入失敗時顯示替代內容

```python
ft.Image(
    src="https://example.com/image.png",
    error_content=ft.Text("圖片載入失敗", color=ft.Colors.RED),
)
```

### 11. 重複使用的 TextStyle

```python
# 定義一個基礎樣式
_body_style = ft.TextStyle(
    size=14,
    color=ft.Colors.GREY_800,
    height=1.5,
)

# 多處重複使用
ft.Text("第一段文字...", style=_body_style)
ft.Text("第二段文字...", style=_body_style.copy(italic=True))
```

---

## 重要發現與注意事項

### 1. Text 與 TextSpan 的繼承差異
- `Text` 繼承 `LayoutControl`（支援更豐富的佈局屬性如 `width`、`height`）
- `TextSpan` 繼承 `Control`（純文字片段，沒有佈局屬性）
- TextSpan 的 `text` 和 `spans` 同時存在時，`text` 優先，`spans` 被忽略

### 2. Icons 是 Proxy 物件，不是 Enum
- `ft.Icons` 並非 `Enum`，而是 `_IconsProxy` 實例
- 所有 8825 個圖示名稱並非直接定義在 Python 程式碼中，而是從 `icons.json` 動態載入
- 這表示 `dir(ft.Icons)` 可以取得完整列表
- 各圖示都有 `_OUTLINED`/`_ROUNDED`/`_SHARP` 三種變體

### 3. Image 的 width/height 特殊處理
- Image 的 `init()` 將 `width` 和 `height` 放入 `skip_properties`，表示這兩個屬性不會傳給 Flutter 層
- Image 的實際尺寸由 `src` 本身和 `fit` 屬性決定

### 4. Image placeholder 不支援 SVG
- 文件明確說明：`placeholder_src` 若為 SVG 來源，會被忽略，直接顯示 `src`

### 5. TextStyle.copy() 是不可變樣式的關鍵
- `TextStyle` 是 dataclass，所有屬性可選
- 建議建立基底樣式後用 `copy()` 派生，避免重複建立

### 6. TextDecoration 是 IntFlag
- 可以用位元運算 `|` 組合多個裝飾效果：`UNDERLINE | LINE_THROUGH`

### 7. TextSpan 的 URL 點擊行為
- `url` 和 `on_click` 可以同時存在，先觸發 `on_click` 再開啟 URL
