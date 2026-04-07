# AI 工作流程助手手冊（單一 Canonical 檔案）

> **Policy（可調整政策）** — 組織本地規則
> 本文件定義「這裡的人偏好什麼 / 允許什麼 / 禁止什麼」
> 版本：2026-04-07（確立為單一 canonical 檔案，整合所有 workflow 手冊）
> ⚠️ **鐵則**：所有 workflow 相關內容只能更新本檔案，嚴禁再建立新的 workflow 指南檔案。

---

## 一、黃金法則：驗證優先於假設

```
❌ 「應該是...」
❌ 「通常這種情況是...」
❌ 「我記得是...」（未驗證）

✅ 用工具驗證事實（read、rg、exec）
✅ 不確定時說「推測，需要驗證」
✅ 模型訓練知識 ≠ 當前事實（只能用於通用知識，須標注推測）
```

**驗證順序**：
```
工具驗證的當前結果 > MEMORY.md 長期記憶 > LanceDB 檢索 > 模型訓練知識
```

---

## 二、安全硬規則（常駐，不可省略）

> 完整版：`docs/policies/runtime-rules.md`

1. **破壞性操作先確認**：涉及刪除/覆寫/重啟/config 變更 → 先告知影響 + 等人類確認。
2. **Gateway restart 必先通知家豪**：內容須含「重啟後 agent 會暫時離線」預警。絕不默默重啟。Gateway 重啟一律由家豪手動執行。
3. **不確定就先問**：指令/參數不確定時，禁止猜測執行。
4. **零檢索不編造**：記憶庫無結果時，聲明「無相關決策可參考」，不捏造。
5. **檔案/路徑/寫入狀態：回覆前必先驗證**：必須用工具實際驗證。
6. **快慢路徑**：閒聊直接答；寫入/刪除/改碼/重啟 → Plan → Dry-run → 確認 → 執行。
7. **涉及維運決策時**，必須先查 `memory/decisions.v2.md` 或 LanceDB recall。

---

## 三、記憶架構與寫入規則

> 完整版：`docs/policies/memory-architecture.md`

### 3.1 三層記憶架構

| 層級 | 工具 | 用途 | 查詢方式 |
|------|------|------|---------|
| **L1：短期** | `active_state_discord.md` | 本次 session 工作進度、pending 事項 | 直接讀取 |
| **L2：中長期** | LanceDB（向量搜尋）| 已確認結論、偏好、決策 | `memory_recall` |
| **L3：長期** | `memory/*.md` | 每日原始日誌、詳細經驗 | `read` tool |

- **LanceDB**（優先查）→ 短結論、偏好、決策。autoRecall 自動注入，直接採用不質疑。
- **QMD**（需要時才翻）→ 長篇 SOP，日誌細節。
- **md 檔案**（最後手段）→ 人類可讀原文。
- **寫入原則**：寧可漏記，決不亂記。Sub-Agent 禁止擅自寫入 LanceDB。
- **衝突處理**：舊決策標 `[Deprecated]` 再立新結論（SSOT）。

### 3.2 記憶寫入規則

- 每條只存一個結論，新舊不混在同一條
- 必須包含：適用版本，最後驗證日期
- 新結論取代舊結論時，舊條目直接刪除不保留
- **why/根因欄只寫已驗證事實**；未驗證的推測假設一律標記 `[unverified]`
- 超過 15 行的條目標記待拆，交由使用者確認

### 3.3 統一標記格式（所有 Agent 強制使用）

| 標記 | 用途 | 範例 |
|------|------|------|
| `[重要]` | 需要記住的結論、關鍵發現 | `[重要]` 使用者偏好繁體中文回覆 |
| `[設定]` | API Key、密鑰、路徑、配置 | `[設定]` dbPath: ~/.openclaw/memory/ |
| `[決策]` | 做過的決定與原因 | `[決策]` Flet 0.82.2 獨立使用 namespace |
| `[學習]` | 新學到的知識、經驗 | `[學習]` page.on_error 無法捕獲 UI handler 異常 |
| `[待追蹤]` | 未完成事項、後續行動 | `[待追蹤]` PR#22 待 James 確認後合併 |

### 3.4 Memory Governance（2026-03-23 起生效）

- `memory/decisions.v2.md` 是 **唯一 canonical 決策來源**（`decisions.md` 已棄用，勿引用）
- 下列內容視為 **記憶污染候選**，預設不應進長期記憶：
  - `System: Model switched ...`
  - `[Subagent Context] ...`
  - `origin.json` / `_meta.json` / `issue_watch_*.json`

---

## 四、Task Routing 與 Discord Channel Skill SOP

> 詳細規則：`docs/dc-agent-skill-sop.md`

### 4.1 Task Routing

- ARCHITECTURE / RULE_SYNTHESIS → `brainstorm`（`-5289694977`）
- CODING / BUGFIX / REFACTOR → 這裡就是 code（`-5108601505`）

### 4.2 Discord Channel Skill SOP（2026-03-23 起生效）

收到任務後，除了判斷要不要開 sub-agent，還要額外做一次 **skill 觸發檢查**：

1. **P1-C 類（強制檢查）**：`self-improvement`、`agent-self-review`、`proactive-agent`
2. **P1-A 類（優先心智檢查）**：`agentlens`、`qmd`、`session-logs`、`healthcheck`、`batch-processor`、`find-skills`、`skill-vetting`
3. **P1-B 類（保留可用，不主動強推）**：`codex-quota`、`node-connect`、`opencode-controller`

---

## 五、依賴管理

### 5.1 用 uv

```
✅ uv sync              # 安裝依賴
✅ uv run python        # 執行
✅ uv run pytest        # 測試
❌ pip install          # 破壞環境
```

### 5.2 修改前必備份

```
修改任何檔案前 → 先建立備份
備份命名 → 檔案.bak 或 檔案_YYYYMMDD_HHMMSS.bak
```

### 5.3 修改後必驗證

```
修改後 → python -m py_compile 確認語法
失敗 → 立即還原
成功 → 才能繼續
```

---

## 六、溝通格式

### 6.1 回報格式

```
📋 任務摘要
- 做了什麼
- 關鍵決策
- 結果
- 下一步建議
```

### 6.2 等待明確指令

```
❌ 自己亂改
❌ 未確認就開 PR
✅ 等待家豪說「執行」「開始」才動作
```

### 6.3 結束語偵測

當 James 說「掰掰」「先這樣」「好了」「收工」「下班了」時：
- 判斷本次 session 有無新知識（系統決策、踩坑解法、環境設定修改）
- 有 → 詢問是否需要執行 /compress 或寫入 LEARNINGS.md
- 無 → 正常回應，不打擾

### 6.4 對外溝通的草稿機制

所有對外（GitHub / Discord / 任何第三人）的溝通，都要經過草稿 → James 確認 → 送出這個流程。

```
1. 理解要溝通的內容
2. 產生草稿（繁體中文）
3. 送給 James 確認（格式：「草稿如下，確認後我送出」）
4. James 確認 → 執行送出
```

**James 話語背後的意義**：

| James 說 | AI 應該做 |
|-----------|-----------|
| 「先規劃，不修改」 | 產生分析報告 / 設計草案，給 James 看過再動 |
| 「先說你打算怎麼做」 | 提出 plan，等 James 確認方向後再執行 |
| 「你建議怎麼做」 | 先分析，提供建議與選項，讓 James 做決定 |
| 「你覺得怎麼樣」 | 給出專業判斷，不要只回「好」|
| 「直接送」 | James 已確認，可以執行送出 |

---

## 七、每日回顧流程

### 7.1 回顧觸發時機

- 當 James 說「先這樣」「好了」「收工」等結束語時
- 主動提出：「今天有哪些地方做得不好，要記錄下來避免之後犯錯？」
- 如果 James 同意，執行每日回顧

### 7.2 回顧流程

```
Step 1：蒸餾當天做得不好的事
  → 找出具體錯誤案例
  → 分析根因（不是表面現象）
  → 對應的具體規則

Step 2：蒸餾當天做得好的事
  → 成功的模式
  → 可複用的做法

Step 3：Sub-agent 犯錯分析（如有）
  → 為什麼 sub-agent 會犯這個錯
  → 這個錯在 main session 會發生嗎

Step 4：蒸餾共通原則
  → 從不同專案任務中找共同模式
  → 寫入 .learnings/LEARNINGS.md
  → 高優先 learning 同步寫入 LanceDB
```

### 7.3 回顧寫入位置對照

| 類型 | 寫入位置 |
|------|---------|
| 工作中的錯誤/學習 | `.learnings/LEARNINGS.md` |
| 重要專案決策 | `memory/YYYY-MM-DD.md` + `decisions.v2.md` |
| 高價值長期經驗 | LanceDB（memory_recall 可查到）|
| 工具踩坑 | `TOOLS.md` 或 `.learnings/LEARNINGS.md` |
| 工具錯誤（gateway timeout 等）| `.learnings/ERRORS.md` |

### 7.4 蒸餾後 commit

回顧完成後將 `.learnings/LEARNINGS.md` 等變更 commit 到 git，確保記錄不遺失。

---

## 八、實戰紀律（2026-03-20 起累積）

### 8.1 pytest 執行規則
- 執行 `python -m pytest` 前，先看測試檔案屬於哪個專案目錄，再 `cd` 進去
- 該專案 `.venv` 有完整套件（ftb_snbt_lib、pandas 等），全域環境沒有

### 8.2 測試失敗處理
- **James 報測試失敗時**：第一句問「清除 `__pycache__` 了嗎」，不要先說本地通過
- **Sub-agent 完成後**：必須檢查 `git status` 和完整輸出；發現「說要做但沒做」的 sub-agent，立即自己補做

### 8.3 工作流程紀律
- PR 任務觸發當下立刻建立 feature branch，在 branch 內完成實作與驗證，絕不在 main 上先做完再補 PR
- 接到實作任務：先讀 `docs/AI_WORKFLOW_MANUAL.md` 對應章節，確認工作原則與驗證 SOP
- **每次 PR review 修正完成後**：一定要再跑一次 `pytest -q` 全域測試，確認所有單元測試通過後才能宣告完成

### 8.4 工具使用策略
- **Flet API 行為必須先驗證再用**：`ft.Page()` 無法不帶參數實例化
- **破壞性失敗必須 raise**：解析/處理失敗時嚴禁 `return {}` 吞掉 exception
- **大量中文寫入時，用 write tool（自動 UTF-8）**，避免 PowerShell redirect 造成檔案截斷
- **Windows 環境統一用 `Get-ChildItem`**，不用 Unix 風格的 `ls -la`

### 8.5 PowerShell vs Python 分工
- 含中文的文字檔處理（JSONL / session log / UTF-8 檔案）：**一律 Python**
- PowerShell 只用於不需要處理中文的簡單系統指令

### 8.6 分析類 Script 統一用 Python
- **PowerShell 處理 UTF-8 中文會亂碼**：分析/統計/資料探索類 script 統一用 Python

### 8.7 Minecraft 翻譯 Pipeline（2026-03-25）
- **zh_tw 含 CJK 會觸發 replace rules**：Pipeline 對含 CJK 的 zh_tw 值執行 `apply_replace_rules()`，Rule 1315 `飽和→飽食` 會破壞 `Saturation` 的正確翻譯。修法：zh_tw 的 CJK 值應跳過 replace rules 或拆分 Rule 1315 排除特定語境
- **`刷怪籠→生怪磚` 為正確翻譯**：zh_cn→zh_tw 某些物品名稱確實有差異，需用網路資料驗證，不能只靠字面規則

### 8.8 檔案寫入 BOM 問題（2026-04-01）
- **PowerShell Out-File -Encoding UTF8 / Copy-Item 會自動加 BOM**
- BOM (0xEF 0xBB 0xBF) 會導致 Node.js parse 失敗：ParseError: Unexpected character
- **修復**：用 Python 二進位寫入 ('wb')
- **禁止**：PowerShell Out-File -Encoding UTF8 / Copy-Item 寫入 JS/TS 原始碼

---

## 九、UI 收斂原則

> **核心問題：UI 任務如果沒有停損點，很容易變成時間黑洞。**

### 9.1 UI 可用標準

當 UI 達到以下標準時，應停止持續打磨，轉往功能與穩定性：
- 看得懂
- 按得到
- 不會誤操作
- 不影響主要流程

### 9.2 UI 時間黑洞的早期警訊

```
當出現以下訊號時，應主動提出停損建議：
- 已來回修改超過 2~3 輪
- 每次都在「太擠 ↔ 太空 ↔ 太散」之間來回
- 修改已經是「視覺微調」而非「功能改善」
- 花費的時間與實際價值不成比例
```

### 9.3 UI 停止條件

UI 優化如果沒有明確停損點，很容易從「可用」一路磨到「時間被吃光」。未來 UI 另開獨立任務，不與功能修改綁在一起。

---

## 十、專案任務共通原則

### 10.1 功能優先於美化

優先把時間放在：功能正確性、穩定性、測試、真正影響效率的流程問題。  
而不是：更漂亮、更像產品、更像正式設定頁。

### 10.2 實作優先於抽象辯論

遇到複雜架構問題：
1. 先讀實際程式碼
2. 小範圍實測驗證
3. 有了具體認知再討論

### 10.3 刪除/移除 PR 必填六欄位

任何刪除/移除/替換的 PR，論文中必須逐項補：
1. 為什麼要改
2. 為什麼能刪
3. 目前誰在用或沒人在用
4. 替代路徑
5. 風險
6. 如何驗證

不足的項目標 `[需確認]`。

---

## 十一、常用工具命令

```bash
# 目錄結構
Get-ChildItem -Recurse -File | Where-Object { $_.Name -notmatch "__pycache__" }

# 搜尋類別/方法
Select-String -Pattern "class |def "

# Python 語法驗證
python -m py_compile <file>.py

# Flet API 存在性驗證
uv run python -c "import flet as ft; print('xxx' in dir(ft.Page))"

# pytest 測試（需在專案目錄執行）
cd C:\Users\admin\Desktop\minecraft_translator_flet
uv run pytest -q

# Git 狀態
git status
git show HEAD --stat
git diff --cached

# PR 操作
gh pr list --state open --limit 10
gh pr view {N} --json title,body,state,url,files
gh api repos/{owner}/{repo}/pulls/{N} --jq '.head.ref'
```

---

## 十二、附錄

### 12.1 專案路徑

| 項目 | 路徑 |
|------|------|
| Minecraft 翻譯專案 | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| 本 workspace | `C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252` |
| 決策 canonical | `memory/decisions.v2.md` |
| 單一工作指南（canonical）| `docs/AI_WORKFLOW_MANUAL.md` |
| QMD 搜尋 | `.\qmd.cmd search "關鍵字"` |

### 12.2 GitHub Issue 回報格式
- **所有 gh issue create / edit 的 body 必須用 Markdown 語法**
- 正確流程：草稿先寫到 `.md` 檔 → 用 `--body-file` 上傳

### 12.3 驗證足跡
- 完成任何修改任務後，**必須用 read/list/exec 驗證磁碟狀態**，再回報完成
- 不得僅依賴 tool return 假設產出已落地
- 適用場景：sub-agent 完成後、本 agent 完成寫入後、執行刪除/搬遷後

### 12.4 Discord 附件上傳路徑
- `workspace-dc-channel--*` 路徑會被 OpenClaw 的 compiled JS 阻擋
- **正確流程**：附件上傳前先複製到 workspace/ 根目錄，再傳送

### 12.5 圖片任務
預設用 AI 視覺模型直接辨識。只有使用者明確要求才走 OCR。

---

## 十三、James 基本資料

### 13.1 身份與偏好

| 項目 | 內容 |
|------|------|
| 名字 | 家豪 |
| 語言 | 繁體中文（强制）；技術術語保留英文原文 |
| 時區 | Asia/Taipei（GMT+8） |
| 位置 | 新北市淡水區（新品苑），座標 25.1973082, 121.4297521 |
| 天氣查詢 | 優先使用 weather skill（Open-Meteo/wttr.in）|
| 互動風格 | 暖但有重點，不要機器人式回覆也不要廢話連篇 |
| 回覆格式 | 數學公式偏好純文字符號；程式碼註解使用繁體中文 |
| 檔案編碼 | 所有中文檔案寫入時必須使用 UTF-8（用 write tool）|
| 通知範圍 | 只通知與 James 相關的訊息，不要泛濫 |

### 13.2 Discord 頻道對照

| 頻道 | channel_id | 用途 |
|------|------------|------|
| #ai-程式修改助手 | `1476866394556465252` | 本 agent——主要工作區 |
| #ai-小助理 | `1476858065914695741` | Review Claw / 稽核 |
| #監控警告 | `1476866274628997231` | Cron 回報 |
| #頭腦風暴 | `1476866144961822791` | 規劃討論 |

---

## 十四、專案知識庫

> 接手新專案前必須先讀取對應章節。

### 14.1 專案 A：Minecraft 翻譯桌面工具

**路徑**：`C:\Users\admin\Desktop\minecraft_translator_flet`

**目的**：將 Minecraft 簡體中文（zh_cn）翻譯為台灣慣用語（zh_tw）的桌面工具。

| 技術 | 版本/備註 |
|------|----------|
| UI 框架 | Flet 0.82.2 |
| 簡繁轉換 | opencc |
| NBT 解析 | ftb_snbt_lib |
| Python 環境 | uv（統一用 `uv run`）|
| 測試 | `uv run pytest -q`（需在專案目錄執行）|

**翻譯流程**：`zh_cn → reverse_index 對照（CJK 值跳過）→ replace rules → zh_tw`

**特殊規則（已驗證踩坑）**：

| 規則 | 問題 | 正確做法 |
|------|------|----------|
| Rule 1315 | `飽和→飽食` 破壞 `Saturation` 翻譯 | 停用 Rule 1315；CJK 值跳過 replace rules |
| CJK 值 | 含中文的 zh_tw 值不應觸發 replace rules | 翻譯時偵測 CJK 範圍，跳過該值 |
| `刷怪籠→生怪磚` | 某些物品名稱兩岸不同 | 需用網路資料驗證，不能只靠字面規則 |

**Flet API 特殊行為**：
- `ft.Page()` 無法不帶參數實例化
- `page.on_error` 無法捕獲 UI handler 異常，handler 內部需自己 try/except
- `ft.run()` 取代 `ft.app()`（0.82.2 新寫法）
- SnackBar 新寫法：`page.show_dialog(ft.SnackBar(...))`

**測試流程（強制三步驟）**：`修改 → 建立備份 → uv run pytest -q → 起工具驗證`  
**⚠️ 嚴禁跳過 pytest 直接起動**。James 報測試失敗時，第一句問「清除 `__pycache__` 了嗎」。

---

### 14.2 專案 B：memory-lancedb-pro

**repo**：`CortexReach/memory-lancedb-pro`（fork：`jlin53882/memory-lancedb-pro`）

**目的**：OpenClaw 增強型長期記憶插件，支援 Hybrid Retrieval、Cross-Encoder 重排序、多範圍隔離、Management CLI。

| 技術 | 備註 |
|------|------|
| 語言 | TypeScript / Node.js |
| 資料庫 | LanceDB |
| 嵌入模型 | MiniMax（apiKey 不能有空白字元）|

**核心模組心智圖**：
```
retriever.ts
  ├── vectorOnlyRetrieval（純向量）
  ├── bm25Retrieval（純 BM25）
  ├── hybridRetrieval（混合）
  ├── applyRecencyBoost（時間衰減）
  └── applyDecayBoost（decay engine）
```

**特殊規則（已驗證踩坑）**：

| 規則 | 問題 | 正確做法 |
|------|------|----------|
| 絕對路徑 | LanceDB 路徑必須是絕對路徑 | `path.resolve()` 處理 |
| apiKey 無空白 | MiniMax apiKey 不能有空白 | 設定前先驗證格式 |
| JSON 反斜槓 | JSON 寫入時 `\` 會變 `\\` | 用 `JSON.stringify()` 驗證 |
| decay + recency 互斥 | 同時有 decayEngine 時不要套用 recencyBoost | vectorOnlyRetrieval 需做 guard |
| BM25 Expansion | Option B 需先確認架構方向 | 先提案，等 maintainer 確認後再實作 |

**Git 權限**：jlin53882 對 upstream 沒有 push 權限，只能推送自己的 fork。**⚠️ Push 失敗時必須立即告知 James**。

**PR 工作流**：`確認 repo/PR → 建立有意義的 feature branch → branch 內實作驗證 → --body-file 送 PR → 確認 push 成功 → 請求 review → 響應意見修正`

**架構決定流程**：`先在 Issue 提案（目標/Architecture/Config/防禦機制）→ 等 maintainer 確認方向 → 才能實作`  
**⚠️ 不要假設「沒有反對 = 可以做」。**

---

### 14.3 專案 C：ai-程式修改助手（OpenClaw Workspace）

**路徑**：`C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252`

**目的**：作為家豪的專屬 AI 開發助理，棲息在 #ai-程式修改助手 頻道。

| 工作類型 | 說明 |
|----------|------|
| 程式實作 | Minecraft 翻譯 / memory-lancedb-pro 實作 |
| PR 管理 | 確認狀態、推送、合併 |
| 規則制定 | SOUL.md / AGENTS.md / AI_WORKFLOW_MANUAL.md 維護 |
| 錯誤檢討 | 蒸餾成規則寫入 `.learnings/LEARNINGS.md` |
| 記憶管理 | 三層記憶架構的查詢與寫入 |

**核心檔案結構**：
```
workspace/
  ├── SOUL.md              # 核心價值觀（與 AGENTS.md 綁定）
  ├── AGENTS.md            # 技術操作鐵則 R1-R16（與 SOUL.md 綁定）
  ├── AI_WORKFLOW_MANUAL.md  # 單一 canonical 工作指南（本檔案）
  ├── MEMORY.md            # 專案長期記憶（蒸餾版）
  ├── HEARTBEAT.md         # 定期主動檢查清單
  ├── IDENTITY.md          # AI 身份設定
  ├── USER.md              # James 資料
  ├── .learnings/
  │     ├── LEARNINGS.md   # 每次對話的學習筆記
  │     ├── ERRORS.md      # 工具錯誤記錄
  │     └── SUBAGENT_ERRORS.md  # Sub-agent 錯誤分析
  └── memory/
        └── decisions.v2.md  # 唯一 canonical 決策來源
```

---

## 十五、memory-lancedb-pro 進階工作流程

### 15.1 Feature PR 標準流程

```
收到 Feature 任務
  ↓
Step 1：確認 repo 與 branch 策略
  → 用 memory_recall 或 gh search repos 確認 repo 名稱
  → 用 gh api --jq '.head.ref' 確認 PR head branch 名稱
  → 建立新 branch 基於 upstream/master（而非 origin/master）
  ↓
Step 2：分析設計文件
  → 查 memory/ 中的現有相關設計
  → 查 PR_STATUS.md 確認是否有相關 Open PR
  → 確認 upstream/master 是否已有相關程式碼（避免重複實作）
  ↓
Step 3：向維護者提案（重要）
  → 先在 Issue 張貼完整提案（含 Architecture、Config、防禦機制）
  → 等維護者回覆確認方向後再實作
  → 不要假設「沒有反對 = 可以做」
  ↓
Step 4：實作
  → 含中文文字操作 → Python script
  → PowerShell 只做：git checkout, git status, mkdir, 簡單系統指令
  ↓
Step 5：對抗性 Review
  → 用 OpenCode 對抗審查（見 15.4）
  → 檢查：介面改變、測試覆蓋、整合問題
  → 發現問題 → 修正 → 再 Review 直到乾淨
  ↓
Step 6：驗證
  → git show HEAD --stat（確認變更範圍）
  → 抽查關鍵檔案實際內容
  → 跑對應測試
  ↓
Step 7：提交 PR
  → PR 標題清楚標明：feat/fix/refactor
  → 內容包含：Summary、What changed、Testing、Files
  → 用 --body-file 避免中文編碼問題
  ↓
Step 8：通知 James
  → 回報 PR URL、狀態、需要 James 做的動作
  → 不主動合併或 push，等 James 指令
```

### 15.2 維護者溝通特殊邏輯

**維護者衝突時的裁決順序**：rwmjhb（最終裁決）> AliceLJY（架構方向）> 其他 reviewer  
**當 AliceLJY 和 rwmjhb 意見衝突時** → 以 Issue 形式請求裁決，不自己猜測

**發給維護者的訊息格式**：
```
## 主題
內容（結構化）
### 問題1｜🔴 阻塞 / 🟡 需確認
說明 + 具體程式執行流程
### 問題2｜...
...
### 建議的 Next Steps
```

### 15.3 PR 拆分策略

**觸發條件**：一個功能涉及多個獨立的關注點（scope drift）  
**拆分原則**：每個 PR 只做一件事（single responsibility）；用疊加策略：PR-A merge → PR-B merge → PR-C merge

**範例**：`PR-498：resetRegistration() WeakSet fix`、`PR-499：auto-capture boilerplate stripping`、`PR-500：recency double-boost guard`...

### 15.4 OpenCode 對抗 Review 的使用方式

**觸發時機**：PR 送出前、維護者提出多位 reviewer concerns 後、重大重構前

**OpenCode 的特殊限制**：
- `model` 參數必須是物件 `{name, providerID, modelID, reasoningEffort}`，不是字串
- OpenCode 可能出現幻覺，需要 main session 監督

**正確做法**：
1. 明確告訴 OpenCode 不要幻覺
2. 詳細驗證 OpenCode 的輸出
3. 對照原始需求確認沒有衝突

---

## 十六、鐵則速查表（R1-R16）

> 完整說明見 `AGENTS.md`。修改任一請同步檢視另一個。

| # | 鐵則 | 觸發時機 |
|---|------|----------|
| R1 | 破壞性操作需「明確指令」才執行 | merge/push-force/delete/restart |
| R2 | Sub-agent 完成後必須驗證 | Sub-agent 回報完成 |
| R3 | 衝突 marker 是合併雙方，不是二選一 | Git rebase 衝突 |
| R4 | PR 操作前確認 head branch 名稱 | PR number 而非 branch 名 |
| R5 | GitHub 中文內容用 `--body-file` | gh cli 送中文 |
| R6 | 寫入前必讀，寫入後確認 | 所有檔案操作 |
| R7 | Gateway 重啟需 James 同意 | gateway restart |
| R8 | 模糊專案名先確認 | repo 名不確定 |
| R9 | Sub-agent task 必須包含目標+底線+驗收 | Spawn sub-agent |
| R10 | Sub-agent 派工後 main session 必須監督 | 派工 sub-agent |
| R11 | Rebase 前先確認 upstream | Config/schema rebase |
| R12 | 模糊指令先問清楚 | 指令有兩種以上解讀 |
| R13 | 含中文 UTF-8 強制 Python | 文字檔操作 |
| R14 | Push 完成後驗證 remote 內容 | 任何 push |
| R15 | Sub-agent 完成後監督檢查清單 | Sub-agent 完成 |
| R16 | 複雜 JSON 衝突用 Python 處理 | JSON 衝突 |

---

## 十七、錯誤分類與預防摘要

> 詳細分析見 `.learnings/SUBAGENT_ERRORS.md`

| 錯誤 | 根因 | 預防 |
|------|------|------|
| 把「準備合併」當成「可以合併」| 意圖解讀錯誤 | R1：等明確指令 |
| Push 失敗沒發現就送 review | 驗證不足 | R14：Push 後驗證 remote |
| 假設「沒有反對=可以做」| 假設未確認 | 先問再實作 |
| PowerShell `>` 搞砸 UTF-8 | 工具不熟悉 | R13：Python subprocess |
| Git 衝突刪除正確內容 | 衝動編輯 | R3：git diff 確認後再 add |

---

## 十八、Session 健康管理

### 18.1 Session 大小警訊

| 檔案大小 | 建議 |
|----------|------|
| < 500KB | 正常 |
| 500KB ~ 1MB | 關注，考慮壓縮 |
| > 1MB | 主動建議 `/new` |
| > 2MB | 強制 `/new`，避免 overflow |

### 18.2 Context Overflow 處理

當出現 `Preemptive context overflow` 時：
1. Session 已難以搶救——compaction 只能蒸餾，無法容納完整歷史
2. 建議 reset session（`/new` 或 `/reset`）
3. Reset 前確認所有工作都已 commit 到 git
4. Reset 後新 session 繼承 MEMORY.md 和 LEARNINGS.md

---

## 十九、SOUL.md × AGENTS.md 綁定規則

> **⚠️ 鐵則**：這是 James 2026-04-07 訂下的行為準則綁定規則。

| 檔案 | 內容 | 與另一檔案關係 |
|------|------|---------------|
| `SOUL.md` | 核心價值觀、行為底層邏輯、行事風格 | 與 AGENTS.md 配對 |
| `AGENTS.md` | 技術操作流程、決策規則、鐵則 R1-R16 | 與 SOUL.md 配對 |

**綁定規則**：
- 當本檔案被讀取、修改或擴展時，必須同步檢視 `SOUL.md` 和 `AGENTS.md` 的內容
- 修改任一檔案前，先對照其他兩個檔案是否需要相應調整
- 三檔案共同構成完整行為準則，缺一不可

---

## 二十、Sub-agent 任務模板

> 完整版：`docs/SUBAGENT_TASK_TEMPLATE.md`。本節為速查版。

### 20.1 所有 sub-agent 任務都必須包含

**🎯 工作開始前檢查清單**：
```
[ ] 確認 repository 位置
[ ] 確認目前 git branch（git branch --show-current）
[ ] 確認 branch 是否乾淨（git status --short）
[ ] 如果是 PR 任務：用 gh api --jq '.head.ref' 確認 head branch 真實名稱
[ ] 確認 upstream/master 是否已有相同修改（git show upstream/master:path/to/file | grep keyword）
```

**✅ 完成後驗證清單**：
```
[ ] git status --short 確認變更範圍
[ ] git show HEAD --stat 抽查 commit 內容
[ ] 實際執行測試（不是只看程式碼）
[ ] 確認變更沒有破壞其他功能
```

**⚠️ 紀律紅線（禁止違反）**：

| 紅線 | 說明 |
|------|------|
| 不確定就問 | 遇到模糊地帶 → 回報 main session，等指示再繼續 |
| 同一方法失敗 3 次就停 | 停止蠻幹，回報目前狀態與卡點 |
| 不跳測試 | 任何修改後必須跑對應測試 |
| 不假設環境 | 用 git status / gh api 確認當前狀態，不靠記憶 |

### 20.2 Sub-agent 完成後：main session 必做清單

```
1. git show HEAD --stat（看變更範圍）
2. 抽查關鍵檔案的實際內容（不能只看 git log）
3. 確認變更範圍符合預期
4. 才能送 review 或 push
```

---

## 二十一、單一 canonical 檔案管理原則

> **⚠️ 2026-04-07 起生效**

### 目的
避免每個討論串都產生新的 workflow 檔案，造成重複勞動與維護混亂。

### 規則
- **`AI_WORKFLOW_MANUAL.md` 是唯一的 workflow canonical 檔案**
- 所有 workflow 相關內容只能更新本檔案，**嚴禁再建立新的 workflow 指南檔案**
- 收到「整理工作流程」類型的任務時：**直接在現有章節中新增/修改，不建立新檔**
- 如果某個 workflow 內容有更好的存放位置，應該**移動到本檔案的適當章節**，而不是建立新檔

### 已整合的廢棄檔案
- `docs/ai_workflow_guide.md`（已整合）
- `docs/ai_workflow_guide_supplement.md`（已廢棄）
- `docs/WORKFLOW_GUIDE.md`（已整合進本檔案，刪除）

---

*本手冊基於 2026-03-18~19 實戰經驗撰寫*
*2026-04-02：重構完成，Process 內容遷出至 `docs/dev_process_flow.md`*
*2026-04-07：確立為單一 canonical 檔案，整合所有 workflow 手冊*
*2026-04-07（整理）：消除重複章節、修正編號錯誤、整合 Discord 頻道對照*
*未來執行工作時依此手冊執行，有新增規則時同步更新本檔案*
