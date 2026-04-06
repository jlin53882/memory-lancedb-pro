"""
OpenCode HTTP API call for code review.
"""
import urllib.request
import urllib.error
import json
import time

base_url = 'http://127.0.0.1:4096'

def create_session():
    req = urllib.request.Request(
        base_url + '/session',
        data=b'{}',
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data['id']

def send_message(session_id, prompt, model_provider='openrouter', model_id='openai/gpt-4o-mini'):
    payload = {
        'parts': [{'type': 'text', 'text': prompt}],
        'model': {'providerID': model_provider, 'modelID': model_id}
    }
    req = urllib.request.Request(
        base_url + '/session/' + session_id + '/message',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())

# Try different providers that might not have credit issues
providers_to_try = [
    ('openrouter', 'openai/gpt-4o-mini'),
    ('openrouter', 'anthropic/claude-3-haiku-20240307'),
    ('openrouter', 'google/gemini-2.0-flash'),
    ('openrouter', 'meta-llama/llama-3-8b-instruct'),
]

prompt = "Code review commit 1bac9e6: regex in stripEnvelopeMetadata changed from 'You are running as a subagent.*?' to 'You are running as a subagent\\b.*?'. Is this correct fix for greedy matching? Reply: LGTM or ISSUES:"

for provider, model in providers_to_try:
    print(f'\nTrying {provider}/{model}...')
    try:
        session_id = create_session()
        print(f'  Session: {session_id}')
        result = send_message(session_id, prompt, provider, model)
        text_parts = [p.get('text', '') for p in result.get('parts', [])]
        text = ''.join(text_parts)
        error = result.get('info', {}).get('error', {})
        if error:
            print(f'  Error: {error.get("message", str(error))[:200]}')
        if text:
            print(f'  Response: {text[:500]}')
            if 'LGTM' in text or 'ISSUES' in text:
                print('SUCCESS!')
                break
    except Exception as e:
        print(f'  Exception: {e}')
