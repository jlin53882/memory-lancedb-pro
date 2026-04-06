import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

# Fix 1
data = json.dumps({"title": "Fix1"}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/session", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=10) as resp:
    sid = json.loads(resp.read().decode())["id"]
print(f"Session: {sid}", file=sys.stderr)

prompt = """請用繁體中文 review commit ef6dc70：在一段 if 判斷中增加 rerankEnabled && guard，確保只在 rerank 啟用時才解析 env var。diff: +const rerankEnabled = retrieval.rerank !== "none"; +if (rerankEnabled && typeof x === "string" && x.includes("${")) { x = resolveEnvVars(x); }"""
body = {"parts": [{"type": "text", "text": prompt}]}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{base_url}/session/{sid}/message", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode())
        for p in result.get("parts", []):
            if p.get("type") == "text":
                text = p.get("text", "")
                with open(f"{outdir}/review_result_fix1.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"OK: {text[:300]}", file=sys.stderr)
except Exception as e:
    with open(f"{outdir}/review_result_fix1.txt", "w") as f:
        f.write(f"ERROR: {e}")
    print(f"ERROR: {e}", file=sys.stderr)
