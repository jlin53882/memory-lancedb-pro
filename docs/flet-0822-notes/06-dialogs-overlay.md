# Flet 0.82.2 對話框與 Overlay — 學習筆記

> 來源：`C:\Users\admin\Desktop\two_project\.venv\Lib\site-packages\flet\controls\material\`
> 學習日期：2026-03-23

---

## DialogControl（共同基底）

所有對話框（AlertDialog、SnackBar、Banner、BottomSheet）都繼承自 `DialogControl`（`flet.controls.dialog_control`）。

```python
# DialogControl 定義（第 14-27 行）
@dataclass(kw_only=True)
class DialogControl(AdaptiveControl):
    open: bool = False           # 設為 True 顯示對話框
    on_dismiss: Optional[ControlEventHandler["DialogControl"]] = None  # 關閉時回呼
```

**核心觀念**：`open` 是控制顯示與否的統一屬性，配合 `page.show_dialog()` / `page.pop_dialog()` 使用。

---

## AlertDialog

**檔案**：`flet/controls/material/alert_dialog.py`（第 1-149 行）

### 主要參數

| 參數 | 類型 | 說明 |
|------|------|------|
| `title` | `StrOrControl` | 對話框頂部大標題，通常放 `ft.Text` |
| `content` | `Control` | 中央顯示的主要內容，通常是 `ft.Column` 包 `ft.Text` |
| `actions` | `list[Control]` | 底部按鈕列，通常是 `ft.TextButton` 列表 |
| `modal` | `bool` | 預設 `False`；設 `True` 可防止點擊遮罩關閉 |
| `bgcolor` | `ColorValue` | 對話框背景色 |
| `elevation` | `Number` | 陰影高度（z-coordinate） |
| `icon` | `Control` | 頂部圖示，通常是 `ft.Icon` |
| `shape` | `OutlinedBorder` | 外框形狀，預設 `RoundedRectangleBorder(radius=4.0)` |

### 驗證規則（第 133-137 行）

```python
def before_update(self):
    super().before_update()
    if not (self.title or self.content or self.actions):
        raise ValueError(
            "AlertDialog has nothing to display. Provide at minimum one of the "
            "following: title, content, actions"
        )
```

**至少要提供 `title`、`content`、`actions` 其中之一**，否則拋例外。

### 開關方式

```python
# 開
dlg = ft.AlertDialog(
    title=ft.Text("提醒"),
    content=ft.Text("確定要刪除嗎？"),
    actions=[ft.TextButton("取消"), ft.TextButton("確定")],
    open=True,
)
page.show_dialog(dlg)

# 關（手動關閉）
dlg.open = False
page.update()
# 或
page.pop_dialog()
```

---

## SnackBar（重要：顯示方式）

**檔案**：`flet/controls/material/snack_bar.py`（第 1-249 行）

### 顯示方式（重要觀念）

**不能用 `open=True`** 直接顯示！ SnackBar 必須透過 `page.show_dialog()` 顯示：

```python
# 錯誤 ❌
snack = ft.SnackBar(ft.Text("訊息"), open=True)  # open 在這裡無效

# 正確 ✅
snack = ft.SnackBar(ft.Text("訊息"))
page.show_dialog(snack)  # 顯示 SnackBar
```

文件範例（第 105-109 行）：
```python
page.show_dialog(ft.SnackBar(ft.Text("Opened snack bar")))
```

### 主要參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `content` | `StrOrControl` | — | 訊息內容，支援 `str` 或 `ft.Text` |
| `bgcolor` | `ColorValue` | — | 背景顏色 |
| `duration` | `DurationValue` | `4000ms` | 自動消失時間 |
| `behavior` | `SnackBarBehavior` | — | `FIXED`（贴底）或 `FLOATING`（浮動） |
| `action` | `str \| SnackBarAction` | — | 可選動作按鈕（如 "Undo"） |
| `show_close_icon` | `bool` | `False` | 是否顯示關閉圖示 |
| `dismiss_direction` | `DismissDirection` | `DOWN` | 滑動關閉方向 |
| `persist` | `bool \| None` | — | `True`=不自動消失；`False`=自動消失；若設 `action` 預設=`True` |
| `on_action` | `Handler` | — | 點擊 action 按鈕回呼 |
| `on_visible` | `Handler` | — | 首次可見時回呼 |

### SnackBarBehavior 列舉（第 20-38 行）

- `FIXED`：固定在底部，若有 `NavigationBar` 會在其上方，其他內容可被推上
- `FLOATING`：作為浮動層疊在底部 widget 之上

### 重要發現

1. **`content` 驗證**（第 215-219 行）：`content` 必須是 `str` 或**可見的** `Control`，不可是隱藏控制項
2. **`persist` 自動行為**：若設了 `action`，預設 `persist=True`（不自動消失，需用戶點擊 action 或關閉圖示）
3. **`duration` 預設 4 秒**：無 action 時 4 秒後自動消失

---

## Banner

**檔案**：`flet/controls/material/banner.py`（第 1-116 行）

### 與 AlertDialog 的差異

| 差異 | Banner | AlertDialog |
|------|--------|-------------|
| 位置 | 畫面**頂部**（app bar 下方） | 畫面**中央** |
| 行為 | **非 modal**（不阻擋互動，用戶可繼續操作） | **可 modal**（可設 `modal=True` 阻擋） |
| 關閉方式 | 需用戶點擊 **actions 按鈕**（無論如何都會關閉） | 可點擊遮罩關閉（`modal=False` 時） |
| 主要用途 | 重要提示+動作選項 | 需確認的對話 |

### 主要參數

| 參數 | 說明 |
|------|------|
| `content` | 訊息內容，`StrOrControl` |
| `actions` | **必填**，至少要有一個可見的按鈕 |
| `leading` | 左側圖示，通常是 `ft.Icon` |
| `bgcolor` | 背景色，預設 `SURFACE_CONTAINER_LOW` |
| `force_actions_below` | 強制 actions 在下方（預設 `False`，1個時在右側） |

### 驗證規則（第 100-108 行）

```python
def before_update(self):
    super().before_update()
    # ...
    if not any(a.visible for a in self.actions):
        raise ValueError("actions must contain at minimum one visible action Control")
```

**`actions` 內至少要有一個可見的控制項**。

### 開關方式

```python
banner = ft.Banner(
    leading=ft.Icon(ft.Icons.INFO_OUTLINED),
    content=ft.Text("備份成功完成"),
    actions=[ft.TextButton("確定")],
    open=True,
)
page.show_dialog(banner)
```

---

## BottomSheet / ModalBottomSheet

**檔案**：`flet/controls/material/bottom_sheet.py`（第 1-120 行）

### 重要特色

- **永遠是 modal**：防止與下方內容互動
- 從畫面**底部**滑出的面板
- 支援**拖曳關閉**（`draggable=True`）

### 主要參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `content` | `Control`（必填） | 面板內容（通常是 `Column`） |
| `open` | `False` | 設 `True` 顯示 |
| `draggable` | `False` | 是否可拖曳上下滑動關閉 |
| `show_drag_handle` | `False` | 是否顯示頂部拖曳把手 |
| `scrollable` | `False` | 設 `True` 讓子內容可滾動 |
| `fullscreen` | `False` | 是否全螢幕（設 `True` 時 `scrollable` 也自動 `True`） |
| `use_safe_area` | `True` | 是否避開系統區域（瀏海等） |
| `bgcolor` | — | 背景色 |
| `elevation` | — | 陰影高度 |
| `dismissible` | `True` | 點擊 scrim（遮罩）是否關閉 |
| `shape` | — | 外框形狀 |

### 開關方式

```python
# 開
sheet = ft.BottomSheet(
    content=ft.Column(
        controls=[
            ft.Text("選擇一個選項"),
            ft.TextButton("關閉", on_click=close_sheet),
        ],
    ),
    open=True,
)
page.show_dialog(sheet)

# 關（方式一）：設 open=False
sheet.open = False
page.update()

# 關（方式二）：用 page.pop_dialog()
page.pop_dialog()

# 關（方式三）：設定 on_dismiss 回呼
def on_dismiss(e):
    print("BottomSheet 已關閉")
sheet.on_dismiss = on_dismiss
```

### 重要發現

1. **`content` 是必填**：不可為 `None`
2. **`scrollable=True` 的關鍵時機**：當內容包含 `ListView`、`GridView` 或自訂高度時，否則面板可能在半高處停止
3. **與 `page.show_dialog()` 的互動**：底層仍是 `DialogControl`，`show_dialog` 將其加入 overlay 顯示

---

## 常用程式碼範例

### 基本 AlertDialog

```python
dlg = ft.AlertDialog(
    title=ft.Text("確認操作"),
    content=ft.Text("此操作無法撤銷，是否繼續？"),
    actions=[
        ft.TextButton("取消", on_click=lambda _: page.pop_dialog()),
        ft.TextButton("確定", on_click=on_confirm),
    ],
    modal=True,
)
page.show_dialog(dlg)
```

### SnackBar（含 Action）

```python
snack = ft.SnackBar(
    content=ft.Text("已刪除 3 筆資料"),
    action="復原",
    on_action=lambda _: restore_data(),
    bgcolor=ft.Colors.INVERSE_SURFACE,
)
page.show_dialog(snack)
```

### Banner

```python
banner = ft.Banner(
    leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER),
    content=ft.Text("網路連線不穩定，部分功能可能異常"),
    actions=[ft.TextButton("重試"), ft.TextButton("略過")],
    open=True,
)
page.show_dialog(banner)
```

### BottomSheet

```python
sheet = ft.BottomSheet(
    content=ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("設定", size=20, weight=ft.FontWeight.BOLD),
                ft.Switch("深色模式", value=False),
                ft.Switch("通知", value=True),
                ft.TextButton("關閉", on_click=lambda _: page.pop_dialog()),
            ],
            tight=True,
        ),
        padding=20,
    ),
    open=True,
    show_drag_handle=True,
    draggable=True,
    scrollable=True,
)
page.show_dialog(sheet)
```

---

## 重要發現與注意事項

### 1. page.show_dialog() vs open 屬性

所有 `DialogControl` 子類都有 `open` 屬性，但**顯示方式有兩種**：
- `AlertDialog`/`Banner`/`BottomSheet`：可單純設 `open=True`，或搭配 `page.show_dialog()`
- **SnackBar**：**必須用 `page.show_dialog()`**，不能只靠 `open=True`

### 2. page.show_dialog() / page.pop_dialog()

兩者是 `flet.Page` 的方法，用於管理對話框棧：
- `page.show_dialog(dlg)`：將 dialog 加入 overlay 並顯示
- `page.pop_dialog()`：移除最上層的 dialog

### 3. modal 行為差異

| 控制項 | modal 支援 | 預設行為 |
|--------|-----------|---------|
| AlertDialog | `modal=True/False`（可設） | `False`（可點外關閉） |
| BottomSheet | 無此參數（永遠 modal） | 永遠阻擋互動 |
| Banner | 無（始終 non-modal） | 不阻擋互動 |
| SnackBar | 無（始終 non-modal） | 不阻擋互動 |

### 4. 驗證時機

所有控制項的 `before_update()` 會在屬性變更前自動執行驗證（不是建立時）：
- `AlertDialog`：至少要有一個顯示元素
- `SnackBar`：`content` 不可為隱藏控制項
- `Banner`：`actions` 至少要有一個可見按鈕
- `BottomSheet`：`content` 不可為 `None`

### 5. 動畫與開關

- `BottomSheet` 可透過 `animation_style` 自訂動畫
- SnackBar 的 `dismiss_direction` 控制滑動手勢方向
- `Banner` 無動畫，為立即顯示/消失
