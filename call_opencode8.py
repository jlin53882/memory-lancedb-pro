import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Create session
session_req = urllib.request.Request(
    f"{base_url}/session",
    method="POST",
    data=json.dumps({}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(session_req, timeout=120) as resp:
    session_data = json.loads(resp.read().decode("utf-8"))
    session_id = session_data['id']
    print(f"Session: {session_id}", flush=True)

# Ultra-short prompt
prompt = "LGTM 還是 ISSUES? 只回覆這一種格式。"

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
}

req = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
        print(f"Response ({len(raw)} chars): {raw[:2000]}")
except Exception as e:
    print(f"Error: {e}")
