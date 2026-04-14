#!/usr/bin/env python3
"""Fix remaining test issues"""
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Fix C-4a: Replace patch.object(log_unit...) with caplog approach
# Find the old assertion and replace it
old = '        # PATCH: 程式碼使用 log_unit.log_warning，非 logger.warning\n        with patch.object(log_unit, "log_warning") as mock_warning:\n            result = extract_from_jar_impl(\n                str(jar_path),\n                str(output_root),\n                re.compile(r".*"),\n            )\n\n            # 正常檔案仍被處理\n            assert result["status"] == "success"\n            # 應有路徑相關的警告（output_root 之外）\n            warning_calls = [str(c) for c in mock_warning.call_args_list]\n            path_warnings = [c for c in warning_calls if "output_root" in c or "之外" in c or "遍歷" in c]\n            assert len(path_warnings) > 0, f"Expected \'outside output_root\' warning, got: {warning_calls}"'

new = '        # 使用 caplog 捕獲日誌\n        import logging\n        caplog.set_level(logging.WARNING)\n            result = extract_from_jar_impl(\n                str(jar_path),\n                str(output_root),\n                re.compile(r".*"),\n            )\n\n            # 正常檔案仍被處理\n            assert result["status"] == "success"\n            # 應有路徑相關的警告（output_root 之外）\n            path_warnings = [r.message for r in caplog.records\n                           if "output_root" in r.message or "之外" in r.message or "遍歷" in r.message]\n            assert len(path_warnings) > 0, f"Expected \'outside output_root\' warning, got: {path_warnings}"'

if old in content:
    content = content.replace(old, new, 1)
    print('Fixed C-4a (patch to caplog)')
else:
    print('C-4a pattern not found')
    idx = content.find('patch.object(log_unit')
    if idx >= 0:
        print('Found at:', repr(content[idx-20:idx+200]))

# Fix C-10: replace the inspect-based test with behavioral test
old10 = '        # PATCH: _MAX_TEXT_SIZE 是 10*1024*1024，搜數值或表達式\n        from translation_tool.core.lang_merge_content_copy import process_content_or_copy_file_impl\n        import inspect\n        source = inspect.getsource(process_content_or_copy_file_impl)\n        # 搜 "10485760"（10MB）或 "10 * 1024 * 1024"\n        has_size_check = ("10485760" in source) or (source.count("1024") >= 2 and "10" in source)\n        assert has_size_check, f"Expected 10MB size constant in source"'

new10 = '        # 改為行為測試：建立超大文字檔，確認被拒絕\n        from translation_tool.core.lang_merge_content_copy import process_content_or_copy_file_impl\n        import zipfile, io\n        jar_path_io = io.BytesIO()\n        big_text = "X" * (11 * 1024 * 1024)\n        with zipfile.ZipFile(jar_path_io, "w") as zf:\n            zf.writestr("assets/testmod/lang/en_us.json", big_text)\n        zf2 = zipfile.ZipFile(io.BytesIO(jar_path_io.getvalue()), "r")\n        result = process_content_or_copy_file_impl(\n            zf=zf2,\n            input_path="assets/testmod/lang/en_us.json",\n            rules=[],\n            output_base=io.BytesIO(),\n        )\n        assert result.get("error") or result.get("skipped"), f"Expected oversized file rejected, got: {result}"'

if old10 in content:
    content = content.replace(old10, new10, 1)
    print('Fixed C-10 (behavioral test)')
else:
    print('C-10 pattern not found')

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)
print('Done')
