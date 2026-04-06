# PR 設計：DRY_RUN / EXPORT_CACHE_ONLY 重構（可選）

> 設計日期：2026-03-17
> 狀態：可選（optional）

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行號 | 驗證方式 | 確認結果 |
|------|------|----------|----------|
| `translation_tool/core/lm_translator_main.py` | 25 | read | ✅ `DRY_RUN = False` |
| `translation_tool/core/lm_translator_main.py` | 26 | read | ✅ `EXPORT_CACHE_ONLY = True` |

### 1.2 問題說明

- **現況**：使用模組級全域變數 `DRY_RUN` 和 `EXPORT_CACHE_ONLY`
- **風險**：
  - 不利於單元測試（全域狀態會互相影響）
  - 多執行緒環境下不安全
  - 難以追蹤狀態來源
- **影響範圍**：
  - `lm_translator_main.py`（定義端）
  - 所有呼叫 `translate_batch_smart()` 的程式碼（使用端）

### 1.3 使用情境

```python
# 目前使用方式
if DRY_RUN:
    # 跳過 API 呼叫，只模擬流程
    pass

if EXPORT_CACHE_ONLY:
    # 只輸出快取內容
    pass
```

---

## 二、重構設計

### 2.1 解決方案：參數注入（Parameter Injection）

```python
# ========== 重構前（lm_translator_main.py）==========
DRY_RUN = False  # True = 不呼叫API，只模擬/預覽 測試使用
EXPORT_CACHE_ONLY = True  # True = 只輸出cache 中的內容


def translate_batch_smart(batch_items, total=None):
    if DRY_RUN:
        # 跳過 API 呼叫
        ...
    if EXPORT_CACHE_ONLY:
        # 只讀快取
        ...


# ========== 重構後 ===========
DEFAULT_DRY_RUN = False
DEFAULT_EXPORT_CACHE_ONLY = True


def translate_batch_smart(
    batch_items,
    total=None,
    dry_run: bool = DEFAULT_DRY_RUN,
    export_cache_only: bool = DEFAULT_EXPORT_CACHE_ONLY
):
    """
    智慧批次翻譯函數
    
    參數:
        batch_items: 翻譯項目列表
        total: 總項目數（可選）
        dry_run: True = 不呼叫API，只模擬流程（測試用）
        export_cache_only: True = 只輸出快取中的內容
    """
    if dry_run:
        # 跳過 API 呼叫
        ...
    if export_cache_only:
        # 只讀快取
        ...
```

### 2.2 呼叫端修改對照

| 檔案 | 目前呼叫 | 修改後呼叫 |
|------|----------|------------|
| `app/views/translate_view.py` | `translate_batch_smart(items)` | `translate_batch_smart(items, dry_run=False)` |
| `tests/test_*.py` | `translate_batch_smart(items)` | `translate_batch_smart(items, dry_run=True)` |

### 2.3 向後相容策略

**選項 A（推薦）：保留預設值**
- 預設值維持原本的全域變數行為
- 舊有呼叫端無需修改
- 新功能：測試時可明確傳入參數

**選項 B：移除全域變數**
- 完全移除 `DRY_RUN` 和 `EXPORT_CACHE_ONLY`
- 所有呼叫端必須明確傳參數
- **風險**：容易漏改導致 runtime 錯誤

### 2.4 影響範圍

| 檔案 | 修改類型 | 說明 |
|------|----------|------|
| `lm_translator_main.py` | API 簽名變更 | 新增 `dry_run`, `export_cache_only` 參數 |
| 所有呼叫端 | 參數傳遞 | 可選擇維持預設或明確傳參 |

---

## 三、測試策略

### 3.1 現有測試

- `tests/test_lm_translator_main.py`
- `tests/test_lm_translator_dry_run.py` - **重點測試**

### 3.2 測試重點

```python
# tests/test_lm_translator_dry_run.py
def test_dry_run_parameter():
    """驗證 dry_run 參數正確運作"""
    items = [{"file": "test.lang", "content": "a=b"}]
    
    # 使用參數
    result, status = translate_batch_smart(items, dry_run=True)
    
    # 驗證：dry_run 應快速返回，不呼叫 API
    assert status == "DRY_RUN"
    assert len(result) == 0  # 無實際翻譯結果


def test_export_cache_only_parameter():
    """驗證 export_cache_only 參數正確運作"""
    items = [{"file": "test.lang", "content": "a=b"}]
    
    # 使用參數
    result, status = translate_batch_smart(items, export_cache_only=True)
    
    # 驗證：應只回傳快取內容
    assert status in ["CACHE_ONLY", "AUTO"]
```

### 3.3 驗證清單

| 驗證項目 | 執行指令 |
|----------|----------|
| 向後相容 | `python -c "from translation_tool.core.lm_translator_main import translate_batch_smart; translate_batch_smart([])"` 正常 |
| 參數傳遞 | `python -c "from translation_tool.core.lm_translator_main import translate_batch_smart; translate_batch_smart([], dry_run=True)"` 正常 |
| 測試通過 | `pytest tests/test_lm_translator_dry_run.py -v` |

---

## 四、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| API 簽名變更 | **中** | 保留預設值，向後相容 |
| 呼叫端漏改 | 中 | 搜尋所有 `translate_batch_smart` 呼叫 |
| 測試失敗 | 低 | 先跑現有測試確認基準 |
| 行為改變 | 低 | 預設值維持原本行為 |

---

## 五、實作檢查清單

### Phase 0：盤點
- [ ] 搜尋所有 `translate_batch_smart` 呼叫點：`rg "translate_batch_smart" --glob "*.py" .`
- [ ] 確認現有測試可通過

### Phase 1：實作
- [ ] 移除全域變數（或標記為 deprecated）
- [ ] 新增函數參數：`dry_run`, `export_cache_only`
- [ ] 設定預設值：`DEFAULT_DRY_RUN`, `DEFAULT_EXPORT_CACHE_ONLY`
- [ ] 更新內部邏輯使用參數而非全域變數

### Phase 2：呼叫端
- [ ] 檢視呼叫端清單
- [ ] 決定是否需要修改（維持預設則不用）

### Phase 3：驗證
- [ ] 執行 `python -m py_compile` 語法檢查
- [ ] 執行 `python -c "import"` 確認匯入正常
- [ ] 執行 `pytest tests/test_lm_translator_main.py -v`
- [ ] 執行 `pytest tests/test_lm_translator_dry_run.py -v`

### Validation checklist：
- [ ] 向後相容：舊有呼叫 `translate_batch_smart(items)` 正常運作
- [ ] 新功能：測試可使用 `translate_batch_smart(items, dry_run=True)`
- [ ] 測試通過：所有現有測試通過

---

## 六、預估工作量

| 項目 | 行數變更 |
|------|----------|
| `lm_translator_main.py` | +5（參數定義）, -2（全域變數可移除或標記 deprecated） |
| 呼叫端修改 | 視呼叫點數量而定（維持預設則不用改） |
| 測試驗證 | - |
| **總計** | ~5-50 行 |

---

## 七、決策點

**是否現在實作？**

| 選項 | 優點 | 缺點 |
|------|------|------|
| **現在做** | 改善測試性與執行緒安全 | API 簽名變更需謹慎 |
| **稍後做** | 避免風險 | 技術債累積 |

**建議**：由於風險中等，可安排在 PR-1（Race Condition）完成後再做，確保基礎設施穩定。
