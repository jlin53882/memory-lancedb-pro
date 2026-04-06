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

# Step 2: Try a minimal request
body = {
    "parts": [{"type": "text", "text": "請用繁體中文回答：這個 fix 的邏輯是否正確？在 stripLeadingRuntimeWrappers 函式中，於空的 if 和 prefix regex if 中間加入對 boilerplate continuation lines 的 continue 處理。"}],
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

with open(r"C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\opencode_response.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(result, indent=2, ensure_ascii=False))
print("Written to file")
