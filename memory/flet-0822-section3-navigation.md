# Flet 0.82.2 Navigation 控制項完整整理

> version: flet:0.82.2
> 整理日期：2026-03-22
> 資料來源：https://docs.flet.dev （官方文件即時抓取）

---

## 目錄

1. [NavigationRail](#1-navigationrail)
2. [NavigationBar](#2-navigationbar)
3. [NavigationBarDestination](#3-navigationbardestination)
4. [Tabs](#4-tabs)
5. [TabBar](#5-tabbar)
6. [Tab](#6-tab)
7. [Pagelet](#7-pagelet)
8. [Navigation 與 Routing 機制](#8-navigation-與-routing-機制)
9. [Navigation 新舊版差異（0.28.3 vs 0.82.2）](#9-navigation-新舊版差異0283-vs-0822)

---

## 1. NavigationRail

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `selected_index` | `int \| None` | 目前選中的 destination 索引 |
| `destinations` | `list[NavigationRailDestination]` | 導航項目清單（至少 2 個） |
| `extended` | `bool` | 是否展開標籤文字（預設 False） |
| `label_type` | `NavigationRailLabelType` | 標籤顯示模式：ALL / SELECTED / NONE |
| `leading` | `Control \| None` | 頂部（上方）自訂控制項，如 FAB |
| `trailing` | `Control \| None` | 底部（下方）自訂控制項 |
| `min_width` | `Number` | 未展開時最小寬度 |
| `min_extended_width` | `Number` | 展開時最大寬度 |
| `use_indicator` | `bool` | 是否顯示選中指示器（圓角背景） |
| `indicator_color` | `ColorValue \| None` | 指示器顏色 |
| `indicator_shape` | `OutlinedBorder \| None` | 指示器形狀 |
| `selected_label_text_style` | `TextStyle \| None` | 選中標籤樣式 |
| `unselected_label_text_style` | `TextStyle \| None` | 未選中標籤樣式 |
| `group_alignment` | `Number` | destinations 垂直對齊（預設 -0.9） |
| `elevation` | `Number \| None` | 陰影大小 |
| `bgcolor` | `ColorValue \| None` | 整體背景色 |

### 主要事件

| 事件 | 說明 |
|------|------|
| `on_change` | 選中項目改變時觸發，回傳 `e.control.selected_index` |

### 用法範例

```python
rail = ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=100,
    min_extended_width=400,
    leading=ft.FloatingActionButton(icon=ft.Icons.CREATE, content="Add"),
    destinations=[
        ft.NavigationRailDestination(
            icon=ft.Icons.FAVORITE_BORDER,
            selected_icon=ft.Icons.FAVORITE,
            label="First",
        ),
        ft.NavigationRailDestination(
            icon=ft.Icons.SETTINGS_OUTLINED,
            selected_icon=ft.Icons.SETTINGS,
            label="Settings",
        ),
    ],
    on_change=lambda e: print("Selected:", e.control.selected_index),
)
```

### 與 0.28.3 差異

- ✅ NavigationRail 在 0.28.3 已存在，屬性大致相同
- ❓ `group_alignment`、`min_extended_width`、`use_indicator` 等進階屬性是否在 0.28.3 就有，需要進一步確認
- ⚠️ 0.82.2 API 文件說 `Inherits: LayoutControl`，0.28.3 可能繼承鏈不同

---

## 2. NavigationBar

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `destinations` | `list[NavigationBarDestination]` | 導航項目清單（至少 2 個） |
| `selected_index` | `int` | 目前選中的 destination 索引 |
| `label_behavior` | `NavigationBarLabelBehavior` | 標籤顯示行為：ALWAYS_SHOW / SELECTED / etc. |
| `animation_duration` | `DurationValue \| None` | 選中過渡動畫時長 |
| `indicator_color` | `ColorValue \| None` | 選中指示器顏色 |
| `indicator_shape` | `OutlinedBorder \| None` | 指示器形狀 |
| `elevation` | `Number \| None` | 陰影大小 |
| `bgcolor` | `ColorValue \| None` | 導航欄背景色 |
| `border` | `Border \| None` | 邊框設定 |
| `shadow_color` | `ColorValue \| None` | 陰影顏色 |
| `overlay_color` | `ControlStateValue[ColorValue] \| None` | HOVER / PRESSED / FOCUSED 狀態顏色 |
| `label_padding` | `PaddingValue \| None` | 標籤內距 |

### 主要事件

| 事件 | 說明 |
|------|------|
| `on_change` | 選中項目改變時觸發 |

### 用法範例

```python
page.navigation_bar = ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explore"),
        ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label="Commute"),
        ft.NavigationBarDestination(
            icon=ft.Icons.BOOKMARK_BORDER,
            selected_icon=ft.Icons.BOOKMARK,
            label="Favorites",
        ),
    ]
)
```

### 與 0.28.3 差異

- ✅ NavigationBar 在 0.28.3 已存在
- ❓ `overlay_color`、`border`、`shadow_color`、`label_padding` 是否為 0.82.2 新增，需要進一步確認
- ⚠️ `Inherits: LayoutControl, AdaptiveControl` — 0.28.3 是否也有 AdaptiveControl 需要確認

---

## 3. NavigationBarDestination

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `icon` | `IconDataOrControl` | 未選中時顯示的圖示（名稱或 Control） |
| `selected_icon` | `IconDataOrControl \| None` | 選中時顯示的圖示 |
| `label` | `str \| None` | 圖示下方標籤文字 |
| `bgcolor` | `ColorValue \| None` | 該項目背景色 |

### 用法範例

```python
ft.NavigationBarDestination(
    icon=ft.Icons.BOOKMARK_BORDER,
    selected_icon=ft.Icons.BOOKMARK,
    label="Favorites",
)
```

### 與 0.28.3 差異

- ✅ NavigationBarDestination 在 0.28.3 已存在
- ❓ `bgcolor` 屬性是否為 0.82.2 新增，需要進一步確認

---

## 4. Tabs

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `selected_index` | `int` | 目前選中的 Tab 索引 |
| `length` | `int` | Tab 總數量 |
| `expand` | `bool` | 是否填滿父容器 |
| `content` | `Control` | 通常是 `Column`，內含 `TabBar` + `TabBarView` |

### 用法範例

```python
ft.Tabs(
    selected_index=1,
    length=3,
    expand=True,
    content=ft.Column(
        expand=True,
        controls=[
            ft.TabBar(tabs=[...]),
            ft.TabBarView(controls=[...]),
        ],
    ),
)
```

### ⚠️ 重大改變：Tabs 結構重構（0.28.3 vs 0.82.2）

| 版本 | 結構 |
|------|------|
| **0.28.3** | `Tabs` 直接包含 `Tab` 作為子控制項（`tabs=[ft.Tab(...)]`） |
| **0.82.2** | `Tabs` 是容器，`TabBar` + `TabBarView` 放在 `content` 內 |

**0.82.2 範例（動態新增 Tab）：**

```python
tab_bar.tabs.append(ft.Tab(label=ft.Text(f"Tab {tab_count}")))
tab_view.controls.append(MyContainer(text=f"Tab {tab_count} content"))
tabs.length = len(tab_bar.tabs)  # 必須手動更新 length
```

### 與 0.28.3 差異

- ❌ **結構完全改變**：0.28.3 的 `Tabs` 內建 `tabs=[Tab]` 直接子項；0.82.2 改為必須搭配 `TabBar` + `TabBarView`
- ✅ `selected_index` 和 `expand` 仍保留
- ❌ `tabs` 屬性在 0.82.2 的 `Tabs` 控制項上已不存在（改由 `TabBar.tabs` 提供）

---

## 5. TabBar

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `tabs` | `list[Control]` | Tab 列表（`Tab` 控制項） |
| `tab_alignment` | `TabAlignment` | 對齊方式：START / CENTER / etc. |
| `indicator` | `UnderlineTabIndicator \| None` | 自訂指示器外觀 |
| `indicator_color` | `ColorValue \| None` | 指示器顏色 |
| `indicator_thickness` | `Number` | 指示器厚度 |
| `indicator_size` | `TabBarIndicatorSize` | LABEL（僅文字寬）或 TAB（整格寬） |
| `indicator_animation` | `TabIndicatorAnimation` | 動畫效果：ELASTIC / etc. |
| `scrollable` | `bool` | 是否可橫向滾動 |
| `secondary` | `bool` | 是否為次級巢狀 TabBar |
| `divider_color` | `ColorValue \| None` | 分隔線顏色 |
| `divider_height` | `Number \| None` | 分隔線高度 |
| `label_color` | `ColorValue \| None` | 選中標籤顏色 |
| `unselected_label_color` | `ColorValue \| None` | 未選中標籤顏色 |
| `label_text_style` | `TextStyle \| None` | 選中標籤文字樣式 |
| `unselected_label_text_style` | `TextStyle \| None` | 未選中標籤文字樣式 |
| `label_padding` | `PaddingValue \| None` | 標籤內距 |
| `padding` | `PaddingValue \| None` | TabBar 內距 |
| `mouse_cursor` | `MouseCursor \| None` | 游標樣式 |
| `enable_feedback` | `bool \| None` | 是否提供點擊音效/震動回饋（Android） |
| `overlay_color` | `ControlStateValue[ColorValue] \| None` | HOVER / PRESSED / FOCUSED 顏色 |
| `splash_border_radius` | `BorderRadiusValue \| None` | 點擊漣漪裁剪半徑 |

### 主要事件

| 事件 | 說明 |
|------|------|
| `on_click` | 點擊 Tab 時觸發 |
| `on_hover` | 游標進入/離開 Tab 時觸發（`ft.TabBarHoverEvent`） |

### 用法範例（自訂指示器）

```python
ft.TabBar(
    tab_alignment=ft.TabAlignment.START,
    indicator_animation=ft.TabIndicatorAnimation.ELASTIC,
    indicator_size=ft.TabBarIndicatorSize.LABEL,
    indicator=ft.UnderlineTabIndicator(
        border_side=ft.BorderSide(5, color=ft.Colors.RED),
        border_radius=ft.BorderRadius.all(1),
        insets=ft.Padding.only(bottom=5),
    ),
    tabs=[
        ft.Tab(label=ft.Text("Home")),
        ft.Tab(label=ft.Text("My Account")),
    ],
)
```

### 與 0.28.3 差異

- ❌ TabBar 在 0.28.3 不存在（Tabs 直接內建 Tab）
- ✅ `tabs`、`indicator_color`、`indicator_thickness`、`indicator_size`、`scrollable`、`label_color` 等可能是從 0.28.3 的 Tabs 屬性迁移过来
- ✅ `enable_feedback` — **0.82.2 新增**（Android 音效/震動回饋）
- ✅ `secondary` — **0.82.2 新增**（次級/巢狀 TabBar）
- ✅ `divider_color`、`divider_height` — **0.82.2 新增**

---

## 6. Tab

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `label` | `str \| Control \| None` | Tab 標題（可為文字或自訂 Control） |
| `icon` | `IconData \| None` | Tab 標題旁的圖示 |
| `content` | `Control \| None` | 自訂 Tab 內容（通常不用，內容放 TabBarView） |
| `tab_style` | `TabStyle \| None` | 自訂 Tab 樣式 |
| `visible` | `bool` | 是否顯示（預設 True） |

### 用法範例

```python
ft.Tab(label="Tab 1", icon=ft.Icons.SETTINGS_PHONE)
ft.Tab(label=ft.Text("Custom Label"))
ft.Tab(label=ft.CircleAvatar(foreground_image_src="..."))
```

### 與 0.28.3 差異

- ✅ Tab 控制項在 0.28.3 已存在
- ❓ `tab_style`、`visible` 是否為 0.82.2 新增，需要進一步確認
- ⚠️ 0.28.3 Tab 直接作為 `Tabs.tabs` 的子項；0.82.2 Tab 作為 `TabBar.tabs` 的子項

---

## 7. Pagelet

### 說明
Pagelet 是一個「頁面化區塊」控制項，類似行動應用的單頁結構，內建 AppBar、Drawer、EndDrawer、FAB 支援。

### 主要屬性

| 屬性 | 類型 | 說明 |
|------|------|------|
| `appbar` | `AppBar \| None` | 頂部應用欄 |
| `bottom_appbar` | `BottomAppBar \| None` | 底部應用欄 |
| `drawer` | `NavigationDrawer \| None` | 左側抽屜 |
| `end_drawer` | `NavigationDrawer \| None` | 右側抽屜 |
| `floating_action_button` | `FloatingActionButton \| None` | 浮動按鈕 |
| `floating_action_button_location` | `FloatingActionButtonLocation` | FAB 位置（CENTER_DOCKED 等） |
| `content` | `Control \| None` | 主內容區 |
| `width`, `height` | `Number` | 尺寸 |
| `bgcolor` | `ColorValue \| None` | 背景色 |

### 主要方法（非同步）

| 方法 | 說明 |
|------|------|
| `await pagelet.show_drawer()` | 開啟左側 drawer |
| `await pagelet.close_drawer()` | 關閉左側 drawer |
| `await pagelet.show_end_drawer()` | 開啟右側 end drawer |
| `await pagelet.close_end_drawer()` | 關閉右側 end drawer |

### 用法範例

```python
pagelet := ft.Pagelet(
    width=500,
    height=500,
    appbar=ft.AppBar(title=ft.Text("Pagelet AppBar"), center_title=True),
    content=ft.Text("Pagelet Body"),
    drawer=ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(icon=ft.Icons.ADD_TO_HOME_SCREEN_SHARP, label="Item 1"),
            ft.NavigationDrawerDestination(icon=ft.Icons.ADD_COMMENT, label="Item 2"),
        ],
    ),
    floating_action_button=ft.FloatingActionButton(icon=ft.Icons.ADD, shape=ft.CircleBorder()),
    floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
)

async def handle_show_drawer(e):
    await pagelet.show_drawer()
```

### 與 0.28.3 差異

- ❌ **Pagelet 在 0.28.3 不存在** — 這是 0.82.2 新增的控制項
- ⚠️ 所有 Pagelet API（`show_drawer()`、`close_end_drawer()` 等）都是全新功能
- ✅ Pagelet 可搭配 NavigationDrawer 使用

---

## 8. Navigation 與 Routing 機制

### 核心 API

| API | 說明 |
|-----|------|
| `page.route` | 目前路由字串（如 `/`、`/store`、`/settings/mail`） |
| `page.views` | 目前檢視堆疊（View 物件列表） |
| `page.on_route_change` | 路由改變時的事件處理常式 |
| `page.on_view_pop` | 返回（pop）檢視時的處理常式 |
| `await page.push_route(route, **query_params)` | 程式化導航（可帶 query 參數） |

### 標準路由模式

```python
def main(page: ft.Page):
    page.title = "Routes Example"

    def route_change():
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                controls=[ft.AppBar(title=ft.Text("Home")), ft.Button("Go to settings", on_click=open_settings)],
            )
        )
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    route="/settings",
                    controls=[ft.AppBar(title=ft.Text("Settings")), ft.Text("Settings!")],
                )
            )
        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()  # 初始化
```

### 導航流程

1. **路由變化**（URL 改變 / `push_route` / 瀏覽器返回）
   → 觸發 `page.on_route_change`
2. **`route_change()` 處理常式**
   → 清空 `page.views` → 根據 `page.route` 重新建構視圖堆疊
3. **用戶點擊「返回」**
   → 觸發 `page.on_view_pop` → 移除頂層 View → `push_route` 到新頂層

### 查詢參數

```python
await page.push_route("/search", q="flet", page=2)
# URL 變為 /search?q=flet&page=2
```

### 返回確認（Pop Confirmation）

```python
# 在 View 上設定
view = ft.View(
    route="/editor",
    controls=[...],
    can_pop=False,  # 禁用自動返回
)
view.on_confirm_pop = confirm_discard_fn
```

### 與 0.28.3 差異

- ✅ `page.route`、`page.views`、`page.on_route_change` 在 0.28.3 已存在
- ❓ `page.push_route()` 的 `**query_params` 語法在 0.28.3 是否支援，需要進一步確認
- ❓ `View.can_pop` + `View.on_confirm_pop` 是否在 0.28.3 就有，需要進一步確認

---

## 9. Navigation 新舊版差異（0.28.3 vs 0.82.2）

### 控制項存在感差異

| 控制項 | 0.28.3 | 0.82.2 | 狀態 |
|--------|--------|--------|------|
| NavigationRail | ✅ 存在 | ✅ 存在 | ✅ 已驗證 |
| NavigationBar | ✅ 存在 | ✅ 存在 | ✅ 已驗證 |
| NavigationBarDestination | ✅ 存在 | ✅ 存在 | ✅ 已驗證 |
| Tabs | ✅ 存在（舊結構） | ✅ 存在（**新結構**） | ⚠️ 結構改變 |
| TabBar | ❌ 不存在 | ✅ 存在 | ❌ **0.82.2 新增** |
| Tab | ✅ 存在 | ✅ 存在 | ✅ 已驗證 |
| Pagelet | ❌ 不存在 | ✅ 存在 | ❌ **0.82.2 新增** |
| Routing (page.views/go) | ✅ 存在 | ✅ 存在 | ✅ 已驗證 |
| page.push_route() | ⚠️ 待確認 | ✅ 存在 | ❓ 待驗證 |

### 破壞性變更：Tabs 結構

**0.28.3（舊）：**
```python
ft.Tabs(
    tabs=[
        ft.Tab(label="Tab 1", content=ft.Text("Content 1")),
        ft.Tab(label="Tab 2", content=ft.Text("Content 2")),
    ]
)
```

**0.82.2（新）：**
```python
ft.Tabs(
    length=2,
    content=ft.Column(
        controls=[
            ft.TabBar(tabs=[
                ft.Tab(label="Tab 1"),
                ft.Tab(label="Tab 2"),
            ]),
            ft.TabBarView(controls=[
                ft.Text("Content 1"),
                ft.Text("Content 2"),
            ]),
        ],
    ),
)
```

### 0.82.2 全新功能清單

| 功能 | 說明 |
|------|------|
| **Pagelet** | 內建 AppBar + Drawer + FAB 的頁面區塊控制項，async drawer API |
| **TabBar** | 獨立的 Tab 列控制項，脫離 Tabs 本身 |
| **enable_feedback** | TabBar 新增，Android 觸控回饋音效/震動 |
| **secondary** | TabBar 新增，次級/巢狀 TabBar 支援 |
| **divider_color/divider_height** | TabBar 新增分隔線設定 |
| **overlay_color** | NavigationBar、TabBar 新增狀態顏色 |
| **border / shadow_color** | NavigationBar 新增 |
| **label_padding** | NavigationBar 新增 |

### 驗證清單

#### ✅ 已驗證（來自官方文件）

- [x] NavigationRail 主要屬性（selected_index, destinations, extended, label_type, leading, trailing）
- [x] NavigationBar 主要屬性（destinations, selected_index, label_behavior, indicator_color）
- [x] NavigationBarDestination 主要屬性（icon, selected_icon, label）
- [x] TabBar 屬性清單（indicator, indicator_animation, indicator_size, scrollable, secondary）
- [x] Tab 主要屬性（label, icon, content）
- [x] Pagelet 結構與 async drawer 方法
- [x] Routing 機制（page.route, page.views, on_route_change, on_view_pop）
- [x] page.push_route() + query 參數
- [x] Tabs 新結構（Tabs + TabBar + TabBarView 三層）
- [x] UnderlineTabIndicator 自訂指示器

#### ❌ 待驗證（需要實際測試或查舊文件）

- [ ] NavigationRail 在 0.28.3 是否已存在（推測：是，但需確認）
- [ ] NavigationRail `group_alignment`、`use_indicator`、`min_extended_width` 是否 0.28.3 就有
- [ ] NavigationBar `overlay_color`、`border`、`shadow_color` 是否 0.28.3 就有
- [ ] NavigationBarDestination `bgcolor` 是否 0.28.3 就有
- [ ] Tab `tab_style`、`visible` 是否 0.28.3 就有
- [ ] `page.push_route()` 在 0.28.3 是否已存在
- [ ] `View.can_pop` + `View.on_confirm_pop` 在 0.28.3 是否已存在
- [ ] `page.on_view_pop` 在 0.28.3 的事件參數型別是否與 0.82.2 相同

---

## 快速參考：Migration 0.28.3 → 0.82.2

### Tabs 重構（最關鍵）

```
舊（0.28.3）：
  ft.Tabs(tabs=[ft.Tab(label="A", content=...)])

新（0.82.2）：
  ft.Tabs(
      length=N,
      content=ft.Column(controls=[
          ft.TabBar(tabs=[ft.Tab(label="A"), ft.Tab(label="B")]),
          ft.TabBarView(controls=[Container("A content"), Container("B content")]),
      ])
  )
```

### Pagelet（新功能）

```python
# 0.28.3 沒有 Pagelet，需要手動組合 AppBar + Container + Drawer
# 0.82.2 可直接使用 Pagelet
ft.Pagelet(
    appbar=...,
    drawer=...,
    floating_action_button=...,
    content=...,
)
# drawer 控制：await pagelet.show_drawer()
```

---

*最後更新：2026-03-22*
