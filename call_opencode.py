import subprocess
import json

# Create a new session
result = subprocess.run([
    'curl.exe', '-X', 'POST',
    'http://127.0.0.1:4096/session',
    '-H', 'Content-Type: application/json',
    '-d', '{}',
    '-s'
], capture_output=True, text=True, timeout=30)
print('create session:', result.stdout)
session_data = json.loads(result.stdout)
session_id = session_data['id']
print('session_id:', session_id)

# Send message
import urllib.request, urllib.error

prompt = '''你是 code review 專家。請用繁體中文回覆。

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

如果有任何問題，請明確說明 issues 有哪些。如果完全沒問題，請回覆「LGTM」。'''

body = {
    'parts': [{'type': 'text', 'text': prompt}],
    'model': {'providerID': 'openrouter', 'modelID': 'anthropic/claude-3-haiku'}
}

msg_req = urllib.request.Request(
    f'http://127.0.0.1:4096/session/{session_id}/message',
    data=json.dumps(body).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

print('Sending message...')
try:
    with urllib.request.urlopen(msg_req, timeout=120) as resp:
        raw = resp.read()
        print('response length:', len(raw))
        if raw:
            result_data = json.loads(raw)
            print('result:', json.dumps(result_data, ensure_ascii=False, indent=2))
        else:
            print('Empty response body')
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode())
except Exception as e:
    print('Error:', e)
