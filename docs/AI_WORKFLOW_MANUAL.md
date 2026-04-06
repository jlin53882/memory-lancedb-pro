# AI 工作流程助手手冊

> **Policy（可調整政策）** — 組織本地規則  
> 本文件定義「這裡的人偏好什麼 / 允許什麼 / 禁止什麼」  
> 版本：2026-03-19（2026-04-02 重構：Process 內容遷出，Policy 內容重整）

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
2a. **Gateway restart 必先通知家豪**：內容須含「重啟後 agent 會暫時離線」預警。絕不默默重啟。
2b. **Gateway 重啟一律由家豪手動執行**：agent 只負責寫入設定 + 通知家豪，由家豪親自執行重啟。
3. **不確定就先問**：指令/參數不確定時，禁止猜測執行。
4. **零檢索不編造**：記憶庫無結果時，聲明「無相關決策可參考」，不捏造。
4b. **檔案/路徑/寫入狀態：回覆前必先驗證**：必須用工具實際驗證。
5. **快慢路徑**：閒聊直接答；寫入/刪除/改碼/重啟 → Plan → Dry-run → 確認 → 執行。
6. **涉及維運決策時**，必須先查 `memory/decisions.v2.md` 或 LanceDB recall。

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

寫入 LanceDB 時，統一使用以下標記前綴：

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

1. **P1-C 類（強制檢查）**
   - `self-improvement`
   - `agent-self-review`
   - `proactive-agent`

2. **P1-A 類（優先心智檢查）**
   - `agentlens`、`qmd`、`session-logs`、`healthcheck`、`batch-processor`、`find-skills`、`skill-vetting`

3. **P1-B 類（保留可用，不主動強推）**
   - `codex-quota`、`node-connect`、`opencode-controller`

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

當家豪說：
- 「掰掰」「先這樣」「好了」「收工」「下班了」

→ 判斷本次 session 有無新知識（系統決策、踩坑解法、環境設定修改）
→ 有 → 詢問是否需要執行 /compress
→ 無 → 正常回應，不打擾

---

## 七、[LEARNED_RULES] 實戰紀律（2026-03-20 起累積）

### 7.1 pytest/vitest 執行規則（2026-03-20）
- 執行 `python -m pytest` 前，先看測試檔案屬於哪個專案目錄，再 `cd` 進去
- 該專案 `.venv` 有完整套件（ftb_snbt_lib、pandas 等），全域環境沒有

### 7.2 測試失敗處理（2026-03-20）
- **James 報測試失敗時**：第一句問「清除 `__pycache__` 了嗎」，不要先說本地通過。
- **Sub-agent 完成後**：必須檢查 `git status` 和完整輸出。發現「說要做但沒做」的 sub-agent，立即自己補做。

### 7.3 工作流程紀律（2026-03-20）
- PR 任務觸發當下立刻建立 feature branch，在 branch 內完成實作與驗證，絕不在 main 上先做完再補 PR。
- 接到實作任務：先讀 `docs/AI_WORKFLOW_MANUAL.md` 對應章節，確認工作原則與驗證 SOP。
- **每次 PR review 修正完成後**：一定要再跑一次 `pytest -q` 全域測試，確認所有單元測試通過後才能宣告完成。

### 7.4 工具使用策略（2026-03-20）
- **Flet API 行為必須先驗證再用**：`ft.Page()` 無法不帶參數實例化。
- **破壞性失敗必須 raise**：解析/處理失敗時嚴禁 `return {}` 吞掉 exception。
- **大量中文寫入時，用 write tool（自動 UTF-8）**，避免 PowerShell redirect 造成檔案截斷。
- **Windows 環境統一用 `Get-ChildItem`**，不用 Unix 風格的 `ls -la`。

### 7.5 PowerShell vs Python 分工（2026-03-24）
- 含中文的文字檔處理（JSONL / session log / UTF-8 檔案）：**一律 Python**
- PowerShell 只用於不需要處理中文的簡單系統指令

### 7.6 分析類 Script 統一用 Python（2026-03-23）
- **PowerShell 處理 UTF-8 中文會亂碼**：分析/統計/資料探索類 script 統一用 Python

### 7.7 Minecraft 翻譯 Pipeline（2026-03-25）
- **zh_tw 含 CJK 會觸發 replace rules**：Pipeline 對含 CJK 的 zh_tw 值執行 `apply_replace_rules()`，Rule 1315 `飽和→飽食` 會破壞 `Saturation` 的正確翻譯。修法：zh_tw 的 CJK 值應跳過 replace rules 或拆分 Rule 1315 排除特定語境。
- **`刷怪籠→生怪磚` 為正確翻譯**：zh_cn→zh_tw 某些物品名稱確實有差異，需用網路資料驗證，不能只靠字面規則。

### 7.8 檔案寫入 BOM 問題（2026-04-01）
- **PowerShell Out-File -Encoding UTF8 / Copy-Item 會自動加 BOM**
- BOM (0xEF 0xBB 0xBF) 會導致 Node.js parse 失敗：ParseError: Unexpected character
- **修復**：用 Python 二進位寫入 ('wb')
- **禁止**：PowerShell Out-File -Encoding UTF8 / Copy-Item 寫入 JS/TS 原始碼

---

## 八、UI 收斂原則

> **核心問題：UI 任務如果沒有停損點，很容易變成時間黑洞。**

### 8.1 UI 可用標準

當 UI 達到以下標準時，應停止持續打磨，轉往功能與穩定性：
- 看得懂
- 按得到
- 不會誤操作
- 不影響主要流程

### 8.2 UI 時間黑洞的早期警訊

```
當出現以下訊號時，應主動提出停損建議：
- 已來回修改超過 2~3 輪
- 每次都在「太擠 ↔ 太空 ↔ 太散」之間來回
- 修改已經是「視覺微調」而非「功能改善」
- 花費的時間與實際價值不成比例
```

### 8.3 UI 停止條件

```
UI 優化如果沒有明確停損點，很容易從「可用」一路磨到「時間被吃光」。
未來 UI 另開獨立任務，不與功能修改綁在一起。
```

---

## 九、專案任務共通原則

### 9.1 功能優先於美化

```
優先把時間放回：
- 功能正確性
- 穩定性
- 測試
- 真正影響效率的流程問題

而不是：
- 更漂亮
- 更像產品
- 更像正式設定頁
```

### 9.2 實作優先於抽象辯論

```
遇到複雜架構問題：
→ 先讀實際程式碼
→ 小范围实测验证
→ 有了具体认知再讨论

而不是：
→ 一直在讨论应该怎样
```

### 9.3 為什麼改 / 為什麼能刪 / 誰在用

```
任何刪除/移除/替換的 PR，論文中必須逐項補6欄位：
1. 為什麼要改
2. 為什麼能刪
3. 目前誰在用或沒人在用
4. 替代路徑
5. 風險
6. 如何驗證

不足的項目標 [需確認]
```

---

## 十、Discord 頻道對照

| 頻道 | ID | 用途 |
|------|-----|------|
| #ai-小助理 | 1476858065914695741 | 統整回報 |
| #ai-程式修改助手 | 1476866394556465252 | Coding 工作 |
| #監控警告 | 1476866274628997231 | Cron 回報 |
| #頭腦風暴 | 1476866144961822791 | 規劃討論 |

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

# pytest 測試
uv run pytest

# Git 狀態
git status
git diff --stat
```

---

## 十二、附錄

### 12.1 專案路徑

| 項目 | 路徑 |
|------|------|
| Minecraft 專案 | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| Stock Trading | `C:\Users\admin\Desktop\Stock_trading` |
| 記憶 | `C:\Users\admin\.openclaw\workspace\memory\` |
| 指南 | `C:\Users\admin\.openclaw\workspace\docs\AI_WORKFLOW_MANUAL.md` |
| 設計稿 | `C:\Users\admin\Desktop\minecraft_translator_flet\docs\pr\` |

### 12.2 GitHub Issue 回報格式（2026-03-23）
- **所有 gh issue create / edit 的 body 必須用 Markdown 語法**
- 正確流程：草稿先寫到 `.md` 檔 → 用 `--body-file` 上傳

### 12.3 驗證足跡（2026-03-31 SA-4 G1）
- 完成任何修改任務後，**必須用 read/list/exec 驗證磁碟狀態**，再回報完成
- 不得僅依賴 tool return 假設產出已落地
- 適用場景：sub-agent 完成後、本 agent 完成寫入後、執行刪除/搬遷後

### 12.4 Discord 附件上傳路徑（2026-03-31 SA-4 G8）
- `workspace-dc-channel--*` 路徑會被 OpenClaw 的 compiled JS 阻擋
- **正確流程**：附件上傳前先複製到 workspace/ 根目錄，再傳送

### 12.5 圖片任務
預設用 AI 視覺模型直接辨識。只有使用者明確要求才走 OCR。

---

*本手冊基於 2026-03-18~19 實戰經驗撰寫*  
*2026-04-02：重構完成，Process 內容遷出至 `docs/dev_process_flow.md`*  
*未來執行工作時依此手冊執行，有新增規則時同步更新本檔案*
