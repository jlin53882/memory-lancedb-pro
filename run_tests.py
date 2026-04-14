#!/usr/bin/env python3
import subprocess
import sys

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

r = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/test_audit_critical_fixes.py",
     "-v", "-k", "api_returns_more_than_batch_callback or untranslated_item_skips_on_translated",
     "--tb=short"],
    cwd=proj, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print('STDOUT:', r.stdout)
print('STDERR:', r.stderr[-3000:] if len(r.stderr) > 3000 else r.stderr)
print('Return code:', r.returncode)
