class TestC11InfiniteLoopProtection:
    """C-11: 測試無限期迴圈防護（no_progress_count >= 3 中斷）。"""

    def test_no_progress_count_3_breaks_loop(self, tmp_path: Path, monkeypatch):
        """當連續 3 次未寫入時，應中斷迴圈並記錄錯誤。

        PATCH: 實作會先 rotate shard 後正常寫入成功，所以我們 mock
        _save_shard_data 讓寫入量永遠為 0，逼出停滯分支。
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

        # PATCH: Mock _save_shard_data 讓每次寫入量都為 0，逼出停滯分支
        orig = cache_shards._save_shard_data
        def fake_save(*args, **kwargs):
            return 0
        cache_shards._save_shard_data = fake_save

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
            cache_shards._save_shard_data = orig

        output = stream.getvalue()
        # 確認有停滯相關的日誌
        assert "停滯" in output or "放棄" in output or "未寫入" in output, (
            f"Expected stall warning in log output, got: {output}"
        )

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
