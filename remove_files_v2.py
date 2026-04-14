#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

files = ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']

for f in files:
    r = subprocess.run(['git', '-C', proj, 'rm', '--cached', '-f', f], capture_output=True, text=True)
    print(f'git rm {f}: {r.returncode}')

# Commit removal
msg = """chore: 再次移除不相關的輔助檔案

移除 pr_body.txt, review_prompt.txt, run_claude_review.py（輔助腳本，不屬於專案）"""

r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print(f'commit: {r2.returncode}')
if r2.returncode != 0:
    print('STDERR:', r2.stderr)

r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print(f'push: {r3.returncode}')
if r3.returncode != 0:
    print('STDERR:', r3.stderr)
else:
    print('Done!')
