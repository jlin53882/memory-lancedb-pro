# OpenCode 可用模型

## 快速挑選

| 任務 | 推薦模型 | reasoning |
|------|----------|-----------|
| 快速簡單 review | `big-pickle:high` | 預設 |
| 一般 code review | `minimax/MiniMax-M2.7` | medium |
| 複雜架構分析 | `minimax/MiniMax-M2.7-highspeed` | high |
| 多檔批次分析 | `minimax/MiniMax-M2.5` | medium |
| 免費深度推理 | `big-pickle:max` | 預設 |

## 完整模型清單

從 `GET /config/providers` 取得。

### Minimax（這台電腦已設定）

| 模型 ID | 思考 | Context |
|---------|------|---------|
| `minimax/MiniMax-M2.7` | ✅ | 200K |
| `minimax/MiniMax-M2.5` | ✅ | 200K |
| `minimax/MiniMax-M2.7-highspeed` | ✅ | 200K |
| `minimax/MiniMax-M2.1` | ✅ | - |
| `minimax/MiniMax-M2` | ✅ | - |

### OpenCode Zen（內建免費）

| 模型 ID | 思考 |
|---------|------|
| `big-pickle:high` | ✅ 16K tokens |
| `big-pickle:max` | ✅ 32K tokens |
| `qwen3.6-plus-free` | ✅ 3級 |
| `minimax-m2.5-free` | ✅ |

## 思考深度

| 值 | 說明 |
|----|------|
| `none` | 關閉 |
| `minimal` | 最少 |
| `low` | 低 |
| `medium` | 標準 |
| `high` | 深度 |
| `xhigh` | 極深度 |
