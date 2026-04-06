import urllib.request
import json

# Reuse the first session from the earlier successful create
# Actually, let's create a brand new session and handle streaming

session_req = urllib.request.Request(
    'http://127.0.0.1:4096/session',
    data=json.dumps({}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(session_req, timeout=30) as resp:
    session_data = json.loads(resp.read())
    session_id = session_data['id']
    print('session_id:', session_id)

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

msg_req = urllib.request.Request(
    f'http://127.0.0.1:4096/session/{session_id}/message',
    data=json.dumps({
        'parts': [{'type': 'text', 'text': prompt}],
        'model': {'providerID': 'openrouter', 'modelID': 'anthropic/claude-3-haiku'}
    }).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

# Use iterator to read streaming response
print('Sending message, waiting for response...')
try:
    with urllib.request.urlopen(msg_req, timeout=120) as resp:
        print('Status:', resp.status)
        print('Headers:', dict(resp.headers))
        
        # Try reading as iterator
        buffer = b''
        for chunk in resp:
            buffer += chunk
            print('chunk received:', len(chunk))
        
        print('Total buffer:', len(buffer))
        print('Buffer text:', buffer.decode('utf-8', errors='replace')[:5000])
except Exception as e:
    print('Error:', e)
    import traceback; traceback.print_exc()
