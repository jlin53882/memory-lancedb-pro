#!/usr/bin/env python3
"""Fix test methods: remove 'self' param and clean up broken mocks"""
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix C-6a: test_extract_rejects_binary_over_100mb
    if 'test_extract_rejects_binary_over_100mb(self, tmp_path: Path, monkeypatch)' in line:
        line = line.replace('test_extract_rejects_binary_over_100mb(self, tmp_path: Path, monkeypatch)',
                          'test_extract_rejects_binary_over_100mb(self, tmp_path: Path)')
    
    # Fix C-6b: test_extract_accepts_normal_sized_binary
    if 'test_extract_accepts_normal_sized_binary(self, tmp_path: Path, monkeypatch)' in line:
        line = line.replace('test_extract_accepts_normal_sized_binary(self, tmp_path: Path, monkeypatch)',
                          'test_extract_accepts_normal_sized_binary(self, tmp_path: Path)')
    
    # Fix C-9: test_icon_preview_module_has_size_check_logic  
    if 'test_icon_preview_module_has_size_check_logic(self):' in line:
        line = line.replace('test_icon_preview_module_has_size_check_logic(self):',
                          'test_icon_preview_module_has_size_check_logic(self):')
    
    # Skip the broken scan_jars mock patch lines and fix the body
    if 'with patch("translation_tool.core.jar_processor_extract.scan_jars", return_value={}):' in line:
        # Remove this line and next line (the indented body starts)
        # Skip this whole mock block - we'll just call the function directly
        i += 1  # skip the 'with patch(' line
        # Skip indented lines until we find unindented code
        while i < len(lines) and (lines[i].startswith('            ') or lines[i].strip() == ''):
            # Skip these lines
            # But we need to keep 'result = extract_from_jar_impl...' onwards
            if lines[i].startswith('            result = extract_from_jar_impl'):
                # Replace the whole mock-wrapped call with just the call
                fixed_lines.append(lines[i].replace('            result = extract_from_jar_impl', '        result = extract_from_jar_impl'))
                i += 1
                # Now copy remaining lines (indented within the mock block)
                while i < len(lines) and (lines[i].startswith('                ') or lines[i].strip() == ''):
                    if lines[i].startswith('                '):
                        fixed_lines.append(lines[i].replace('                ', '            ', 1))
                    i += 1
                break
            else:
                i += 1
        continue
    
    # Remove 'from unittest.mock import' lines that were added for patches
    if 'from unittest.mock import MagicMock, patch, Mock' in line and 'from translation_tool' not in line:
        i += 1
        continue
    
    fixed_lines.append(line)
    i += 1

new_content = '\n'.join(fixed_lines)
with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(new_content)
print(f'Done! Fixed file from {len(lines)} to {len(fixed_lines)} lines')
