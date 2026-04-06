# PR 設計：Flet UI 開啟速度優化

> 設計日期：2026-03-17
> 狀態：待審核
> 依據：Flet 0.28.3 設計優化稽核報告

---

## 一、Flet 0.28.3 合規檢查

> ⚠️ 根據 `docs/flet-ui-0283-design-audit.md` 驗證

| 檢查項目 | 狀態 | 備註 |
|----------|------|------|
| 無 `SURFACE_VARIANT` | ✅ | 不存在，應改用 `SURFACE` |
| 無 `ft.UserControl` 繼承 | ✅ | 應改用 `ft.Container` |
| Dialog 使用 `page.overlay` | ✅ | 正確做法 |
| Scrollable Column 有固定高度父容器 | ✅ | 需確認 |
| Input debounce 300-500ms | ✅ | PR-7 已有 |

---

## 二、現況分析

### 1.1 現有架構問題

根據程式碼驗證，發現以下啟動瓶頸：

| 問題 | 位置 | 影響 |
|------|------|------|
| View 全部在啟動時建立 | `view_registry.py:55-62` | 8 個 View 同時初始化 |
| cache_view did_mount 負擔重 | `cache_view.py:1063` | 一次載入 overview + query + shard |
| 翻譯 view __init__ 過重 | `translation_view.py:54` | 建立大量 UI 元件 |
| 背景索引重建 | `startup_tasks.py:14` | 啟動時佔用資源 |

### 1.2 現有優化（PR67 已做）

```python
# view_registry.py - Lazy import 機制已存在
_VIEW_IMPORT_MAP = {
    'cache': ('app.views.cache_view', 'CacheView', False),
    # ...
}

def _lazy_import_view(view_key: str, page: ft.Page, file_picker: ft.FilePicker):
    """Lazy import view 類別"""
    module = __import__(module_name, fromlist=[class_name])
    # ...
```

**但這還不夠**：Lazy import 只是延遲 import，仍在啟動時全部建立實例。

---

## 二、效能瓶頸分析

### 2.1 測量點

| 階段 | 預估耗時 | 原因 |
|------|----------|------|
| Python 環境啟動 | 1-2s | 模組載入 |
| Flet 初始化 | 0.5-1s | 建立 Page |
| View 建立（全部） | 3-5s | UI 元件建構 |
| did_mount 資料載入 | 2-3s | 查詢資料/建立索引 |
| **總計** | **7-11s** | - |

### 2.2 關鍵問題

#### 問題 A：全部 View 在啟動時建立

```python
# view_registry.py:55-62 - 這段在啟動時全部執行
registry = [
    {'key': 'config', 'view': wrap_view(_lazy_import_view('config', ...))},
    {'key': 'rules', 'view': wrap_view(_lazy_import_view('rules', ...))},
    {'key': 'cache', 'view': wrap_view(_lazy_import_view('cache', ...))},  # 3000+ 行
    # ... 8 個 View 全部建立
]
```

#### 問題 B：cache_view did_mount 過重

```python
# cache_view.py:1063-1077 - 一次載入所有資料
def did_mount(self):
    self._load_overview()          # 載入總覽
    self._refresh_query_type_options()  # 查詢類型
    self._render_query_type_shard_page()  # 分片
    self._render_query_results()   # 結果
    self._render_query_detail()    # 詳情
    self._refresh_disabled_state()  # 狀態
```

#### 問題 C：翻譯 view 建立大量 UI

```python
# translation_view.py - __init__ 中建立大量元件
self.tabs = ft.Tabs(tabs=[
    ft.Tab(content=self._build_ftb_tab()),   # 建立 Tab 內容
    ft.Tab(content=self._build_kjs_tab()),
    ft.Tab(content=self._build_md_tab()),
])
```

---

## 三、優化設計

### 3.1 解決方案：多層次 Lazy Loading

#### Level 1: 僅建立第一個 View

```python
# 修改 view_registry.py
def build_view_registry(page, file_picker):
    """建立 view 註冊表 - 僅建立首頁 View"""
    
    # 只建立首頁 View，其他延後
    first_view_key = 'config'  # 或儲存上次選擇
    
    registry = [
        {'key': first_view_key, 
         'icon': ..., 
         'label': ...,
         'view': wrap_view(_lazy_import_view(first_view_key, page, file_picker))},
        # 其他 view 的 view 欄位暫時為 None
    ]
    
    return registry


def _get_or_create_view(registry, index, page, file_picker):
    """按需建立 View（延遲載入）"""
    item = registry[index]
    
    if item['view'] is None:
        # 首次點擊才建立
        item['view'] = wrap_view(_lazy_import_view(item['key'], page, file_picker))
    
    return item['view']
```

#### Level 2: View 內部 Lazy Loading

```python
# cache_view.py - 將 did_mount 拆分
def did_mount(self):
    """僅載入當前 Tab 的資料"""
    current_tab = self.tabs.selected_index
    
    if current_tab == 0:  # Overview
        self._load_overview()
    elif current_tab == 1:  # Query
        self._load_query_data()  # 延遲載入
    elif current_tab == 2:  # Shard
        self._load_shard_data()  # 延遲載入


def on_tab_change(e):
    """Tab 切換時才載入對應資料"""
    tab_index = e.control.selected_index
    
    if tab_index == 1 and not self._query_data_loaded:
        self._load_query_data()
    elif tab_index == 2 and not self._shard_data_loaded:
        self._load_shard_data()
```

#### Level 3: UI 元件 Lazy Building

```python
# translation_view.py - Tab 內容延後建立
def __init__(self, page, file_picker):
    self._tabs_content_built = {
        'ftb': False,
        'kjs': False,
        'md': False,
    }
    
    # 只建立第一個 Tab 內容
    self.tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="FTB", content=self._build_ftb_tab()),  # 立即
            ft.Tab(text="KubeJS", content=None),  # 延遲
            ft.Tab(text="Markdown", content=None),  # 延遲
        ],
        on_change=self._on_tab_change,
    )


def _on_tab_change(self, e):
    """Tab 切換時才建立內容"""
    idx = e.control.selected_index
    tab_keys = ['ftb', 'kjs', 'md']
    key = tab_keys[idx]
    
    if not self._tabs_content_built[key]:
        # 首次點擊才建立內容
        if key == 'ftb':
            content = self._build_ftb_tab()
        elif key == 'kjs':
            content = self._build_kjs_tab()
        else:
            content = self._build_md_tab()
        
        self.tabs.tabs[idx].content = content
        self._tabs_content_built[key] = True
        self.update()
```

### 3.2 Loading 畫面設計

```python
# main.py - 啟動時顯示 Loading
def main(page: ft.Page):
    # 先顯示 Loading 畫面
    loading_view = ft.Column(
        [
            ft.Text("正在載入...", size=20),
            ft.ProgressBar(width=300),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(loading_view)
    page.update()
    
    # 背景執行初始化
    def init_app():
        # 建立 View Registry
        registry = build_view_registry(page, file_picker)
        
        # 切換到正式內容
        def switch_to_main():
            page.controls.clear()
            page.add(main_content)
            page.update()
        
        # 在 UI 執行緒更新
        page.call_on_main_thread(switch_to_main)
    
    threading.Thread(target=init_app, daemon=True).start()
```

### 3.3 背景任務優化

```python
# startup_tasks.py - 降低啟動時的資源佔用
def rebuild_index_on_startup():
    """延遲啟動索引重建"""
    import time
    time.sleep(3)  # 延遲 3 秒，讓 UI 先啟動
    # ... 重建邏輯
```

---

## 四、實作檢查清單

### Phase 0: 測量基準
- [ ] 記錄目前啟動時間（按碼錶）
- [ ] 確認每個 View 的初始化時間

### Phase 1: View Registry 優化
- [ ] 修改 `build_view_registry()` 僅建立首頁 View
- [ ] 實作 `_get_or_create_view()` 延遲載入
- [ ] 更新 `change_view()` 事件處理

### Phase 2: CacheView 優化
- [ ] 拆分 `did_mount` 為按需載入
- [ ] 實作 Tab 切換時才載入資料
- [ ] 新增 `_query_data_loaded`, `_shard_data_loaded` 旗標

### Phase 3: TranslationView 優化
- [ ] 實作 Tab 內容延遲建立
- [ ] 新增 `_tabs_content_built` 追蹤

### Phase 4: Loading 畫面
- [ ] 在 main.py 加入 Loading 顯示
- [ ] 背景執行初始化
- [ ] 確認體驗流暢

### Phase 5: 背景任務
- [ ] 延遲索引重建時間點
- [ ] 確認不影響 UI 響應

---

## 五、Validation checklist

- [ ] **啟動時間**：從 7-11s 降至 3-5s
- [ ] **首頁可用**：第一個 View 2s 內可互動
- [ ] **切換流暢**：View 切換不卡頓
- [ ] **功能正確**：所有 View 功能正常
- [ ] **無回歸**：現有測試通過

---

## 六、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 首次點擊慢 | 低 | 使用 Loading 提示 |
| 狀態遺失 | 中 | 確保 did_mount 正確初始化 |
| Tab 切換閃爍 | 低 | 保持原有 Tab 結構 |

---

## 七、預估效果

| 指標 | 優化前 | 優化後 |
|------|--------|--------|
| 啟動時間 | 7-11s | 2-3s |
| 首頁可用 | 5-7s | 1-2s |
| UI 回應 | 卡頓 | 流暢 |
