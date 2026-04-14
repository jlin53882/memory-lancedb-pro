import subprocess, json, os

with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\docs\pr_analysis\pr_body_v3.txt', 'r', encoding='utf-8') as f:
    body = f.read()

tmp = os.path.expanduser('~/tmp_pr_patch.json')
payload = json.dumps({'body': body}, ensure_ascii=False)
with open(tmp, 'w', encoding='utf-8') as f:
    f.write(payload)

result = subprocess.run(
    ['gh', 'api', '--method', 'PATCH',
     'repos/CortexReach/memory-lancedb-pro/pulls/597',
     '--input', tmp],
    capture_output=True, timeout=30
)
print(f'return code: {result.returncode}')
try:
    print('response:', result.stdout[:500])
except:
    pass
try:
    if result.stderr:
        print('stderr:', result.stderr[:300])
except:
    pass
os.remove(tmp)
