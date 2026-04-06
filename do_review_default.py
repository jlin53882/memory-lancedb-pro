import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

try:
    # Create session
    data = json.dumps({"title": "Fix1 Review"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        sid = json.loads(resp.read().decode())["id"]
    print(f"Session: {sid}", file=sys.stderr)
    
    prompt = """請用繁體中文 review commit 484845d：
在 rerankApiKey/rerankEndpoint/rerankModel/rerankProvider 的 resolveEnvVars 前加上 .includes("${") 檢查，只在有 placeholder 時才解析。確認：1)邏輯 2)副作用 3)風格"""

    # Use default model (no model field)
    body = {"parts": [{"type": "text", "text": prompt}]}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session/{sid}/message",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    print("Sending request (default model)...", file=sys.stderr)
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        for p in result.get("parts", []):
            if p.get("type") == "text":
                text = p.get("text", "")
                with open(f"{outdir}/review_output.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"SUCCESS: wrote {len(text)} chars", file=sys.stderr)
                print("SUCCESS")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)[:300]}", file=sys.stderr)
