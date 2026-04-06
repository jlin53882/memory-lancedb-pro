import sys, json, urllib.request, urllib.error
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")

base_url = "http://127.0.0.1:4096"

def create_session():
    data = json.dumps({"title": "PR Review"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))["id"]

def send_message(session_id, prompt, provider="minimax", model="MiniMax-M2.7"):
    body = {
        "parts": [{"type": "text", "text": prompt}],
        "model": {"providerID": provider, "modelID": model}
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session/{session_id}/message",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))

prompt = """請用繁體中文 review commit 484845d：
在 rerank 相關欄位的 resolveEnvVars 前加上 includes check 防止停用時失敗。
請確認：1)邏輯 2)副作用 3)風格"""

session_id = create_session()
print("Created session:", session_id)
result = send_message(session_id, prompt)
for p in result.get("parts", []):
    if p.get("type") == "text":
        print("Review result:", p.get("text", ""))
