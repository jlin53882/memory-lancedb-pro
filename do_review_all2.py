import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

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

def do_review(sid, prompt, timeout=90):
    # No model specified = use default (fast)
    body = {"parts": [{"type": "text", "text": prompt}]}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/session/{sid}/message",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        for p in result.get("parts", []):
            if p.get("type") == "text":
                return p.get("text", "")
    return ""

# Fix 1
print("Reviewing Fix 1 (ef6dc70)...", file=sys.stderr)
sid = create_session("Fix1")
result = do_review(sid, """請用繁體中文 review commit ef6dc70：
在 rerankApiKey/rerankEndpoint/rerankModel/rerankProvider 的 resolveEnvVars 前加 rerankEnabled && guard。
diff: +const rerankEnabled = retrieval.rerank !== "none"; +if (rerankEnabled && typeof x === "string" && x.includes("${")) { x = resolveEnvVars(x); }
請確認：1)邏輯 2)副作用 3)風格。如有問題說明需修改的內容。""")
with open(f"{outdir}/review_result_fix1.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(f"Fix1: {result[:500]}", file=sys.stderr)

# Fix 2
print("Reviewing Fix 2 (736eae1)...", file=sys.stderr)
sid = create_session("Fix2")
result = do_review(sid, """請用繁體中文 review commit 736eae1：
在 vectorOnlyRetrieval 中，當 this.decayEngine 存在時跳過 applyRecencyBoost。
diff: const recencyBoosted = this.decayEngine ? mapped : this.applyRecencyBoost(mapped);
請確認：1)邏輯 2)副作用 3)風格。""")
with open(f"{outdir}/review_result_fix2.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(f"Fix2: {result[:500]}", file=sys.stderr)

# Fix 3
print("Reviewing Fix 3 (f487772)...", file=sys.stderr)
sid = create_session("Fix3")
result = do_review(sid, """請用繁體中文 review commit f487772：
在 stripLeadingRuntimeWrappers 中新增對 boilerplate continuation lines 的處理。
diff: +if (strippingLeadIn) { AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE.test(current) { continue; } }
請確認：1)邏輯 2)副作用 3)風格。""")
with open(f"{outdir}/review_result_fix3.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(f"Fix3: {result[:500]}", file=sys.stderr)

# Fix 4
print("Reviewing Fix 4 (1bac9e6)...", file=sys.stderr)
sid = create_session("Fix4")
result = do_review(sid, """請用繁體中文 review commit 1bac9e6：
在 stripEnvelopeMetadata 的 regex 中，把 "You are running as a subagent.*?" 改為 "You are running as a subagent\\b.*?"（加 word boundary）。
請確認：1)邏輯 2)副作用 3)風格。""")
with open(f"{outdir}/review_result_fix4.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(f"Fix4: {result[:500]}", file=sys.stderr)

# Fix 5
print("Reviewing Fix 5 (c621d91)...", file=sys.stderr)
sid = create_session("Fix5")
result = do_review(sid, """請用繁體中文 review commit c621d91：
把 _registeredApis.clear(); 改為註解 // (WeakSet.clear() does not exist...)
diff: -_registeredApis.clear(); +// (WeakSet.clear() does not exist...)
請確認：1)邏輯 2)副作用 3)風格。""")
with open(f"{outdir}/review_result_fix5.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(f"Fix5: {result[:500]}", file=sys.stderr)

print("ALL DONE", file=sys.stderr)
