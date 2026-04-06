import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

data = json.dumps({"title": "Fix1"}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/session", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=10) as resp:
    sid = json.loads(resp.read().decode())["id"]
print(f"Session: {sid}", file=sys.stderr)

prompt = """用繁體中文回答：這個 fix 正確嗎？

目的：當 rerank === "none"（停用）時，若 rerankApiKey 含未解析的 ${...}，resolveEnvVars 會失敗。
修復：加 if (rerankEnabled && ...) guard，只在 rerank 啟用時才解析。

改動：
const rerankEnabled = retrieval.rerank !== "none";
if (rerankEnabled && typeof retrieval.rerankApiKey === "string" && retrieval.rerankApiKey.includes("${")) {
  retrieval.rerankApiKey = resolveEnvVars(retrieval.rerankApiKey);
}

請說：LGTM 或 有問題+原因。"""
body = {"parts": [{"type": "text", "text": prompt}]}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(f"{base_url}/session/{sid}/message", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        for p in result.get("parts", []):
            if p.get("type") == "text":
                text = p.get("text", "")
                with open(f"{outdir}/review_result_fix1.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"OK: {text}", file=sys.stderr)
except Exception as e:
    err = str(e)
    with open(f"{outdir}/review_result_fix1.txt", "w") as f:
        f.write(f"ERROR: {err[:200]}")
    print(f"ERROR: {err[:200]}", file=sys.stderr)
