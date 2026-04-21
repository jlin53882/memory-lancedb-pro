---
name: hermes-bridge
description: 透過 WSL 呼叫本地 Hermes Agent（MiniMax 模型）。當需要快速、特定角色、或本地終端工具時使用。適用：跨系統協作、Hermes 勝出的任務分流。
---

# Hermes Agent Bridge（OpenClaw ↔ Hermes 跨系統橋接）

## 概述

本技能讓 OpenClaw 能直接呼叫同一機器上 WSL 裡的 Hermes Agent，兩者共享同一個 hermes-knowledge Obsidian vault。

**使用時機**：
- 需要 Hermes 的特定角色或工具能力
- 分流複雜任務到 Hermes 處理
- 快速獲取 Hermes 的觀點

## 呼叫方式

### 呼叫範本（Python subprocess → WSL）

```python
import subprocess

def call_hermes(prompt, provider="minimax", timeout=60):
    cmd = f'/home/jlin53882/.local/bin/hermes chat -q "{prompt}" -Q --provider {provider}'
    r = subprocess.run(
        ['wsl', 'bash', '-lc', cmd],
        capture_output=True, timeout=timeout
    )
    return r.stdout.decode('utf-8', errors='replace')
```

### 關鍵參數說明

| 參數 | 用途 | 範例 |
|------|------|------|
| `-q "..."` | 單次查詢（非互動模式） | `-q "你好"` |
| `-Q` | 安靜模式：只輸出回覆，不顯示 banner/tool 過程 | `-Q` |
| `--provider minimax` | 指定 provider（**必須**，否則 fallback 到 Anthropic 然後 401） | `--provider minimax` |
| `--provider minimax-cn` | 中國版 MiniMax（需另外設定 API key） | `--provider minimax-cn` |
| `--model <name>` | 覆寫預設模型 | `--model MiniMax-M2.7` |
| `--skills <name>` | 預載特定 skill | `--skills my-skill` |

### 可用 Providers（`--provider`）

`auto`, `openrouter`, `nous`, `openai-codex`, `copilot-acp`, `copilot`, `anthropic`, `gemini`, `huggingface`, `zai`, `kimi-coding`, `kimi-coding-cn`, `minimax`, `minimax-cn`, `kilocode`, `xiaomi`, `arcee`

## 已知限制

- **timeout 建議 ≤ 90s**：Hermes 單次查詢預設上限 90 turns
- **中文 prompt**：需明確指定「請用繁體中文回覆」，否則可能輸出簡體
- **API Key 狀態**：使用 `wsl hermes status` 確認各 provider 的認證狀態
- **WSL 環境**：Hermes 跑在 WSL Ubuntu，必須透過 `wsl bash -lc` 呼叫
- **回覆延遲**：MiniMax 模型約 5-15 秒回覆，視任務複雜度

## 使用範例

### 範例 1：簡單提問
```
prompt = "請用繁體中文解釋什麼是向量資料庫"
call_hermes(prompt)
```

### 範例 2：複雜任務（長 timeout）
```python
prompt = "請分析這個專案的架構並提出改進建議：..."
call_hermes(prompt, timeout=120)
```

## 驗證連線

```bash
# 確認 hermes 在 WSL 內可執行
wsl hermes --version

# 確認 MiniMax 認證狀態
wsl hermes status
```

## 錯誤處理

| 錯誤訊息 | 原因 | 解法 |
|---------|------|------|
| `anthropic 401` | 未指定 `--provider minimax`，fallback 到無 key 的 provider | 加上 `--provider minimax` |
| `minimax-cn not configured` | 該 provider 未設定 API key | 改用 `--provider minimax` |
| `hermes: command not found` | PATH 未正確設定 | 用完整路徑 `/home/jlin53882/.local/bin/hermes` |
| `TimeoutExpired` | 任務太複雜 | 增加 timeout 參數 |
