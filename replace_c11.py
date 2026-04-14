#!/usr/bin/env python3
"""Replace the C-11 class in test_audit_critical_fixes.py"""
import os

test_file = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
fix_file = r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\test_c11_fix.py'

with open(test_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

with open(fix_file, 'r', encoding='utf-8', errors='replace') as f:
    new_class = f.read()

# Find C-11 class start
idx_start = content.find('class TestC11InfiniteLoopProtection:')
if idx_start < 0:
    print('ERROR: C-11 class not found!')
else:
    # Find the end of the file (since C-11 is the last class)
    # Remove the old C-11 class
    old_class = content[idx_start:]
    new_content = content[:idx_start] + new_class + '\n'
    
    with open(test_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write(new_content)
    
    print('Replaced C-11 class successfully')
    print(f'New class length: {len(new_class)} chars')
