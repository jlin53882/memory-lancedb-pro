# PR 設計：魔法數字重構

> 設計日期：2026-03-17
> 狀態：待審核

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行號 | 驗證方式 | 確認結果 |
|------|------|----------|----------|
| `translation_tool/core/lm_translator_main.py` | 583 | read | ✅ `wait_sec = 12` |
| `translation_tool/core/lm_translator_main.py` | 683 | read | ✅ `MIN_BATCH_SIZE if not is_lang else 20` |
| `main.py` | 41-44 | read | ✅ `1200, 850, 1050, 760` 視窗尺寸 |

### 1.2 問題說明

- **現況**：多處使用魔術數字（magic numbers），缺乏常數命名
- **風險**：日後修改需全域搜尋 + 手動替換，容易漏改
- **影響範圍**：
  - `lm_translator_main.py`
  - `main.py`
  - `app/view_registry.py`（可能使用視窗尺寸）

### 1.3 待重構清單

| 常數名稱 | 目前值 | 檔案:行號 |
|----------|--------|-----------|
| `RPM_COOLDOWN_SEC` | 12 | `lm_translator_main.py:583` |
| `MIN_LANG_BATCH_SIZE` | 20 | `lm_translator_main.py:683` |
| `WINDOW_WIDTH_DEFAULT` | 1200 | `main.py:41` |
| `WINDOW_HEIGHT_DEFAULT` | 850 | `main.py:42` |
| `WINDOW_MIN_WIDTH` | 1050 | `main.py:43` |
| `WINDOW_MIN_HEIGHT` | 760 | `main.py:44` |

---

## 二、重構設計

### 2.1 解決方案：常數集中定義

```python
# ========== lm_translator_main.py 頂部 ==========
# =========================================================
# Time Constants
# =========================================================
RPM_COOLDOWN_SEC = 12  # RPM 限制冷卻秒數
OVERLOAD_RETRY_WAIT_SEC = 12  # Overload 重試等待秒數

# =========================================================
# Size Constants
# =========================================================
MIN_LANG_BATCH_SIZE = 20  # Lang 類型最小批次大小
DEFAULT_BATCH_SIZE = 50  # 預設批次大小


# ========== main.py 頂部 ==========
# =========================================================
# Window Constants
# =========================================================
WINDOW_WIDTH_DEFAULT = 1200
WINDOW_HEIGHT_DEFAULT = 850
WINDOW_MIN_WIDTH = 1050
WINDOW_MIN_HEIGHT = 760
```

### 2.2 修改對照表

| 檔案 | 行號 | 重構前 | 重構後 |
|------|------|--------|--------|
| `lm_translator_main.py` | 583 | `wait_sec = 12` | `wait_sec = OVERLOAD_RETRY_WAIT_SEC` |
| `lm_translator_main.py` | 683 | `20` | `MIN_LANG_BATCH_SIZE` |
| `main.py` | 41 | `1200` | `WINDOW_WIDTH_DEFAULT` |
| `main.py` | 42 | `850` | `WINDOW_HEIGHT_DEFAULT` |
| `main.py` | 43 | `1050` | `WINDOW_MIN_WIDTH` |
| `main.py` | 44 | `760` | `WINDOW_MIN_HEIGHT` |

### 2.3 影響範圍

| 檔案 | 修改類型 | 說明 |
|------|----------|------|
| `lm_translator_main.py` | 常數定義 + 參考替換 | 頂部加常數區塊，替換 2 處參考 |
| `main.py` | 常數定義 + 參考替換 | 頂部加常數區塊，替換 4 處參考 |

---

## 三、測試策略

### 3.1 現有測試

- `tests/test_lm_translator_main.py` - 需確認通過
- `tests/test_main_imports.py` - 需確認匯入正常
- `tests/test_view_registry.py` - 需確認視窗尺寸正常

### 3.2 驗證方式

```bash
# 語法檢查
python -m py_compile translation_tool/core/lm_translator_main.py
python -m py_compile main.py

# 匯入測試
python -c "from translation_tool.core.lm_translator_main import RPM_COOLDOWN_SEC, MIN_LANG_BATCH_SIZE; print(RPM_COOLDOWN_SEC)"
python -c "from main import WINDOW_WIDTH_DEFAULT; print(WINDOW_WIDTH_DEFAULT)"
```

---

## 四、風險評估

| 風險 | 等級 | 緩解措施 |
|------|------|----------|
| 漏改參考 | 低 | 使用 IDE 搜尋替換（取代手動） |
| 向後相容 | 低 | 只改常數值，不改 API |
| 測試失敗 | 低 | 現有測試應不受影響 |

---

## 五、實作檢查清單

- [ ] Phase 0 盤點：確認現有測試可通過
- [ ] Phase 1：
  - [ ] 在 `lm_translator_main.py` 頂部加入 Time/Size Constants 區塊
  - [ ] 替換 `wait_sec = 12` → `wait_sec = OVERLOAD_RETRY_WAIT_SEC`
  - [ ] 替換 `else 20` → `else MIN_LANG_BATCH_SIZE`
  - [ ] 在 `main.py` 頂部加入 Window Constants 區塊
  - [ ] 替換 4 處視窗尺寸魔術數字
- [ ] Phase 2：
  - [ ] 執行 `python -m py_compile` 語法檢查
  - [ ] 執行 `python -c "from main import *"` 確認匯入正常
  - [ ] 執行 `pytest tests/test_lm_translator_main.py -v`
- [ ] Validation checklist：
  - [ ] `rg "RPM_COOLDOWN_SEC" translation_tool/` 確認有使用
  - [ ] `rg "MIN_LANG_BATCH_SIZE" translation_tool/` 確認有使用

---

## 六、預估工作量

| 項目 | 行數變更 |
|------|----------|
| `lm_translator_main.py` | +8（常數定義）, -0（替換不改行數） |
| `main.py` | +8（常數定義）, -0（替換不改行數） |
| 測試驗證 | - |
| **總計** | ~16 行 |
