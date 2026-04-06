import sys, json, urllib.request, urllib.error
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")

base_url = "http://127.0.0.1:4096"
session_id = "ses_2a965b644ffeeVqW3LkqtM5YXk"

prompt = """請用繁體中文 review commit 484845d：
在 rerank 相關欄位的 resolveEnvVars 前加上 includes check 防止停用時失敗。
請確認：1)邏輯 2)副作用 3)風格"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "minimax", "modelID": "MiniMax-M2.7"}
}

data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    data=data,
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print("Result keys:", list(result.keys()))
        for p in result.get("parts", []):
            if p.get("type") == "text":
                print("Text:", p.get("text", "")[:3000])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode("utf-8")[:1000])
except Exception as e:
    print("Error:", e)
