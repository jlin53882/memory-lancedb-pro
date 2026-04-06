#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

base_url = "http://127.0.0.1:4096"

# Step 1: Create session
req = urllib.request.Request(
    f"{base_url}/session",
    method="POST",
    data=json.dumps({}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=120) as resp:
    session = json.loads(resp.read().decode("utf-8"))
    session_id = session["id"]
    print(f"Session ID: {session_id}")

# Step 2: Send message using correct format
prompt = """你是 code review 專家（繁體中文回覆）。

以下是一個 fix commit 的 diff，請確認：
1. 邏輯是否正確（當 this.decayEngine 存在時，recencyBoosted = mapped，跳過 applyRecencyBoost 以避免重複加成）
2. 是否有副作用或 regression
3. 程式碼風格是否一致

【原始】：
const recencyBoosted = this.applyRecencyBoost(mapped);

【修改後】：
const recencyBoosted = this.decayEngine
  ? mapped
  : this.applyRecencyBoost(mapped);

【註解】：當 decayEngine 存在時，跳過 applyRecencyBoost 以避免重複加成。

回覆格式（只選一種）：
- 完全沒問題：LGTM
- 有問題：ISSUES: [說明問題及修復方式]
"""

body = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "minimax", "modelID": "MiniMax-M2.7"},
    "reasoningEffort": "high"
}

req2 = urllib.request.Request(
    f"{base_url}/session/{session_id}/message",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

print("Sending message...")
try:
    with urllib.request.urlopen(req2, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        info = result.get("info", {})
        if info.get("error"):
            print(f"API Error: {info['error']}")
        parts = result.get("parts", [])
        for p in parts:
            if p.get("type") == "text" and p.get("text", "").strip():
                print(p["text"].strip())
except urllib.error.HTTPError as e:
    body_err = e.read().decode("utf-8", errors="replace")
    print(f"HTTPError {e.code}: {body_err[:500]}")
