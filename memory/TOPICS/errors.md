# 錯誤踩坑 知識索引
> 蒸餾日期：2026-03-25
> 來源：memory/decisions.v2.md、memory/2026-03-24-subagent-results-verification.md、AGENTS.md

---

## 核心知識點

1. **精準讀檔策略** - 先 `Select-String` 拿行號 → 小範圍 read（±20 行）→ 每次小改 20-50 行。對話 > 80k tokens 主動建議 `/reset`。禁止暴掃 `dist/`、`node_modules/`、整個 workspace。- 來源：P-2026-02-15-PRECISE-READING-WINDOW、D-2026-03-23-PRECISE-READ-STRATEGY

2. **ENOENT / 路徑解析錯誤處理** - 先查 LanceDB / memory 決策 → 若需原文再查 QMD → 只有記憶層無結論時才進入程式碼搜尋。搜尋前先縮到單一目標。禁止暴掃。- 來源：P-2026-03-09-PATH-DEBUG-RECALL-FIRST

3. **PowerShell 處理 UTF-8 中文會亂碼** - 含中文的文字檔處理（JSONL / session log / UTF-8 檔案）一律 Python。PowerShell 只用於不需要處理中文的簡單系統指令。- 來源：AGENTS.md [LEARNED_RULES]

4. **`write` 不能拿空字串建 `.gitkeep`** - 空 `content=""` 會被當成缺參數，正確做法：exec + `New-Item` 建空檔，或寫入非空內容。- 來源：2026-03-09-session-memory-pitfalls.md

5. **CLI 批次處理原則** - 批次大小 20 / timeout 300s per batch / 成功後才寫 cache / 單批失敗停止後續批次不盲跑。- 來源：P-2026-03-16-CLI-TIMEOUT-BATCH-POLICY

6. **Ollama 不穩定時的處理** - 先手動測 `ollama list` 確認模型在 → 加 `--continue-on-error` 參數慢慢跑 → 避開凌晨高峰期。- 來源：D-2026-03-23-BATCH-ERROR-HANDLING

7. **Sub-agent timeout → 主線立即接手** - 接管前讀一次目標檔案確認現有內容。若 sub-agent 已有產出，直接用其結果不重複產出。- 來源：AGENTS.md [LEARNED_RULES]

---

## 常見踩坑

1. **Sub-agent fan-out 失控（最多 3 顆）** - 一次開太多 sub-agent 導致 timeout 與結果遺失。解法：任何 sub-agent 任務先確認不超過 3 顆。- 來源：2026-03-24-subagent-results-verification.md

2. **Sub-agent 結果未驗證** - 沒有在 sub-agent 回來後檢查磁碟寫入。解法：完成後立刻 exec 確認，不假設。- 來源：2026-03-24-subagent-results-verification.md

3. **PowerShell 讀 UTF-8 中文檔** - 直接用 `Get-Content` 讀會乱码。解法：用 Python 讀或設定 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`。- 來源：TOOLS.md

4. **write 空字串建 .gitkeep 失敗** - `Missing required parameter: content`。解法：用 exec + New-Item。- 來源：2026-03-09-session-memory-pitfalls.md

5. **page.on_error 無法捕獲 UI handler 異常** - 解法：驗證 Flet API 行為後再用。- 來源：AGENTS.md
