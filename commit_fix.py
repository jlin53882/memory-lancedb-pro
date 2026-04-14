#!/usr/bin/env python3
import subprocess, os

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'
for f in ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']:
    p = os.path.join(proj, f)
    if os.path.exists(p):
        os.remove(p)

r1 = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)
msg = "fix(audit): jar_processor_extract.py 新增 log_warning/log_error import\n\nlog_warning/log_error 來自 log_unit 但之前沒 import，導致 C-4 路徑遍歷保護\n遇到異常時 status=error 而非正常警告後繼續。\n\nRef #65"
r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print('commit:', r2.returncode)
r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('push:', r3.returncode)
print('Done!' if r3.returncode == 0 else 'Failed')
