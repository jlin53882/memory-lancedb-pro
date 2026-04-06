# PR 設計：rules_view 拆分優化

> 設計日期：2026-03-17
> 狀態：待審核

---

## 一、現況分析

### 1.1 問題位置（已驗證）

| 檔案 | 行數 | 驗證方式 |
|------|------|----------|
| `app/views/rules_view.py` | 658 | line count |
| `app/views/rules_view.py` | 多個 DataTable | Select-String |

### 1.2 問題說明

- `rules_view.py` 有 658 行，職責過多
- 包含多個 DataTable（規則設定）
- 與 cache_view 類似，一次建立所有 UI

---

## 二、優化設計

### 2.1 拆分方案

將 `rules_view.py` 拆分為：

| View | 檔案 | 職責 |
|------|------|------|
| RulesMainView | `rules/rules_main_view.py` | 規則列表總覽 |
| RulesEditView | `rules/rules_edit_view.py` | 規則編輯 |

### 2.2 具體優化

- Tab 切換時才載入對應資料
- DataTable 使用分頁
- 搜尋加入 debounce

---

## 三、實作檢查清單

### Phase 1: 建立目錄結構
- [ ] 建立 `app/views/rules/` 目錄
- [ ] 建立 `__init__.py`

### Phase 2: 拆分 View
- [ ] 建立 RulesMainView
- [ ] 建立 RulesEditView

### Phase 3: 更新 Registry
- [ ] 更新 view_registry.py
- [ ] 測試切換

---

## 四、Validation checklist

- [ ] 規則列表顯示正確
- [ ] 規則編輯功能正常
- [ ] 切換流暢

---

## 五、預估工作量

| 項目 | 行數變更 |
|------|----------|
| 新建目錄 | +2 |
| RulesMainView | ~300 |
| RulesEditView | ~300 |
| 測試驗證 | - |
| **總計** | ~600 行 |
