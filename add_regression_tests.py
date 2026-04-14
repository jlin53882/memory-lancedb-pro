#!/usr/bin/env python3
"""補兩個 regression test 到 test_audit_critical_fixes.py"""
import re

file_path = r'C:\Users\admin\Desktop\minecraft_translator_flet\tests\test_audit_critical_fixes.py'
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# The new regression tests to add
new_tests = '''

    # =============================================================================
    # Regression Tests（針對 James 發現的深層 bug）
    # =============================================================================

    def test_api_returns_more_than_batch_callback_called_only_for_batch_size(self, tmp_path, monkeypatch):
        """Regression: API 回傳多於 batch 時，callback 只應被呼叫 batch_size 次（不是 API 回傳次數）。

        James 發現：原本 C-1 修正在 line 177 才截斷 safe_translated，
        但 for loop 已在 line 139 處理完所有回傳項目。
        2 筆 batch 回 3 筆時，callback 真的會吃到第 3 筆。
        修復後：safe_translated[:expected] 必須在 loop 之前執行。
        """
        from translation_tool.core.lm_translator_shared_loop import translate_items_with_cache_loop

        callback_calls = []

        def on_item(it):
            callback_calls.append(it)

        def fake_translate_batch(batch, total):
            # 回傳 5 項，但 batch 只有 3 項
            return [
                {"path": f"item_{i}", "text": f"T{i}", "source_text": f"s{i}", "cache_type": "lang"}
                for i in range(5)
            ], "OK"

        monkeypatch.setattr("translation_tool.core.lm_translator_shared_loop.reload_translation_cache", lambda: None)
        monkeypatch.setattr("translation_tool.core.lm_translator_shared_loop.save_translation_cache", lambda *a, **k: None)
        monkeypatch.setattr("translation_tool.utils.cache_manager.save_translation_cache", lambda *a, **k: None)
        monkeypatch.setattr("translation_tool.utils.cache_manager.reload_translation_cache", lambda: None)

        items = [{"path": f"item_{i}", "source_text": f"s{i}", "cache_type": "lang"} for i in range(3)]
        result = translate_items_with_cache_loop(
            items,
            translate_batch_smart=fake_translate_batch,
            batch_size_by_type={"lang": 3},
            on_translated_item=on_item,
        )

        # callback 只應被呼叫 3 次（batch_size），不是 5 次（API 回傳數）
        assert len(callback_calls) == 3, (
            f"Callback 應只被呼叫 3 次，實際被呼叫 {len(callback_calls)} 次。"
            f"這表示 C-1 修正在 loop 之前沒有正確截斷。"
        )
        # 確認吃到的是前 3 項，不是 API 的後 2 項
        assert callback_calls[0]["path"] == "item_0"
        assert callback_calls[1]["path"] == "item_1"
        assert callback_calls[2]["path"] == "item_2"

    def test_untranslated_item_skips_on_translated_item_callback(self, tmp_path, monkeypatch):
        """Regression: _untranslated 標記的項目不應呼叫 on_translated_item callback。

        James 發現：原本 C-3 只在 cache 寫入前檢查 _untranslated，
        但 on_translated_item() 在 cache 寫入前就被呼叫了。
        FTB/KubeJS/MD 的 callback 直接把 text 寫回輸出，
        所以原文混入輸出並沒有被堵住。
        修復後：_untranslated 項目在 on_translated_item 之前就 continue。
        """
        from translation_tool.core.lm_translator_shared_loop import translate_items_with_cache_loop

        callback_calls = []
        cache_writes = []

        def on_item(it):
            callback_calls.append(it)

        def add_to_cache(ctype, key, src, txt):
            cache_writes.append({"ctype": ctype, "key": key, "src": src, "txt": txt})

        def fake_translate_batch(batch, total):
            # 回傳時，第 0 項標記為 _untranslated
            return [
                {"path": "item_0", "text": "ORIGINAL_TEXT", "source_text": "src0", "cache_type": "lang", "_untranslated": True},
                {"path": "item_1", "text": "TRANSLATED_B", "source_text": "src1", "cache_type": "lang"},
                {"path": "item_2", "text": "TRANSLATED_C", "source_text": "src2", "cache_type": "lang"},
            ], "OK"

        monkeypatch.setattr("translation_tool.core.lm_translator_shared_loop.reload_translation_cache", lambda: None)
        monkeypatch.setattr("translation_tool.core.lm_translator_shared_loop.save_translation_cache", lambda *a, **k: None)
        monkeypatch.setattr("translation_tool.utils.cache_manager.save_translation_cache", lambda *a, **k: None)
        monkeypatch.setattr("translation_tool.utils.cache_manager.reload_translation_cache", lambda: None)
        monkeypatch.setattr("translation_tool.core.lm_translator_shared_loop.add_to_cache", add_to_cache)

        items = [{"path": f"item_{i}", "source_text": f"s{i}", "cache_type": "lang"} for i in range(3)]
        result = translate_items_with_cache_loop(
            items,
            translate_batch_smart=fake_translate_batch,
            batch_size_by_type={"lang": 3},
            on_translated_item=on_item,
        )

        # _untranslated 項目不應被 callback 處理（防止原文被寫回輸出）
        callback_paths = [c["path"] for c in callback_calls]
        assert "item_0" not in callback_paths, (
            f"_untranslated 項目 item_0 不應被 callback 處理，但 callback_calls={callback_paths}。"
            f"這表示 C-3 修復不完整，on_translated_item 仍被呼叫。"
        )
        # _untranslated 項目不應寫入 cache
        cache_keys = [c["key"] for c in cache_writes]
        assert "item_0" not in cache_keys, (
            f"_untranslated 項目 item_0 不應寫入 cache，但 cache_keys={cache_keys}。"
        )
        # 正常項目應被正常處理
        assert "item_1" in callback_paths
        assert "item_2" in callback_paths

'''

# Find a good insertion point: before the last blank lines at end of file
# Insert before the last "def" (which should be the last test function)
# Actually, let's find the last "def test_" and insert after it

# Find all test methods
import re
test_matches = list(re.finditer(r'    def (test_\w+)\(', content))
last_test = test_matches[-1]
last_test_name = last_test.group(1)
last_test_pos = last_test.start()

print(f'Last test: {last_test_name} at position {last_test_pos}')

# Find the end of that function (next def or class end)
rest = content[last_test_pos:]
next_def = re.search(r'\n    def ', rest[100:])  # skip past current def
if next_def:
    insert_pos = last_test_pos + 100 + next_def.start()
else:
    insert_pos = len(content.rstrip())

print(f'Will insert at position {insert_pos}')
print(f'Content around insert: {repr(content[insert_pos-50:insert_pos+50])}')

new_content = content[:insert_pos] + new_tests + content[insert_pos:]

with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
    f.write(new_content)

print('Done!')
