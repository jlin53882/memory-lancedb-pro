# FLET_FIXES.md

## Flet 0.28.3 灰色區塊/灰畫面防呆清單

- 主要 View 佈局優先在 `__init__` 完成，避免把核心掛載放到 `build()`。
- 開啟全域錯誤入口：`page.on_error`，並落地寫 `exports/error.log`。
- 各頁 `did_mount()` 必加 `try/except`，錯誤要可見（SnackBar + log）。
- 灰畫面排查順序：事件有無進來 → layout 衝突 → 資料層。
- 避免高風險組合：`expand + scroll + 巢狀 expand`。
- 捲動區建議：固定高度容器 + 單一可控 scroll 容器。
- 結果清單優先 `Column + scroll`，減少 `ListView/expand` 巢狀衝突。
- 佈局調整策略：先確保可見，再逐步加功能；每次小改即驗證。
- 查詢分頁灰塊優先檢查：
  - tab host 是否加了多餘 `scroll/expand`
  - 分頁列是否用了 `Container(expand=True)` spacer
- 查詢/分類子 tab 需一致層級與撐高策略。
- 查詢歷史建議雙軌：
  - `cache_history/<cache_type>/jsonl/*.jsonl`（機器寫入）
  - `json/*.json`（人類可讀）
  - `jsonl/.history.active` 控制 rotate（每檔 10000 筆）
