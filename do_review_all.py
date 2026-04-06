import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

def do_review(session_id, commit_hash, fix_desc, prompt):
    body = {
        "parts": [{"type": "text", "text": prompt}],
        "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session/{session_id}/message",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            for p in result.get("parts", []):
                if p.get("type") == "text":
                    return p.get("text", "")
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)[:200]}"

def create_session(title):
    data = json.dumps({"title": title}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())["id"]

# Review Fix 1
print("Reviewing Fix 1...", file=sys.stderr)
sid1 = create_session("Fix1")
result1 = do_review(sid1, "ef6dc70", "Fix1", """Review commit ef6dc70 in Chinese:
Fix: 在 parsePluginConfig 的 rerank 欄位 resolveEnvVars 前加 rerankEnabled && guard。
確認：1)邏輯正確 2)無副作用 3)風格一致
如有任何問題，說明需要修改的內容。""")
with open(f"{outdir}/review_result_fix1.txt", "w", encoding="utf-8") as f:
    f.write(result1)
print(f"Fix1: {result1[:300] if len(result1)>300 else result1}", file=sys.stderr)
print("Fix1 done", file=sys.stderr)
