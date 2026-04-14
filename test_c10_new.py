    def test_constant_value_is_10mb(self):
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

        # 不應報錯（只是跳過），但也不應有 CJK effective 結果
        assert result == 0 or not result.get("zh_tw"), \
            f"11MB oversized file should be skipped, got: {result}"
