import sys, json, urllib.request, urllib.error
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import OpenCodeAPI

client = OpenCodeAPI(base_url="http://127.0.0.1:4096", auto_start=False)

prompt = """請用繁體中文 review commit 484845d：
在 rerank 相關欄位的 resolveEnvVars 前加上 includes check 防止停用時失敗。
請確認：1)邏輯 2)副作用 3)風格"""

sid = client.create_session(title="Fix1 Review")
print("Session:", sid)

# Check what format the API expects
body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "minimax", "modelID": "MiniMax-M2.7"}
}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(
    f"http://127.0.0.1:4096/session/{sid}/message",
    data=data,
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        for p in result.get("parts", []):
            if p.get("type") == "text":
                print("Review:", p.get("text", "")[:3000])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode("utf-8")[:1000])
except Exception as e:
    print("Error:", type(e).__name__, str(e))
