# Flet 0.82.2 導航與 AppBar — 學習筆記

> 來源：`.venv\Lib\site-packages\flet\controls\`  
> 行號對照各 source 檔案。

---

## AppBar

**檔案**：`flet/controls/material/app_bar.py`

### 重要屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `title` | `StrOrControl` | 主標題，通常放 `Text`（第 37 行） |
| `leading` | `Control` | 左側控制項，常放 `Icon` 或 `IconButton`（第 23 行） |
| `leading_width` | `Number` | leading 的寬度（第 27 行） |
| `automatically_imply_leading` | `bool` | 若 `leading=None` 是否自動產生一個（第 31 行，預設 `True`） |
| `actions` | `list[Control]` | 標題右側的控制項列表，常放 `IconButton` 或 `PopupMenuButton`（第 107 行） |
| `center_title` | `bool` | title 是否居中（第 43 行） |
| `toolbar_height` | `Number` | 工具列高度（第 47 行） |
| `bgcolor` | `ColorValue` | 背景顏色（第 59 行） |
| `color` | `ColorValue` | toolbar 內文字/圖示的預設顏色（第 52 行） |
| `elevation` | `Number` | 陰影高度，僅 Material 2 有效（第 65 行） |
| `elevation_on_scroll` | `Number` | 滾動時的陰影高度（第 70 行） |
| `shadow_color` | `ColorValue` | 陰影顏色（第 78 行） |
| `toolbar_opacity` | `Number` | 工具列透明度，0.0~1.0（第 119 行） |
| `toolbar_text_style` | `TextStyle` | leading/actions 的文字樣式（第 129 行） |
| `title_text_style` | `TextStyle` | title 的文字樣式（第 125 行） |
| `actions_padding` | `PaddingValue` | actions 與右側邊緣的間距（第 111 行） |
| `title_spacing` | `Number` | title 左右間距，可設 0 讓 title 吃滿剩餘空間（第 98 行） |
| `shape` | `OutlinedBorder` | AppBar 的形狀（第 133 行） |
| `secondary` | `bool` | 是否為非頂層的 secondary AppBar（第 90 行） |
| `clip_behavior` | `ClipBehavior` | 內容裁切行為（第 82 行） |
| `force_material_transparency` | `bool` | 強制透明，會移除 bgcolor/elevation 視覺效果（第 85 行） |
| `exclude_header_semantics` | `bool` | title 是否包在 Semantics 裡（第 101 行） |

### 驗證規則（`before_update`，第 136-148 行）

- `elevation` >= 0，否則拋 `ValueError`
- `elevation_on_scroll` >= 0
- `toolbar_opacity` 必須在 0.0~1.0 範圍內

### 如何自訂

```python
ft.AppBar(
    leading=ft.IconButton(ft.Icons.MENU, on_click=...),
    title=ft.Text("我的標題", style=ft.TextStyle(size=20)),
    center_title=True,
    bgcolor=ft.Colors.SURFACE_CONTAINER,
    toolbar_height=56,
    actions=[
        ft.IconButton(ft.Icons.SEARCH),
        ft.PopupMenuButton(items=[...])
    ],
    actions_padding=10,
)
```

---

## NavigationBar

**檔案**：`flet/controls/material/navigation_bar.py`

### NavigationBarDestination（第 44-91 行）

每個導航列項目，用 `NavigationBarDestination` 建立。

| 屬性 | 說明 |
|------|------|
| `icon` | 未選中時顯示的 icon，可為字串名稱或 `Control`（第 48 行） |
| `selected_icon` | 選中時顯示的 icon（第 60 行） |
| `label` | 圖示下方的文字標籤（第 55 行） |
| `bgcolor` | 該項目的背景顏色（第 80 行） |

### NavigationBar 本體

| 屬性 | 說明 |
|------|------|
| `destinations` | `list[NavigationBarDestination]`，至少 2 個可見項目（第 107 行） |
| `selected_index` | 目前選中的目的地索引，預設 0（第 114 行） |
| `on_change` | 選中項目改變時觸發的事件 handler（第 140 行） |
| `label_behavior` | 標籤顯示行為：`ALWAYS_SHOW` / `ALWAYS_HIDE` / `ONLY_SHOW_SELECTED`（枚舉第 8-16 行） |
| `indicator_color` | 選中指示器的顏色（第 133 行） |
| `indicator_shape` | 選中指示器的形狀（第 136 行） |
| `bgcolor` | 整個導航列的背景色（第 118 行） |
| `elevation` | 陰影高度（第 126 行） |
| `shadow_color` | 陰影顏色（第 129 行） |
| `animation_duration` | 選中切換動畫時間（第 138 行） |
| `label_padding` | 標籤內邊距（第 123 行） |
| `border` | 導航列邊框（第 136 行） |
| `overlay_color` | HOVERED/PRESSED/FOCUSED 狀態的顏色（第 141 行） |

### 驗證規則

- `destinations` 至少要有 **2 個可見** 控制項（第 149-154 行）
- `selected_index` 必須在 `0` 到 `visible_destinations_count - 1` 範圍內

```python
ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(
            icon=ft.Icons.HOME_OUTLINED,
            selected_icon=ft.Icons.HOME,
            label="首頁"
        ),
        ft.NavigationBarDestination(
            icon=ft.Icons.SETTINGS_OUTLINED,
            selected_icon=ft.Icons.SETTINGS,
            label="設定"
        ),
    ],
    selected_index=0,
    on_change=lambda e: print(f"切換到 {e.control.selected_index}"),
    label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED,
)
```

---

## Tabs

**檔案**：`flet/controls/material/tabs.py`

### 三個主要類

| 類別 | 職責 | 行號 |
|------|------|------|
| `Tabs` | 容器，管理 `selected_index`、動畫、`on_change` | 第 127 行 |
| `Tab` | 個別 Tab 項目（標籤），放在 `TabBar.tabs` 裡 | 第 297 行 |
| `TabBar` | 純粹的標籤列（含 indicator 設定） | 第 203 行 |
| `TabBarView` | 內容區，和 `Tab` 一一對應 | 第 162 行 |

> **重要：實際使用 `Tabs` 時，`Tab` 是放在 `TabBar.tabs` 裡還是在 `Tabs.content` 裡？**  
> 從架構看，`Tabs` 是 layout control（第 127 行），其 `content` 屬性放 `TabBarView`，`Tab` 本身在 `TabBar.tabs` 裡。兩者是分開的，TabBar 控制 tab 頭，TabBarView 控制內容。

### Tab（第 297-342 行）

| 屬性 | 說明 |
|------|------|
| `label` | Tab 顯示文字，可為 `str` 或 `Control`（第 305 行） |
| `icon` | label 左側的 icon（第 311 行） |
| `height` | Tab 高度，有 icon+label 預設 72px，只有 label 預設 46px（第 317 行） |
| `icon_margin` | icon 周圍的 margin（第 325 行） |

- **至少要有 `label` 或 `icon` 其中之一**（`before_update` 驗證）

### TabAlignment（第 8-35 行）

| 值 | 說明 |
|----|------|
| `START` | 靠左對齊（可滾動時） |
| `START_OFFSET` | 靠左加 52px offset |
| `FILL` | 伸展填滿（不可滾動時） |
| `CENTER` | 居中 |

### TabBarIndicatorSize（第 50-65 行）

| 值 | 說明 |
|----|------|
| `TAB` | indicator 寬度 = 整個 tab 的寬度（上一 tab 右邊緣到下一 tab 左邊緣） |
| `LABEL` | indicator 寬度 = tab widget 本身寬度（僅含 label/icon） |

### Tabs 類別（第 127-157 行）

| 屬性 | 說明 |
|------|------|
| `content` | 需為 `TabBarView`，放實際內容（第 132 行） |
| `length` | Tab 總數，必須與 `TabBar.tabs` 和 `TabBarView.controls` 长度一致（第 137 行） |
| `selected_index` | 目前選中索引，支援負索引（第 148 行） |
| `animation_duration` | 動畫持續時間，預設 100ms（第 154 行） |
| `on_change` | 選中改變時回呼，`e.data` 包含新索引（第 160 行） |

```python
# TabBar + TabBarView + Tabs 完整範例
tabs = ft.Tabs(
    selected_index=0,
    length=3,
    animation_duration=100,
    on_change=lambda e: print(f"切換到 {e.data}"),
    content=ft.TabBarView(
        controls=[
            ft.Text("內容 1"),
            ft.Text("內容 2"),
            ft.Text("內容 3"),
        ]
    ),
)

# TabBar 要另外放（通常在 AppBar 或單獨區域）
tab_bar = ft.TabBar(
    tabs=[
        ft.Tab(label="Tab 1", icon=ft.Icons.HOME),
        ft.Tab(label="Tab 2", icon=ft.Icons.SETTINGS),
        ft.Tab(label="Tab 3", icon=ft.Icons.INFO),
    ],
    scrollable=True,
    tab_alignment=ft.TabAlignment.START,
    indicator_color=ft.Colors.PRIMARY,
)
```

---

## NavigationDrawer

**檔案**：`flet/controls/material/navigation_drawer.py`

### NavigationDrawerDestination（第 38-85 行）

和 `NavigationBarDestination` 幾乎相同，但無 `adaptive`（因為是 Control 不是 AdaptiveControl）。

| 屬性 | 說明 |
|------|------|
| `label` | 文字標籤（第 44 行） |
| `icon` | 未選中時的 icon（第 52 行） |
| `selected_icon` | 選中時的 icon（第 64 行） |
| `bgcolor` | 該項目背景色（第 80 行） |

### NavigationDrawer 本體（第 95-154 行）

| 屬性 | 說明 |
|------|------|
| `controls` | 列表，可放 `NavigationDrawerDestination` 或其他控制項如標題、分隔線（第 104 行） |
| `selected_index` | 目前選中目的地，整數；`-1` 表示全部不選中（第 112 行） |
| `on_change` | 選中改變時回呼（第 130 行） |
| `on_dismiss` | 關閉抽屜時回呼（第 136 行） |
| `bgcolor` | 抽屜背景色（第 116 行） |
| `elevation` | 陰影高度（第 120 行） |
| `indicator_color` | 選中指示器顏色（第 124 行） |
| `indicator_shape` | 選中指示器形狀（第 127 行） |
| `shadow_color` | 陰影顏色（第 131 行） |
| `tile_padding` | 項目內邊距（第 137 行） |

### 如何開 / 關

在 `View` 層級透過 method 控制：

```python
# view 是目標 View 實例
await view.show_drawer()          # 開 drawer（從左側滑入）
await view.close_drawer()         # 關 drawer

await view.show_end_drawer()      # 開 end_drawer（從右側滑入）
await view.close_end_drawer()     # 關 end_drawer
```

### 在 View 中設定

```python
page.add(
    ft.Text("Hello"),
)

page.drawer = ft.NavigationDrawer(
    controls=[
        ft.NavigationDrawerDestination(label="首頁", icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME),
        ft.NavigationDrawerDestination(label="設定", icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS),
        ft.Divider(),
        ft.NavigationDrawerDestination(label="關於", icon=ft.Icons.INFO_OUTLINED),
    ],
    selected_index=0,
    on_change=lambda e: print(f"選擇了 {e.control.selected_index}"),
)

page.end_drawer = ft.NavigationDrawer(
    # 從右側滑入的抽屜
    controls=[...],
)
```

---

## View（基礎堆疊）

**檔案**：`flet/controls/core/view.py`

### 重要定位

- `View` 是所有控制項的**最頂層容器**（第 57 行）
- 從 layout 角度，`View` 等同於 `Column`（第 61 行說明）
- Session 開始時自動建立 root view

### 重要屬性

| 屬性 | 說明 |
|------|------|
| `controls` | `list[BaseControl]`，放所有子控制項（第 65 行） |
| `route` | 視圖路由，預設 `/`（第 71 行） |
| `appbar` | 頁面頂部的 `AppBar` 或 `CupertinoAppBar`（第 77 行） |
| `bottom_appbar` | 頁面底部的 `BottomAppBar`（第 83 行） |
| `navigation_bar` | 底部的 `NavigationBar` 或 `CupertinoNavigationBar`（第 95 行） |
| `drawer` | 左側滑入的 `NavigationDrawer`（第 100 行） |
| `end_drawer` | 右側滑入的 `NavigationDrawer`（第 106 行） |
| `floating_action_button` | FAB（第 88 行） |
| `floating_action_button_location` | FAB 位置（第 92 行） |
| `vertical_alignment` | 子控制項的垂直對齊（`MainAxisAlignment`，預設 `START`）（第 110 行） |
| `horizontal_alignment` | 子控制項的水平對齊（`CrossAxisAlignment`，預設 `START`）（第 115 行） |
| `spacing` | 控制項間的垂直間距，預設 10（第 120 行） |
| `padding` | 頁面邊緣與內容的間距，預設 `Padding.all(10)`（第 128 行） |
| `bgcolor` | 背景色（第 133 行） |
| `decoration` | 背景裝飾（`BoxDecoration`，可畫邊框/漸層等）（第 138 行） |
| `foreground_decoration` | 前景裝飾（第 143 行） |
| `fullscreen_dialog` | 是否為全屏對話框（第 148 行） |
| `can_pop` | 是否允許 pop（第 153 行） |
| `on_confirm_pop` | pop 確認回呼，可呼叫 `confirm_pop()`（第 158 行） |

### 抽屜控制 method

```python
await view.show_drawer()          # 第 175 行：顯示左側 drawer
await view.close_drawer()         # 第 183 行：關閉左側 drawer
await view.show_end_drawer()      # 第 191 行：顯示右側 end_drawer
await view.close_end_drawer()     # 第 199 行：關閉右側 end_drawer
```

### pop 確認

```python
async def on_back(e: ft.ViewEvent):
    await e.control.confirm_pop(should_pop=True)  # 允許返回
    # 或
    await e.control.confirm_pop(should_pop=False)  # 取消返回

view.on_confirm_pop = on_back
```

---

## 常用程式碼範例

### 基本頁面含 AppBar + NavigationBar

```python
import flet as ft

def main(page: ft.Page):
    def on_nav_change(e):
        print(f"切換到索引: {e.control.selected_index}")

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="首頁"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SEARCH,
                selected_icon=ft.Icons.SEARCH,
                label="搜尋"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="設定"
            ),
        ],
        selected_index=0,
        on_change=on_nav_change,
    )

ft.app(target=main)
```

### 含 Drawer 的完整視圖

```python
def main(page: ft.Page):
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(label="首頁", icon=ft.Icons.HOME_OUTLINED),
            ft.NavigationDrawerDestination(label="設定", icon=ft.Icons.SETTINGS_OUTLINED),
        ],
        on_change=lambda e: print(f"drawer 選擇: {e.control.selected_index}"),
    )

    page.add(ft.Text("請按左上角 MENU 開啟抽屜"))

    # 在某處開/關 drawer
    # await page.views[-1].show_drawer()
    # await page.views[-1].close_drawer()
```

### Tabs 範例（Tabs + TabBar + TabBarView）

```python
def main(page: ft.Page):
    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="聊天", icon=ft.Icons.CHAT),
            ft.Tab(label="通話", icon=ft.Icons.CALL),
            ft.Tab(label="設定", icon=ft.Icons.SETTINGS),
        ],
        scrollable=True,
        indicator_color=ft.Colors.PRIMARY,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("我的 App"),
        actions=[ft.IconButton(ft.Icons.MORE_VERT)],
    )

    tabs = ft.Tabs(
        length=3,
        selected_index=0,
        content=ft.TabBarView(
            controls=[
                ft.Text("聊天內容"),
                ft.Text("通話內容"),
                ft.Text("設定內容"),
            ]
        ),
    )

    page.add(tab_bar, tabs)
```

### AppBar + BottomAppBar + FAB

```python
page.appbar = ft.AppBar(
    title=ft.Text("Dashboard"),
    center_title=True,
    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
    actions=[
        ft.IconButton(ft.Icons.NOTIFICATIONS),
        ft.IconButton(ft.Icons.SETTINGS),
    ],
)

page.floating_action_button = ft.FloatingActionButton(
    icon=ft.Icons.ADD,
    on_click=lambda _: print("FAB clicked"),
)

page.bottom_appbar = ft.BottomAppBar(
    content=ft.Row([...]),
)
```

---

## 重要發現與注意事項

1. **View 的 `controls` 是 `list[BaseControl]`**，繼承自 `Column` 的行為，元素由上往下排列（`vertical_alignment` 預設 `START`）。

2. **AppBar 的 `leading`**：若設為 `None` 且 `automatically_imply_leading=True`，Flet 會自動幫你產生一個。但若不想顯示 leading，又希望 title 吃掉 leading 的空間，設 `leading=None` + `automatically_imply_leading=False`。

3. **AppBar `toolbar_height`**：預設取決於平台與 Theme，若需要精確高度才自訂。

4. **NavigationBar 的 `destinations`**：`before_update` 驗證至少要有 **2 個可見** 項目。隱藏項目（`visible=False`）不計入。

5. **NavigationBar `selected_index`**：若設超出範圍，`before_update` 會拋 `IndexError`。

6. **Tabs 架構拆分**：`Tabs`（管理狀態）、`TabBar`（純標頭）、`TabBarView`（純內容）是三個獨立的類，需手動同步 `length`、`tabs` 數量、`controls` 數量。忘記同步會導致 `ValueError` 或顯示錯誤。

7. **Tab `label` 或 `icon` 至少要一個**：`before_update` 驗證，兩者都為 `None` 會拋 `ValueError`。

8. **NavigationDrawer 的 `selected_index=-1`**：是一個特殊值，表示**全部不選中**（和 NavigationBar 不同）。

9. **View 的 `drawer` vs `end_drawer`**：前者從左側滑入，後者從右側滑入。兩個可以同時存在。

10. **`view.show_drawer()` 是 async method**：必須 `await view.show_drawer()`，否則不會執行。

11. **View 的 `confirm_pop`**：用於自定義返回確認對話框，必須在被 pop 之前呼叫，否則前端超時後 pop 會被取消。

12. **`View.init()` 會設定 `host_expanded=True`**（第 169 行）：這讓 view 填滿整個可用的空間，這是 View 和普通 Column 的關鍵差異。
