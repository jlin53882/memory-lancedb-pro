---
name: opencode-api
description: 透過 HTTP API 呼叫 OpenCode Server 進行 code review 與編碼任務。適用於 OpenClaw 派工給 OpenCode 執行的場景。
version: "1.0.0"
author: james53882
license: MIT
clawhub: https://clawhub.com/opencode-api
tags:
  - opencode
  - code-review
  - http-api
  - integration
category: workflow
department: coding
languages:
  - zh
  - en
models:
  recommended:
    - minimax-portal/MiniMax-M2.7
  compatible:
    - minimax-portal/MiniMax-M2.5
    - openai-codex/gpt-5.4
---

# OpenCode API Skill

透過 HTTP API 呼叫已啟動的 OpenCode Server，讓 OpenClaw 可以派工給 OpenCode 處理 code review 或編碼任務。

## 前置條件

- OpenCode Server 必須已在 `http://127.0.0.1:4096` 啟動（會自動啟動）
- 或使用 `--no-auto-start` 手動管理模式

## 快速開始

### Sub-agent 直接 import（推薦）

```python
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import run_opencode_task, OpenCodeAPI

# 單次任務
result = run_opencode_task(
    prompt="請用繁體中文對以下程式碼進行 code review：\ndef foo(): pass",
    model="minimax/MiniMax-M2.7",
    reasoning="high",
)
print(result.text)        # 回覆文字
print(result.session_id)  # 可續接多輪
print(result.ok)          # True/False

# 多輪對話
client = OpenCodeAPI(auto_start=True)
sid = client.create_session(title="PR Review")
r1 = client.send_message("請 review...", session_id=sid, model="minimax/MiniMax-M2.7")
r2 = client.send_message("第三點再詳細點", session_id=sid)
```

### CLI 呼叫

```bash
python scripts/opencode_task.py --prompt "請幫我分析這個函數" --model minimax/MiniMax-M2.7 --reasoning high
```

---

## Script 總覽

| 檔案 | 用途 | 推薦場景 |
|------|------|----------|
| `opencode_task.py` | 乾淨的任務封裝（推薦）| 單次/多輪對話、sub-agent import |
| `opencode_client.py` | 完整 HTTP client | 需精細控制 API 底層 |
| `opencode_review.py` | PR Review 專用 wrapper | 直接 review GitHub PR |

---

## 模型速查表

| 模型 ID | 名稱 | 思考支援 | 適合場景 |
|---------|------|----------|----------|
| `minimax/MiniMax-M2.7` | MiniMax M2.7 | ✅ | 性價比 coding（預設）|
| `minimax/MiniMax-M2.5` | MiniMax M2.5 | ✅ | 中等複雜度任務 |
| `minimax/MiniMax-M2.7-highspeed` | MiniMax M2.7 高速 | ✅ | 快速響應 |
| `big-pickle:high` | Big Pickle High | ✅ 16K tokens | 深度分析（免費）|
| `big-pickle:max` | Big Pickle Max | ✅ 32K tokens | 極深度推理（免費）|

> 查看完整模型清單：`GET /config/providers`

---

## 思考深度（reasoning）

| 值 | 說明 |
|----|------|
| `none` | 關閉 |
| `minimal` / `low` | 輕量思考 |
| `medium` | 標準（預設）|
| `high` | 深度分析 |
| `xhigh` | 極深度推理 |

---

## ⚡ 自動啟動 Server

所有 script 都支援自動啟動 OpenCode Server（預設開啟）：

```
執行 script
    ├── 檢查 health
    │       ├── ✅ 已運行 → 直接執行
    │       └── ❌ 未運行 → 自動執行 opencode serve
    │               └── 等待最多 15 秒直到就緒
```

關閉自動啟動：`--no-auto-start`

---

## 觸發關鍵字

| 關鍵字 | 對應行為 |
|--------|----------|
| `用 OpenCode review PR#xxx` | CLI: `opencode_task.py --prompt "review PR#xxx"` |
| `用 OpenCode 分析這個檔案` | CLI: `opencode_client.py --task analyze` |
| `用 OpenCode 多輪對話` | import `OpenCodeAPI` + 多輪 |
| `OpenCode 用高思考` | `--reasoning high` |

---

## 依賴

```bash
# opencode_task.py：無外部依賴（標準函式庫）
# opencode_client.py：pip install requests
```
