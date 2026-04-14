#!/usr/bin/env python3
import subprocess
import sys

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

r = subprocess.run(
    [sys.executable, "-m", "pytest", "-q"],
    cwd=proj, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(r.stdout)
print(r.stderr[-2000:] if len(r.stderr) > 2000 else r.stderr)
print('Return code:', r.returncode)
