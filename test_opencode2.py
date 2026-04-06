#!/usr/bin/env python3
import urllib.request
import json

base_url = 'http://127.0.0.1:4096'

# Create session
req = urllib.request.Request(
    base_url + '/session',
    data=json.dumps({}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=30) as resp:
    session_data = json.loads(resp.read())
    session_id = session_data['id']
    print(f'Session: {session_id}')

# Send message with correct model format
prompt = "Say hello in one word"
payload = {
    "parts": [{"type": "text", "text": prompt}],
    "model": {"providerID": "minimax", "modelID": "MiniMax-M2.7"}
}

req = urllib.request.Request(
    base_url + '/session/' + session_id + '/message',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        text_parts = [p.get('text', '') for p in result.get('parts', [])]
        print('Response:', ''.join(text_parts))
except Exception as e:
    print('Error:', e)
