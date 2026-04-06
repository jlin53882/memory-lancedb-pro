import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Try different free/supported models
models_to_try = [
    ("openrouter", "google/gemini-2.0-flash-exp"),
    ("openrouter", "anthropic/claude-3-haiku-20240709"),
    ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
    ("openrouter", "qwen/qwen-2.5-72b-instruct"),
    ("openrouter", "mistralai/mistral-nemo-12b-instruct"),
    ("openrouter", "openai/gpt-4o"),
]

for provider, model in models_to_try:
    print(f"\n--- Trying: {provider}/{model} ---", flush=True)
    
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
        
        body = {
            "parts": [{"type": "text", "text": "Hi"}],
            "model": {"providerID": provider, "modelID": model}
        }
        
        req = urllib.request.Request(
            f"{base_url}/session/{session_id}/message",
            method="POST",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            error = data.get("info", {}).get("error")
            if error:
                print(f"  ERROR: {error.get('data', {}).get('message', str(error))[:200]}")
            else:
                parts = data.get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
                print(f"  SUCCESS: {text[:300]}")
                break
    except Exception as e:
        print(f"  Exception: {e}")
