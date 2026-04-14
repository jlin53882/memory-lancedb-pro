#!/usr/bin/env python3
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find positions
c10_idx = content.find('class TestC10ZipBombLangMergeContentCopy')
c11_idx = content.find('class TestC11InfiniteLoopProtection')

c10_line = content[:c10_idx].count('\n') + 1
c11_line = content[:c11_idx].count('\n') + 1

# Find end of file (no Regression section after C-11)
print(f'C-10 class at line {c10_line}')
print(f'C-11 class at line {c11_line}')
print(f'File total lines: {len(content.split(chr(10)))}')

# Show C-10 and C-11 class headers
lines = content.split('\n')
for i in range(c10_line-1, min(c11_line+5, len(lines))):
    print(f'{i+1}: {repr(lines[i][:80])}')
