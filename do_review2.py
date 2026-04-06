import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts")
from opencode_task import OpenCodeAPI

prompt = """你是 code review 專家。請用繁體中文回覆。

請 review 以下這個 commit 的改動：

commit c621d913ced3aa1b394498bfd536fb85e66d1d1b
fix: remove invalid WeakSet.clear() call from resetRegistration()

diff:
-  _registeredApis.clear();
+  // (WeakSet.clear() does not exist, so we do nothing here.)

請確認：
1. 這個 fix 的邏輯是否正確（WeakSet.clear() 是否真的不存在）
2. 是否有副作用或 regression
3. 程式碼風格是否一致

如果有任何問題，請明確說明 issues 有哪些。如果完全沒問題，請回覆「LGTM」。"""

client = OpenCodeAPI(timeout=120)
print("health:", client.is_healthy())
sid = client.create_session(title="code-review")
print("session_id:", sid)

try:
    response = client.send_message(
        prompt=prompt,
        session_id=sid,
        model="minimax/MiniMax-M2.7",
        reasoning="medium",
    )
    print("response:", response)
    text = client.extract_text(response)
    print("text:", text)
except Exception as e:
    print("Error:", e)
    import traceback; traceback.print_exc()
