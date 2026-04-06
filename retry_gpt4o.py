import urllib.request
import json
import time

base_url = "http://127.0.0.1:4096"

for attempt in range(3):
    print(f"\n--- Attempt {attempt+1} ---", flush=True)
    
    # Create session
    session_req = urllib.request.Request(
        f"{base_url}/session",
        method="POST",
        data=json.dumps({}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(session_req, timeout=120) as resp:
            session_data = json.loads(resp.read().decode("utf-8"))
            session_id = session_data['id']
            print(f"Session: {session_id}", flush=True)
    except Exception as e:
        print(f"Session error: {e}")
        time.sleep(5)
        continue
    
    body = {
        "parts": [{"type": "text", "text": "Say 'test' only"}],
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
            raw = resp.read()
            print(f"Raw bytes: {len(raw)}")
            if raw:
                data = json.loads(raw)
                error = data.get("info", {}).get("error")
                if error:
                    print(f"Error: {error.get('data', {}).get('message', str(error))[:200]}")
                else:
                    parts = data.get("parts", [])
                    text = "".join(p.get("text", "") for p in parts)
                    print(f"Response: {text[:300]}")
            else:
                print("Empty response!")
    except Exception as e:
        print(f"Request error: {e}")
    
    time.sleep(3)
