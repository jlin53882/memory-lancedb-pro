import sys, json, urllib.request, urllib.error

base_url = "http://127.0.0.1:4096"
outdir = "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252"

def review(session_title, commit, prompt, filename, timeout=120):
    data = json.dumps({"title": session_title}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/session", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        sid = json.loads(resp.read().decode())["id"]
    print(f"Session {session_title}: {sid}", file=sys.stderr)
    body = {"parts": [{"type": "text", "text": prompt}]}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/session/{sid}/message", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode())
            for p in result.get("parts", []):
                if p.get("type") == "text":
                    text = p.get("text", "")
                    with open(f"{outdir}/{filename}", "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"{session_title} OK: {text[:200]}", file=sys.stderr)
                    return text
    except Exception as e:
        err = str(e)
        with open(f"{outdir}/{filename}", "w") as f:
            f.write(f"ERROR: {err[:200]}")
        print(f"{session_title} ERROR: {err[:200]}", file=sys.stderr)
        return None

# Fix 3: auto-capture-cleanup boilerplate
review("Fix3", "f487772",
"""用繁體中文回答：這個 fix 正確嗎？

目的：在 stripLeadingRuntimeWrappers 中，遇到 boilerplate continuation lines 時 skip（continue），避免它們被當成 content。

改動：
if (strippingLeadIn) {
  AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE.lastIndex = 0;
  if (AUTO_CAPTURE_RUNTIME_WRAPPER_BOILERPLATE_RE.test(current)) {
    continue;
  }
}

請說：LGTM 或 有問題+原因。""",
"review_result_fix3.txt")

# Fix 4: smart-extractor regex
review("Fix4", "1bac9e6",
"""用繁體中文回答：這個 fix 正確嗎？

目的：在 stripEnvelopeMetadata 的 regex 中，把 "You are running as a subagent.*?" 改為 "You are running as a subagent\\b.*?"，加 word boundary 防止貪心匹配。

請說：LGTM 或 有問題+原因。""",
"review_result_fix4.txt")

# Fix 5: resetRegistration WeakSet
review("Fix5", "c621d91",
"""用繁體中文回答：這個 fix 正確嗎？

目的：WeakSet.clear() 不存在，註解掉 _registeredApis.clear(); 並說明原因。

改動：
- _registeredApis.clear();
+ // (WeakSet.clear() does not exist, so we do nothing here.)

請說：LGTM 或 有問題+原因。""",
"review_result_fix5.txt")

print("ALL DONE", file=sys.stderr)
