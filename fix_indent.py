#!/usr/bin/env python3
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

old = '''            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r".*"),
            )

            # 正常檔案仍被處理
            assert result["status"] == "success"
            # 應有路徑相關的警告（output_root 之外）
            path_warnings = [r.message for r in caplog.records
                           if "output_root" in r.message or "之外" in r.message or "遍歷" in r.message]
            assert len(path_warnings) > 0'''

new = '''        result = extract_from_jar_impl(
            str(jar_path),
            str(output_root),
            re.compile(r".*"),
        )

        # 正常檔案仍被處理
        assert result["status"] == "success"
        # 應有路徑相關的警告（output_root 之外）
        path_warnings = [r.message for r in caplog.records
                        if "output_root" in r.message or "之外" in r.message or "遍歷" in r.message]
        assert len(path_warnings) > 0'''

if old in content:
    content = content.replace(old, new, 1)
    print('Fixed C-4a indentation')
else:
    print('Pattern not found, trying alternate...')
    # Show what's around line 394
    lines = content.split('\n')
    for i in range(392, 406):
        print(f'{i+1}: {repr(lines[i])}')

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)
