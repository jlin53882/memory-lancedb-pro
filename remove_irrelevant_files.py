#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

files_to_remove = ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']

for f in files_to_remove:
    r = subprocess.run(['git', '-C', proj, 'rm', '--cached', '-f', f], capture_output=True, text=True)
    print(f'git rm {f}: {r.returncode}')

# Commit the removal
msg = '''chore: 移除不相關的輔助檔案

移除 review_prompt.txt, run_claude_review.py, pr_body.txt（這些是輔助腳本，不屬於專案程式碼）

'''
r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print(f'commit: {r2.returncode}')
if r2.returncode != 0:
    print('STDERR:', r2.stderr)

# Force push to update PR
r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print(f'push: {r3.returncode}')
if r3.returncode != 0:
    print('STDERR:', r3.stderr)
else:
    print('Done!')
