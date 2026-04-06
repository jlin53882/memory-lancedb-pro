# Minecraft 翻譯 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/

---

## 核心知識點

1. **依賴套件三本柱**
   - 內容：`opencc`（簡繁轉換，s2t/t2s）、`ftb_snbt_lib`（NBT 標籤解析）、`markdown_it`（Markdown 解析）
   - 來源：minecraft_translator_deps_learning.md

2. **zh_tw 翻譯含 CJK 時不走 replace rules（已驗證）**
   - 內容：當 `tw_val` 含 CJK 字元時，跳過 `apply_replace_rules()`，直接保留原文
   - 來源：2026-03-20-translation-rule-bug-fix.md

3. **Rule 1315「飽和→飽食」破壞正確翻譯**
   - 內容：Rule 1315 匹配 `飽和→飽食`，但「飽和度」是 saturation 正確譯名，被錯誤改成「飽食度」。解決：停用該規則或縮小範圍
   - 來源：2026-03-20-translation-rule-bug-fix.md

4. **刷怪籠→生怪磚（Rule 1092）為正確翻譯**
   - 內容：James 確認 `yog.spawner.setting` 的 `刷怪籠→生怪磚` 為正確台灣慣用語，不應回退
   - 來源：2026-03-20-translation-rule-bug-fix.md

5. **lang_merge_pipeline 的 intermediate directory 剝離邏輯**
   - 內容：`lang_merge_pipeline.py` 處理輸出 ZIP 時需剝離 `lang_merge_content_copy` 這層目錄結構，否則路徑錯誤
   - 來源：2026-03-21-lang-merge-pipeline-fix.md

6. **errordata_dir 參數缺失 bug**
   - 內容：`lang_merge_content_copy.py` 呼叫 quarantine 時缺少 `errordata_dir` 參數，需同步補上
   - 來源：2026-03-21-lang-merge-pipeline-fix.md

7. **專案根目錄：`C:\Users\admin\Desktop\minecraft_translator_flet`**
   - 內容：所有路徑以專案根目錄為準
   - 來源：minecraft_translator_deps_learning.md

8. **reverse_index 用途與翻譯流程**
   - 內容：用於將英文字串對應回原始 key，協助翻譯品質管理
   - 來源：2026-02-24-minecraft-translator.md

9. **KubeJS 翻譯相關**
   - 內容：KubeJS 物品/方塊 key 的命名需要對照台灣慣用語，reverse_index 可輔助查詢
   - 來源：2026-02-24-minecraft-translator.md

10. **模組驗證流程（每個 PR 必跑）**
    - 內容：修改後依序執行 `python -m py_compile`（語法）→ `uv run pytest -q`（測試）→ `uv run main.py`（起動驗證）
    - 來源：2026-03-19-forgot-pytest-lesson.md

---

## 常見踩坑

1. **Rule 1315 錯誤覆寫「飽和度」**
   - 問題：Rule 1315 將 `飽和` 替換成 `飽食`，破壞了 Minecraft 食物系統的 saturation 翻譯
   - 解法：停用該規則；或確認 Rule 1315 的上下文確實是「吃飽」而非「飽和度」後再啟用
   - 來源：2026-03-20-translation-rule-bug-fix.md

2. **zh_tw 值含 CJK 時仍觸發 replace rules**
   - 問題：pipeline 邏輯 `if tw_val and has_cjk(tw_val)` 會對含 CJK 的值執行 `apply_replace_rules`，Rule 1315 在此被觸發
   - 解法：對含 CJK 的 zh_tw 值，跳過所有 replace rules，直接保留原始翻譯
   - 來源：2026-03-20-translation-rule-bug-fix.md

3. **忘記跑 pytest 直接起動**
   - 問題：2026-03-19 因跳過 pytest 直接起動，導致問題未被及時發現
   - 解法：修改 → 備份 → `uv run pytest -q` → `uv run main.py`，三步缺一不可
   - 來源：2026-03-19-forgot-pytest-lesson.md
