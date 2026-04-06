# KubeJS 翻譯流程 DRY RUN 驗證報告

**驗證日期**: 2026-03-23
**測試資料**: `C:\Users\admin\Desktop\.minecraft\versions\All the Mods 10 4.3測試\測試 kubejs處理資料\All the Mods 10 5.2`
**專案路徑**: `C:\Users\admin\Desktop\minecraft_translator_flet`

---

## 1. 執行的指令

### 1.1 Step 1 Extract + Clean（不走翻譯 API）

```python
from translation_tool.core.kubejs_translator import step1_extract_and_clean

result = step1_extract_and_clean(
    pack_or_kubejs_dir=TEST_DATA,
    raw_dir=RAW_DIR,
    pending_dir=PENDING_DIR,
    final_dir=FINAL_DIR,
    session=None,
    progress_base=0.0,
    progress_span=0.33,
)
```

### 1.2 Color Char Checker

```python
from translation_tool.checkers.color_char_checker import check_directory

errors = list(check_directory(dir_path))
```

---

## 2. 觀察到的輸出摘要

### 2.1 Step 1 Extract + Clean 結果

| 項目 | 數值 |
|------|------|
| 解析到的 KubeJS 目錄 | `...\All the Mods 10 5.2\kubejs` |
| 提取的檔案數 | 157 |
| 提取的總 key 數 | 40,294 |
| 處理群組數 | 62 |
| 產出待翻譯 (pending) | 0 個 lang 檔 |
| 產出完成品 (final) | 62 個 zh_tw.json |
| 複製的其他 JSON | 11 個 (client_scripts) |

### 2.2 PENDING 目錄內容

共 **11 個 JSON 檔案**（皆為 client_scripts 相關）：

| 檔案 | 大小 |
|------|------|
| `client_scripts/Mekanism-Tooltips.json` | 2,184 bytes |
| `client_scripts/ponder/fission_mek.json` | 309 bytes |
| `client_scripts/ponder/fission_mek_fuelrod.json` | 598 bytes |
| `client_scripts/ponder/fission_mek_logic.json` | 820 bytes |
| `client_scripts/ponder/fission_mek_port.json` | 413 bytes |
| `client_scripts/ponder/fusion_activate.json` | 636 bytes |
| `client_scripts/ponder/fusion_reactor.json` | 685 bytes |
| `client_scripts/ponder/induction_mek.json` | 646 bytes |
| `client_scripts/ponder/sps.json` | 632 bytes |
| `client_scripts/ponder/turbine_mek.json` | 1,306 bytes |
| `client_scripts/tooltips.json` | 6,984 bytes |

### 2.3 FINAL 目錄內容

共 **62 個 zh_tw.json 檔案**，總輸出約 **122KB+**（zh_tw.json 內容已經過 OpenCC s2t 轉換）。

---

## 3. rich_text_shield.py 驗證結果

### 3.1 現況

| 項目 | 狀態 |
|------|------|
| `rich_text_shield.py` 原始碼檔案 | ❌ **不存在**（只有 `.pyc` 快取） |
| `kubejs_translator_clean.py` 的 shield import | ❌ **未使用** |
| 物品 ID 保護 (`#minecraft:diamond`) | ❌ **未實現** |
| 色彩碼保護 (`&aHello&r`) | ❌ **未實現** |

### 3.2 重要發現

1. **`rich_text_shield.py` 原始碼已遺失**：只存在 `__pycache__/rich_text_shield.cpython-312.pyc` 編譯快取，但原始 `.py` 檔案不存在。

2. **`kubejs_translator_clean.py` 未使用防護**：當前程式碼直接呼叫 `safe_convert_text_fn(v_cn)` 而沒有先經過 `shield_text()` 保護。

3. **之前 `read` 工具看到的 shield import 是過時快取**：inject context 中的程式碼片段顯示有 shield import，但實際檔案已不包含該 import。

### 3.3 預期行為 vs 實際行為

| 情境 | 預期行為 | 實際行為 |
|------|---------|---------|
| 物品 ID `#minecraft:diamond` | 應該被 `$P0$` 保護，不被 OpenCC 轉換 | ❌ 直接被轉換 |
| 色彩碼 `&aHello&r` | 應該被 `$C0$` 保護，不被 OpenCC 轉換 | ❌ 直接被轉換 |
| OpenCC 轉換時的保護 | 翻譯前 shield → 轉換 → unshield | ❌ 無保護直接轉換 |

---

## 4. color_char_checker.py 驗證結果

### 4.1 檢查結果

| 目錄 | 結果 | 錯誤數 |
|------|------|--------|
| PENDING 目錄 | ✅ 無非法顏色字元 | 0 |
| FINAL 目錄 | ❌ 有非法顏色字元 | 28 |
| RAW 目錄 | ❌ 有非法顏色字元 | 53 |

### 4.2 FINAL 目錄錯誤範例

錯誤幾乎全部來自 `assets/evilcraft/lang/zh_tw.json`，原因是 OpenCC s2t 轉換後產生了非法的 `&N` 色彩碼：

```
Key: info_book.evilcraft.second_age.weapons.mace_of_destruction.text
位置 4 發現非法顏色字元 '&扭'

Key: info_book.evilcraft.second_age.tools.broom.modifiers.text.levitation
位置 9 發現非法顏色字元 '&N'
```

### 4.3 RAW 目錄錯誤來源

錯誤主要來自 `ru_ru.json`（俄文）等原始檔案，這些是原始資料的問題，不是翻譯流程造成的。

---

## 5. 總結

### 5.1 修改前/修改後差異點

| 項目 | 當前狀態 (DRY RUN) | 預期狀態 |
|------|-------------------|---------|
| Step 1 提取+清理 | ✅ 正常運作 | ✅ 正常 |
| pending 目錄輸出 | ✅ 正確產生 11 個 client_scripts JSON | ✅ 正確 |
| final 目錄輸出 | ✅ 正確產生 62 個 zh_tw.json | ✅ 正確 |
| 物品 ID 保護 | ❌ 未實現（`#minecraft:diamond` 會被破壞） | ✅ 需要實現 |
| 色彩碼保護 | ❌ 未實現（`&a` 會被破壞） | ✅ 需要實現 |
| OpenCC 轉換時的 shield/unshield | ❌ 未實現 | ✅ 需要實現 |
| 非法色彩碼檢查 | ✅ PENDING 乾淨，但 FINAL 有 28 個錯誤 | ❌ 需要修復 |

### 5.2 待解決問題

1. **`rich_text_shield.py` 原始碼已遺失**：需要恢復或重新實作
2. **非法色彩碼問題**：FINAL 目錄有 28 個 `&N` 錯誤（來自 evilcraft）
3. **`kubejs_translator_clean.py` 未使用 shield**：需要整合 `shield_text()` 保護機制

---

## 6. 附錄：相關檔案路徑

| 檔案 | 路徑 |
|------|------|
| kubejs_translator.py | `translation_tool/core/kubejs_translator.py` |
| kubejs_translator_clean.py | `translation_tool/core/kubejs_translator_clean.py` |
| rich_text_shield.py | `translation_tool/plugins/shared/rich_text_shield.py` (❌ 不存在) |
| color_char_checker.py | `translation_tool/checkers/color_char_checker.py` |
| 測試資料 | `...\All the Mods 10 4.3測試\測試 kubejs處理資料\All the Mods 10 5.2` |
| 輸出目錄 | `...\All the Mods 10 5.2\Output\kubejs\` |
