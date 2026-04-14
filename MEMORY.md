# MEMORY.md — 專案長期記憶

> 最後更新：2026-04-07
> 用途：每次 session startup 時自動注入的核心上下文
> 蒸餾自：舊 workspace memory/（~300 個 .md 檔案）+ 2026-04-07 工作指南蒸餾

---

## 專案概述

### memory-lancedb-pro（主要專案）
- **Repo**：upstream `CortexReach/memory-lancedb-pro` / fork `jlin53882/memory-lancedb-pro`
- **本地路徑**：`C:\Users\admin\.openclaw\memory-lancedb-pro`
- **我們的角色**：Contributor（透過 fork + PR 貢獻）
- **核心技術**：TypeScript、LanceDB、BM25 Retrieval、Weibull Decay、Reflection System
- **主要維護者**：rwmjhb（最終裁決）、AliceLJY（架構方向確認）
- **開發模式**：Issue 提案 → 維護者確認方向 → 實作 → PR → Review → Merge

### Minecraft 翻譯（minecart_translator_flet）
- **路徑**：`C:\Users\admin\Desktop\minecraft_translator_flet`
- **用途**：將 Minecraft 簡體中文（zh_cn）翻譯為台灣慣用語（zh_tw）的桌面工具
- **核心技術**：Python、opencc（簡繁轉換）、ftb_snbt_lib（NBT 解析）、Flet 0.82.2 UI
- **翻譯流程**：zh_cn → reverse_index 對照 → replace rules → zh_tw；CJK 值跳過 replace rules

### two_project（Minecraft 翻譯第二階段）
- 相關決策與實作細節見 memory/TOPICS/minecraft-translator.md

### ai-程式修改助手（Discord bot）
- **頻道**：#ai-程式修改助手（channel_id: 1476866394556465252）
- **用途**：協調開發工作流，管理 Minecraft 翻譯專案，執行 PR 流程
- **主要工具**：OpenClaw + MiniMax M2.7 模型

---

## 核心架構決策

| 決策 | 結論 | 日期 |
|------|------|------|
| Flet 版本標準 | 0.82.2（2026-03-22 建檔） | 2026-03-22 |
| PR 工作流 | 接到 PR 任務立刻建 feature branch，branch 內完成實作與驗證；大 PR 用疊加策略拆分成多個小 PR | 2026-03-20 |
| 維護者驅動節奏 | 所有 Feature 必須先在 Issue 提案等維護者確認方向，不能假設「沒反對=可以做」| 2026-04-04 |
| Gateway restart | 必先通知 James（含離線預警），由 James 手動執行 | 2026-02-25 |
| 每日更新 cron | B 方案：update+restart job → 獨立 verify job（避免通知中斷） | 2026-02-25 |
| 記憶系統分工 | QMD 查原文（長篇 SOP）；LanceDB 存精煉結論 | 2026-02-28 |
| decisions.v2.md | 為唯一 canonical 決策來源；decisions.md 已棄用 | 2026-03-23 |
| memory-lancedb-pro | 三坑：絕對路徑 / apiKey 無空白 / JSON 反斜槓轉義 | 2026-03-23 |
| Sub-agent 策略 | M2.7 預設；timeout → 立即切 M2.5；hard limit 10 顆 | 2026-03-21 |
| PowerShell vs Python | 含中文的文字處理統一 Python；PowerShell 只做簡單系統指令 | 2026-03-24 |
| Flet API 驗證 | `ft.Page()` 無法不帶參數實例化；使用前先驗證行為 | 2026-03-20 |

---

## 重要踩坑（已驗證）

| 問題 | 根因 | 解法 |
|------|------|------|
| Rule 1315「飽和→飽食」破壞翻譯 | replace rules 對 CJK 值錯誤觸發 | 停用 Rule 1315；CJK 值跳過 replace rules |
| 忘記跑 pytest 直接起動 | 跳過測試步驟 | 修改→備份→pytest→起動三步缺一不可 |
| `__pycache__` 造成測試失敗假象 | 快取殘留 | 清除後再測；James 報失敗第一句問快取 |
| PowerShell redirect 造成檔案截斷 | PowerShell 編碼問題 | 統一用 write tool（自動 UTF-8）|
| Sub-agent 說要做但沒做 | 沒有驗證產出 | 完成後檢查 git status 和完整輸出 |
| `page.on_error` 無法捕獲 UI handler 異常 | 只能捕 page-level 錯誤 | handler 內部自己 try/except |
| PR head branch ≠ local branch | PR number 對應的 head branch 名稱未知 | 先 `gh api --jq '.head.ref'` 確認再 push |
| PowerShell `>` 重新導向造成 CRLF 錯誤 | `\n` 被轉成 `\r\n`，多次 `>` 疊加 | 含中文檔案操作統一用 Python script |
| GitHub 中文 body 控制字元 | PowerShell 直送 `--body` 中文有 cp950 編碼問題 | 一律用 `--body-file` |

---

## James 的偏好

- **語言**：繁體中文回覆，技術術語保留英文原文
- **互動風格**：溫暖聊天，但內容要有重點
- **天氣查詢**：優先使用 weather skill（Open-Meteo/wttr.in），不用 web_search/Brave
- **天氣位置**：「新品苑」= 新北市淡水區新市三路一段 276 號（座標 25.1973082, 121.4297521）
- **通知範圍**：只通知 James 負責內容的相關訊息
- **檔案編碼**：所有中文檔案寫入時必須使用 UTF-8（用 write tool）
- **破壞性操作**：涉及刪除/覆寫/重啟/config 變更 → 先告知影響 + 等確認
- **Gateway restart**：通知 James（含「重啟後 agent 會暫時離線」預警），由 James 手動執行
- **工作完成確認**：Sub-agent 完成後檢查 git status；James 報失敗第一句問 `__pycache__`

---

## 共通指導原則摘要

> 詳細說明與觸發時機見 `docs/AI_WORKFLOW_MANUAL.md`（單一 canonical 檔案）

### 安全與確認原則（P1-P6）
| # | 原則 | 觸發時機 |
|---|------|---------|
| P1 | 「準備合併」= 純記錄，不執行任何變更 | PR 準備就緒 |
| P2 | 破壞性操作需 James 明確指令才能執行 | 任何變更意圖 |
| P3 | 重要架構決定先問再實作，不要假設「沒反對=可以做」 | 新功能實作前 |
| P4 | Push 完成後驗證 remote 包含正確內容 | 任何 push |
| P5 | Sub-agent 完成後：stat + 抽查內容 + 測試驗證 | 任何 Sub-agent 完成 |
| P6 | 禁止未經 James 同意自行重啟 OpenClaw Gateway | gateway restart 需求 |

### 準確性原則
| # | 原則 | 觸發時機 |
|---|------|---------|
| P7 | 模糊專案名 → 先 memory_recall / gh search repos 確認 | repo 名不確定 |
| P8 | PR 操作前用 `gh api --jq '.head.ref'` 確認 branch 名 | PR number 而非 branch 名 |
| P9 | 衝突解決後先 `git diff` 確認，再 continue | rebase 衝突場景 |
| P10 | 編輯任何檔案前先讀取；寫入後確認 | 所有檔案操作 |
| P11 | 複雜架構問題 → 先查 memory/ 中的現有設計文件 | 分析維護者回覆、Feature 設計 |
| P12 | 重要外部回覆 → 立即結構化，區分「已確認」vs「待確認」 | 收到重要訊息 |

### 工具使用原則
| # | 原則 | 觸發時機 |
|---|------|---------|
| P13 | 含中文/複雜操作 → Python script；PowerShell 只做簡單系統指令 | 檔案操作、shell 命令 |
| P14 | GitHub body → `--body-file` 而非 `--body` | gh cli 送中文內容 |
| P15 | 新建 TypeScript/JS 專案 → 第一個 commit 加 `.gitattributes` | 新 repo 初始化 |
| P16 | 對抗性 review 不只檢查實作，也要檢查：介面改變、測試覆蓋、整合問題 | PR review |

### 成長與學習原則
| # | 原則 | 觸發時機 |
|---|------|---------|
| P17 | 被糾正時不回嘴 → 認錯 → 記錄 → 確認不再犯 | 任何被 James 糾正 |
| P18 | PR 關閉後 → 在原 Issue 和原 PR 都要留言說明 redirect | PR 被關閉/重新導向 |
| P19 | SOUL.md 與 AGENTS.md 是綁定準則，修改任一請同步檢視另一個 | 任何準則修改場景 |
| P20 | 新 Feature 實作前 → 先在對應 Issue 提案（含 Architecture、Config、防禦機制）| Feature 實作前 |
| P21 | `sessions_list` timeout → 改用直接讀取 JSONL 檔案 + Python 解析 | gateway timeout |

---

## 常用工具與路徑

| 工具 | 路徑 |
|------|------|
| Minecraft 翻譯專案 | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| 新 workspace | `C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252` |
| 舊 workspace（已遷移） | `C:\Users\admin\.openclaw\workspace` |
| memory-lancedb-pro 本地 | `C:\Users\admin\.openclaw\memory-lancedb-pro`（fork，sub-agent 工作目錄）|
| decisions.v2.md（canonical） | `memory/decisions.v2.md` |
| AI 工作流程指南（canonical） | `docs/AI_WORKFLOW_MANUAL.md` |
| dev_process_flow.md | `docs/dev_process_flow.md` |
| Flet 0.82.2 知識庫索引 | `docs/flet-0822-knowledge-index.md` |
| QMD 搜尋 | `.\qmd.cmd search "關鍵字"` |
| 單一工作指南（canonical） | `docs/AI_WORKFLOW_MANUAL.md` |
| pytest（在專案 .venv） | `uv run pytest -q`（需先 cd 到專案目錄）|

---

## Discord 頻道對照

| 頻道 | channel_id | 用途 |
|------|------------|------|
| #ai-程式修改助手 | `1476866394556465252` | 本 agent——主要工作區 |
| #ai-小助理 | `1476858065914695741` | Review Claw / 稽核頻道 |
| #頭腦風暴 | `1476866144961822791` | 腦暴/規劃 |
| #監控警告 | `1476866274628997231` | 監控群（告警通知） |

---

## 共享任務接收 Protocol（shared/ 任務分流）

當 James 透過指揮中心派發任務時，任務會寫在 `~/.openclaw/workspace/shared/tasks/<taskId>.json`。

**收到任務後：**
1. 讀取 `shared/tasks/<taskId>.json`，理解任務內容
2. 建立 `shared/status/<taskId>.status.json`（status=in_progress）
3. 執行任務
4. 在 `shared/results/<taskId>__dc-channel--1476866394556465252-result.json` 寫入結果
5. 更新 `shared/status/<taskId>.status.json`（status=completed）

**任務成功標準：**
- 程式碼能編譯/執行
- 對應測試通過
- 沒有破壞其他功能

---

*本檔案為蒸餾產物（2026-03-25），由 sub-agent 從舊 workspace memory/ 萃取精華建立。*
*如需更新，請透過 MEMORY.md 更新流程處理，勿直接修改。*
