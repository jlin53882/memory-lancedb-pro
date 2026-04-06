import sys, json, urllib.request, urllib.error
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")

base_url = "http://127.0.0.1:4096"

prompt = """請用繁體中文 review commit 484845d：
在 rerank 相關欄位的 resolveEnvVars 前加上 includes check 防止停用時失敗。
請確認：1)邏輯 2)副作用 3)風格"""

# Try using session API
# Create session first
data = json.dumps({"title": "PR Review"}).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/session",
    data=data,
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        session = json.loads(resp.read().decode("utf-8"))
        print("Session:", json.dumps(session, ensure_ascii=False)[:500])
except Exception as e:
    print("Session error:", e)
