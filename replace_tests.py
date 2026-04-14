#!/usr/bin/env python3
"""Replace C-10 and C-11 tests with new behavioral versions"""
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'

with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Read new test content
with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\test_c10_new.py', 'r', encoding='utf-8', errors='replace') as f:
    new_c10 = f.read().strip()
with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\test_c11_new.py', 'r', encoding='utf-8', errors='replace') as f:
    new_c11 = f.read().strip()

# Find C-10 test
idx_c10_start = content.find('# C-10: ZIP bomb 防護')
idx_c10_end = content.find('\n# =============================================================================\n# C-11:', idx_c10_start)
if idx_c10_end < 0:
    idx_c10_end = content.find('\nclass TestC11', idx_c10_start)

# Find C-11 test
idx_c11_start = idx_c10_end
idx_c11_end = content.find('\n\n\n# =============================================================================\n# Regression', idx_c11_start)
if idx_c11_end < 0:
    idx_c11_end = len(content)

print(f'C-10: {idx_c10_start} - {idx_c10_end}')
print(f'C-11: {idx_c11_start} - {idx_c11_end}')

# Replace
new_content = content[:idx_c10_start] + new_c10 + '\n\n\n' + new_c11 + content[idx_c11_end:]

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(new_content)

print('Done!')
print(f'New file size: {len(new_content)} chars')
