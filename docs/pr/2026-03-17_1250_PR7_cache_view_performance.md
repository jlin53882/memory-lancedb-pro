# PR 設計：cache_view UI 效能優化

> 設計日期：2026-03-17
> 狀態：待審核
> 依據：Flet 0.28.3 設計優化稽核報告

---

## 一、Flet 0.28.3 合規檢查

> ⚠️ 根據 `docs/flet-ui-0283-design-audit.md` 驗證

### 1.1 已確認正確

| 檢查項目 | 狀態 | 備註 |
|----------|------|------|
| ListView 使用 | ✅ | 已有 ListView，但可優化為 builder 模式 |
| scroll=ft.ScrollMode.AUTO | ✅ | 已有使用 |
| Debounce 搜尋 | ✅ | 設計已包含 |
| 批次 update | ✅ | 設計已包含 |

### 1.2 需要優化

| 項目 | 當前 | 優化後 |
|------|------|--------|
| ListView 渲染 | 一次全部渲染 | 使用 `ListView.builder()` 虛擬滾動 |
| 大量資料 | 直接 append | 分頁載入 + builder |

---

## 二、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 問題 | 數量 | 驗證方式 |
|------|------|------|----------|
| `cache_view.py` | `.update()` 呼叫過多 | 53 次 | Select-String |
| `cache_view.py` | 迴圈內建 UI | 20+ 處 | Select-String |
| `cache_view.py` | ListView 一次渲染大量資料 | 5 處 | Select-String |

### 1.2 具體問題

#### 問題 A：迴圈內多次 update（最嚴重）

```python
# cache_view.py:1500-1502 - ❌ 糟糕：迴圈內每次都 update
for line in rows[-800:]:
    self.log_list.controls.append(ft.Text(line, size=12, selectable=True))
    self.page.update()  # 800 次 update！
```

#### 問題 B：ListView 一次渲染大量項目

```python
# cache_view.py:1542-1546 - ❌ 上千個項目一次建立
self.type_list.controls.clear()
for ctype, st in self._iter_type_states(data):
    self.type_list.controls.append(...)  # 全部一次建立
```

#### 問題 C：搜尋無 Debounce

每次按鍵都觸發搜尋，導致 UI 卡頓。

---

## 二、優化設計

### 2.1 優化一：批次 Update

```python
# ========== 重構前（壞範例）==========
for line in rows[-800:]:
    self.log_list.controls.append(ft.Text(line, size=12, selectable=True))
    self.page.update()  # ❌ 每次迴圈都更新

# ========== 重構後（好範例）==========
for line in rows[-800:]:
    self.log_list.controls.append(ft.Text(line, size=12, selectable=True))
self.page.update()  # ✅ 只更新一次
```

### 2.2 優化二：分頁載入

```python
# 常數定義
PAGE_SIZE = 50  # 每頁顯示數量

# 分頁載入函式
def _load_type_list_paged(self, data, page: int = 0):
    """分頁載入類型列表"""
    self.type_list.controls.clear()
    
    # 只載入當前頁面
    items = list(self._iter_type_states(data))
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(items))
    
    for ctype, st in items[start:end]:
        self.type_list.controls.append(self._build_type_item(ctype, st))
    
    # 記錄總頁數
    self._type_list_total_pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
    self._type_list_current_page = page
```

### 2.3 優化三：搜尋 Debounce

> 根據 Flet 0.28.3 稽核報告，建議搜尋框 debounce 為 300-500ms

```python
import threading

class CacheView(ft.Column):
    def __init__(self, page):
        # ...
        self._search_timer = None
        self._search_debounce_ms = 300  # ✅ Flet 0.28.3 建議 300-500ms
    
    def _on_query_text_change(self, e):
        """搜尋文字改變（帶 debounce）"""
        # 取消之前的計時器
        if self._search_timer is not None:
            self._search_timer.cancel()
        
        # 建立新的延遲搜尋
        self._search_timer = threading.Timer(
            self._search_debounce_ms / 1000,
            self._do_search,
            args=(e.control.value,)
        )
        self._search_timer.start()
    
    def _do_search(self, keyword: str):
        """實際執行搜尋"""
        # 這裡放搜尋邏輯
        self._render_query_results()
        self.page.update()
```

### 2.4 優化四：ListView.builder() 虛擬滾動

> 根據 Flet 0.28.3 稽核報告，使用 `ListView.builder()` 獲得虛擬滾動效果

```python
# ✅ 正確：使用 builder 模式
self.type_list = ft.ListView(
    expand=True,
    spacing=6,
    auto_scroll=True,
    # 使用 builder 模式（需設定 item_count 和 item_builder）
    item_count=len(all_items),
    item_builder=lambda i, item: self._build_type_item(item),
)

def _build_type_item(self, item):
    """建立單一類型項目"""
    return ft.Container(
        content=ft.Text(item['name']),
        padding=10,
    )
```

**優點**：只渲染可見區域的項目，大幅提升大量資料時的效能。

---

## 三、修改範圍

### 3.1 需要修改的函數

| 函數 | 問題 | 優化方式 |
|------|------|----------|
| `_render_logs()` | 迴圈內 update | 批次 update |
| `_load_overview()` | 一次建立全部 | 分頁載入 |
| `_render_query_results()` | 一次渲染全部 | 分頁 + debounce |
| `_load_shard_rows()` | 一次渲染全部 | 分頁載入 |
| `_on_query_text_change()` | 無 debounce | 加入 debounce |

### 3.2 預期改善

| 指標 | 優化前 | 優化後 |
|------|--------|--------|
| update 次數（搜尋） | 每次按鍵 1 次 | 最多 3 次/秒 |
| ListView 項目數 | 一次 1000+ | 每次 50 |
| UI 回應速度 | 卡頓 | 流暢 |

---

## 四、實作檢查清單

### Phase 1: 批次 Update
- [ ] 找出所有迴圈內的 `.update()` 呼叫
- [ ] 將 update 移到迴圈外部
- [ ] 測試功能正常

### Phase 2: 分頁載入
- [ ] 在 cache_view.py 頂部加入 `PAGE_SIZE = 50`
- [ ] 實作 `_load_type_list_paged()` 函式
- [ ] 實作分頁控制 UI（上一頁/下一頁按鈕）

### Phase 3: Debounce
- [ ] 加入搜尋 debounce
- [ ] 設定 300ms 延遲
- [ ] 測試搜尋功能

### Phase 4: 驗證
- [ ] 執行 `python -m py_compile cache_view.py`
- [ ] 手動測試 scroll 流暢度
- [ ] 手動測試搜尋反應速度

---

## 五、Validation checklist

- [ ] **效能改善**：
  - [ ] 迴圈內 update 已移除
  - [ ] ListView 使用分頁載入
  - [ ] 搜尋有 debounce

- [ ] **功能正確**：
  - [ ] 搜尋結果正確
  - [ ] 分頁切換正常
  - [ ] 資料顯示正確

- [ ] **無回歸**：
  - [ ] 原有功能不受影響

---

## 六、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 分頁導致資訊不足 | 低 | 顯示「載入更多」按鈕 |
| Debounce 搜尋慢 | 低 | 300ms 是合理延遲 |
| 程式碼變複雜 | 中 | 加註解說明 |

---

## 七、預估工作量

| 項目 | 行數變更 |
|------|----------|
| 批次 update 優化 | -10（移除重複 update） |
| 分頁載入 | +40 |
| Debounce | +20 |
| **總計** | ~50 行 |
