# Minecraft 翻譯 知識索引
> 蒸餾日期：2026-03-25
> 來源：memory/minecraft_translator_deps_learning.md、2026-03-20-translation-rule-bug-fix.md

---

## 核心知識點

1. **opencc 簡繁轉換** - `OpenCC('s2t')` 支援 s2t/t2s/s2tw 等配置，基於詞典最長匹配。- 來源：minecraft_translator_deps_learning.md

2. **ftb_snbt_lib NBT 解析** - `parse()` 解析 `{Id:"minecraft:stone",Count:1}`，用 `write()` 寫回 NBT 字串。- 來源：minecraft_translator_deps_learning.md

3. **zh_tw 翻譯含 CJK 會觸發 replace rules** - Pipeline 對含 CJK 的 zh_tw 值會執行 `apply_replace_rules()`，可能破壞正確翻譯（如 Rule 1315 `飽和→飽食` 破壞了 `Saturation` 翻譯）。- 來源：2026-03-20-translation-rule-bug-fix.md

4. **Rule 1092 `刷怪籠→生怪磚` 為正確翻譯** - 確認 zh_cn→zh_tw 某些物品名稱確實有差異，需用網路資料驗證，不能只靠字面規則。- 來源：2026-03-20-translation-rule-bug-fix.md

5. **Rule 1092 與 Rule 1315 是完全獨立規則** - `籠`(U+7C60) ≠ `飽`(U+98FD)，兩者是不同字元，獨立匹配。- 來源：2026-03-20-translation-rule-bug-fix.md

---

## 常見踩坑

1. **Rule 1315 破壞 zh_tw 翻譯** - `apply_replace_rules()` 對含 CJK 的 zh_tw 值也會執行，Rule 1315 `飽和→飽食` 把正確的 `飽和度` 改成錯誤的 `飽食度`。解法：zh_tw 的 CJK 值應跳過 replace rules 或拆分 Rule 1315 排除特定語境。- 來源：2026-03-20-translation-rule-bug-fix.md

2. **markdown_it 解析** - `MarkdownIt().render()` 可將 Markdown 轉為 HTML。- 來源：minecraft_translator_deps_learning.md
