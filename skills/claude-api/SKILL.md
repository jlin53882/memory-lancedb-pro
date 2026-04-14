---
name: claude-api
description: >
  透過 subprocess 呼叫 Claude Code CLI 進行 code review、程式碼分析與編碼任務。
  涵蓋：Models（minimax/claude 系列）、Custom System Prompt、CLI 參數、
  Session 管理（單次/多輪對話）、Code Review 強化 checklist、
  Config（完整環境變數設定）、派工範本（Minecraft-translate 專用）。
  適用於 OpenClaw 派工給 Claude Code 執行的場景。
version: "1.0.0"
author: james53882
license: MIT
clawhub: https://clawhub.com/claude-api
tags:
  - claude
  - claude-code
  - code-review
  - minimax
  - subprocess
  - models
  - system-prompt
  - session
  - review-checklist
  - providers
category: workflow
department: coding
languages:
  - zh
  - en
models:
  recommended:
    - minimax-m2.7
  compatible:
    - minimax-m2.5
    - claude-opus-4
    - claude-sonnet-4
    - claude-haiku-4
---

# Claude Code API Skill（完整版 v1.0）

透過 subprocess 呼叫 Claude Code CLI，讓 OpenClaw 可以派工給 Claude Code 處理 code review、程式碼分析、編碼任務。

---

## 📚 目錄索引

需要哪個主題的詳細內容，請讀對應的 reference 檔案：

| 主題 | 檔案 | 說明 |
|------|------|------|
| 快速開始 | — | 直接看下方第 1 節 |
| Scripts 總覽 | `scripts/claude_task.py` | 單次/多輪對話、sub-agent import |
| 模型速查 | 直接看下方第 3 節 | minimax / claude 系列 |
| 環境變數 | 直接看下方第 4 節 | ANTHROPIC_BASE_URL / AUTH_TOKEN / MODEL |
| 派工範本 | 直接看下方第 5 節 | Minecraft-translate 專用 prompt |
| **強化 Code Review Checklist** | `references/review-checklist.md` | **必讀** — 每次 review 都要問的 6 大問題（Schema 對應實作、Pattern 邊界、常數清理、改動範圍、Error logging、向後相容）|

---

## 1. 快速開始

### Sub-agent import（推薦）

```python
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/claude-api/scripts")
from claude_task import run_claude_task, ClaudeAPI

# 單次任務
result = run_claude_task(
    prompt="請用繁體中文對以下程式碼進行 code review：\ndef foo(): pass",
    model="minimax-m2.7",
)
print(result.text)
print(result.ok)

# 多輪對話
client = ClaudeAPI(model="minimax-m2.7")
r1 = client.send_message("請 review...", system_prompt="你是專業的 code reviewer")
r2 = client.send_message("第三點再詳細點")
```

### CLI

```bash
python scripts/claude_task.py --prompt "請幫我分析這個函數" --model minimax-m2.7
```

---

## 2. Scripts 總覽

| 檔案 | 用途 | 推薦場景 |
|------|------|----------|
| `claude_task.py` | 乾淨的任務封裝（推薦）| 單次/多輪對話、sub-agent import |

---

## 3. 模型速查

| 模型 ID | 名稱 | 說明 |
|---------|------|------|
| `minimax-m2.7` | MiniMax M2.7 | 性價比 coding（預設）|
| `minimax-m2.5` | MiniMax M2.5 | 中等複雜度任務 |
| `claude-opus-4` | Claude Opus 4 | 深度推理（付費）|
| `claude-sonnet-4` | Claude Sonnet 4 | 平衡型（付費）|
| `claude-haiku-4` | Claude Haiku 4 | 快速響應（付費）|

查詢方式：Claude Code 會自動讀取 `ANTHROPIC_MODEL` 環境變數

---

## 4. 環境變數

Claude Code 會自動讀取以下環境變數：

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `ANTHROPIC_BASE_URL` | API 端點 | `https://api.anthropic.com` |
| `ANTHROPIC_AUTH_TOKEN` | API 金鑰 | （必填）|
| `ANTHROPIC_MODEL` | 預設模型 | `minimax-m2.7` |

**建議設定方式（永久環境變數）：**

```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.minimax.io/anthropic", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "你的API金鑰", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL", "minimax-m2.7", "User")
```

---

## 5. 派工上下文範本（Minecraft-translate 專用）

當派工給 Claude Code 時，**必須**在 prompt 裡附上：

### 專案基本資訊

| 項目 | 內容 |
|------|------|
| 工作目錄 | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| 主要語言 | Python 3.12 + Flet 0.82.x |
| 測試框架 | pytest（需用 `.venv\Scripts\python.exe`） |
| Git | `gh` 已認證，可存取 `jlin53882/Minecraft-translate` |

### 重要資料夾對照

```
minecraft_translator_flet/
├── app/                          # Flet UI 主程式
│   ├── views/                    # View 元件
│   ├── icon_reader.py            # ZIP icon reader（含 LRU cache）
│   └── icon_index.py             # Icon 索引建立
├── translation_tool/             # 核心 CLI 工具
│   ├── core/                     # 翻譯引擎（lm_translator, kubejs, ftb...）
│   ├── plugins/                  # 插件（ftbquests, kubejs, md...）
│   └── utils/                    # 共用工具（jar_browser.py, cache_shards.py...）
├── tests/                        # pytest 測試（需 venv）
├── docs/                          # 開發文件（SOP、AI_WORKFLOW_MANUAL...）
├── .icon_cache/                  # JAR icon 快取
└── .venv/                        # Python 虛擬環境（依賴在此）
```

### 禁止假設

| ❌ 錯誤假設 | ✅ 正確做法 |
|------------|------------|
| 「pytest 直接跑」 | 必須先 `cd` 進專案目錄，用 `.venv\Scripts\python.exe -m pytest` |
| 「全域 Python 有套件」 | 專案依賴（`ftb_snbt_lib`、`pandas`）只在 `.venv` 裡 |
| 「直接用 `python`」 | 明確指定 `.venv\Scripts\python.exe` |
| 「桌面是工作目錄」 | 工作目錄是 `minecraft_translator_flet` |
| 「PowerShell redirect 寫中文」 | 會變成 UTF-16 截斷；改用 Python script 或 `write` tool |

### 典型派工 prompt 範例

```
你是一個專業的 Python 開發者，幫我對以下 PR 進行 code review。

## 專案背景
- 工作目錄：`C:\Users\admin\Desktop\minecraft_translator_flet`
- 主要語言：Python 3.12 + Flet 0.82.x
- 測試：`cd` 進專案目錄後，用 `.venv\Scripts\python.exe -m pytest` 執行

## 任務
請用繁體中文 review 這個 PR 的變更：
[這裡貼 PR 內容或 diff]

## 審查重點
1. 是否有破壞性變更未告知
2. 測試覆蓋是否足夠
3. 錯誤處理是否完整
4. 程式碼風格是否一致（建議使用 ruff formatter）
5. 是否有安全疑慮
6. **Schema 新增欄位 → 確認有對應實作讀取**（見 `references/review-checklist.md`）
7. **Pattern matching 函式 → 提供邊界條件測試**（見 `references/review-checklist.md`）
8. **常數/函式定義 → 確認沒有被取代後遺留**（見 `references/review-checklist.md`）
9. **改動範圍 → 只涵蓋需要修改的範圍，無關程式碼不受影響**

## 輸出格式
最後列出：
- ✅ 建議保留的優點
- ⚠️ 需要修改的問題（附檔案:行號）
- 💡 改進建議

請用繁體中文回覆，並在結尾列出你修改了哪些檔案。
```

---

## 6. 觸發關鍵字對照

| 關鍵字 | 對應行為 |
|--------|----------|
| `用 Claude review PR#xxx` | CLI: `claude_task.py --prompt "review PR#xxx"` |
| `用 Claude 分析這個檔案` | `client.send_message("請分析...")` |
| `用 Claude 多輪對話` | import `ClaudeAPI` + 多輪 |
| `Claude 用高思考` | 設定 `ANTHROPIC_MODEL` 為 `minimax-m2.7` |
| `Claude 做規劃` | `client.send_message(system_prompt="你是一個規劃專家")` |
| `Claude 結構化輸出` | 自行解析 JSON 回應 |
| `Claude 中止任務` | Ctrl+C 或停止 subprocess |

---

## 依賴

```bash
# claude_task.py：無外部依賴（標準函式庫）
```

---

## 與 OpenCode 的比較

| 特性 | Claude Code | OpenCode |
|------|-------------|----------|
| 介面 | CLI subprocess | HTTP API |
| 模型 | 支援 minimax | 支援 minimax |
| Code Review | ✅ | ✅ |
| 工具呼叫 | ✅ | ✅ |
| 多輪對話 | ✅ (session-dir) | ✅ |
| 安裝難度 | 簡單 | 需要啟動 server |
| 思考深度 | 依模型支援 | `--reasoning` 參數 |
| 結構化輸出 | JSON parse | 內建 `outputFormat` |

---

## 提示

1. **確保 `claude` 在 PATH 中** — 安裝 Claude Code 並確認可以從命令行執行
2. **設定環境變數** — 建議將 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL` 設為系統環境變數
3. **使用 session-dir 進行多輪對話** — Claude Code 支援 `--session-dir` 參數保存對話歷史
4. **疑難排解** — 如果任務失敗，檢查 `result.error` 取得錯誤訊息
5. **禁止假設** — 請務必附上專案背景資訊，避免 Claude Code 做出錯誤假設