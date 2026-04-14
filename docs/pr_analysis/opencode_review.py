import json, requests, time, sys

BASE = "http://127.0.0.1:18799"

REVIEW_PROMPT = """你是專業的程式碼安全審查員。請對 memory-lancedb-pro 的 Phase 1 實作做全面的對抗性審查，特別檢查以下內容：

1. pendingRecall TTL cleanup 邏輯是否正確
2. isRecallUsed() AND gate 是否完整（ID path + Summary path）
3. bad_recall_count 的讀寫邏輯是否有問題
4. autoCapture block boundary 是否正確
5. suppression threshold 是否一致（>= 2 與 scoring path）
6. 任何其他 hidden bug 或 edge case

請用繁體中文輸出，列出所有發現的問題（標明 P0/P1/P2）。
"""

# Create session
r = requests.post(f"{BASE}/session", json={
    "path": r"C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro",
    "agentId": "default"
})
print(f"Create session: {r.status_code}")
session = r.json()
sid = session["id"]
print(f"Session ID: {sid}")

# Send message
r = requests.post(f"{BASE}/session/{sid}/message", json={
    "message": REVIEW_PROMPT,
    "noReply": False
})
print(f"Send message: {r.status_code}")

# Poll for completion
for i in range(60):
    time.sleep(5)
    r = requests.get(f"{BASE}/session/{sid}/messages")
    msgs = r.json()
    # Get last assistant message
    for m in msgs:
        if m.get("role") == "assistant":
            content = m.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        print(f"\n=== OpenCode Response ===")
                        print(block.get("text", "")[:5000])
            break
    # Check if done
    r2 = requests.get(f"{BASE}/session/{sid}")
    s = r2.json()
    if s.get("status") != "running":
        print(f"\nSession done: {s.get('status')}")
        break
    print(f"  [{i*5}s] still running...")
else:
    print("Timeout!")

# Cleanup
print(f"\nSession URL: http://127.0.0.1:18799/session/{sid}")
