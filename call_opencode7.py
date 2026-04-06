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

prompt = """請用繁體中文回覆：LGTM 還是 ISSUES: (說明)

Review commit ef6dc70 改動（index.ts）：
目的：當 retrieval.rerank !== "none" 時才解析 rerank 欄位的 env var。
```diff
+          const rerankEnabled = retrieval.rerank !== "none";
+          if (rerankEnabled && typeof retrieval.rerankApiKey === "string" && retrieval.rerankApiKey.includes("${")) {
             retrieval.rerankApiKey = resolveEnvVars(retrieval.rerankApiKey);
           }
+          if (rerankEnabled && typeof retrieval.rerankEndpoint === "string" && retrieval.rerankEndpoint.includes("${")) {
             retrieval.rerankEndpoint = resolveEnvVars(retrieval.rerankEndpoint);
           }
+          if (rerankEnabled && typeof retrieval.rerankModel === "string" && retrieval.rerankModel.includes("${")) {
             retrieval.rerankModel = resolveEnvVars(retrieval.rerankModel);
           }
+          if (rerankEnabled && typeof retrieval.rerankProvider === "string" && retrieval.rerankProvider.includes("${")) {
             retrieval.rerankProvider = resolveEnvVars(retrieval.rerankProvider);
           }
```
請確認：1)邏輯是否正確 2)是否有 regression 3)程式碼風格是否一致。
"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "openrouter", "modelID": "openai/gpt-4o-mini"}
}

req = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json", "Accept": "text/event-stream"}
)

try:
    import urllib.error
    opener = urllib.request.build_opener()
    resp = opener.open(req, timeout=120)
    print(f"Status: {resp.status}", flush=True)
    print(f"Headers: {dict(resp.headers)}", flush=True)
    
    content_type = resp.headers.get("Content-Type", "")
    print(f"Content-Type: {content_type}", flush=True)
    
    # Read streaming response
    chunks = []
    while True:
        chunk = resp.read(1)
        if not chunk:
            break
        chunks.append(chunk.decode("utf-8", errors="replace"))
    
    full = "".join(chunks)
    print(f"Full streaming response ({len(full)} chars):", flush=True)
    print(full[:5000], flush=True)
    
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
