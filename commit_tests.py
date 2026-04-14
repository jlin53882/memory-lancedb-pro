#!/usr/bin/env python3
import subprocess, os

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

# Check for untracked helper files
for f in ['pr_body.txt', 'review_prompt.txt', 'run_claude_review.py']:
    p = os.path.join(proj, f)
    if os.path.exists(p):
        os.remove(p)
        print(f'Re removed: {f}')

# Stage all
r1 = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)

msg = """test(audit): 修補測試與實作不同步的問題

8 個過時測試修正：
- C-4a/b: monkeypatch(logger) -> caplog fixture
- C-6a/b: 移除失效的 scan_jars mock，改為直接測試行為
- C-7: 改用 _scan_single_jar（原 scan_jars 為內部函式）
- C-9: _extract_jar_icon_impl -> _extract_jar_icon
- C-10: 改為行為測試（超大文字檔被拒絕）
- C-11: Option A（驗證不凍住 + 新 shard 建立）

29/29 tests passed

Ref #65"""

r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print('commit:', r2.returncode)
if r2.returncode != 0:
    print('STDERR:', r2.stderr[:500])

r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('push:', r3.returncode)
if r3.returncode != 0:
    print('STDERR:', r3.stderr[:500])
else:
    print('Done!')
