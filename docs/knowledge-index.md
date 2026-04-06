# 知識庫索引 — ai-程式修改助手

> 最後更新：2026-03-25
> 蒸餾自：舊 workspace memory/（約 300+ 個 .md 檔案）

---

## 快速導航

| 類別 | 索引檔案 | 核心數量 |
|------|---------|---------|
| Minecraft 翻譯 | memory/TOPICS/minecraft-translator.md | 10 點 |
| Flet 桌面應用 | memory/TOPICS/flet-desktop.md | 10 點 |
| OpenClaw 設定 | memory/TOPICS/openclaw-config.md | 10 點 |
| PR/開發流程 | memory/TOPICS/pr-workflow.md | 10 點 |
| 錯誤踩坑 | memory/TOPICS/errors-lessons.md | 10 點 |
| 決策記錄 | memory/TOPICS/decisions.md | 14 點 |

---

## 最重要知識（前 10 名）

1. **PR 工作流鐵則（2026-03-20）**：接工作前讀手冊 → 建 feature branch → branch 內實作驗證 → 開 PR，**嚴禁先在 main做完再補 PR**
2. **Gateway restart 必先通知家豪**：所有重啟必須告知（含離線預警），由家豪手動執行重啟
3. **PowerShell 處理中文會乱码**：含中文的文字處理統一用 Python，PowerShell 只做簡單系統指令
4. **Rule 1315 破壞「飽和度」**：zh_tw 翻譯中「飽和→飽食」錯誤，停用該規則；CJK 值跳過 replace rules
5. **pytest 前先清除 `__pycache__`**：James 報測試失敗時，第一句問快取問題
6. **`decisions.v2.md` 是唯一 canonical**：舊 decisions.md 已棄用，衝突時舊決策標 `[Deprecated]`
7. **Flet 0.82.2：`ft.run()` 標準寫法**；`page.show_dialog(ft.SnackBar(...))` 取代舊寫法
8. **memory-lancedb-pro 三坑**：絕對路徑 / apiKey 無空白 / JSON 反斜槓轉義
9. **Sub-agent timeout → 主線立即接手**：接管前先讀目標檔案確認現有內容
10. **大量中文寫入用 write tool**：嚴禁 PowerShell redirect，會截斷檔案

---

## 各類別精華

### Minecraft 翻譯
- 專案路徑：`C:\Users\admin\Desktop\minecraft_translator_flet`
- 三本柱依賴：`opencc`（簡繁）、`ftb_snbt_lib`（NBT）、`markdown_it`
- 關鍵踩坑：Rule 1315 破壞 saturation 翻譯；CJK 值跳過 replace rules

### Flet 桌面應用
- 版本標準：0.82.2（2026-03-22 建檔，共 19 個檔案 229KB）
- `ft.run()` 取代 `ft.app()`；BasePage/Page 分層是 0.82.2 新增
- SnackBar 新寫法：`page.show_dialog(ft.SnackBar(...))`
- `page.on_error` 無法捕獲 UI handler 異常

### OpenClaw 設定
- 每日更新 cron：B 方案（update+restart → 驗證 job 分離）
- SecretRef 模式：密鑰不放明文，用 env source
- Sub-agent：M2.7 預設，timeout → 立即切 M2.5，hard limit 10 顆

### PR/開發流程
- AI_WORKFLOW_MANUAL.md 為主工作指南
- 驗證迴圈：Build → Types → Lint → Tests → Security → Diff
- 設計相關問題：先讀 `docs/dev_process_flow.md`
- GitHub Issue：body 必須 Markdown 語法，用 `--body-file` 上傳

### 錯誤踩坑
- PowerShell redirect 寫中文會截斷：統一 write tool
- `__pycache__` 造成測試失敗假象：先清除再測
- 破壞性失敗必須 raise：嚴禁 `return {}` 吞掉 exception

### 決策記錄（SSOT）
- canonical：`memory/decisions.v2.md`（25 條結構化決策）
- 記憶分工：QMD 查原文，LanceDB 存精煉結論
- 衝突處理：舊決策標 `[Deprecated]` 再立新結論

---

## 產出說明

本索引為**知識蒸餾**產物（2026-03-25），從舊 workspace `C:\Users\admin\.openclaw\workspace\memory\` 的 300+ 個 .md 檔案中萃取精華。

蒸餾原則：
- 只蒸餾 `.md` 檔（不處理 .json / .jsonl）
- 每個類別最多 10~14 個核心點
- 來源皆有標注原始檔案

相關檔案：
- `MEMORY.md` → 濃縮長期記憶（每次 session startup 注入）
- `docs/knowledge-index.md` → 本檔（類別導航）
- `memory/TOPICS/*.md` → 各類別詳細索引
