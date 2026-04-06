# PR 分支驗證報告

**驗證日期**：2026-03-23  
**專案路徑**：`C:\Users\admin\Desktop\minecraft_translator_flet`  
**驗證資料**：`C:\Users\admin\Desktop\.minecraft\versions\All the Mods 10 4.3測試\測試 kubejs處理資料\All the Mods 10 5.2`  
**重要**：全部 DRY RUN，未實際呼叫翻譯 API

---

## 分支：`pr/rich-text-shield` ✅

### 測試結果

| 項目 | 結果 |
|------|------|
| 模組 import | ✅ `from translation_tool.plugins.shared.rich_text_shield import shield_text, unshield_text` 成功 |
| 測試輸入 | `{"text": "Hello &aWorld #minecraft:diamond"}` |
| Shield 輸出 | `ShieldedText(clean='Hello $C0$World $P0$', ...)` |
| 色彩碼 `&a` 識別 | ✅ `&a` 被識別為 `category='color'` 並 shield |
| 物品ID `#minecraft:diamond` 識別 | ✅ `had_item_ref=True`，`category='item_id'` |
| Round-trip（shield→unshield） | ✅ 完全還原原文 |
| pytest | ✅ **1119 passed in 7.93s** |

### 備註
- `unshield_text()` 需要兩個參數：`unshield_text(clean_text, shields_list)`
- `ShieldedText` 不是可迭代物件，需用 `.clean` 屬性取得乾淨文本

---

## 分支：`pr/dual-track-dedup` ✅

### 測試結果

| 項目 | 結果 |
|------|------|
| 模組 import | ✅ `from translation_tool.core.kubejs_translator_clean import clean_kubejs_from_raw_impl` 成功 |
| reverse_index 邏輯位置 | ✅ 在 `clean_kubejs_from_raw_impl` 函式內，第 142–170 行（第 156–169 行為核心） |
| reverse_index 核心邏輯 | 建立 `final_tw_lookup` 的反向索引（英文文字 → 對應 key 列表），用於過濾「英文文字已存在於 final 的不同 key」，避免重複翻譯 |
| pytest | ✅ **1119 passed in 7.98s** |

### reverse_index 邏輯摘要
```
第 156 行：reverse_index: dict[str, list[str]] = {}
第 157-159 行：for k, v in final_tw_lookup.items(): if is_filled_text_impl(v): reverse_index.setdefault(v, []).append(k)
第 161-169 行：過濾 pending_en，跳過「英文文字已存在於 final 但 key 不同的項目」
```

---

## 分支：`pr/color-checker` ✅（但發現潛在 bug）

### 測試結果

| 項目 | 結果 |
|------|------|
| 模組 import | ✅ `from translation_tool.checkers.color_char_checker import check_color_chars, COLOR_PATTERN` 成功 |
| `check_color_chars("&aValid")` | ✅ 回傳 `None`（無錯誤，符合預期） |
| `check_color_chars("&zInvalid")` | ❌ **回傳 `None`（應回傳錯誤列表）** |
| pytest | ✅ **1119 passed in 8.48s** |

### ⚠️ 發現問題

**`COLOR_PATTERN` 正則表達式有誤**：

```
目前：&([^a-vz0-9\s\\#])
```

`[a-vz0-9\s\\#]` 這個字符類包含了 `z`，導致 `&z` 被視為合法 Minecraft 色彩碼。

**Minecraft 合法色彩碼**：`&0`-`&9`、`&a`-`&v`（`&w` 無效）。`z` 不在合法範圍內。

**修復建議**：將 `COLOR_PATTERN` 中的 `[a-vz0-9\s\\#]` 改為 `[a-v0-9\s\\#]`（移除 `z`）。

---

## 總結

| 分支 | 測試通過 | 狀態 |
|------|---------|------|
| pr/rich-text-shield | 1119/1119 | ✅ 功能正常 |
| pr/dual-track-dedup | 1119/1119 | ✅ 功能正常 |
| pr/color-checker | 1119/1119 | ⚠️ regex bug：`z` 被誤列為合法色彩字符 |
