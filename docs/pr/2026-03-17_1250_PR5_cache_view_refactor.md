# PR 設計：Cache View 重構 + UI 流暢性優化

> 設計日期：2026-03-17
> 狀態：待審核

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行數 | 驗證方式 | 確認結果 |
|------|------|----------|----------|
| `app/views/cache_view.py` | 3064 | line count | ✅ 單一檔案過大 |
| `app/views/cache_manager/` | 9 個檔案 | dir listing | ✅ 已分離幫手類 |
| `app/views/cache/` | 空目錄 | dir listing | ✅ 準備放置新 View |
| `app/view_registry.py` | - | Select-String | ✅ cache 對應 `CacheView` |

### 1.2 現有架構

```
app/views/
├── cache_view.py          # 3064 行（太大）
├── cache_manager/         # 幫手類目錄
│   ├── cache_actions.py
│   ├── cache_controller.py
│   ├── cache_history_store.py
│   ├── cache_overview_panel.py
│   ├── cache_presenter.py
│   ├── cache_state.py
│   └── ...
└── cache/                 # 空目錄（準備放置新 View）
```

### 1.3 現有 UI 技術驗證

| 項目 | 位置 | 驗證結果 |
|------|------|----------|
| ListView + expand | cache_view.py:118, 171 | ✅ 使用 `ft.ListView(expand=True)` |
| ScrollMode.AUTO | cache_view.py:207, 331, 360 | ✅ 使用 `scroll=ft.ScrollMode.AUTO` |
| ScrollMode.ALWAYS | cache_view.py:658 | ✅ 使用 `scroll=ft.ScrollMode.ALWAYS` |
| Column scroll | cache_view.py:707 | ✅ `ft.Column(..., scroll=ft.ScrollMode.AUTO)` |

---

## 二、重構目標

### 2.1 主要目標

1. **拆分 View**：將 3064 行的 `cache_view.py` 拆分為三個獨立 View
2. **UI 流暢**：優化 scroll 體驗，確保流暢操作
3. **視窗自適應**：視窗大小改變時，View 自動調整縮放

### 2.2 拆分後的 View

| View 名稱 | 檔案 | 預估行數 | 職責 |
|-----------|------|----------|------|
| CacheOverviewView | `cache/cache_overview_view.py` | ~600 | 總覽 / 管理 |
| CacheQueryView | `cache/cache_query_view.py` | ~800 | 查詢（唯讀） |
| CacheShardView | `cache/cache_shard_view.py` | ~1000 | 分片編輯 |

---

## 三、UI 流暢性設計

### 3.1 Scrollable 設計原則

根據現有程式碼驗證，採用以下 Flet 技術：

#### A. ListView 最佳實踐

```python
# ✅ 正確：使用 expand + auto_scroll
self.type_list = ft.ListView(
    expand=True,           # 填滿可用空間
    spacing=6,             # 項目間距
    auto_scroll=True,      # 自動捲動到底部
)

# ✅ 正確：結果列表不使用 auto_scroll（避免干擾使用者）
self.query_result_list = ft.ListView(
    expand=True,
    spacing=2,
    auto_scroll=False,     # 保持位置讓使用者閱讀
)
```

#### B. Column Scroll 設計

```python
# ✅ 正確：使用 ScrollMode 列舉
self.query_history_column = ft.Column(
    spacing=4,
    scroll=ft.ScrollMode.AUTO,   # 需要時顯示 scrollbar
)

# ✅ 正確：大型內容區塊使用 ALWAYS
self.shard_detail_column = ft.Column(
    scroll=ft.ScrollMode.ALWAYS,  # 始終顯示 scrollbar
    expand=True,
)
```

#### C. 巢狀滾動容器

```python
# 設計：外層 Column + 內層 ListView
def build_query_page(self):
    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            # 1. 搜尋列（固定不滾動）
            self._build_search_bar(),
            
            # 2. 結果列表（可滾動）
            ft.ListView(
                expand=True,
                controls=[...],
            ),
            
            # 3. 詳情區（可滾動）
            ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[...],
            ),
        ],
    )
```

### 3.2 效能優化

| 技術 | 用途 | 實現方式 |
|------|------|----------|
| Lazy Loading | 按需載入資料 | 每個 View 獨立 did_mount |
| Virtual Scrolling | 大列表效能 | ft.ListView 自動支援 |
| Debounce | 搜尋輸入 | 300ms delay |
| 分頁載入 | 大量結果 | 每次載入 50 筆 |

---

## 四、視窗大小自適應設計

### 4.1 現有視窗尺寸配置（已驗證）

```python
# view_registry.py:13
'cache': (1360, 940),  # 預設寬 x 高
```

### 4.2 自適應策略

#### A. 響應式斷點

```python
# UI 寬度斷點
WINDOW_BREAKPOINT_LARGE = 1400   # 大螢幕
WINDOW_BREAKPOINT_MEDIUM = 1000  # 中螢幕
WINDOW_BREAKPOINT_SMALL = 800    # 小螢幕

# 響應式調整函式
def _get_column_width(page: ft.Page) -> int:
    """根據視窗寬度回傳 Column 寬度"""
    width = page.window_width
    
    if width >= WINDOW_BREAKPOINT_LARGE:
        return 600  # 寬鬆布局
    elif width >= WINDOW_BREAKPOINT_MEDIUM:
        return 450  # 標準布局
    else:
        return "max"  # 滿寬
```

#### B. Flet Page 事件監聽

```python
class CacheQueryView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        
        # 監聽視窗大小改變
        self.page.on_resize = self._on_window_resize
        
        # 初始設定
        self._apply_responsive_layout()
    
    def _on_window_resize(self, e):
        """視窗大小改變時自動調整"""
        self._apply_responsive_layout()
        self.update()  # 觸發 Flet 重新渲染
    
    def _apply_responsive_layout(self):
        """根據視窗大小調整布局"""
        width = self.page.window_width
        
        # 調整元素寬度
        if hasattr(self, 'query_result_list'):
            # 大螢幕：多欄顯示
            if width >= 1400:
                self.query_result_list.width = None  # 自動寬度
            # 小螂幕：單欄顯示
            else:
                self.query_result_list.width = width - 40
```

#### C. 彈性布局範例

```python
def build_query_view(self) -> ft.Column:
    return ft.Column(
        expand=True,
        spacing=10,
        controls=[
            # 搜尋列：始终完整显示
            self._build_search_bar(),
            
            # 結果區域：根據可用空間自動調整
            ft.Container(
                content=self.query_result_list,
                expand=True,
                # 最小高度確保搜尋結果可見
                min_height=200,
            ),
            
            # 詳情區：根據剩餘空間調整
            ft.Container(
                content=self.detail_panel,
                expand=True if self.page.window_height > 700 else False,
                # 視窗太小時可折疊
                visible=self.page.window_height > 500,
            ),
        ],
    )
```

#### D. View 切換時的視窗管理

```python
# view_registry.py 中設定每個 View 的尺寸
VIEW_DIMENSIONS = {
    'cache_overview': {'width': 1360, 'height': 940},
    'cache_query': {'width': 1400, 'height': 950},   # 查詢需要更寬
    'cache_shard': {'width': 1500, 'height': 1000},  # 編輯需要最大
}

def _switch_to_cache_view(view_key: str):
    """切換 View 時調整視窗大小"""
    dims = VIEW_DIMENSIONS.get(view_key, (1360, 940))
    page.window_width = dims['width']
    page.window_height = dims['height']
```

---

## 五、拆分細節

### 5.1 目錄結構

```
app/views/cache/
├── __init__.py
├── cache_overview_view.py   # 新增
├── cache_query_view.py       # 新增
└── cache_shard_view.py       # 新增
```

### 5.2 遷移對照

| 原始位置 | 目標 View | 搬移內容 |
|----------|-----------|----------|
| `cache_view.py:overview_*` | CacheOverviewView | 總覽 UI + 事件 |
| `cache_view.py:query_*` | CacheQueryView | 查詢 UI + 事件 |
| `cache_view.py:shard_*` | CacheShardView | 分片 UI + 事件 |
| `cache_view.py:query_sub_tabs` | 各 View 獨立實例 | 第二層 Tabs |

### 5.3 view_registry.py 更新

```python
# 新增三個 view 入口
VIEW_REGISTRY = {
    # ... 現有 ...
    
    # Cache 三個子 View
    'cache_overview': {
        'view': CacheOverviewView,
        'icon': ft.Icons.STORAGE,
        'label': '快取總覽',
        'dims': (1360, 940),
    },
    'cache_query': {
        'view': CacheQueryView,
        'icon': ft.Icons.SEARCH,
        'label': '快取查詢',
        'dims': (1400, 950),
    },
    'cache_shard': {
        'view': CacheShardView,
        'icon': ft.Icons.EDIT,
        'label': '快取分片',
        'dims': (1500, 1000),
    },
}
```

---

## 六、實作檢查清單

### Phase 0: 盤點
- [ ] 確認 cache_view.py 所有 UI 元件
- [ ] 確認 cache_state.py 實例化方式
- [ ] 確認現有測試可通過

### Phase 1: CacheOverviewView
- [ ] 建立 `app/views/cache/__init__.py`
- [ ] 建立 `cache_overview_view.py`
- [ ] 搬移 Overview 相關程式碼
- [ ] 實作 scrollable UI
- [ ] 測試編譯

### Phase 2: CacheQueryView
- [ ] 建立 `cache_query_view.py`
- [ ] 搬移 Query 相關程式碼
- [ ] 實作獨立 query_sub_tabs
- [ ] 實作 scrollable + 響應式
- [ ] 測試編譯

### Phase 3: CacheShardView
- [ ] 建立 `cache_shard_view.py`
- [ ] 搬移 Shard 相關程式碼
- [ ] 實作獨立 query_sub_tabs
- [ ] 實作 scrollable + 響應式
- [ ] 測試編譯

### Phase 4: Registry 更新
- [ ] 更新 view_registry.py
- [ ] 新增 NavigationRail 項目
- [ ] 實作 View 切換時的視窗調整
- [ ] 測試完整流程

### Phase 5: 清理
- [ ] 刪除舊 cache_view.py
- [ ] 執行全部測試

---

## 七、Validation checklist（每個 View）

- [ ] **Scrollable 流暢**：
  - [ ] 大列表（>100 項目）操作流暢
  - [ ] 巢狀滾動區域無衝突
  - [ ] `auto_scroll` 行為正確

- [ ] **視窗自適應**：
  - [ ] 視窗放大時布局正確
  - [ ] 視窗縮小時內容可見
  - [ ] View 切換時視窗自動調整

- [ ] **功能正確**：
  - [ ] Overview 統計顯示正確
  - [ ] Query 搜尋結果正確
  - [ ] Shard 編輯存檔正確

- [ ] **向後相容**：
  - [ ] 原有 cache 相關測試通過
  - [ ] import 路徑變更正確

---

## 八、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 狀態共享問題 | 中 | 確認 cache_state 單例模式 |
| UI 破壞 | 中 | 每個 View 獨立測試 |
| 效能下降 | 低 | Lazy Loading 保持 |
| 向後相容 | 中 | 完整測試覆蓋 |

---

## 九、預估工作量

| 項目 | 行數變更 |
|------|----------|
| 新建 3 個 View | +2400 |
| 刪除舊 cache_view.py | -3064 |
| view_registry.py 更新 | ~30 |
| 測試驗證 | - |
| **總計** | 實質 ~2000 行重組 |
