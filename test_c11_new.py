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
        assert (type_dir / "lang_00002.json").exists(), \
            "New shard should be created after rotation"
        # 驗證 3: 新 shard 應該包含新資料
        new_shard = json.loads((type_dir / "lang_00002.json").read_bytes())
        assert "new1" in new_shard, f"New data should be in new shard, got: {new_shard}"
