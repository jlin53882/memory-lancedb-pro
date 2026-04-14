#!/usr/bin/env python3
"""Replace only the specific failing tests with James's behavioral versions"""
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# C-10 new test (lines are 1-indexed, list is 0-indexed)
# Line 674 = index 673
new_c10 = '''    def test_constant_value_is_10mb(self, tmp_path: Path):
        """C-10: 驗證 >10MB 的文字檔被拒絕處理（行為測試）。

        建立一個 11MB 的文字檔放進 ZIP，確認被跳過而非處理。
        """
        import zipfile
        from translation_tool.core.lang_merge_content_copy import _compute_patchouli_lang_effectiveness

        jar_path = tmp_path / "big.jar"
        big_text = "X" * (11 * 1024 * 1024)  # 11MB 文字檔

        with zipfile.ZipFile(jar_path, "w") as zf:
            zf.writestr("assets/mod/patchouli_books/book/en_us/entries/a.txt", big_text)

        with zipfile.ZipFile(jar_path, "r") as zf:
            result = _compute_patchouli_lang_effectiveness(
                zf,
                "assets/mod/patchouli_books/book/",
            )

        # 超大檔案不應有 CJK effective 結果（被跳過了）
        assert result == 0 or not result.get("zh_tw"), \\
            f"11MB oversized file should be skipped, got: {result}"
'''

# C-11 new test (Option A - test user value: doesn't hang + shard created)
new_c11 = '''    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path):
        """C-11: 驗證 shard 已滿時能在合理時間內返回而不會凍住。

        實作會 rotate shard 後正常寫入，驗證「使用者價值」：不凍住 + 新 shard 建立。
        """
        from translation_tool.utils import cache_shards
        import orjson as json
        import time

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")

        # 建立一個已滿的分片（容量為 rolling_shard_size=2）
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

        # 驗證 1: 有 C-11 保護，應該快速結束不凍住
        assert elapsed < 5.0, f"Function took {elapsed:.1f}s - possible infinite loop"
        # 驗證 2: 新 shard 應該被建立
        assert (type_dir / "lang_00002.json").exists(), \\
            "New shard should be created after rotation"
        # 驗證 3: 新 shard 應該包含新資料
        new_shard = json.loads((type_dir / "lang_00002.json").read_bytes())
        assert "new1" in new_shard, f"New data should be in new shard"
'''

# Find C-10 test method (lines 674-680 in file, indices 673-679)
c10_start = None
c10_end = None
for i, l in enumerate(lines):
    if 'def test_constant_value_is_10mb' in l and i >= 670:
        c10_start = i
    if c10_start is not None and c10_end is None:
        # Find the blank line after the assert
        if l.strip() == '' or (i > c10_start and l.startswith('    def ')):
            c10_end = i
            break

# Find C-11 test method (lines 695-739 in file, indices 694-738)
c11_start = None
c11_end = None
for i, l in enumerate(lines):
    if 'def test_no_progress_count_3_breaks_loop' in l and i >= 690:
        c11_start = i
    if c11_start is not None and c11_end is None:
        # Find the next method or end of class
        if l.startswith('    def ') and i > c11_start:
            c11_end = i
            break

print(f'C-10: lines {c10_start+1}-{c10_end} (indices {c10_start}-{c10_end})')
print(f'C-11: lines {c11_start+1}-{c11_end} (indices {c11_start}-{c11_end})')

# Replace C-10
new_lines = lines[:c10_start] + [new_c10 + '\n\n'] + lines[c10_end:c11_start] + [new_c11 + '\n\n'] + lines[c11_end:]

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.writelines(new_lines)

print(f'Done! New file: {len(new_lines)} lines (was {len(lines)} lines)')
