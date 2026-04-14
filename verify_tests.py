#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

r = subprocess.run(
    [subprocess.getoutput('python'), "-m", "pytest",
     "tests/test_audit_critical_fixes.py",
     "-v", "-k", "api_returns_more_than_batch_callback or untranslated_item_skips_on_translated or C1 or C3",
     "--tb=short"],
    cwd=proj, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print('STDOUT:', r.stdout[-3000:] if len(r.stdout) > 3000 else r.stdout)
print('Return code:', r.returncode)
