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
    print(f"Session: {session_id}")

body = {
    "parts": [{"type": "text", "text": "Say 'test' only"}],
    "model": {"providerID": "openrouter", "modelID": "google/gemini-2.0-flash-exp"}
}

req = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
        print(f"Raw bytes: {len(raw)}")
        print(f"Decoded: {raw.decode('utf-8', errors='replace')[:2000]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    body = e.read()
    print(f"Body: {body.decode('utf-8', errors='replace')[:1000]}")
except Exception as e:
    print(f"Error: {e}")
