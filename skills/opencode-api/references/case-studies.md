# OpenCode × OpenClaw 整合案例

## 案例一：PR Code Review

```python
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

result = run_opencode_task(
    prompt="""請用繁體中文對以下 Git diff 進行 code review：

```diff
+def translate(items):
+    for item in items:
+        print(item)
```

分析：1) Bug  2) 安全性  3) 風格  4) 改進建議""",
    model="minimax/MiniMax-M2.7",
    reasoning="high",
)
print(result.text)
```

## 案例二：多輪對話

```python
from opencode_task import OpenCodeAPI

client = OpenCodeAPI(auto_start=True)
sid = client.create_session(title="PR Review #374")

r1 = client.send_message(
    "請 review 這個函數：\ndef translate(items): pass",
    session_id=sid,
    model="minimax/MiniMax-M2.7"
)
print(client.extract_text(r1))

r2 = client.send_message(
    "可以針對第三點給更具體的修改範例嗎？",
    session_id=sid,
)
print(client.extract_text(r2))
```

## 案例三：批次多檔分析

```python
from pathlib import Path
from opencode_task import OpenCodeAPI

client = OpenCodeAPI()
files = {
    "core/translator.py": Path("core/translator.py").read_text(encoding="utf-8"),
    "core/parser.py": Path("core/parser.py").read_text(encoding="utf-8"),
}

parts = [{"type": "text", "text": "請用繁體中文分析以下所有檔案的架構："}]
for fname, content in files.items():
    parts.append({"type": "text", "text": f"\n=== {fname} ===\n{content[:2000]}"})

sid = client.create_session(title="Batch Analyze")
response = client.send_message("", parts=parts, session_id=sid, model="minimax/MiniMax-M2.7")
print(client.extract_text(response))
```

## 與 Codex 比較

| 面向 | Codex CLI | OpenCode HTTP API |
|------|-----------|-------------------|
| 部署 | 獨立程序 | HTTP Server |
| 延遲 | 較高 | 低（keep-alive）|
| 多工 | 困難 | 原生 multi-session |
| OpenClaw 整合 | PTY 模式 | HTTP REST |
| 適用場景 | 即時互動 | 自動化派工 |
