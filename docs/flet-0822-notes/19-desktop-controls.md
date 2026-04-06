# Flet 桌面控制項（Cupertino / ListTile / Card / ExpansionTile）— 學習筆記

> 來源：Flet 0.82.2 原始碼
> 路徑：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\controls\...`
> 記錄日期：2026-03-23

---

## Cupertino iOS 風格控制項

### 概述

Cupertino 家族提供 iOS 風格的 UI 元件，位於 `flet.controls.cupertino` 命名空間下。
所有 Cupertino 控制項都使用 `@control()` 裝飾器，並繼承自 `LayoutControl`（或 `DialogControl`、`AdaptiveControl`）。

---

### 1. CupertinoAlertDialog（警示對話框）

**檔案：** `cupertino_alert_dialog.py`（第 1-77 行）

**類別階層：**
```
CupertinoAlertDialog → DialogControl → LayoutControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `modal` | `bool` | `False` | 是否為強制 modal（點擊外部不可關閉） |
| `title` | `StrOrControl` | `None` | 對話框標題（大字體，頂部顯示） |
| `content` | `Control` | `None` | 對話框內容（通常放 `Column` 夾多個 `Text`） |
| `actions` | `list[Control]` | `[]` | 底部動作按鈕列表（通常放 `CupertinoDialogAction`） |
| `inset_animation` | `Animation` | `Animation(DECELERATE, 100ms)` | 鍵盤彈出時的動畫 |
| `barrier_color` | `ColorValue` | `None`（預設 `Colors.BLACK_54`） | modal 遮罩顏色 |

**驗證規則（第 66-72 行）：**
- `before_update()` 檢查：title 可見、或 content 可見、或至少有一個 visible 的 action
- 否則拋出 `ValueError("AlertDialog has nothing to display...")`

**使用範例亮點：** 可搭配 `page.show_dialog()` 顯示

---

### 2. CupertinoButton（iOS 按鈕）

**檔案：** `cupertino_button.py`（第 1-167 行）

**類別階層：**
```
CupertinoButton → LayoutControl → Control
```

**按鈕尺寸枚舉 `CupertinoButtonSize`（第 19-41 行）：**

| 成員 | 說明 |
|------|------|
| `SMALL` | 緊湊型，文字與尺寸都較小 |
| `MEDIUM` | 中等尺寸 |
| `LARGE` | 經典大 Cupertino 按鈕（預設） |

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `content` | `StrOrControl` | `None` | 按鈕內容 |
| `icon` | `IconDataOrControl` | `None` | 按鈕圖示 |
| `icon_color` | `ColorValue` | `None` | 圖示前景色 |
| `bgcolor` | `ColorValue` | `None` | 按鈕背景色 |
| `color` | `ColorValue` | `None` | 按鈕文字顏色 |
| `disabled_bgcolor` | `ColorValue` | `None` | 禁用時的背景色 |
| `opacity_on_click` | `Number` | `0.4` | 點擊時的透明度（0.0-1.0） |
| `min_size` | `Size` | `None` | 最小尺寸 |
| `size` | `CupertinoButtonSize` | `LARGE` | 按鈕尺寸 preset |
| `padding` | `PaddingValue` | `None` | 內距 |
| `alignment` | `Alignment` | `CENTER` | 內容對齊（預設置中） |
| `border_radius` | `BorderRadiusValue` | `8.0` 圓角 | 圓角 |
| `url` | `str \| Url` | `None` | 點擊時開啟的 URL |
| `autofocus` | `bool` | `False` | 是否自動聚焦 |
| `focus_color` | `ColorValue` | `None` | 鍵盤聚焦時的顏色（預設為 `bgcolor` 半透明 or `ACTIVE_BLUE` 半透明） |
| `mouse_cursor` | `MouseCursor` | `None` | 滑鼠游標 |
| `on_click` | `ControlEventHandler` | `None` | 點擊事件 |
| `on_long_press` | `ControlEventHandler` | `None` | 長按事件 |
| `on_focus` / `on_blur` | `ControlEventHandler` | `None` | 聚焦/失焦事件 |

**驗證規則（第 155-160 行）：** `opacity_on_click` 必須在 0.0 到 1.0 之間。

---

### 3. CupertinoSwitch（iOS 開關）

**檔案：** `cupertino_switch.py`（第 1-119 行）

**類別階層：**
```
CupertinoSwitch → LayoutControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `label` | `str` | `None` | Switch 右側的標籤文字（可點擊） |
| `value` | `bool` | `False` | 當前開關狀態 |
| `label_position` | `LabelPosition` | `RIGHT` | 標籤位於左或右 |
| `thumb_color` | `ColorValue` | `None` | 滑塊顏色 |
| `focus_color` | `ColorValue` | `None` | 聚焦時的高亮顏色 |
| `autofocus` | `bool` | `False` | 自動聚焦 |
| `on_label_color` / `off_label_color` | `ColorValue` | `None` | 開/關時的標籤顏色 |
| `active_thumb_image_src` / `inactive_thumb_image_src` | `str \| bytes` | `None` | 滑塊上的圖片（可為 URL / asset 路徑 / base64 / 原始 bytes） |
| `active_track_color` / `inactive_track_color` | `ColorValue` | `None` | 軌道顏色 |
| `inactive_thumb_color` | `ColorValue` | `None` | 關閉時滑塊顏色（預設 `thumb_color` → `WHITE`） |
| `track_outline_color` / `track_outline_width` | `ControlStateValue` | `None` | 軌道邊框（支援各狀態） |
| `thumb_icon` | `ControlStateValue[IconData]` | `None` | 滑塊圖示（支援各狀態） |
| `on_change` | `ControlEventHandler` | `None` | 狀態改變事件 |
| `on_focus` / `on_blur` | `ControlEventHandler` | `None` | 聚焦/失焦事件 |
| `on_image_error` | `ControlEventHandler` | `None` | 圖片載入失敗事件 |

**重要細節：** Switch 的 thumb 和 track 顏色是分開設定的，支援各自獨立設定開/關狀態。

---

### 4. CupertinoSlider（iOS 滑桿）

**檔案：** `cupertino_slider.py`（第 1-97 行）

**類別階層：**
```
CupertinoSlider → LayoutControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `value` | `Number` | `None`（fallback = `min`） | 目前選取值 |
| `min` | `Number` | `0.0` | 最小值 |
| `max` | `Number` | `1.0` | 最大值 |
| `divisions` | `int` | `None`（連續） | 離散分段數 |
| `active_color` | `ColorValue` | `None` | 已選取範圍的顏色（thumb 到 min 端） |
| `thumb_color` | `ColorValue` | `None` | 滑塊顏色 |
| `on_change` | `ControlEventHandler` | `None` | 值改變時 |
| `on_change_start` | `ControlEventHandler` | `None` | 開始拖曳時 |
| `on_change_end` | `ControlEventHandler` | `None` | 結束拖曳時 |
| `on_focus` / `on_blur` | `ControlEventHandler` | `None` | 聚焦/失焦 |

**驗證規則（第 73-87 行）：**
- `min <= max`
- `min <= value <= max`
- 與 Material `Slider` 不同，CupertinoSlider **沒有 `on_acquired`** 或 **`on_dispose`** 事件

---

### 5. CupertinoTextField（iOS 文字輸入框）

**檔案：** `cupertino_textfield.py`（第 1-93 行）

**類別階層：**
```
CupertinoTextField → TextField → FormFieldControl → ... → Control
```

**Cupertino 特有屬性（繼承 TextField 的基礎上）：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `placeholder_text` | `str` | `None` | 輸入框空時的佔位提示文字 |
| `placeholder_style` | `TextStyle` | `None` | 佔位文字的樣式 |
| `gradient` | `Gradient` | `None` | 背景漸層 |
| `blend_mode` | `BlendMode` | `None` | 背景混合模式 |
| `shadows` | `BoxShadowValue` | `None` | 文字框陰影 |
| `prefix_visibility_mode` | `OverlayVisibilityMode` | `ALWAYS` | 前綴圖示可見性模式 |
| `suffix_visibility_mode` | `OverlayVisibilityMode` | `ALWAYS` | 後綴圖示可見性模式 |
| `clear_button_visibility_mode` | `OverlayVisibilityMode` | `NEVER` | 清除按鈕可見性模式 |
| `clear_button_semantics_label` | `str` | `"Clear"` | 清除按鈕的無障礙標籤 |
| `image` | `DecorationImage` | `None` | 背景圖片 |
| `padding` | `PaddingValue` | `Padding.all(7)` | 文字區域內距（預設 7，與 TextField 不同） |

**`OverlayVisibilityMode` 枚舉（第 17-38 行）：**

| 成員 | 說明 |
|------|------|
| `NEVER` | 無論輸入狀態如何，覆蓋層都不顯示 |
| `EDITING` | 只在有文字輸入時顯示（非空） |
| `NOT_EDITING` | 只在輸入為空時顯示 |
| `ALWAYS` | 永遠顯示（prefix/suffix 預設） |

**與 Material `TextField` 的差異：**
- Cupertino 版本有 `shadows`、`gradient`、`blend_mode`、`image` 等裝飾性屬性
- 預設 padding 是 7 而非 TextField 的通常值
- `clear_button_visibility_mode` 預設是 `NEVER`

---

### 6. CupertinoDatePicker（iOS 日期選擇器）

**檔案：** `cupertino_date_picker.py`（第 1-209 行）

**類別階層：**
```
CupertinoDatePicker → LayoutControl → Control
```

**`CupertinoDatePickerMode` 枚舉（第 26-60 行）：**

| 成員 | 說明 | 範例 |
|------|------|------|
| `TIME` | 只顯示時分（+ AM/PM） | `4 \| 14 \| PM` |
| `DATE` | 顯示月/日/年 | `July \| 13 \| 2012` |
| `DATE_AND_TIME` | 顯示星期/月/日 + 時分 | `Fri Jul 13 \| 4 \| 14 \| PM` |
| `MONTH_YEAR` | 只顯示月/年 | `July \| 2012` |

**`CupertinoDatePickerDateOrder` 枚舉（第 69-96 行）：**

| 成員 | 順序 | 範例 |
|------|------|------|
| `DAY_MONTH_YEAR` | 日→月→年 | `12 \| March \| 1996` |
| `MONTH_DAY_YEAR` | 月→日→年（美國常用） | `March \| 12 \| 1996` |
| `YEAR_MONTH_DAY` | 年→月→日 | `1996 \| March \| 12` |
| `YEAR_DAY_MONTH` | 年→日→月 | `1996 \| 12 \| March` |

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `value` | `DateTimeValue` | `datetime.now()` | 目前選取的日期/時間 |
| `locale` | `Locale` | `None` | 地區設定 |
| `first_date` / `last_date` | `DateTimeValue` | `None` | 可選日期範圍 |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `minute_interval` | `int` | `1` | 分鐘間隔（必須是 60 的正因數） |
| `minimum_year` | `int` | `1` | 最小年份 |
| `maximum_year` | `int` | `None`（無限制） | 最大年份 |
| `item_extent` | `Number` | `32.0` | 每個滾輪項目的高度 |
| `use_24h_format` | `bool` | `False` | 是否使用 24 小時制 |
| `show_day_of_week` | `bool` | `False` | 是否顯示星期（僅 `DATE` 模式） |
| `date_picker_mode` | `CupertinoDatePickerMode` | `DATE_AND_TIME` | 選擇器模式 |
| `date_order` | `CupertinoDatePickerDateOrder` | `None` | 日期欄位順序 |
| `on_change` | `ControlEventHandler` | `None` | 值改變事件 |

**驗證規則（第 129-208 行）：** 非常多，包括：
- `item_extent > 0`
- `minute_interval` 是 60 的正因數
- `value` 必須在 `first_date` / `last_date` 範圍內
- `value.minute` 必須可被 `minute_interval` 整除
- `show_day_of_week` 只能在 `DATE` 模式下使用

---

### 7. CupertinoTimerPicker（iOS 倒數計時器選擇器）

**檔案：** `cupertino_timer_picker.py`（第 1-120 行）

**類別階層：**
```
CupertinoTimerPicker → LayoutControl → Control
```

**`CupertinoTimerPickerMode` 枚舉（第 10-31 行）：**

| 成員 | 說明 | 範例 |
|------|------|------|
| `HOUR_MINUTE` | 時:分 | `16 hours \| 14 min` |
| `HOUR_MINUTE_SECONDS` | 時:分:秒 | `16 hours \| 14 min \| 43 sec` |
| `MINUTE_SECONDS` | 分:秒 | `14 min \| 43 sec` |

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `value` | `DurationValue` | `Duration()` | 初始倒數時間（可為 int 秒 或 `Duration`） |
| `alignment` | `Alignment` | `CENTER` | 在父容器中的對齊方式 |
| `second_interval` | `int` | `1` | 秒針間隔（60 的正因數） |
| `minute_interval` | `int` | `1` | 分針間隔（60 的正因數） |
| `mode` | `CupertinoTimerPickerMode` | `HOUR_MINUTE_SECONDS` | 顯示模式 |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `item_extent` | `Number` | `32.0` | 每個滾輪項目高度 |
| `on_change` | `ControlEventHandler` | `None` | 時間改變事件（`data` 為 `Duration` 或 `int`） |

**驗證規則（第 91-120 行）：**
- `value >= 0` 且 `< 24 hours`
- `minute_interval` 和 `second_interval` 都是 60 的正因數
- `value` 必須是 `minute_interval` 和 `second_interval` 的倍數
- `item_extent > 0`

**重要：** 計時上限為 24 小時（不到 24 小時，嚴格小於）。

---

### 8. CupertinoPicker（iOS 滾輪選擇器）

**檔案：** `cupertino_picker.py`（第 1-116 行）

**類別階層：**
```
CupertinoPicker → LayoutControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `controls` | `list[Control]` | `[]` | 滾輪中的項目列表 |
| `item_extent` | `Number` | `32.0` | 每個項目高度 |
| `selected_index` | `int` | `0` | 目前選取的項目索引 |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `use_magnifier` | `bool` | `False` | 是否使用放大鏡效果 |
| `looping` | `bool` | `False` | 是否循環滾動 |
| `magnification` | `Number` | `1.0` | 放大倍率（>1 放大，<1 縮小） |
| `squeeze` | `Number` | `1.45` | 滾輪項目的緊湊程度 |
| `diameter_ratio` | `Number` | `1.07` | 高度與圓筒直徑的比例（越小越彎曲） |
| `off_axis_fraction` | `Number` | `0.0` | 水平偏置（以寬度比例） |
| `selection_overlay` | `Control` | `None` | 選中項目的覆蓋層（預設為圓角矩形） |
| `default_selection_overlay_bgcolor` | `ColorValue` | `TERTIARY_SYSTEM_FILL` | 預設覆蓋層背景色 |
| `on_change` | `ControlEventHandler` | `None` | 選取改變事件 |

**驗證規則（第 96-108 行）：** `squeeze > 0.0`、`magnification > 0.0`、`item_extent > 0.0`

---

### 9. CupertinoActionSheet（iOS 操作列表）

**檔案：** `cupertino_action_sheet.py`（第 1-73 行）

**類別階層：**
```
CupertinoActionSheet → LayoutControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `title` | `StrOrControl` | `None` | 標題 |
| `message` | `StrOrControl` | `None` | 說明訊息 |
| `actions` | `list[Control]` | `None` | 操作按鈕列表（通常放 `CupertinoActionSheetAction`） |
| `cancel` | `Control` | `None` | 取消按鈕（單獨分組，顯示在底部） |

**驗證規則（第 55-61 行）：** 至少要提供 `actions`、`title`、`message` 或 `cancel` 其中之一。

**使用方式：** 需搭配 `CupertinoBottomSheet`：`page.show_dialog(ft.CupertinoBottomSheet(sheet))`

---

### 10. CupertinoContextMenu（長按上下文選單）

**檔案：** `cupertino_context_menu.py`（第 1-58 行）

**類別階層：**
```
CupertinoContextMenu → AdaptiveControl → Control
```

**主要屬性：**

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `content` | `Control` | （必填） | 要長按的目標內容 |
| `actions` | `list[Control]` | （必填） | 長按後顯示的動作列表 |
| `enable_haptic_feedback` | `bool` | `True` | 是否啟用觸控回饋 |

**重要行為（第 24-31 行）：**
- `content` 會被移至新的全螢幕 modal route 並展開
- 這讓 `content` 可以自適應調整大小

**驗證規則（第 41-47 行）：**
- `content` 必須可見（`visible=True`）
- `actions` 至少要有一個可見的 action

**注意：** 這是 `AdaptiveControl` 的子類，會根據平台自動選擇使用原生或自訂實作。

---

### 11. CupertinoIcons（iOS 圖示）

**檔案：** `cupertino_icons.py`（第 1-92 行）

**實作方式：** 使用 `_CupertinoIconsProxy` 代理類別，圖示資料來自 `cupertino_icons.json`（透過 `importlib.resources` 讀取）。

**特殊設計：**
- `_CupertinoIconData` 繼承 `IconData`，並實作了 `_missing_()` 方法動態建立成員（應對未知的 icon code）
- 代理類別延遲載入（lazy load）json，直到第一次存取才載入
- 支援 `.random()` 方法可隨機取得一個 icon（可排除、可加權重）

**使用方式：**
```python
ft.CupertinoIcons.NAME_OF_ICON  # 例：ft.CupertinoIcons.settings
```

---

## ListTile

**檔案：** `list_tile.py`（第 1-216 行）

**類別階層：**
```
ListTile → LayoutControl, AdaptiveControl
```

### 與 Row 的差異

| 比較點 | `ListTile` | `Row` |
|--------|-----------|-------|
| 設計目的 | Material Design 列表項目 | 一般水平佈局 |
| 內建標題/副標題 | ✅ `title` / `subtitle` | ❌ 需自行組合 |
| 內建 leading/trailing 插槽 | ✅ | ❌ 需自行放 Icon/Avatar |
| 點擊/長按事件 | ✅ `on_click` / `on_long_press` | ❌ 需包 Container |
| 選中狀態 | ✅ `selected` + `selected_color` | ❌ |
| 密集模式 | ✅ `dense` | ❌ |
| 捷徑綁定（Radio/Checkbox/Switch） | ✅ `toggle_inputs` | ❌ |
| 三行模式 | ✅ `is_three_line` | ❌ |
| 回饋（splash/hover） | ✅ `splash_color` / `hover_color` | ❌ |
| 點擊標籤 | ✅ `label`（Switch 右側） | ❌ |

**ListTile 是專為列表項目設計的元件，Row 是通用水平佈局容器。**

### 主要屬性

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `title` | `StrOrControl` | `None` | 主要文字（通常為 `Text`） |
| `subtitle` | `StrOrControl` | `None` | 次要文字（通常為 `Text`） |
| `is_three_line` | `bool` | `None` | 是否為三行模式 |
| `leading` | `IconDataOrControl` | `None` | 左側圖示/頭像 |
| `trailing` | `IconDataOrControl` | `None` | 右側圖示（通常為 `Icon(ft.Icons.CHEVRON_RIGHT)`） |
| `content_padding` | `PaddingValue` | `None` | 內距 |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `splash_color` | `ColorValue` | `None` | 點擊漣漪顏色 |
| `hover_color` | `ColorValue` | `None` | 懸停顏色 |
| `selected` | `bool` | `False` | 選中狀態（會套用 `selected_color`） |
| `dense` | `bool` | `None` | 密集模式 |
| `autofocus` | `bool` | `False` | 自動聚焦 |
| `toggle_inputs` | `bool` | `False` | 點擊是否切換 Radio/Checkbox/Switch 狀態 |
| `selected_color` | `ColorValue` | `None` | 選中時的顏色 |
| `selected_tile_color` | `ColorValue` | `None` | 選中時的背景色 |
| `style` | `ListTileStyle` | `None` | 標題字體樣式（LIST 或 DRAWER） |
| `enable_feedback` | `bool` | `None` | 是否有聲音/震動回饋 |
| `horizontal_spacing` | `Number` | `None` | leading/trailing 與 title 的間距 |
| `min_leading_width` | `Number` | `None` | leading 最小寬度 |
| `min_vertical_padding` | `Number` | `None` | title/subtitle 上下最小內距 |
| `url` | `str \| Url` | `None` | 點擊時開啟的 URL |
| `title_alignment` | `ListTileTitleAlignment` | `None` | leading/trailing 與 title 的對齊方式 |
| `icon_color` | `ColorValue` | `None` | leading/trailing 圖示預設顏色 |
| `text_color` | `ColorValue` | `None` | title/subtitle 文字顏色 |
| `shape` | `OutlinedBorder` | `None` | 形狀 |
| `visual_density` | `VisualDensity` | `None` | 佈局緊湊程度 |
| `mouse_cursor` | `MouseCursor` | `None` | 滑鼠游標 |
| `title_text_style` / `subtitle_text_style` | `TextStyle` | `None` | 各文字的自訂樣式 |
| `leading_and_trailing_text_style` | `TextStyle` | `None` | leading/trailing 的文字樣式 |
| `min_height` | `Number` | `None` | 最小高度（預設：無=56/72/88，dense=48/64/76） |
| `on_click` / `on_long_press` | `ControlEventHandler` | `None` | 點擊/長按事件 |

**`ListTileTitleAlignment`（第 15-48 行）：**

| 成員 | 說明 |
|------|------|
| `TOP` | leading/trailing 對齊到 title 區域頂部 |
| `CENTER` | leading/trailing 與 title/subtitle 垂直置中 |
| `BOTTOM` | leading/trailing 對齊到 title 區域底部 |
| `THREE_LINE` | Material 3 預設，三行優化對齊 |
| `TITLE_HEIGHT` | Material 2 預設，基於標題高度的對齊方式 |

---

## Card

**檔案：** `card.py`（第 1-100 行）

**類別階層：**
```
Card → LayoutControl, AdaptiveControl
```

### Card的本質

Card 是一個**包裝容器**，用來承載內容，帶有圓角和陰影效果。
預設 `margin` 屬於內部屬性（`skip_properties` 包含 `"margin"`，見第 98 行）。

### 主要屬性

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `content` | `Control` | `None` | 卡片內的單一子控制項（要放多個需用 Row/Column/Stack 包） |
| `elevation` | `Number` | `None`（fallback=1.0） | Z軸高度（陰影大小） |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `shadow_color` | `ColorValue` | `None` | 陰影顏色 |
| `shape` | `OutlinedBorder` | `None`（fallback=`RoundedRectangleBorder(radius=12.0)`） | 形狀 |
| `clip_behavior` | `ClipBehavior` | `None`（fallback=`NONE`） | 內容裁切行為 |
| `semantic_container` | `bool` | `True` | 是否代表單一語意容器 |
| `show_border_on_foreground` | `bool` | `True` | border 繪製在前或後 |
| `variant` | `CardVariant` | `ELEVATED` | 視覺風格 preset |

**`CardVariant`（第 12-30 行）：**

| 成員 | 說明 |
|------|------|
| `ELEVATED` | 標準陰影卡片（預設） |
| `FILLED` | 強調背景色的填充卡片 |
| `OUTLINED` | 可見邊框的卡片 |

### 重要發現

- **`content` 只有一個子控制項**。如果要放多個子項，必須先用 `Row`、`Column` 或 `Stack` 包起來。
- **`margin` 被跳過**（`skip_properties`），表示 Card 的 margin 由 Flutter 層面控制，Python 層面無法直接設定。

---

## ExpansionTile / ExpansionPanel

### ExpansionTile

**檔案：** `expansion_tile.py`（第 1-248 行）

**類別階層：**
```
ExpansionTile → LayoutControl, AdaptiveControl
```

ExpansionTile 是一個**可折疊的單行 ListTile**，帶有展開/收起箭頭圖示。

### 與 ExpansionPanel 的差異

| 比較點 | `ExpansionTile` | `ExpansionPanel` + `ExpansionPanelList` |
|--------|-----------------|---------------------------------------|
| 結構 | 單一控制項，自身包含標題和內容 | 兩個控制項：`ExpansionPanel`（內容）+ `ExpansionPanelList`（容器） |
| 標題/內容 | `title` + `controls`（多個子項） | `header` + `content`（各一個控制項） |
| 動畫 | 內建展開/收起動畫 | 由 `ExpansionPanelList` 控制動畫 |
| 分隔線 | 無明確分隔線 | `divider_color` 控制折叠面板間的分隔線 |
| 面板群組 | 不支援面板群組 | `ExpansionPanelList` 可管理多個面板，自動處理互斥展開 |

### ExpansionTile 主要屬性

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `title` | `StrOrControl` | （必填） | 主標題（字串或 Control） |
| `controls` | `list[Control]` | `None` | 展開後顯示的子控制項列表 |
| `subtitle` | `StrOrControl` | `None` | 副標題 |
| `leading` | `IconDataOrControl` | `None` | 左側圖示（可被 expansion arrow 取代） |
| `trailing` | `IconDataOrControl` | `None` | 右側（可被 expansion arrow 取代） |
| `controls_padding` | `PaddingValue` | `None` | controls 區域的內距 |
| `tile_padding` | `PaddingValue` | `None` | tile 本體的內距 |
| `affinity` | `TileAffinity` | `None`（預設 `TRAILING`） | expansion arrow 的位置偏好 |
| `expanded_alignment` | `Alignment` | `None`（預設 `CENTER`） | controls 的對齊方式 |
| `expanded_cross_axis_alignment` | `CrossAxisAlignment` | `CENTER` | 每個 child 的對齊（不可為 `BASELINE`） |
| `clip_behavior` | `ClipBehavior` | `None`（預設 `ANTI_ALIAS`） | 裁切行為 |
| `maintain_state` | `bool` | `False` | 收起時是否維持子控制項狀態 |
| `text_color` / `icon_color` | `ColorValue` | `None` | 展開時的顏色 |
| `collapsed_*` 系列 | `ColorValue` | `None` | 折疊時的對應顏色 |
| `shape` / `collapsed_shape` | `OutlinedBorder` | `None` | 展開/折疊時的形狀 |
| `bgcolor` / `collapsed_bgcolor` | `ColorValue` | `None` | 展開/折疊時的背景色 |
| `dense` | `bool` | `None` | 密集模式 |
| `enable_feedback` | `bool` | `True` | 聲音/震動回饋 |
| `show_trailing_icon` | `bool` | `True` | 是否顯示箭頭圖示 |
| `min_tile_height` | `Number` | `None` | tile 最小高度 |
| `expanded` | `bool` | `False` | 目前是否展開 |
| `visual_density` | `VisualDensity` | `None` | 佈局緊湊程度 |
| `animation_style` | `AnimationStyle` | `None` | 展開/收起動畫（可用 `no_animation()` 禁用） |
| `on_change` | `ControlEventHandler` | `None` | 展開狀態改變事件（`data` 為新的 `expanded` 值） |

**`TileAffinity`（第 18-41 行）：**

| 成員 | 說明 |
|------|------|
| `LEADING` | 強制 expansion arrow 在 leading 側 |
| `TRAILING` | 強制 expansion arrow 在 trailing 側（預設） |
| `PLATFORM` | 跟隨平台預設行為 |

**驗證規則（第 240-247 行）：** `expanded_cross_axis_alignment` 不可為 `BASELINE`（因為 expanded controls 是 column 排列，不是 row）。

---

### ExpansionPanel / ExpansionPanelList

**檔案：** `expansion_panel.py`（第 1-143 行）

#### ExpansionPanel

**類別階層：**
```
ExpansionPanel → LayoutControl, AdaptiveControl
```

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `header` | `Control` | `None` | 面板標題（可為 `Text` 或其他控制項） |
| `content` | `Control` | `None` | 展開後顯示的內容 |
| `bgcolor` | `ColorValue` | `None` | 背景色 |
| `expanded` | `bool` | `False` | 是否展開 |
| `can_tap_header` | `bool` | `False` | 點擊標題是否可以切換展開狀態 |
| `splash_color` / `highlight_color` | `ColorValue` | `None` | TBD |

#### ExpansionPanelList

**類別階層：**
```
ExpansionPanelList → LayoutControl → Control
```

| 屬性 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `controls` | `list[ExpansionPanel]` | `[]` | 面板列表 |
| `divider_color` | `ColorValue` | `None` | 分隔線顏色（折疊狀態時可見） |
| `elevation` | `Number` | `2` | 展開時的面板 elevation（須 >= 0） |
| `expanded_header_padding` | `PaddingValue` | `Padding.symmetric(vertical=16.0)` | 展開時的 header 內距 |
| `expand_icon_color` | `ColorValue` | `None` | 展開箭頭顏色（預設淺色主題 `BLACK_54`，深色主題 `WHITE_60`） |
| `spacing` | `Number` | `None` | 展開時面板之間的間距 |
| `on_change` | `ControlEventHandler` | `None` | 展開狀態改變事件（`data` 為觸發面板的 index） |

**驗證規則（第 140-143 行）：** `elevation >= 0`

---

## CupertinoContextMenu

**屬性速查：**

| 屬性 | 說明 |
|------|------|
| `content` | 長按目標（必填，且需 `visible=True`） |
| `actions` | 長按後顯示的動作列表（至少一個 visible action） |
| `enable_haptic_feedback` | 是否觸發觸控回饋（預設 `True`） |

**使用重點：**
- `content` 會在長按時被移至全螢幕 modal route 並展開
- 需搭配 `CupertinoContextMenuAction` 作為 actions 項目
- 是 `AdaptiveControl` 子類，會根據平台使用不同實作

---

## 常用程式碼範例

### CupertinoAlertDialog 搭配頁面對話框

```python
# 顯示 iOS 風格警示對話框
dialog = ft.CupertinoAlertDialog(
    title="確認刪除",
    content=ft.Column([
        ft.Text("您確定要刪除這個項目嗎？"),
        ft.Text("此操作無法撤銷。", size=12, color=ft.Colors.GREY),
    ]),
    actions=[
        ft.CupertinoDialogAction("取消"),
        ft.CupertinoDialogAction("刪除", destructive=True),
    ],
)
page.show_dialog(dialog)
```

### CupertinoButton 基本使用

```python
# iOS 風格按鈕
ft.CupertinoButton(
    "Tap me",
    icon=ft.CupertinoIcons.PLAY_CIRCLE,
    size=ft.CupertinoButtonSize.MEDIUM,
    bgcolor=ft.Colors.ACTIVE_BLUE,
    on_click=lambda e: print("Clicked!"),
)
```

### CupertinoSwitch 搭配事件

```python
# iOS 風格開關
def toggle_dark_mode(e):
    page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
    page.update()

switch = ft.CupertinoSwitch(
    label="深色模式",
    value=False,
    on_change=toggle_dark_mode,
)
```

### CupertinoSlider 離散分段

```python
# 離散滑桿（5 段）
slider = ft.CupertinoSlider(
    value=2,
    min=0,
    max=4,
    divisions=4,
    active_color=ft.Colors.ACTIVE_BLUE,
    on_change=lambda e: print(f"Value: {e.control.value}"),
)
```

### CupertinoTextField 具備清除按鈕

```python
# iOS 風格文字輸入框
ft.CupertinoTextField(
    placeholder_text="搜尋...",
    clear_button_visibility_mode=ft.OverlayVisibilityMode.WHILE_EDITING,
    prefix=ft.Icon(ft.CupertinoIcons.SEARCH),
    suffix=ft.Icon(ft.CupertinoIcons.CLEAR_CIRCLE_FILLED),
)
```

### CupertinoDatePicker 日期範圍限制

```python
# 日期選擇器（僅月份）
picker = ft.CupertinoDatePicker(
    date_picker_mode=ft.CupertinoDatePickerMode.MONTH_YEAR,
    value=datetime(2024, 1, 1),
    minimum_year=2020,
    maximum_year=2030,
    on_change=lambda e: print(f"Selected: {e.control.value}"),
)
```

### CupertinoTimerPicker 倒數計時

```python
# 倒數計時器（分:秒模式）
timer_picker = ft.CupertinoTimerPicker(
    mode=ft.CupertinoTimerPickerMode.MINUTE_SECONDS,
    value=300,  # 5 分鐘（秒為單位）
    minute_interval=5,
    second_interval=10,
    on_change=lambda e: print(f"Duration: {e.data}"),
)
```

### CupertinoContextMenu 長按選單

```python
# 長按顯示上下文選單
menu = ft.CupertinoContextMenu(
    content=ft.Image(src="photo.png", width=200),
    actions=[
        ft.CupertinoContextMenuAction(
            "分享",
            icon=ft.CupertinoIcons.SHARE,
        ),
        ft.CupertinoContextMenuAction(
            "複製",
            icon=ft.CupertinoIcons.DOC_ON_DOC,
        ),
        ft.CupertinoContextMenuAction(
            "刪除",
            is_destructive=True,
            icon=ft.CupertinoIcons.TRASH,
        ),
    ],
)
```

### ListTile 設定面板列表

```python
# 設定頁面列表
ft.ListTile(
    width=400,
    leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
    title="Jane Doe",
    subtitle="Product Manager",
    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
    selected=True,
    on_click=lambda e: print("Tile clicked"),
)
```

### Card 包裝容器

```python
# 卡片包裝 ListTile
ft.Card(
    elevation=2,
    variant=ft.CardVariant.ELEVATED,
    content=ft.Container(
        width=400,
        padding=10,
        content=ft.ListTile(
            leading=ft.Icon(ft.Icons.FOREST),
            title=ft.Text("Card Name"),
            subtitle=ft.Text("Card subtitle"),
        ),
    ),
)
```

### ExpansionTile 可折疊面板

```python
# 可折疊設定面板
ft.ExpansionTile(
    title="帳戶",
    subtitle="管理個人資料與安全性",
    expanded=True,
    controls=[
        ft.ListTile(title=ft.Text("個人資料")),
        ft.ListTile(title=ft.Text("安全性")),
        ft.ListTile(title=ft.Text("隱私設定")),
    ],
    on_change=lambda e: print(f"Expanded: {e.data}"),
)
```

### ExpansionPanelList 手風琴列表

```python
# 手風琴式面板列表（同時只有一個展開）
ft.ExpansionPanelList(
    width=400,
    elevation=4,
    divider_color=ft.Colors.GREY_300,
    controls=[
        ft.ExpansionPanel(
            header=ft.Text("第一章"),
            content=ft.Text("第一章內容..."),
            expanded=True,
        ),
        ft.ExpansionPanel(
            header=ft.Text("第二章"),
            content=ft.Text("第二章內容..."),
        ),
    ],
    on_change=lambda e: print(f"Panel {e.data} changed"),
)
```

---

## 重要發現與注意事項

### 1. CupertinoAlertDialog 的 barrier_color 預設值

`barrier_color` 若為 `None`，會 fallback 到 `DialogTheme.barrier_color`，若仍為 `None`，預設才是 `Colors.BLACK_54`（第 63-65 行）。

### 2. CupertinoSlider 的 value 預設行為

`before_update()` 中（第 73 行）會自動將 `None` 的 `value` 設定為 `min`：
```python
self.value = self.value if self.value is not None else self.min
```

### 3. CupertinoTimerPicker 的值上限

計時上限嚴格小於 24 小時（`value < Duration(hours=24)`），不能等於 24 小時。

### 4. CupertinoDatePicker 的 TIME 模式與 first_date/last_date

在 `TIME` 模式時，`first_date`/`last_date` 的檢查會將時間部分與 `value` 的日期部分組合後再比較。因此 `first_date` 通常需要與 `value` 同一天。

### 5. Card 的 content 只有一個子控制項

`Card.content` 只接受一個 `Control`，要放多個子項需要用 `Row`/`Column`/`Stack` 包裝後再傳入。

### 6. Card 的 margin 不可直接設定

`skip_properties` 包含 `"margin"`（第 98 行），margin 由 Flutter 層管理。

### 7. ListTile 與 Row 的核心差異

`ListTile` 是 Material Design 列表專用元件，內建 `title`/`subtitle`/`leading`/`trailing` 佈局；`Row` 是通用水平容器，需自行組合子元件。ListTile 還內建點擊、長按、選中、密集等列表相關行為。

### 8. ExpansionTile 與 ExpansionPanel 的抉擇

- **ExpansionTile**：適合單一可折疊區塊，或巢狀在 ListView 中；支援多個 controls 子項
- **ExpansionPanelList**：適合手風琴式群組行為（同時只有一個展開）；每個面板的 header/content 各自只有一個子控制項

### 9. ExpansionTile 的 maintain_state

預設 `False`，收起時子控制項會從 tree 中移除再重建。若設為 `True`，子控制項狀態會被保留，但要注意記憶體佔用。

### 10. CupertinoTextField 的 `padding` 預設值

CupertinoTextField 的 `padding` 預設是 `Padding.all(7)`（第 88 行），比 Material TextField 更緊湊。

### 11. CupertinoContextMenu 的 AdaptiveControl 特性

`CupertinoContextMenu` 是 `AdaptiveControl` 子類，在不同平台會使用不同的實作方式，桌面環境可能使用自訂 Flutter widget 而非原生實現。

### 12. CupertinoIcons 的延遲載入

`CupertinoIcons` 代理類別使用 lazy load，json 資料直到第一次存取 `_map` 時才載入。這對於減少啟動時間有幫助。

### 13. CupertinoSwitch 的 thumb_image_src 支援多格式

`active_thumb_image_src` 和 `inactive_thumb_image_src` 可接受：URL、asset 路徑、base64 字串、或原始 bytes。

### 14. 所有 Cupertino 控制項皆無 `tooltip` 屬性

與 Material 版本不同，Cupertino 家族的按鈕/開關/滑桿等控制項**都沒有** `tooltip` 屬性。如果需要 tooltip，需自行用 `Tooltip` 包裝。

### 15. ExpansionTile 的 collapsed_shape vs shape

ExpansionTile 有兩套顏色/形狀屬性：
- `shape` / `text_color` / `icon_color` / `bgcolor` → **展開時**
- `collapsed_shape` / `collapsed_text_color` / `collapsed_icon_color` / `collapsed_bgcolor` → **折疊時**

動畫過渡時會自動從 collapsed 狀態插值到 expanded 狀態。