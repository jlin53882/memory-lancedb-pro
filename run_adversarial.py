import subprocess, os, json

with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\adversarial_prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

print(f"Prompt length: {len(prompt)} chars", flush=True)

cmd = ['claude', '-p', prompt, '--output-format', 'json']
r = subprocess.run(cmd, capture_output=True, timeout=300)
print(f"RC: {r.returncode}", flush=True)

if r.returncode == 0:
    try:
        stdout_text = r.stdout.decode('utf-8', errors='replace')
        out = json.loads(stdout_text.strip())
    except Exception as e:
        print(f"JSON parse error: {e}", flush=True)
        print(f"Stdout preview: {r.stdout[:200]}", flush=True)
        out = {}

    result = out.get('result', '')
    if result:
        with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\proposal-b-adversarial-review.md', 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Written {len(result)} chars", flush=True)
        print("SUCCESS - first 500 chars:", flush=True)
        print(result[:500], flush=True)
    else:
        print("No result field found", flush=True)
        print("Full output:", flush=True)
        print(str(out)[:1000], flush=True)
else:
    stderr_text = r.stderr.decode('utf-8', errors='replace') if r.stderr else ''
    print(f"RC != 0: {r.returncode}", flush=True)
    print(f"Stderr: {stderr_text[:500]}", flush=True)
