# PR5-PR7 設計稿稽核報告

> 稽核日期：2026-03-18  
> 專案：minecraft-translator-flet  
> 設計稿：Cache View 重構 + 效能優化

---

## 一、驗證數據

| 項目 | 設計稿聲稱 | 實際驗證 |
|------|------------|----------|
| cache_view.py 行數 | 3075 行 | ✅ 3075 行 |
| .update() 呼叫次數 | 53 次 | ✅ 53 次 |
| cache_manager/ 子模組 | 10 個 | ✅ 10 個 |

---

## 二、潛在設計問題

### 2.1 Modal 實作問題 ⚠️

| 問題 | 說明 | 風險 |
|------|------|------|
| page.overlay 層級 | 設計稿建議用 `page.overlay.append()`，但沒有處理 z-index 層級問題 | 中 |
| 多次開啟 Modal | 沒有防止重複開啟的機制 | 低 |
| Modal 關閉回調 | 設計稿提到回調函數，但沒有說明錯誤處理 | 中 |

**建議**：
```python
# 加入防止重複開啟
def show_query_modal(self):
    if hasattr(self, '_query_modal_open') and self._query_modal_open:
        return  # 已有 Modal 開啟
    self._query_modal_open = True
    # ... 建立 Modal
```

---

### 2.2 .update() 優化問題 ⚠️

| 問題 | 說明 | 風險 |
|------|------|------|
| Dirty Flag 設計 | 設計稿提到 Dirty Flag，但沒有說明何時清除 | 高 |
| Debounce 實現 | 需要額外的計時器，可能與 Flet 生命週期衝突 | 中 |
| Fallback 機制 | 設計稿說保留 fallback，但沒說明觸發條件 | 中 |

**建議**：
```python
# 明確的 Dirty Flag 管理
def mark_dirty(self):
    self._dirty = True
    self._dirty_reason = "user_input"  # 記錄原因

def clear_dirty(self):
    self._dirty = False
    self._dirty_reason = None

def maybe_update(self):
    if self._dirty:
        self.update()
        self.clear_dirty()
```

---

### 2.3 目錄結構問題 ⚠️

| 問題 | 說明 |
|------|------|
| 設計稿建議 `app/views/cache/` | 但現有 `app/views/cache_manager/` |
| 兩個目錄並存 | 會造成混淆 |

**建議**：
```
方案 A：保留 cache_manager/，新增 cache/cache_main_view.py
方案 B：合併到 cache_manager/，廢除 cache_view.py
```

---

### 2.4 回調函數設計問題 ⚠️

| 問題 | 說明 |
|------|------|
| 同步/非同步 | 沒有說明回調是同步還是 async |
| 錯誤處理 | 沒有說明 Modal 內部錯誤如何上報 |
| 資料驗證 | 沒有說明回調資料的格式驗證 |

**建議**：
```python
class CacheQueryModal(ft.Container):
    def __init__(self, on_complete=None, on_error=None, initial_data=None):
        self.on_complete = on_complete  # 成功回調
        self.on_error = on_error        # 錯誤回調
        self.initial_data = initial_data

    def _handle_save(self, data):
        # 驗證資料
        if self._validate(data):
            if self.on_complete:
                self.on_complete(data)
        else:
            if self.on_error:
                self.on_error("資料格式錯誤")
        self.close()
```

---

### 2.5 現有程式碼遷移問題 ⚠️

| 問題 | 說明 |
|------|------|
| 現有 Query Panel | 已有獨立的 `cache_query_panel.py`，搬到 Modal 會重複 |
| 現有 Shard Panel | 已有獨立的 `cache_shard_panel.py`，搬到 Modal 會重複 |
| 歷史紀錄 | 設計稿沒有說明 `_query_history_`, `_shard_history_` 如何處理 |

---

## 三、驗證清單建議

設計稿的驗證清單缺少以下項目：

| 缺失項目 | 建議 |
|----------|------|
| Modal 重複開啟 | 加入防呆機制 |
| 回調錯誤處理 | 明確錯誤傳遞方式 |
| 資料格式驗證 | Modal 內部驗證 |
| 目錄命名 | 決定 cache/ vs cache_manager/ |
| 現有 Panel 遷移 | 保留或廢除策略 |

---

## 四、總結

### 設計可行 ✅
- 目標明確（減少 .update()、Modal 化）
- 架構合理（分離關注點）

### 需要補充 ⚠️
- Modal 錯誤處理
- Dirty Flag 清除時機
- 目錄命名策略
- 現有 Panel 遷移計畫

### 風險評估
| 項目 | 風險 |
|------|------|
| .update() 優化複雜度 | 中 |
| Modal 與現有 UI 整合 | 中 |
| 遷移過程破壞功能 | 高 |

---

## 五、建議

### 建議 1：先做 Phase 0 驗證

在實作前，先驗證現有架構可以支援 Modal：
1. 在現有 cache_view.py 加入一個測試 Modal
2. 確認 overlay + 回調機制運作正常
3. 再擴展到完整實作

### 建議 2：分階段實作

```
Phase 1：只搬移 Query 到 Modal（不改動 Shard）
Phase 2：搬移 Shard 到 Modal
Phase 3：優化 .update()
```

### 建議 4：保留現有 Tab

設計稿說要移除 Tab，但可以考慮「退化方案」：
- 預設開 Modal
- 若 Modal 有問題，仍可用 Tab 作為 fallback

---

*本報告基於設計稿 + 現有程式碼分析*
