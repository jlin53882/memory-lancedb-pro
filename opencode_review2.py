import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:4096"

# Step 1: Create session
req = urllib.request.Request(
    f"{base_url}/session",
    method="POST",
    data=json.dumps({}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=120) as resp:
    session = json.loads(resp.read())
    session_id = session.get("id") or session.get("sessionId")
    print(f"Session ID: {session_id}")

# Step 2: Send review request with minimal prompt
prompt = """你是 code review 專家（繁體中文）。

以下是一個 fix commit 的 diff，請確認邏輯是否正確、有無副作用或 regression、程式碼風格是否一致：

```diff
- const recencyBoosted = this.applyRecencyBoost(mapped);
+ // Bug 7 fix: when decayEngine is active, skip applyRecencyBoost here because
+ // decayEngine already handles temporal scoring; avoid double-boost.
+ const recencyBoosted = this.decayEngine
+   ? mapped
+   : this.applyRecencyBoost(mapped);
```

Fix 目的：當 this.decayEngine 存在時，recencyBoosted = mapped（跳過 applyRecencyBoost），避免 decayEngine 與 applyRecencyBoost 重複加成。

回覆格式（只回覆其中一種）：
- 完全沒問題：「LGTM」
- 有問題：「ISSUES: [說明問題及修復方式]」
"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
}

req2 = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"}
)

print("Sending review request...")
try:
    with urllib.request.urlopen(req2, timeout=120) as resp:
        result = json.loads(resp.read())
        print("Response:", json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    body_err = e.read().decode()
    print(f"HTTPError {e.code}: {body_err}")
except Exception as e:
    print(f"Error: {e}")
