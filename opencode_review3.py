import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Check config endpoint
try:
    req = urllib.request.Request(f"{base_url}/config", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        config = json.loads(resp.read())
        print("Config:", json.dumps(config, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Config error: {e}")

# Check models endpoint
try:
    req = urllib.request.Request(f"{base_url}/models", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        models = json.loads(resp.read())
        print("Models:", json.dumps(models, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Models error: {e}")
