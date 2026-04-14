#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

for f in ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']:
    subprocess.run(['git', '-C', proj, 'rm', '--cached', '-f', f], capture_output=True, text=True)
    print(f'Removed: {f}')

msg = "chore: 再次移除不相關輔助檔案"

r = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print('commit:', r.returncode)

r2 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('push:', r2.returncode)
print('Done!' if r2.returncode == 0 else 'Failed!')
