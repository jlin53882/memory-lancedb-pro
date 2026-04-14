import subprocess, os, json

prompt_file = r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\issue-514-adversarial-prompt.py'
with open(prompt_file, 'r', encoding='utf-8') as f:
    prompt = f.read()

report_file = r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\issue-514-comprehensive-report.md'
with open(report_file, 'r', encoding='utf-8') as f:
    report = f.read()

full_prompt = prompt + '\n\n---\n\n## 分析報告全文：\n\n' + report

print(f'Full prompt length: {len(full_prompt)} chars', flush=True)

cmd = ['claude', '-p', full_prompt, '--output-format', 'json']
r = subprocess.run(cmd, capture_output=True, timeout=300)

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
        with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\issue-514-adversarial-review.md', 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Written {len(result)} chars", flush=True)
        print("SUCCESS", flush=True)
        print(result[:1000], flush=True)
    else:
        print("No result field found", flush=True)
        print(str(out)[:1000], flush=True)
else:
    stderr_text = r.stderr.decode('utf-8', errors='replace') if r.stderr else ''
    print(f"RC != 0: {r.returncode}", flush=True)
    print(f"Stderr: {stderr_text[:500]}", flush=True)
