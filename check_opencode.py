import urllib.request
import json

# Check if there's a config endpoint
for path in ["/api/v1/config", "/v1/config", "/api/config", "/config"]:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:4096{path}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"{path}: {resp.read()[:500]}")
    except Exception as e:
        print(f"{path}: {e}")

# Check OpenCode API info
try:
    req = urllib.request.Request("http://127.0.0.1:4096/api/v1")
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(f"/api/v1: {resp.read()[:500]}")
except Exception as e:
    print(f"/api/v1: {e}")

# Check what API key is being used by looking at the running process
import subprocess
result = subprocess.run(["wmic", "process", "where", "name='node.exe'", "get", "commandline", "/format:csv"], 
                       capture_output=True, text=True, timeout=10)
print("\nNode processes:")
for line in result.stdout.split("\n"):
    if "opencode" in line.lower() or "4096" in line:
        print(line[:500])
