import urllib.request
import json

base_url = "http://127.0.0.1:4096"

# Step 1: Create session
session_req = urllib.request.Request(
    f"{base_url}/session",
    method="POST",
    data=json.dumps({}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(session_req, timeout=120) as resp:
    session_data = json.loads(resp.read().decode("utf-8"))
    session_id = session_data['id']
    print(f"Session: {session_id}")

# Step 2: Send review request with gemini via openrouter (often has better free tier)
prompt = """請用繁體中文回覆。

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
回覆：「LGTM，0 issues」或「ISSUES: N 個問題：(說明)」
"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "openrouter", "modelID": "google/gemini-2.0-flash-thinking-exp"}
}

req = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
        print(f"Raw response ({len(raw)} chars): {raw[:2000]}")
except Exception as e:
    print(f"Error: {e}")
