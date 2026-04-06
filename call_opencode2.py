import subprocess
import json
import urllib.request
import threading

# Create a new session
result = subprocess.run([
    'curl.exe', '-X', 'POST',
    'http://127.0.0.1:4096/session',
    '-H', 'Content-Type: application/json',
    '-d', '{}',
    '-s'
], capture_output=True, text=True, timeout=30)
session_data = json.loads(result.stdout)
session_id = session_data['id']
print('session_id:', session_id)

prompt = '''你是 code review 專家。請用繁體中文回覆。請 review commit：_registeredApis.clear(); 改為 // (WeakSet.clear() does not exist, so we do nothing here.)。確認：1.邏輯正確 2.無副作用 3.風格一致。如果沒問題回覆 LGTM。'''

body = {
    'parts': [{'type': 'text', 'text': prompt}],
    'model': {'providerID': 'openrouter', 'modelID': 'anthropic/claude-3-haiku'}
}

# Try with curl to see streaming output
result2 = subprocess.run([
    'curl.exe', '-X', 'POST',
    f'http://127.0.0.1:4096/session/{session_id}/message',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(body),
    '-s', '-N', '-w', '\n---HTTP:%{http_code}---'
], capture_output=True, text=True, timeout=120)
print('curl stdout:', repr(result2.stdout[:3000]))
print('curl stderr:', result2.stderr[:500])
