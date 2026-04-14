#!/usr/bin/env python3
import os
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

files = ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']

for f in files:
    path = os.path.join(proj, f)
    if os.path.exists(path):
        os.remove(path)
        print(f'Deleted: {f}')
    else:
        print(f'Not found: {f}')

# Now commit the deletion
msg = "chore: 實體刪除輔助檔案，避免 git add -A 反覆加入"

r = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)
print('git add:', r.returncode)

r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print('commit:', r2.returncode)
if r2.returncode != 0:
    print('STDERR:', r2.stderr)

r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('push:', r3.returncode)
if r3.returncode != 0:
    print('STDERR:', r3.stderr)
else:
    print('Done!')
