import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Step 1: Create session
req = urllib.request.Request(
    base_url + "/session",
    method="POST",
    data=json.dumps({}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=120) as resp:
    session_data = json.loads(resp.read())
    session_id = session_data["id"]
    print("Session created:", session_id)

# Step 2: Send review request - shorter prompt
prompt = """你是 code review 專家。請用繁體中文回覆。

請 review 以下 commit 的改動：

src/auto-capture-cleanup.ts 中 stripLeadingRuntimeWrappers 函式新增了以下程式碼：

```typescript
// Bug fix: also strip known boilerplate continuation lines (e.g.
// "Results auto-announce to your requester.", "Do not use any memory tools.")
// that appear right after the wrapper prefix. These lines do NOT match the
// wrapper prefix regex but are part of the wrapper boilerplate.
if (strippingLeadIn) {
  AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE.lastIndex = 0;
  if (AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE.test(current)) {
    continue;
  }
}
```

請確認：
1. 這個 fix 的邏輯是否正確？
2. 是否有副作用或 regression？
3. 程式碼風格是否一致？
4. 請列出所有發現的 issues（如果有的話），並詳細說明。"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
}

req2 = urllib.request.Request(
    base_url + "/session/" + session_id + "/message",
    method="POST",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req2, timeout=120) as resp:
    result = json.loads(resp.read())
    if "error" in result and result["error"]:
        print("Error:", json.dumps(result["error"], indent=2, ensure_ascii=False))
    if "parts" in result:
        for p in result["parts"]:
            if p.get("type") == "text":
                print("Response:", p["text"])
    # print full for debugging
    print("\nFull response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
