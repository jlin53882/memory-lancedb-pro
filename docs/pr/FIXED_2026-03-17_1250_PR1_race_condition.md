# PR 設計：移除全域變數 Race Condition

> 設計日期：2026-03-17
> 狀態：待審核
> 依據：Flet 0.28.3 設計優化稽核報告

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行號 | 驗證方式 | 確認結果 |
|------|------|----------|----------|
| `translation_tool/core/lm_config_rules.py` | 19 | read | ✅ `_current_key_index = 0` 確認存在 |
| `translation_tool/core/lm_translator_main.py` | 24 | read | ✅ `from ... import _current_key_index` 確認有使用 |

### 1.2 問題說明

- **現況**：`lm_config_rules.py:19` 使用模組級全域變數 `_current_key_index = 0`，無執行緒保護
- **風險**：多執行緒同時讀寫時會發生 race condition，導致 API key 輪替錯誤
- **影響範圍**：
  - `lm_config_rules.py`（定義端）
  - `lm_translator_main.py`（使用端）

### 1.3 依賴分析

```
lm_config_rules.py
├── get_current_api_key()       # 讀取 _current_key_index
├── rotate_api_key()             # 修改 _current_key_index
└── _get_all_keys()              # 輔助

lm_translator_main.py
├── import _current_key_index    # 直接引用（危險）
└── translate_batch_smart()      # 使用 API key
```

---

## 二、重構設計

### 2.1 解決方案：類別封裝 + Threading.Lock

```python
# ========== 重構前（lm_config_rules.py:19）==========
_current_key_index = 0  # ❌ 多執行緒不安全


# ========== 重構後 ==========
import threading


class KeyIndexTracker:
    """執行緒安全的 API Key 索引追蹤器"""
    
    def __init__(self, key_count: int = 0):
        self._index = 0
        self._key_count = key_count  # ✅ 新增：記錄 key 總數
        self._lock = threading.Lock()
    
    def get_current(self) -> int:
        with self._lock:
            return self._index
    
    def next(self) -> int:
        """輪替至下一個索引（執行緒安全，自動環繞）"""
        with self._lock:
            self._index += 1
            # ✅ 修正：加入 modulo 邏輯，自動環繞
            if hasattr(self, '_key_count') and self._key_count > 0:
                self._index = self._index % self._key_count
            return self._index
    
    def set_key_count(self, count: int):
        """設定 API Key 總數（用於 modulo 計算）"""
        with self._lock:
            self._key_count = count
    
    def reset(self) -> None:
        with self._lock:
            self._index = 0


# 模組級單例
_key_tracker = KeyIndexTracker()


# 向後相容：保留舊API
def get_current_key_index() -> int:
    """取得目前索引（向後相容用）"""
    return _key_tracker.get_current()


def rotate_key_index() -> int:
    """輪替至下一個索引（向後相容用）"""
    return _key_tracker.next()


def reset_key_index() -> None:
    """重置索引（向後相容用）"""
    return _key_tracker.reset()
```

### 2.2 影響範圍

| 檔案 | 修改類型 | 說明 |
|------|----------|------|
| `lm_config_rules.py` | 重構 | 移除全域變數，改用類別 + Lock |
| `lm_translator_main.py` | 移除 import | 移除 `from ... import _current_key_index` |

### 2.3 向後相容

- 保留 `get_current_key_index()`, `rotate_key_index()`, `reset_key_index()` 函式
- 內部改呼叫 `_key_tracker` 實作
- 舊有呼叫端無需修改

---

## 三、測試策略

### 3.1 現有測試

- `tests/test_lm_config_rules.py` - 需確認存在並通過

### 3.2 新增測試

```python
# tests/test_lm_config_rules_thread_safe.py
import threading
import pytest
from translation_tool.core.lm_config_rules import _key_tracker, reset_key_index


def test_concurrent_access():
    """驗證多執行緒並發存取不會造成 race condition"""
    reset_key_index()
    results = []
    
    def worker():
        for _ in range(100):
            idx = _key_tracker.next()
            results.append(idx)
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # 預期：總共 10 threads * 100 次 = 1000 個 unique index
    assert len(results) == 1000
    assert len(set(results)) == 1000  # 無重複
```

---

## 四、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 向後相容破壞 | 低 | 保留舊函式簽名 |
| 測試覆蓋不足 | 中 | 新增並發測試 |
| 效能影響 | 低 | Lock 只在關鍵區塊 |

---

## 五、實作檢查清單

- [ ] Phase 0 盤點：確認現有測試可通過
- [ ] Phase 1：
  - [ ] 建立 `KeyIndexTracker` 類別
  - [ ] 建立模組級 `_key_tracker` 單例
  - [ ] 實作 `get_current_key_index()`, `rotate_key_index()`, `reset_key_index()` 向後相容函式
  - [ ] 移除 `lm_translator_main.py` 中的 `from ... import _current_key_index`
- [ ] Phase 2：
  - [ ] 新增執行緒安全測試
  - [ ] 執行 `pytest tests/test_lm_config_rules.py`
  - [ ] 執行 `pytest tests/test_lm_translator_main.py`
- [ ] Validation checklist：
  - [ ] 執行 `python -c "from translation_tool.core.lm_config_rules import get_current_key_index; print(get_current_key_index())"` 確認匯入正常

---

## 六、預估工作量

| 項目 | 行數變更 |
|------|----------|
| `lm_config_rules.py` | +30 |
| `lm_translator_main.py` | -1 |
| 新測試 | +25 |
| **總計** | ~55 行 |
