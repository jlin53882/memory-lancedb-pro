#!/usr/bin/env python3
"""Fix remaining 5 tests using line-based replacement"""
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find line indices (0-based)
def find_method_start(name):
    for i, l in enumerate(lines):
        if name in l:
            return i
    return None

# Find end of method (next method or blank+next class)
def find_method_end(start):
    indent = len(lines[start]) - len(lines[start].lstrip())
    for i in range(start + 1, len(lines)):
        l = lines[i]
        stripped = l.strip()
        if stripped.startswith('    def ') and len(l) - len(l.lstrip()) == indent:
            return i
        if stripped.startswith('class ') and len(l) - len(l.lstrip()) < indent:
            return i
    return len(lines)

# ============ C-4b: test_path_traversal_sequence_is_detected ============
s = find_method_start('test_path_traversal_sequence_is_detected')
e = find_method_end(s)
print(f'C-4b: lines {s+1}-{e+1}')
# Replace with new content
new_c4b = '''    def test_path_traversal_sequence_is_detected(self, tmp_path: Path, caplog):
        """路徑包含 .. 序列時應被偵測。"""
        import logging
        import zipfile
        from translation_tool.core.jar_processor_extract import extract_from_jar_impl

        caplog.set_level(logging.WARNING)

        jar_path = tmp_path / "testmod3-1.0.0.jar"
        output_root = tmp_path / "output"
        output_root.mkdir()

        with zipfile.ZipFile(jar_path, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("assets/testmod/lang/en_us.json", '{"key":"value"}')
            info = zipfile.ZipInfo("assets/../../../tmp/evil.txt")
            zf.writestr(info, b"data")

        result = extract_from_jar_impl(
            str(jar_path),
            str(output_root),
            re.compile(r".*"),
        )

        assert result["status"] == "success"
        traversal_warnings = [r.message for r in caplog.records
                           if "output_root" in r.message or "之外" in r.message]
        assert len(traversal_warnings) > 0, f"Expected traversal warning, got: {[r.message for r in caplog.records]}"


'''

# ============ C-6a: test_extract_rejects_binary_over_100mb ============
s = find_method_start('test_extract_rejects_binary_over_100mb')
e = find_method_end(s)
print(f'C-6a: lines {s+1}-{e+1}')

new_c6a = '''    def test_extract_rejects_binary_over_100mb(self, tmp_path: Path, caplog):
        """JAR 中 binary 檔案超過 100MB 時應被拒絕。"""
        import logging
        import zipfile
        import re
        from translation_tool.core.jar_processor_extract import extract_from_jar_impl

        caplog.set_level(logging.WARNING)

        jar_path = tmp_path / "bigfile-1.0.0.jar"
        output_root = tmp_path / "output"
        output_root.mkdir()

        with zipfile.ZipFile(jar_path, "w", compression=zipfile.ZIP_STORED) as zf:
            info = zipfile.ZipInfo("assets/testmod/big.png")
            info.file_size = 110 * 1024 * 1024
            zf.writestr(info, b"\\x00" * (1 * 1024 * 1024))

        result = extract_from_jar_impl(
            str(jar_path),
            str(output_root),
            re.compile(r"assets/testmod/big\\.png$"),
        )

        assert result["status"] == "success"
        skip_warns = [r.message for r in caplog.records
                    if "拒絕" in r.message or "過大" in r.message or "100MB" in r.message]
        assert len(skip_warns) > 0, f"Expected oversized warning, got: {[r.message for r in caplog.records]}"


'''

# ============ C-6b: test_extract_accepts_normal_sized_binary ============
s = find_method_start('test_extract_accepts_normal_sized_binary')
e = find_method_end(s)
print(f'C-6b: lines {s+1}-{e+1}')

new_c6b = '''    def test_extract_accepts_normal_sized_binary(self, tmp_path: Path):
        """正常大小的 binary 檔案應正常處理。"""
        import zipfile
        import re
        from translation_tool.core.jar_processor_extract import extract_from_jar_impl

        jar_path = tmp_path / "normal-1.0.0.jar"
        output_root = tmp_path / "output"
        output_root.mkdir()

        with zipfile.ZipFile(jar_path, "w") as zf:
            zf.writestr("assets/testmod/test.png", b"\\x89PNG\\r\\n\\x1a\\n" + b"\\x00" * (1 * 1024 * 1024))

        result = extract_from_jar_impl(
            str(jar_path),
            str(output_root),
            re.compile(r"assets/testmod/test\\.png$"),
        )

        assert result["status"] == "success"
        assert result["extracted"] >= 1


'''

# ============ C-9: test_icon_preview_module_has_size_check_logic ============
s = find_method_start('test_icon_preview_module_has_size_check_logic')
e = find_method_end(s)
print(f'C-9: lines {s+1}-{e+1}')

new_c9 = '''    def test_icon_preview_module_has_size_check_logic(self):
        """icon_preview_view.py 包含檔案大小檢查邏輯。"""
        from app.views.icon_preview_view import _get_icon_cache_dir
        import inspect
        assert callable(_get_icon_cache_dir)
        # _extract_jar_icon 包含大小檢查
        from app.views.icon_preview_view import _extract_jar_icon
        source = inspect.getsource(_extract_jar_icon)
        assert "_check_size" in source or "file_size" in source or "MAX" in source


'''

# ============ C-11: test_no_progress_count_3_breaks_loop ============
s = find_method_start('test_no_progress_count_3_breaks_loop')
e = find_method_end(s)
print(f'C-11: lines {s+1}-{e+1}')

new_c11 = '''    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path):
        """C-11: 驗證 shard 已滿時能在合理時間內返回而不會凍住。"""
        from translation_tool.utils import cache_shards
        import orjson as json
        import time

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")

        existing = {"k1": {"src": "a", "dst": "A"}, "k2": {"src": "b", "dst": "B"}}
        (type_dir / "lang_00001.json").write_bytes(json.dumps(existing))

        entries = {"new1": {"src": "c", "dst": "C"}}

        start = time.time()
        cache_shards._save_entries_to_active_shards(
            type_dir=type_dir,
            cache_type="lang",
            entries=entries,
            rolling_shard_size=2,
            active_shard_file=".active",
        )
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Function took {elapsed:.1f}s - possible infinite loop"
        assert (type_dir / "lang_00002.json").exists(), "New shard should be created after rotation"
        new_shard = json.loads((type_dir / "lang_00002.json").read_bytes())
        assert "new1" in new_shard, f"New data should be in new shard"


'''

# Apply replacements
replacements = [
    (s, e, new_c11),  # C-11 first (highest line number, apply in reverse order)
    (s, e, new_c9),   # will apply C-9, C-6b, C-6a, C-4b
    (s, e, new_c6b),
    (s, e, new_c6a),
    (s, e, new_c4b),
]

# Actually, let me do this properly
# Find all first, then replace from bottom to top

# Find all
c4b = find_method_start('test_path_traversal_sequence_is_detected'), find_method_end(find_method_start('test_path_traversal_sequence_is_detected'))
c6a = find_method_start('test_extract_rejects_binary_over_100mb'), find_method_end(find_method_start('test_extract_rejects_binary_over_100mb'))
c6b = find_method_start('test_extract_accepts_normal_sized_binary'), find_method_end(find_method_start('test_extract_accepts_normal_sized_binary'))
c9 = find_method_start('test_icon_preview_module_has_size_check_logic'), find_method_end(find_method_start('test_icon_preview_module_has_size_check_logic'))
c11 = find_method_start('test_no_progress_count_3_breaks_loop'), find_method_end(find_method_start('test_no_progress_count_3_breaks_loop'))

# Sort by start line descending
all_replacements = sorted([
    (c4b[0], c4b[1], new_c4b),
    (c6a[0], c6a[1], new_c6a),
    (c6b[0], c6b[1], new_c6b),
    (c9[0], c9[1], new_c9),
    (c11[0], c11[1], new_c11),
], key=lambda x: x[0], reverse=True)

# Build new content
new_lines = list(lines)
for start, end, new_content in all_replacements:
    print(f'Replacing lines {start+1}-{end+1}')
    new_lines[start:end] = [new_content]

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.writelines(new_lines)

print('Done!')
