# SA-3 InstructionAnalyzer 報告

> 分析日期：2026-03-22
> 資料來源：LanceDB recall、session logs（2026-03-13 ~ 2026-03-21）、AGENTS.md LEARNED_RULES、MEMORY.md

---

## 誤解事件彙總

以下為實際從記憶庫與 session logs 中鉤出的誤解事件（非假設）：

| # | 日期 | 事件 | 類別 | 根因 |
|---|------|------|------|------|
| 1 | 2026-03-18 | PR5-PR7 設計稿聲稱「可執行」，實際有 4 個 P0 問題（super().__init__() 缺失、asyncio 不相容、_search() 未定義、目錄結構不完整）| 設計 | 没驗證 |
| 2 | 2026-03-19 | Flet UI 測試：`ft.Page()` 被假設可無參數實例化；`Icons.FILL_OUTLINED` 被假設存在於 Flet 0.28.3 | 設計/coding | 假設 |
| 3 | 2026-03-19 | Stock Trading：連續 3 輪宣稱「本地測試通過，是快取問題」，實際問題未真正解決 | coding | 没驗證 |
| 4 | 2026-03-19 | scraper.py 中 `total_assets = remaining_cash` 只算現金不算庫存，AI 未主動發現 | coding | 没驗證 |
| 5 | 2026-03-20 | 記憶（MEMORY.md 版本）與磁盤實際內容不一致時，堅持「記憶中是對的」| 操作 | 假設 |
| 6 | 2026-03-20 | `edit` 失敗後在同樣的 oldText 比對上盲試多次 | 操作 | 没驗證 |
| 7 | 2026-03-20 | PowerShell redirect 寫入中文檔案導致 UTF-8 截斷 | 操作 | 假設 |
| 8 | 2026-03-20 | PR 任務：先在 main 完成實作，再試圖補 feature branch（流程顛倒）| 工作流程 | 假設 |
| 9 | 2026-03-20 | 大量檔案處理前未計數，直接串流式 exec，導致 context 累積 timeout | 操作 | 没驗證 |
| 10 | 2026-03-21 | Sub-agent 正在跑就直接發新任務（sub-agent 間 quota 競爭）| 操作 | 假設 |

---

## 量化指標

```
總觀測 session 數（2026-03-13 ~ 2026-03-21）：約 7 個 session
含誤解/被糾正的 session 數：6 個
misunderstanding_rate：85%

具體修正次數（問題單論）：
  - A2（回答前未驗證事實）：3 次
  - F1（API 假設錯誤）：2 次
  - H2（串流式探索 timeout）：2 次
  - C1/G1（edit 盲試）：2 次
  - B1（PR 流程顛倒）：1 次
  - F2（UTF-8 截斷）：1 次
```

---

## top_ambiguous_categories

```json
[
  {
    "category": "設計（Design）",
    "frequency": "高（3 次重大誤解）",
    "example": "PR5-PR7 設計稿聲稱可執行，實際有 4 個 P0 問題；Flet API 假設錯誤（Page()/Icons）",
    "根因": "在未完整讀取相關檔案、未驗證 API 實際行為的情況下，直接輸出設計結論"
  },
  {
    "category": "事實驗證（Coding/操作）",
    "frequency": "高（5 次）",
    "example": "堅持「本地通過」未先確認 James 的磁盤狀態；edit 失敗後盲試而非重讀檔案",
    "根因": "用「我以為的」代替工具驗證；未遵守 SOUL.md 事實驗證強制規則"
  },
  {
    "category": "工作流程假設",
    "frequency": "中（2 次）",
    "example": "PR 任務先實作後補 branch；未收到觸發指令就開 PR",
    "根因": "對流程的前提假設與 James 實際要求不符（James 重視 PR 流程規範）"
  },
  {
    "category": "工具行為假設",
    "frequency": "中（2 次）",
    "example": "PowerShell redirect 中文處理；Windows 環境用 ls -la",
    "根因": "未確認 Windows 與 Unix 環境差異就直接套用"
  }
]
```

---

## vocab_supplement

> 建議補進 SOUL.md 或建立專用詞彙頁

```json
{
  "PR5": "minecraft-translator-flet 專案的 Pull Request #5（Cache View 重構，2026-03-18 實驗性 PR）",
  "PR7": "minecraft-translator-flet 專案的 Pull Request #7（cache_view UI 效能優化，2026-03-17）",
  "PR9": "minecraft-translator-flet 專案的 Pull Request #9（移除靜音 pass + 強化錯誤日誌，2026-03-17）",
  "PR35": "minecraft-translator-flet 專案的 Pull Request #35（Phase 2，2026-03-21）",
  "FTBQuest": "FTB Quests（ Minecraft 模組，用於任務/任務樹管理）",
  "OpenClaw": "家豪的 AI Agent 框架（基於 OpenClaw 專案）",
  "SnackBar": "Flet UI 的 SnackBar 元件；曾誤解 self.update() 與 self.page.update() 的適用場景",
  "CacheModalBase": "PR5-PR7 中的 Flet Modal 基礎類別（曾有多次 P0/P1 問題）",
  "CacheViewOptimized": "PR5-PR7 中的優化後 CacheView 類別",
  "super().__init__() 順序問題": "PR5-PR7 常見 P0：super().__init__() 必須在 self.page 初始化之後才能安全呼叫"
}
```

---

## implicit_context_map

> 建議補進 MEMORY.md 的隱性假設

```json
{
  "假設：James 的環境和本地（測試環境）完全一致": "說明：James 的磁盤內容可能落後於本地的 .pyc 快取。James 報失敗時，必須先問「清除 __pycache__ 了嗎」，不能直接說「本地通過」。",
  "假設：PowerShell redirect 支援 UTF-8 中文": "說明：PowerShell redirect 寫入中文時會截斷或變成 UTF-16。必須用 Python 或 write tool 處理中文寫入。",
  "假設：flet.ft.Page() 可無參數實例化": "說明：Flet 0.28.3 的 ft.Page() 需要 page 參數，不能直接調用。UI 測試需建立 MockPage。",
  "假設：設計搞產出後就等於「驗證完成」": "說明：James 的標準是「可執行」=實際能跑通過，而非語法正確。PR5-PR7 的4個P0問題就是在未實際跑的情況下聲稱可執行。",
  "假設：Windows 環境可以用 Unix 風格 shell 指令": "說明：Windows 環境統一用 Get-ChildItem / dir，ls -la 等 Unix 指令可能失效。",
  "假設：PR 工作流是先實作後補 branch": "說明：James 強調 PR 任務必須先建 feature branch 再實作。流程顛倒（B1）已被列為高優先錯誤。",
  "假設：MiniMax API 回應格式是確定的": "說明：曾混淆 Anthropic 格式與 OpenAI 格式，實際上有兩種格式差異（Stock Trading 任務中驗證）。"
}
```

---

## prompt_improvement_suggestions

```json
[
  {
    "優先": "高",
    "建議": "設計任務輸入時，強制觸發「設計前檢查清單」：① 相關程式碼完整讀取 ② API 存在性 rg 驗證 ③ 同步/非同步架構確認 ④ 實際執行語法檢查（py_compile）",
    "對應問題": "D1, PR5-PR7"
  },
  {
    "優先": "高",
    "建議": "James 提到「錯了/不對/重新」時，進入「驗證模式」：先完整讀取相關程式碼，再指出具體問題行號，嚴禁在未讀取的情況下回覆「了解，我重新...」",
    "對應問題": "A2, 編碼/操作類誤解"
  },
  {
    "優先": "高",
    "建議": "任何「本地通過」的聲明之前，必須先問 James 是否清除過 __pycache__；若 James 報失敗，預設是磁盤不一致而非代碼邏輯錯誤",
    "對應問題": "Stock Trading 3次循環"
  },
  {
    "優先": "中",
    "建議": "edit 失敗後：立刻放棄 oldText 比對，改用「重新 read + 整檔 write」策略，並記錄本次失敗到 ERRORS.md",
    "對應問題": "C1/G1"
  },
  {
    "優先": "中",
    "建議": "PR 任務接單前，必須先建立 feature branch；若發現自己在 main 上已實作，立即告知 James 並請求確認如何補救",
    "對應問題": "B1"
  },
  {
    "優先": "中",
    "建議": "James 專有詞彙（PR5/PR7/PR9/PR35、FTBQuest、SnackBar）建立主動識別：當 James 提到這些詞時，主動從記憶庫抓取相關上下文",
    "對應問題": "vocabulary gap"
  },
  {
    "優先": "低",
    "建議": "大量檔案處理前，先統計數量（exec count），未超過門檻（>50）不要直接開 sub-agent；結果寫入檔案，主線只讀摘要",
    "對應問題": "H1/H2"
  }
]
```

---

## 分析備註

- **資料限制**：memory_recall 以「不是這樣」等精確關鍵字未命中任何記憶（可能因語意差異或記憶尚未結構化）。本報告主要依據：(1) AGENTS.md LEARNED_RULES 的 14 個問題代碼索引，(2) session logs 中的具體誤解事件，(3) PR5-PR7 設計稿的 10 個版本的迭代記錄。
- **置信度**：問題代碼清單（A1-H4）來自 James 人工審核過的 self-review，故列為高置信度。vocab_supplement 來自記憶庫中的事實記錄，置信度中。implicit_context_map 為從錯誤事件反推的假設，置信度中偏低（建議 James 確認）。