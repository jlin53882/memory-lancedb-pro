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
    
    prompt = """請用繁體中文 review 以下程式碼變更：

commit hash: 484845d

變更摘要：
在 rerank 相關欄位的 resolveEnvVars 呼叫前，加上 .includes("${") 檢查，
只在確定有 ${...} placeholder 時才解析，否則跳過。
這可以防止當 reranking 停用時（rerank === "none"），解析未定義的 placeholder 導致失敗。

具體改動（index.ts parsePluginConfig 函式）：
- 新增註解說明此為 Bug fix
- if (typeof retrieval.rerankApiKey === "string" && retrieval.rerankApiKey.includes("${")) {
- if (typeof retrieval.rerankEndpoint === "string" && retrieval.rerankEndpoint.includes("${")) {
- if (typeof retrieval.rerankModel === "string" && retrieval.rerankModel.includes("${")) {
- if (typeof retrieval.rerankProvider === "string" && retrieval.rerankProvider.includes("${")) {

請確認：
1. 這個 fix 是否邏輯正確
2. 是否有副作用或 regression
3. 程式碼風格是否一致"""

    # gpt-4o-mini worked in tests, use it
    body = {
        "parts": [{"type": "text", "text": prompt}],
        "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session/{sid}/message",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    print("Sending request (gpt-4o-mini)...", file=sys.stderr)
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
