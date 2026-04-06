# Flet 套件學習筆記（v0.28.3）

> 學習日期：2026-03-15
> 版本：0.28.3

---

## 1. 核心架構

### 1.1 模組結構

```
flet/
├── core/           # 核心 UI 元件（約 150+ 檔案）
│   ├── control.py       # 所有控制項基類
│   ├── page.py          # 頁面物件
│   ├── navigation_rail.py
│   ├── tabs.py
│   ├── container.py
│   ├── snack_bar.py
│   └── ...（150+ 個 UI 元件）
├── auth/          # 認證相關
├── canvas/        # 畫布
├── map/           # 地圖
├── security/      # 安全
└── utils/        # 工具
```

### 1.2 類別繼承層級

```
Control (基類)
├── ConstrainedControl
│   ├── NavigationRail
│   ├── Tabs
│   ├── Container
│   └── ...（大部分複雜元件）
├── AdaptiveControl
│   ├── Tab
│   └── ...
├── 其他獨立元件
    ├── TextField
    ├── Button 系列
    ├── ListView
    └── ...
```

---

## 2. 重要發現（與模型記憶差異）

### 2.1 Keyboard Event

**✅ 正確認知**：
- Flet 支援鍵盤事件透過 `page.on_keyboard_event`

**⚠️ 差異點**：
```python
# 正確用法
def main(page: ft.Page):
    def on_keyboard(e: ft.KeyboardEvent):
        print(f"Key: {e.key}, Ctrl: {e.ctrl}, Shift: {e.shift}")
    
    page.on_keyboard_event = on_keyboard

# KeyboardEvent 屬性：
# - key: str           # 按鍵名稱
# - shift: bool        # Shift 是否按下
# - ctrl: bool         # Ctrl 是否按下
# - alt: bool          # Alt 是否按下
# - meta: bool         # Meta (Cmd/Win) 是否按下
```

### 2.2 SnackBar 用法

**✅ 正確認知**：
- 需要將 SnackBar 加入 page.overlay
- 使用 `open` 屬性控制顯示

**⚠️ 差異點**：
```python
# 正確用法（專案中的用法是對的）
snack = ft.SnackBar(ft.Text(message), bgcolor=color)
page.overlay.append(snack)
snack.open = True
page.update()

# 但更好的方式是直接設定 page.snack_bar
page.snack_bar = ft.SnackBar(content=ft.Text("Hello"))
page.snack_bar.open = True
page.update()
```

### 2.3 NavigationRail

**⚠️ 差異點**：
- `on_change` 事件回傳的物件：`e.control` 是 NavigationRail 本身
- `e.control.selected_index` 可以取得當前選取索引
- 專案中使用 `e.control.selected_index` 是正確的

```python
# 正確用法
rail = ft.NavigationRail(
    selected_index=0,
    destinations=[...],
    on_change=lambda e: print(f"Selected: {e.control.selected_index}")
)
```

### 2.4 Tabs / Tab

**⚠️ 差異點**：
- `Tab` 繼承自 `AdaptiveControl`，不是直接繼承 `Control`
- `on_change` 回傳 `e.control` 是 Tabs 本身
- `e.control.selected_index` 取得當前標籤索引
- 專案中使用 `on_change=self._on_tab_change` 是正確的

### 2.5 Control 的可見性控制

**✅ 正確認知**：
- `visible` 屬性控制可見性
- `disabled` 屬性控制禁用狀態

**⚠️ 差異點**：
```python
# 不要用 display: none 方式隱藏，用 visible
container.visible = False  # 正確
container.opacity = 0      # 也可以但不是最佳實踐
```

### 2.6 page.update() 時機

**⚠️ 重要發現**：
- 所有 UI 變更後都需要 `page.update()` 才會渲染
- Control 的 `update()` 方法實際上是呼叫 `self.page.update(self)`
- 在 `did_mount` 中不應該立即呼叫 `page.update()`，因為頁面尚未完全初始化

---

## 3. 專案特定用法驗證

### 3.1 TranslationView 用法正確性

| 用法 | 狀態 | 說明 |
|------|------|------|
| `ft.Column(expand=True, spacing=16)` | ✅ 正確 | expand 屬性可用 |
| `ft.Container(content=..., expand=True)` | ✅ 正確 | Container expand 用法正確 |
| `page.overlay.append(file_picker)` | ✅ 正確 | FilePicker 需要加入 overlay |
| `ft.Tabs` + `ft.Tab` | ✅ 正確 | 用法符合官方 API |
| `on_change=lambda e: ...` | ✅ 正確 | 事件處理正確 |

### 3.2 CacheView 用法正確性

| 用法 | 狀態 | 說明 |
|------|------|------|
| `ft.ListView(expand=True, auto_scroll=True)` | ✅ 正確 | ListView expand 用法正確 |
| `ft.DataTable` | ✅ 正確 | 用法正確 |
| `ft.Stack` + 浮動視窗 | ✅ 正確 | Stack 用於疊加元素 |
| `ft.ExpansionTile` | ✅ 正確 | 展開式列表用法正確 |
| `ft.GestureDetector` + `on_pan_update` | ✅ 正確 | 拖曳功能正確實作 |

---

## 4. 常見陷阱

### 4.1 屬性大小寫

Flet 使用駝峰命名法（camelCase）轉換為 Python 的蛇形命名（snake_case）：
- `selectedIndex` → `selected_index`
- `minWidth` → `min_width`
- `onChange` → `on_change`

### 4.2 expand 屬性

```python
# expand 可以是 bool 或 int
expand=True      # 佔用 1 份可用空間
expand=3         # 佔用 3 份可用空間
expand=False     # 不擴展（預設）
```

### 4.3 on_click vs on_change

- `on_click`：點擊事件（Button, IconButton 等）
- `on_change`：值變更事件（Dropdown, Tabs, Radio 等）

---

## 5. 需要更新的記憶

### 5.1 KeyboardEvent 屬性

```
舊認知：可能只有 key 和 code
新認知：key, shift, ctrl, alt, meta 五個屬性
```

### 5.2 SnackBar 最佳實踐

```
舊認知：在 overlay 中手動管理
新認知：可使用 page.snack_bar = ... 的簡便方式
```

### 5.3 Control 生命周期

```
舊認知：不清楚 did_mount 時機
新認知：did_mount 在控制項添加到頁面後調用
```

---

## 6. 後續修改時的注意事項

1. **修改 NavigationRail**：
   - 確認 `destinations` 是 `List[NavigationRailDestination]`
   - `selected_index` 從 0 開始

2. **修改 Tabs**：
   - `tabs` 屬性是 `List[Tab]`
   - 每個 Tab 的 `content` 可以是任何 Control

3. **自定義事件處理**：
   - 使用 `_add_event_handler` 註冊事件
   - 使用 `_get_event_handler` 取得處理函式

4. **屬性設置**：
   - 使用 `_set_attr(name, value)` 設置屬性
   - 使用 `_get_attr(name, def_value)` 取得屬性

---

## 7. 驗證指令

修改 UI 後可用以下方式驗證語法：

```python
# 語法檢查
python -c "import flet as ft; print(ft.__version__)"

# 驗證 Control 實例
print(isinstance(control, ft.Control))

# 驗證屬性
print(control._get_attr('expand'))
```

---

## 8. 常見 Bug 與解決方案（2026-03-15 實戰經驗）

### 8.1 顏色問題
- ❌ `Colors.SURFACE_VARIANT` - 不存在
- ✅ `Colors.SURFACE` / `Colors.ON_SURFACE_VARIANT`

### 8.2 NavigationRail
- leading 屬性不支持複雜嵌套（Column 等），會導致圖標不顯示

### 8.3 分頁功能
- 分頁函數必須調用：
  1. `_render_xxx()` 渲染函數
  2. `self.update()` 更新自身
  3. `self.page.update()` 更新頁面
- 狀態必須同步：`self.xxx` 和 `self._state.xxx` 都要更新
- 防止重複點擊：添加渲染標誌（如 `_is_xxx_rendering`）

### 8.4 可見性設置
- 設置 `visible` 後必須調用 `page.update()` 否則不生效

### 8.5 編碼問題
- 文件開頭有 BOM（\ufeff）會導致 SyntaxError
- 修復：使用 `utf-8-sig` 編碼讀取後用 `utf-8` 寫入
