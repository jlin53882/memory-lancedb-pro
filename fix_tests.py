#!/usr/bin/env python3
"""修補 test_audit_critical_fixes.py 中 8 個過時的測試"""
import re

fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

changes = 0

# ============================================================
# Fix 1: C-4 兩個測試 - patch log_unit.log_warning 而非 logger.warning
# ============================================================
old_c4_import = 'from unittest.mock import MagicMock, patch, Mock'
new_c4_import = 'from unittest.mock import MagicMock, patch, Mock\nfrom translation_tool.utils import log_unit'

if old_c4_import in content and new_c4_import not in content:
    content = content.replace(old_c4_import, new_c4_import)
    changes += 1
    print('Fix 1: Added log_unit import')

# Patch the C-4 tests to use log_unit.log_warning
# Test 1: test_path_outside_output_root_is_rejected
old_c4_test1 = '''        logger = logging.getLogger("translation_tool.core.jar_processor_extract")
        with patch.object(logger, "warning") as mock_warning:
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r".*"),
            )

            # 正常檔案仍被處理
            assert result["status"] == "success"
            # 應有路徑相關的警告（output_root 之外）
            warning_messages = [str(m) for m in mock_warning.call_args_list]
            path_warnings = [m for m in warning_messages if "output_root" in m or "之外" in m or "遍歷" in m]
            assert len(path_warnings) > 0, f"Expected 'outside output_root' warning, got: {warning_messages}"'''

new_c4_test1 = '''        # PATCH: 程式碼使用 log_unit.log_warning，非 logger.warning
        with patch.object(log_unit, "log_warning") as mock_warning:
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r".*"),
            )

            # 正常檔案仍被處理
            assert result["status"] == "success"
            # 應有路徑相關的警告（output_root 之外）
            warning_calls = [str(c) for c in mock_warning.call_args_list]
            path_warnings = [c for c in warning_calls if "output_root" in c or "之外" in c or "遍歷" in c]
            assert len(path_warnings) > 0, f"Expected 'outside output_root' warning, got: {warning_calls}"'''

if old_c4_test1 in content:
    content = content.replace(old_c4_test1, new_c4_test1)
    changes += 1
    print('Fix 1a: test_path_outside_output_root_is_rejected patched')
else:
    print('Fix 1a: Pattern not found')

# Test 2: test_path_traversal_sequence_is_detected
old_c4_test2 = '''        logger = logging.getLogger("translation_tool.core.jar_processor_extract")
        with patch.object(logger, "warning") as mock_warning:
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r".*"),
            )

            assert result["status"] == "success"
            warning_messages = [str(m) for m in mock_warning.call_args_list]
            # 檢查是否有路徑遍歷相關的警告
            traversal_warnings = [m for m in warning_messages if "output_root" in m or "之外" in m]
            assert len(traversal_warnings) > 0'''

new_c4_test2 = '''        # PATCH: 程式碼使用 log_unit.log_warning，非 logger.warning
        with patch.object(log_unit, "log_warning") as mock_warning:
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r".*"),
            )

            assert result["status"] == "success"
            warning_calls = [str(c) for c in mock_warning.call_args_list]
            traversal_warnings = [c for c in warning_calls if "output_root" in c or "之外" in c]
            assert len(traversal_warnings) > 0, f"Expected traversal warning, got: {warning_calls}"'''

if old_c4_test2 in content:
    content = content.replace(old_c4_test2, new_c4_test2)
    changes += 1
    print('Fix 1b: test_path_traversal_sequence_is_detected patched')
else:
    print('Fix 1b: Pattern not found')

# ============================================================
# Fix 2: C-6 兩個測試 - scan_jars 在 jar_browser，需正確 patch
# ============================================================
old_c6_test1 = '''        with patch("translation_tool.core.jar_processor_extract.scan_jars", return_value={}):
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r"assets/testmod/big\\.png$"),
            )

            assert result["status"] == "success"
            assert result["skipped"] >= 1
            assert result["extracted"] == 0'''

new_c6_test1 = '''        # PATCH: scan_jars 是從 jar_browser 動態 import，patch 來源模組
        with patch("translation_tool.utils.jar_browser.scan_single_jar", return_value=(jar_path, {})):
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r"assets/testmod/big\\.png$"),
            )

            assert result["status"] == "success"
            assert result["skipped"] >= 1
            assert result["extracted"] == 0'''

if old_c6_test1 in content:
    content = content.replace(old_c6_test1, new_c6_test1)
    changes += 1
    print('Fix 2a: test_extract_rejects_binary_over_100mb patched')
else:
    print('Fix 2a: Pattern not found')

old_c6_test2 = '''        with patch("translation_tool.core.jar_processor_extract.scan_jars", return_value={}):
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r"assets/testmod/test\\.png$"),
            )

            assert result["status"] == "success"
            assert result["extracted"] == 1'''

new_c6_test2 = '''        # PATCH: scan_jars 是從 jar_browser 動態 import，patch 來源模組
        with patch("translation_tool.utils.jar_browser.scan_single_jar", return_value=(jar_path, {})):
            result = extract_from_jar_impl(
                str(jar_path),
                str(output_root),
                re.compile(r"assets/testmod/test\\.png$"),
            )

            assert result["status"] == "success"
            assert result["extracted"] == 1'''

if old_c6_test2 in content:
    content = content.replace(old_c6_test2, new_c6_test2)
    changes += 1
    print('Fix 2b: test_extract_accepts_normal_sized_binary patched')
else:
    print('Fix 2b: Pattern not found')

# ============================================================
# Fix 3: C-7 - jar_browser._MAX_TEXT_FILE_SIZE 是 10*1024*1024
# 用 inspect.getsource 搜數值而非字串 "10"
# ============================================================
old_c7 = '''        from translation_tool.utils.jar_browser import scan_jars
        import inspect
        source = inspect.getsource(scan_jars)
        assert "10" in source and "1024" in source'''

new_c7 = '''        # PATCH: _MAX_TEXT_FILE_SIZE = 10*1024*1024，搜數值而非字串
        from translation_tool.utils.jar_browser import scan_single_jar
        import inspect
        source = inspect.getsource(scan_single_jar)
        # 搜 "10485760"（10MB 的 bytes 數值）或 "10 * 1024 * 1024" 表達式
        has_10mb = "10485760" in source or ("10" in source and "1024" in source and "1024" in source)
        assert has_10mb, f"Expected 10MB size constant in source"'''

if old_c7 in content:
    content = content.replace(old_c7, new_c7)
    changes += 1
    print('Fix 3: C-7 constant test fixed')
else:
    print('Fix 3: C-7 pattern not found')

# ============================================================
# Fix 4: C-9 - _extract_jar_icon_impl 不存在，改為測試 _extract_jar_icon
# ============================================================
old_c9 = '''        from app.views.icon_preview_view import _extract_jar_icon_impl
        import inspect
        # 確認函式可以被引用
        assert callable(_extract_jar_icon_impl)
        # _extract_jar_icon_impl 存在（包含大小檢查）
        from app.views.icon_preview_view import _extract_jar_icon_impl
        source = inspect.getsource(_extract_jar_icon_impl)
        # 驗證有 _check_size 的呼叫
        has_check = "_check_size" in source or "file_size" in source
        assert has_check, "Expected size check in _extract_jar_icon_impl"'''

new_c9 = '''        # PATCH: _extract_jar_icon_impl 已改名為 _extract_jar_icon
        from app.views.icon_preview_view import _extract_jar_icon
        import inspect
        # 確認函式可以被引用
        assert callable(_extract_jar_icon)
        source = inspect.getsource(_extract_jar_icon)
        # 驗證有 _check_size 的呼叫（大小檢查存在）
        has_check = "_check_size" in source or "file_size" in source
        assert has_check, "Expected size check in _extract_jar_icon"'''

if old_c9 in content:
    content = content.replace(old_c9, new_c9)
    changes += 1
    print('Fix 4: C-9 import fixed')
else:
    print('Fix 4: C-9 pattern not found')

# ============================================================
# Fix 5: C-10 - lang_merge_content_copy 的 _MAX_TEXT_SIZE
# ============================================================
old_c10 = '''        from translation_tool.core.lang_merge_content_copy import process_content_or_copy_file_impl
        import inspect
        source = inspect.getsource(process_content_or_copy_file_impl)
        # 確認原始碼中有 10MB 大小限制
        assert "10" in source and "1024" in source'''

new_c10 = '''        # PATCH: _MAX_TEXT_SIZE 是 10*1024*1024，搜數值或表達式
        from translation_tool.core.lang_merge_content_copy import process_content_or_copy_file_impl
        import inspect
        source = inspect.getsource(process_content_or_copy_file_impl)
        # 搜 "10485760"（10MB）或 "10 * 1024 * 1024"
        has_10mb = "10485760" in source or ("10" in source and source.count("1024") >= 2)
        assert has_10mb, f"Expected 10MB size constant in source"'''

if old_c10 in content:
    content = content.replace(old_c10, new_c10)
    changes += 1
    print('Fix 5: C-10 constant test fixed')
else:
    print('Fix 5: C-10 pattern not found')

# ============================================================
# Fix 6: C-11 - 實作會先 rotate shard，正常寫入；調整測試期望
# 測試「第 4 個 full shard」情境，強制進入停滯分支
# ============================================================
old_c11 = '''    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path, monkeypatch):
        """當連續 3 次未寫入時，應中斷迴圈並記錄錯誤。"""
        from translation_tool.utils import cache_shards
        import orjson as json
        import logging
        import io

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")

        # 寫入一個已滿的分片（容量為 rolling_shard_size=2，但分片已經是 2 個項目）
        existing = {"k1": {"src": "a", "dst": "A"}, "k2": {"src": "b", "dst": "B"}}
        (type_dir / "lang_00001.json").write_bytes(json.dumps(existing))

        # 設定 logger mock
        test_logger = logging.getLogger("translation_tool.utils.cache_shards")
        original_handlers = test_logger.handlers[:]
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.DEBUG)

        entries = {"new1": {"src": "c", "dst": "C"}}

        cache_shards._save_entries_to_active_shards(
            type_dir=type_dir,
            cache_type="lang",
            entries=entries,
            rolling_shard_size=2,
            active_shard_file=".active",
            logger=test_logger,
        )

        output = stream.getvalue()

        # 確認有停滯相關的日誌
        assert "停滯" in output or "放棄寫入" in output or "未寫入" in output, \\
            f"Expected stall warning in log output, got: {output}"'''

new_c11 = '''    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path, monkeypatch):
        """當連續 3 次嘗試寫入但寫入量為 0 時，應中斷迴圈並記錄錯誤。

        PATCH: 實作會先 rotate shard，正常情況下會成功寫入。
        因此我們 mock save 讓它每次都拋異常，逼出停滯分支。
        """
        from translation_tool.utils import cache_shards
        import orjson as json
        import logging
        import io

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")

        # 寫入一個已滿的分片（容量為 rolling_shard_size=2，但分片已經是 2 個項目）
        existing = {"k1": {"src": "a", "dst": "A"}, "k2": {"src": "b", "dst": "B"}}
        (type_dir / "lang_00001.json").write_bytes(json.dumps(existing))

        # 設定 logger mock
        test_logger = logging.getLogger("translation_tool.utils.cache_shards")
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.DEBUG)

        entries = {"new1": {"src": "c", "dst": "C"}}

        # PATCH: Mock save 讓它每次都失敗，逼出停滯分支
        def fake_save(*args, **kwargs):
            return 0  # 回傳 0 表示寫入量為 0

        import translation_tool.utils.cache_shards as cs_module
        orig_save = cs_module._save_shard_data
        cs_module._save_shard_data = fake_save

        try:
            cache_shards._save_entries_to_active_shards(
                type_dir=type_dir,
                cache_type="lang",
                entries=entries,
                rolling_shard_size=2,
                active_shard_file=".active",
                logger=test_logger,
            )
        finally:
            cs_module._save_shard_data = orig_save

        output = stream.getvalue()

        # 確認有停滯相關的日誌
        assert "停滯" in output or "放棄寫入" in output or "未寫入" in output, \\
            f"Expected stall warning in log output, got: {output}"'''

if old_c11 in content:
    content = content.replace(old_c11, new_c11)
    changes += 1
    print('Fix 6: C-11 stall test fixed')
else:
    print('Fix 6: C-11 pattern not found')

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)

print(f'\\nAll {changes} fixes applied!')
