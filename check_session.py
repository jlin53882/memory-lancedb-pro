import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Check what providers are available
try:
    req = urllib.request.Request(
        f"{base_url}/session",
        method="POST",
        data=json.dumps({}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        session_data = json.loads(resp.read().decode("utf-8"))
        session_id = session_data['id']
        print(f"Session: {session_id}")
        print(f"Full session data: {json.dumps(session_data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")
