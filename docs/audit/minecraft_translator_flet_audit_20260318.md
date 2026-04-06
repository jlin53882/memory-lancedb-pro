# Minecraft Translator Flet 專案稽核報告

> 稽核日期：2026-03-18  
> 專案路徑：`C:\Users\admin\Desktop\minecraft_translator_flet`

---

## 📊 專案概覽

| 指標 | 數值 |
|------|------|
| Python 檔案總數 | 159 個 |
| 測試個數 | 863 個 |
| 測試通過率 | 96% (829/863) |
| 測試收集錯誤 | 34 個 |

---

## 🔴 嚴重問題（需立即處理）

### 1. 依賴缺失導致測試失敗（34 個 import error）

以下模組缺失導致測試無法執行：

| 缺失模組 | 受影響測試數 | 受影響檔案 |
|----------|-------------|-----------|
| `opencc` | 27 個 | `text_processor.py`, `variant_comparator.py` |
| `ftb_snbt_lib` | 5 個 | `ftbquests_snbt_extractor.py`, `ftbquests_snbt_inject.py` |
| `pandas` | 1 個 | `variant_comparator_tsv.py` |

**受影響的測試檔案**：
- `test_ftb_translator*.py` (5 個)
- `test_kubejs_*.py` (4 個)
- `test_lang_merge_*.py` (5 個)
- `test_lm_view_characterization.py`
- `test_merge_view_characterization.py`
- `test_qc_*.py` (2 個)
- `test_variant_comparator*.py` (2 個)
- 以及其他 15+ 個測試檔案

**建議**：
```bash
pip install opencc-python-replaced opencc ftb-snbt-lib pandas
# 或確認 pyproject.toml 中的依賴是否完整
```

---

### 2. Flet API 版本不相容

**問題檔案**：
- `app\views\icon_preview_view.py:160` - `ft.FilePickerResultEvent`
- `app\views\translation_view.py:223` - `ft.FilePickerResultEvent`

**錯誤訊息**：
```
AttributeError: module 'flet' has no attribute 'FilePickerResultEvent'. 
Did you mean: 'FilePickerUploadEvent'?
```

**原因**：Flet 0.28.3 中 `FilePickerResultEvent` 已被移除或改名

**建議修復**：
```python
# 舊寫法
def _on_pick_source(self, e: ft.FilePickerResultEvent):

# 新寫法（需確認正確的 event 類型）
def _on_pick_source(self, e: ft.FilePickerResultEvent):  # 可能改為 
# 或查閱 Flet 0.28.3 API 文件
```

---

## 🟡 中等問題

### 3. 程式碼異味：Hardcoded Windows 路徑

以下檔案包含硬編碼的 Windows 路徑作為範例提示：

| 檔案 | 行號 | 內容 |
|------|------|------|
| `app\views\extractor_view.py` | 76 | `hint_text="C:\\Example\\Mods"` |
| `app\views\translation\translation_panels.py` | 35, 50, 64 | 多個 `C:\\Modpack` 範例路徑 |
| `translation_tool\plugins\ftbquests\ftbquests_snbt_extractor.py` | 295 | 日誌中的範例路徑 |

**影響**：可能造成跨平台相容性問題

**建議**：改用相對路徑或環境變數

---

### 4. Bare Except 子句

**檔案**：`analyze_coverage.py:21`

```python
except:  # 不推薦：會捕捉所有異常
    pass
```

**風險**：隱藏意外錯誤，難以調試

**建議**：
```python
except SpecificException as e:
    logger.error(...)
```

---

## 🟢 低優先級問題

### 5. TODO / FIXME 標記

| 檔案 | 行號 | 內容 |
|------|------|------|
| `app\views\cache_manager\panels\query_panel.py` | 51 | `# TODO: 實作搜尋邏輯` |
| `translation_tool\checkers\english_residue_checker.py` | 80 | `# NOTE: 原始的 check_untranslated.py 使用了 should_skip_lm_translation` |
| `translation_tool\core\ftb_translator.py` | 201 | `# NOTE: FTB pipeline does NOT use translate_directory_generator` |

---

### 6. 未使用函數分析（誤判問題）

**發現**：分析工具報告 192 個「未使用」函數

**驗證結果**：**絕大部分是誤判**

這些函數實際上是 **Flet UI 回調函數**，透過 Flet 的事件系統在執行期動態綁定，常見模式：

```python
class MyView(ft.Column):
    def __init__(self):
        self.btn = ft.Button(on_click=self.on_button_clicked)  # 動態綁定
    
    def on_button_clicked(self, e):  # 被分析工具標記為「未使用」
        pass  # 但執行期會被點擊事件觸發
```

**被錯誤標記的函數類型**：
- `*_clicked` - 按鈕點擊回調
- `*_picked` - FilePicker 回調
- `*_changed` - 狀態變更回調
- `did_mount` - Flet 生命週期鉤子
- `refresh*` - UI 刷新函數

**結論**：**不需要清理這些函數**，它們是 Flet 框架的正常用法

---

### 7. 相似函數名稱（15 組）

| 私有版本 | 公開版本 | 相似度 |
|----------|----------|--------|
| `_history_active_default` | `history_active_default` | 98% |
| `_update_stats_from_log` | `update_stats_from_log` | 98% |
| `_history_append_event` | `history_append_event` | 98% |
| `_detect_batch_profile` | `detect_batch_profile` | 98% |
| `_build_overview_page` | `build_overview_page` | 97% |
| ... | ... | ... |

**說明**：這些是 Python 私有/公開命名慣例的正常模式（私有版本為內部使用）

---

## ✅ 正常運作區域

### 測試覆蓋良好的模組

以下模組測試通過，架構良好：
- `translation_tool\core\lm_translator*` - 翻譯核心
- `translation_tool\core\lang_codec` - 語言編碼
- `translation_tool\utils\cache_*` - 快取管理
- `app\views\cache_manager\` - 快取 UI
- `app\services_impl\logging_service` - 日誌服務

---

## 📋 建議處理順序

| 優先級 | 問題 | 處理方式 |
|--------|------|----------|
| P0 | 依賴缺失 | 安裝 `opencc`, `ftb_snbt_lib`, `pandas` |
| P0 | Flet API 不相容 | 修正 `FilePickerResultEvent` 引用 |
| P1 | Bare except | 改為具體例外類型 |
| P2 | Hardcoded 路徑 | 考慮跨平台相容性 |
| P3 | TODO 標記 | 視情況實作或移除 |
| N/A | 「未使用」函數 | **無需處理**（Flet 回調） |

---

## 📁 附加分析：專案結構

```
minecraft_translator_flet/
├── app/
│   ├── services.py              # QC 服務 facade
│   ├── services_impl/           # 服務實作
│   │   ├── pipelines/           # 翻譯管線
│   │   ├── cache/               # 快取服務
│   │   ├── config_service.py    # 配置服務
│   │   └── logging_service.py   # 日誌服務
│   ├── views/                   # UI 視圖
│   │   ├── cache_manager/       # 快取管理（已模組化）
│   │   ├── config/              # 配置 UI
│   │   ├── extractor/           # 提取 UI
│   │   ├── rules/               # 規則 UI
│   │   └── translation/         # 翻譯 UI
│   └── ui/                     # UI 元件
├── translation_tool/
│   ├── core/                    # 翻譯核心
│   ├── plugins/                 # 外掛（FTBQuests, KubeJS, MD）
│   ├── utils/                   # 工具函式
│   └── checkers/                # QC 檢查器
└── tests/                       # 測試（863 個）
```

---

*報告生成工具：自製 Python 靜態分析腳本*
