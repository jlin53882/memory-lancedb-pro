import urllib.request
import urllib.error
import json
import os

base_url = 'http://127.0.0.1:4096'
session_id = 'ses_2a94f5cb4ffe7wk8f71GXkY4db'

# Check OpenCode config for model settings
config_paths = [
    os.path.expanduser('~/.opencode/settings.json'),
    os.path.expanduser('~/.opencode/config.json'),
    'C:/Users/admin/.opencode/settings.json',
]
for p in config_paths:
    try:
        if os.path.exists(p):
            with open(p) as f:
                print(f'Config {p}:', f.read()[:500])
    except Exception as e:
        print(f'Error reading {p}: {e}')

# Check environment for API keys
print('\n--- Environment ---')
for k in ['OPENROUTER_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
    v = os.environ.get(k, '')
    print(f'{k}: {"set" if v else "not set"}')
