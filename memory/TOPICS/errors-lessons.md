# 錯誤踩坑 知識索引

> 蒸餾日期：2026-03-25
> 來源：舊 workspace memory/

---

## 核心知識點

1. **PowerShell 處理 UTF-8 中文會乱码**
   - 內容：分析/統計/資料探索類 script 統一用 Python；PowerShell 只用於不需要處理中文的簡單系統指令
   - 來源：AGENTS.md [LEARNED_RULES]（2026-03-24 補充）

2. **大量中文寫入時用 write tool（自動 UTF-8）**
   - 內容：嚴禁 PowerShell redirect / `Set-Content` / `Out-File` 寫入中文，會截斷或乱码
   - 來源：AGENTS.md [LEARNED_RULES]

3. **破壞性失敗必須 raise，嚴禁 return {} 吞掉 exception**
   - 內容：解析/處理失敗時，`return {}` 等於隱藏錯誤，應 raise 讓錯誤明確曝光
   - 來源：AGENTS.md [LEARNED_RULES]

4. **`page.on_error` 無法捕獲 UI handler 異常**
   - 內容：`page.on_error` 只能捕獲 page-level 錯誤；按鈕等 UI handler 異常需在 handler 內部自己 try/except
   - 來源：AGENTS.md [LEARNED_RULES]

5. **Flet API 行為必須先驗證再用**
   - 內容：`ft.Page()` 無法不帶參數實例化；任何 API 使用前先確認實際行為
   - 來源：AGENTS.md [LEARNED_RULES]

6. **Windows 環境統一用 Get-ChildItem，不用 Unix 風格 ls -la**
   - 內容：系統指令在 Windows 環境的正確姿勢
   - 來源：AGENTS.md [LEARNED_RULES]

7. **Sub-agent timeout → 主線立即接手，不等待**
   - 內容：接管前讀一次目標檔案確認現有內容；sub-agent 已有產出直接用，不重複
   - 來源：AGENTS.md [LEARNED_RULES]（2026-03-24）

8. **Rule 1315 破壞 zh_tw「飽和度」翻譯**
   - 問題：「飽和」（saturation）被錯誤改成「飽食」（satiation）
   - 解法：停用 Rule 1315；含 CJK 的 zh_tw 值跳過所有 replace rules
   - 來源：2026-03-20-translation-rule-bug-fix.md

9. **pytest 執行前先確認專案目錄與 .venv**
   - 內容：執行 `python -m pytest` 前，先看測試檔案屬於哪個專案目錄，再 `cd` 進去。專案 `.venv` 有完整套件（ftb_snbt_lib、pandas），全域環境沒有
   - 來源：AGENTS.md [LEARNED_RULES]

10. **`__pycache__` 造成測試失敗假象**
    - 問題：James 報測試失敗時，可能只是快取問題而非真的失敗
    - 解法：清除 `__pycache__` 後再測試；收到失敗報告第一句問「清除 `__pycache__` 了嗎」
    - 來源：AGENTS.md [LEARNED_RULES]

---

## 常見踩坑（已驗證）

1. **忘記跑 pytest 直接起動（2026-03-19）**
   - 問題：修改後跳過測試步驟直接起動，導致問題未被及時發現
   - 解法：嚴格執行「修改→備份→pytest→起動」四步流程
   - 來源：2026-03-19-forgot-pytest-lesson.md

2. **批次修改未做完整模組驗證（2026-03-20）**
   - 問題：只驗一個模組就宣告完成，結果其他模組的 UI 傳入有問題
   - 解法：全部修改完成後跑完整模組驗證流程
   - 來源：2026-03-20-module-verification-fix.md

3. **Rule 1315 破壞 zh_tw 翻譯正確性（2026-03-20）**
   - 問題：規則匹配「飽和→飽食」，破壞了食物系統 saturation 的正確譯名
   - 解法：停用該規則；CJK 值跳過 replace rules
   - 來源：2026-03-20-translation-rule-bug-fix.md

4. **PowerShell redirect 造成檔案截斷**
   - 問題：大量中文內容寫入時用 PowerShell redirect，檔案內容被截斷
   - 解法：統一用 write tool 處理中文寫入
   - 來源：AGENTS.md [LEARNED_RULES]

5. **Sub-agent 說要做但沒做**
   - 問題：sub-agent 完成後沒有實際產出或產出不完整
   - 解法：每次 sub-agent 完成後檢查 `git status` 和完整輸出，發現問題立即自己補做
   - 來源：AGENTS.md [LEARNED_RULES]
