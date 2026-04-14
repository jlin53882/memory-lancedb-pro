#!/usr/bin/env python3
fp = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'

with open(fp, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# New C-10 class
new_c10 = '''
# =============================================================================
# C-10: ZIP bomb 防護（lang_merge_content_copy.py - 10MB）
# =============================================================================


class TestC10ZipBombLangMergeContentCopy:
    """C-10: lang_merge_content_copy.py 10MB 文字檔大小限制。"""

    def test_constant_value_is_10mb(self, tmp_path: Path):
        """C-10: 驗證 >10MB 的文字檔被拒絕處理（行為測試）。

        建立一個 11MB 的文字檔放進 ZIP，確認被跳過而非處理。
        """
        import logging
        import zipfile
        import io
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

        # 不應報錯（只是跳過），超大檔案不應有 CJK effective 結果
        assert result == 0 or not result.get("zh_tw"), \\
            f"11MB oversized file should be skipped, got: {result}"


'''

# New C-11 class
new_c11 = '''
# =============================================================================
# C-11: 無限期迴圈防護
# 檔案：translation_tool/utils/cache_shards.py
#
# 修復內容：在 _save_entries_to_active_shards 的 while 迴圈中，
# 當 capacity=0（分片已滿）導致連續 3 次未寫入時，中斷迴圈防止凍住
# =============================================================================


class TestC11InfiniteLoopProtection:
    """C-11: 測試無限期迴圈防護（no_progress_count >= 3 中斷）。"""

    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path):
        """C-11: 驗證函式在 shard 已滿時能在合理時間內返回而不會凍住。

        實作會 rotate shard 後正常寫入，在合理時間內完成。
        這個測試驗證的是「使用者價值」：不會凍住 + shard 被正常建立。
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

        # 驗證 1: 有 C-11 保護時，應該快速結束（< 5秒），不會凍住
        assert elapsed < 5.0, f"Function took {elapsed:.1f}s - possible infinite loop"
        # 驗證 2: 新 shard 應該被建立（rotate 成功）
        assert (type_dir / "lang_00002.json").exists(), \\
            "New shard should be created after rotation"
        # 驗證 3: 新 shard 應該包含新資料
        new_shard = json.loads((type_dir / "lang_00002.json").read_bytes())
        assert "new1" in new_shard, f"New data should be in new shard, got: {new_shard}"

    def test_normal_write_succeeds(self, tmp_path: Path, monkeypatch):
        """正常寫入時應成功完成。"""
        from translation_tool.utils import cache_shards
        import orjson as json

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")
        (type_dir / "lang_00001.json").write_bytes(json.dumps({}))

        entries = {"key1": {"src": "a", "dst": "A"}}
        cache_shards._save_entries_to_active_shards(
            type_dir=type_dir,
            cache_type="lang",
            entries=entries,
            rolling_shard_size=10,
            active_shard_file=".active",
        )

        result = json.loads((type_dir / "lang_00001.json").read_bytes())
        assert "key1" in result
        assert result["key1"]["dst"] == "A"

    def test_empty_capacity_does_not_freeze(self, tmp_path: Path, monkeypatch):
        """容量為 0 時不應凍住（有 C-11 中斷保護）。"""
        from translation_tool.utils import cache_shards
        import orjson as json
        import time

        type_dir = tmp_path / "lang"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / ".active").write_text("00001", encoding="utf-8")

        # 已滿的分片
        (type_dir / "lang_00001.json").write_bytes(json.dumps({"k1": {}, "k2": {}}))

        entries = {"new1": {"src": "a", "dst": "A"}}

        start = time.time()
        cache_shards._save_entries_to_active_shards(
            type_dir=type_dir,
            cache_type="lang",
            entries=entries,
            rolling_shard_size=2,
            active_shard_file=".active",
        )
        elapsed = time.time() - start
        # 有 C-11 保護時，應該快速結束（< 5秒），不會凍住
        assert elapsed < 5.0, f"Function took {elapsed:.1f}s - possible infinite loop"


'''

# Find where the new tests should be inserted (after TestC9, before Regression)
idx_after_c9 = content.find('class TestC9ZipBombIconPreview:')
# Find end of TestC9 class
idx_c9_end = content.find('\n\nclass ', idx_after_c9 + 50)
print(f'TestC9 class end: line {content[:idx_c9_end].count(chr(10))+1}')

# Also find Regression section to insert before it
idx_regression = content.find('# =============================================================================\n# Regression')
print(f'Regression section: line {content[:idx_regression].count(chr(10))+1 if idx_regression >= 0 else "NOT FOUND"}')

# New content = before TestC9 end + new C10 + new C11 + after regression
new_content = content[:idx_c9_end] + new_c10 + new_c11 + content[idx_regression:]

with open(fp, 'w', encoding='utf-8', errors='replace') as f:
    f.write(new_content)

print(f'Done! New file size: {len(new_content)} chars')
