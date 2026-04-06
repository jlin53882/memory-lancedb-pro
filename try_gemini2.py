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
    import urllib.error
    opener = urllib.request.build_opener()
    resp = opener.open(req, timeout=120)
    print(f"Status: {resp.status}", flush=True)
    print(f"Content-Type: {resp.headers.get('Content-Type')}", flush=True)
    
    # Try reading all at once
    import select
    if hasattr(select, 'poll'):
        print("Has poll")
    
    # Read in chunks
    chunks = []
    while True:
        try:
            chunk = resp.read(1024)
            if not chunk:
                break
            chunks.append(chunk)
            print(f"Read chunk: {len(chunk)} bytes", flush=True)
        except Exception as e:
            print(f"Read error: {e}", flush=True)
            break
    
    full = b"".join(chunks)
    print(f"Total: {len(full)} bytes", flush=True)
    print(f"Content: {full.decode('utf-8', errors='replace')[:2000]}", flush=True)
    
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    body = e.read()
    print(f"Body: {body.decode('utf-8', errors='replace')[:1000]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
