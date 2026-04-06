# PR 設計：函數過長重構

> 設計日期：2026-03-17
> 狀態：待審核

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行號 | 函數名 | 行數 | 驗證方式 |
|------|------|--------|------|----------|
| `translation_tool/core/lm_translator_main.py` | 28-~582 | `translate_batch_smart` | ~554 | line count + read |
| `translation_tool/core/lm_translator.py` | 106-~562 | `translate_directory_generator` | ~456 | line count + read |

### 1.2 問題說明

- **現況**：兩個核心翻譯函數過長，超過 400 行，職責過多
- **風險**：
  - 難以測試（只能做 end-to-end）
  - 難以維護（修改時容易漏改）
  - 難以理解（邏輯分支過多）
- **影響範圍**：
  - `lm_translator_main.py`
  - `lm_translator.py`

### 1.3 函數職責分析

#### `translate_batch_smart` (554 行) 應拆分為：

| 子函數 | 職責 | 預估行數 |
|--------|------|----------|
| `_validate_batch_items()` | 驗證與正規化輸入資料 | ~30 |
| `_detect_batch_profile()` | 偵測翻譯類型（lang/patchouli/md） | ~50 |
| `_calculate_batch_size()` | 計算批次大小 | ~40 |
| `_execute_translation()` | 執行翻譯 API 呼叫 | ~300 |
| `_process_output()` | 處理輸出結果 | ~50 |
| `_handle_errors()` | 錯誤處理與重試邏輯 | ~80 |

#### `translate_directory_generator` (456 行) 應拆分為：

| 子函數 | 職責 | 預估行數 |
|--------|------|----------|
| `_scan_directory()` | 掃描目錄結構 | ~40 |
| `_group_by_type()` | 按類型分組檔案 | ~30 |
| `_process_directory()` | 處理目錄流程 | ~300 |
| `_write_results()` | 寫入結果 | ~50 |

---

## 二、重構設計

### 2.1 解決方案：職責分離 + Helper 函數

```python
# ========== 重構後結構（lm_translator_main.py）==========
def translate_batch_smart(batch_items, total=None):
    """
    智慧批次翻譯函數（主流程）
    
    職責：協調各子流程，不直接處理細節
    """
    # 1. 驗證與正規化
    items = _validate_batch_items(batch_items)
    
    # 2. 偵測 profile
    profile = _detect_batch_profile(items)
    
    # 3. 計算批次大小
    batch_size = _calculate_batch_size(profile)
    
    # 4. 執行翻譯
    results = _execute_translation(items, batch_size, profile)
    
    # 5. 處理輸出
    return _process_output(results)


def _validate_batch_items(items):
    """驗證批次資料格式"""
    # ... 30 行


def _detect_batch_profile(items):
    """偵測翻譯類型"""
    # ... 50 行


def _calculate_batch_size(profile):
    """計算批次大小"""
    # ... 40 行


def _execute_translation(items, batch_size, profile):
    """執行翻譯"""
    # ... 300 行


def _process_output(results):
    """處理輸出"""
    # ... 50 行


def _handle_errors(e, context):
    """錯誤處理與重試"""
    # ... 80 行
```

### 2.2 影響範圍

| 檔案 | 修改類型 | 說明 |
|------|----------|------|
| `lm_translator_main.py` | 拆分 + 新增 helper | 主函數縮短，新增 6 個 `_` 前綴 helper |
| `lm_translator.py` | 拆分 + 新增 helper | 主函數縮短，新增 4 個 `_` 前綴 helper |

### 2.3 向後相容

- **保持 API 簽名不變**：`translate_batch_smart(batch_items, total=None)` 簽名不變
- **內部實作改變**：細節邏輯遷移至 helper 函數
- **測試策略**：輸入相同測試資料，輸出應完全一致

---

## 三、測試策略

### 3.1 現有測試

- `tests/test_lm_translator_main.py`
- `tests/test_lm_translator.py`
- `tests/test_lm_translator_dry_run.py`

### 3.2 測試重點

```python
# 驗證重構前後行為一致
def test_refactor_preserves_behavior():
    """重構後行為應與重構前完全一致"""
    # 準備測試資料
    test_items = [
        {"file": "test.lang", "cache_type": "lang", "content": "hello=Hello"},
        {"file": "patchouli/test.json", "cache_type": "patchouli", "content": "{\"key\": \"value\"}"}
    ]
    
    # 呼叫主函數
    result, status = translate_batch_smart(test_items, total=2)
    
    # 驗證輸出格式正確
    assert isinstance(result, list)
    assert status in ["AUTO", "MANUAL", "PARTIAL"]
```

### 3.3 驗證清單

| 驗證項目 | 執行指令 |
|----------|----------|
| 語法正確 | `python -m py_compile lm_translator_main.py lm_translator.py` |
| 匯入正常 | `python -c "from translation_tool.core.lm_translator_main import translate_batch_smart"` |
| 測試通過 | `pytest tests/test_lm_translator_main.py -v` |
| DRY_RUN 正常 | `pytest tests/test_lm_translator_dry_run.py -v` |

---

## 四、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 行為改變 | 中 | **嚴格比對重構前後輸出** |
| 測試覆蓋不足 | 中 | 先增加測試案例，再重構 |
| 漏改參考 | 低 | Helper 函數使用 `_` 前綴（私有） |
| 效能影響 | 低 | 不應有效能變化 |

---

## 五、實作檢查清單

### Phase 0：盤點
- [ ] 確認 `pytest tests/test_lm_translator_main.py -v` 通過
- [ ] 確認 `pytest tests/test_lm_translator.py -v` 通過

### Phase 1：`translate_batch_smart` 拆分
- [ ] 建立 `_validate_batch_items()` helper
- [ ] 建立 `_detect_batch_profile()` helper
- [ ] 建立 `_calculate_batch_size()` helper
- [ ] 建立 `_execute_translation()` helper
- [ ] 建立 `_process_output()` helper
- [ ] 建立 `_handle_errors()` helper
- [ ] 重構 `translate_batch_smart()` 為協調者

### Phase 2：`translate_directory_generator` 拆分
- [ ] 建立 `_scan_directory()` helper
- [ ] 建立 `_group_by_type()` helper
- [ ] 建立 `_process_directory()` helper
- [ ] 建立 `_write_results()` helper
- [ ] 重構 `translate_directory_generator()` 為協調者

### Phase 3：驗證
- [ ] 執行 `python -m py_compile` 語法檢查
- [ ] 執行 `python -c "import"` 確認匯入正常
- [ ] 執行 `pytest tests/test_lm_translator_main.py -v`
- [ ] 執行 `pytest tests/test_lm_translator.py -v`
- [ ] 執行 `pytest tests/test_lm_translator_dry_run.py -v`

### Validation checklist（每顆 PR 都要）：
- [ ] **行為一致性**：輸入相同測試資料，輸出與重構前完全一致
- [ ] **測試通過**：所有現有測試通過
- [ ] **程式碼可讀性**：每個 helper 函數不超過 100 行

---

## 七、執行順序建議

> ⚠️ 與 PR4 的相依性

PR3 和 PR4 都會修改 `translate_batch_smart()` 函式：
- **PR3**：拆分函式為多個 helper
- **PR4**：新增 `dry_run`, `export_cache_only` 參數

**建議執行順序**：
1. 先做 **PR3**（拆分函式結構）
2. 再做 **PR4**（在拆分後的結構上新增參數）

如果順序顛倒，PR4 的參數會需要重新 merge 到 PR3 拆分後的程式碼中。

| 項目 | 行數變更 |
|------|----------|
| `lm_translator_main.py` | 重構 ~554 → ~100（主）+ ~450（helpers） |
| `lm_translator.py` | 重構 ~456 → ~100（主）+ ~350（helpers） |
| 測試驗證 | 需要完整測試執行 |
| **總計** | 實質行數不變，結構重組 |
