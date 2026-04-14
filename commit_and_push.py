#!/usr/bin/env python3
import subprocess
import sys

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

# Stage all changes
r1 = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)
print('git add:', r1.returncode)

# Amend commit
msg = '''fix(audit): CRITICAL 問題修復（C-1~C-11）+ C-3/C-1 增強

- C-1: 修正 remaining 切片邏輯 + 增強：API 回傳多於預期時截斷並報錯
- C-2: 新增 Gemini API 指數退避重試機制（3次+jitter）
- C-3: 批次縮減時標記原文而非混入輸出 + caller 檢查 _untranslated 標記
- C-4: 新增路徑遍歷防護，驗證 output_root 範圍
- C-5~C-10: 6處 ZIP bomb 防護，加大小限制
- C-11: while 迴圈加 break 保護

Fixes #65'''

r2 = subprocess.run(['git', '-C', proj, 'commit', '--amend', '-m', msg], capture_output=True, text=True)
print('git commit amend:', r2.returncode)
if r2.returncode != 0:
    print('STDERR:', r2.stderr)

# Force push to update PR
r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('git push:', r3.returncode)
if r3.returncode != 0:
    print('STDERR:', r3.stderr)
else:
    print('Push successful!')
