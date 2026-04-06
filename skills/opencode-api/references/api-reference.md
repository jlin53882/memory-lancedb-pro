# OpenCode HTTP API 完整參考

## 基礎資訊

- **Base URL**: `http://127.0.0.1:4096`
- **格式**: JSON / UTF-8

## 全域端點

| Method | Path | 說明 |
|--------|------|------|
| `GET` | `/global/health` | 健康檢查 |

```python
requests.get("http://127.0.0.1:4096/global/health")
# {"healthy": true, "version": "1.3.13"}
```

## Session 管理

| Method | Path | 說明 |
|--------|------|------|
| `GET` | `/session` | 列出所有 session |
| `POST` | `/session` | 建立新 session |
| `GET` | `/session/{id}` | 取得 session 詳情 |
| `DELETE` | `/session/{id}` | 刪除 session |
| `GET` | `/session/{id}/message` | 取得訊息歷史 |

### 建立 Session

```python
body = {"title": "PR Review", "parentID": "ses_xxx"}  # parentID 可選
r = requests.post("http://127.0.0.1:4096/session", json=body)
session_id = r.json()["id"]
```

## 傳送訊息（核心）

### 同步 `POST /session/{id}/message`

```python
body = {
    "parts": [{"type": "text", "text": "prompt"}],
    "model": "minimax/MiniMax-M2.7:high",   # 模型:思考深度
    # 或分開寫：
    # "model": "minimax/MiniMax-M2.7",
    # "reasoningEffort": "high",
}
r = requests.post(f"http://127.0.0.1:4096/session/{sid}/message", json=body)
# 回應：
# {
#   "info": {"id": "msg_xxx", "role": "assistant"},
#   "parts": [
#     {"type": "text", "text": "..."},
#     {"type": "tool", "tool": "read", "state": {"status": "completed"}},
#   ]
# }
```

### 非同步 `POST /session/{id}/prompt_async`

不等回覆，立即返回 204。適用長時間任務。

## 回應 Parts 類型

| type | 說明 |
|------|------|
| `text` | 文字回覆 |
| `tool` | 工具呼叫 |
| `reasoning` | 思考過程 |
| `step-start` | 步驟開始 |
| `step-finish` | 步驟完成 |

## 檔案操作

| Method | Path | 說明 |
|--------|------|------|
| `GET` | `/file/content?path=...` | 讀取檔案 |
| `GET` | `/find?pattern=...` | 搜尋程式碼 |
| `GET` | `/session/{id}/diff` | 取得工作區變更 |
