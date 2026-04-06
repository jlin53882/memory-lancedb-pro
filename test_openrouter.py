import urllib.request
import json

# Try calling OpenRouter directly
api_key = "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"
model = "openai/gpt-4o-mini"

body = {
    "model": model,
    "messages": [{"role": "user", "content": "請用繁體中文回答：這個 fix 的邏輯是否正確？"}],
    "max_tokens": 500
}

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    method="POST",
    data=json.dumps(body).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "OpenClaw-Review"
    }
)
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        print(json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
