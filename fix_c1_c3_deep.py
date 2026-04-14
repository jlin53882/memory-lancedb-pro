#!/usr/bin/env python3
"""修補 lm_translator_shared_loop.py 的 C-1 和 C-3 深層問題"""
import re

file_path = r'C:\Users\admin\Desktop\minecraft_translator_flet\translation_tool\core\lm_translator_shared_loop.py'
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# === Fix 1: Move API-overrun protection BEFORE the loop ===
# Remove the post-loop truncation block
old_c1_block = '''        # C-1 修復：使用原始批次大小切片，而非實際處理的數量
        # 若 API 回傳數量少於傳送量（截斷/配額），剩餘項目不會被遺漏
        # C-1 增強：若翻譯 API 回傳多於預期（模型串接錯誤/JSON截斷污染），多出的項目會被永久跳過
        expected = len(batch)
        if len(safe_translated) > expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量異常多於預期 ({len(safe_translated)} > {expected})，"
                f"拒絕處理以防資料遺失，只取前 {expected} 項"
            )
            safe_translated = safe_translated[:expected]
        if actual_processed_in_this_batch < expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量低於預期（預期 {expected}，實際 {actual_processed_in_this_batch}）"
                f"，剩餘 {expected - actual_processed_in_this_batch} 項將重新處理"
            )
        remaining = remaining[expected:]'''

# Insert the C-1 protection BEFORE the loop (after line "safe_translated = translated or []")
# And remove the old post-loop block
new_c1_block = ''

if old_c1_block in content:
    content = content.replace(old_c1_block, new_c1_block)
    print('Fix 1: Removed post-loop C-1 block')
else:
    print('Fix 1: Pattern not found!')
    # Try to find it
    idx = content.find('C-1 修復：使用原始批次大小切片')
    if idx >= 0:
        print('Found at index:', idx)
        print(repr(content[idx-50:idx+500]))

# Now insert the pre-loop C-1 protection right after "safe_translated = translated or []"
old_init = '        safe_translated = translated or []\n        actual_processed_in_this_batch = 0'
new_init = '''        safe_translated = translated or []

        # C-1 修復：使用原始批次大小切片，而非實際處理的數量
        # 若 API 回傳數量少於傳送量（截斷/配額），剩餘項目不會被遺漏
        # C-1 增強：若翻譯 API 回傳多於預期（模型串接錯誤/JSON截斷污染），
        #           在 loop 處理前就截斷，防止 callback 吃到多餘項目
        expected = len(batch)
        if len(safe_translated) > expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量異常多於預期 ({len(safe_translated)} > {expected})，"
                f"拒絕處理以防資料遺失，只取前 {expected} 項"
            )
            safe_translated = safe_translated[:expected]
        if len(safe_translated) < expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量低於預期（預期 {expected}，實際 {len(safe_translated)}）"
                f"，剩餘 {expected - len(safe_translated)} 項將重新處理"
            )

        actual_processed_in_this_batch = 0'''

if old_init in content:
    content = content.replace(old_init, new_init)
    print('Fix 1: Inserted pre-loop C-1 protection')
else:
    print('Fix 1: Could not find init line')

# === Fix 2: Skip on_translated_item for _untranslated items ===
# Change the order: check _untranslated BEFORE calling on_translated_item
old_callback = '''            actual_processed_in_this_batch += 1
            processed += 1

            if on_translated_item is not None:
                try:
                    on_translated_item(it)
                except Exception as e:
                    log_info(f"[SharedLM] 處理翻譯結果失敗: {e}")

            rule = cache_rules.get(ctype) or CacheRule("path|source_text")
            cache_key = rule.make_key({"path": pth, "source_text": src})
            # C-3 修復：若此項目被標記為未翻譯（批次縮減時的原項目），則跳過快取寫入
            if it.get("_untranslated"):
                log_info(f"[SharedLM] 略過未翻譯項目的快取寫入: {pth}")
            else:
                try:
                    add_to_cache(ctype, cache_key, src, txt)
                except Exception as e:
                    log_info(f"[SharedLM] 新增快取失敗: {e}")'''

new_callback = '''            actual_processed_in_this_batch += 1
            processed += 1

            # C-3 修復：對 _untranslated 標記的項目，跳過所有後續處理
            # 包括：on_translated_item callback（防止原文被寫回輸出）+ cache 寫入
            if it.get("_untranslated"):
                log_info(f"[SharedLM] 略過未翻譯項目的所有處理（含 callback）: {pth}")
                continue

            if on_translated_item is not None:
                try:
                    on_translated_item(it)
                except Exception as e:
                    log_info(f"[SharedLM] 處理翻譯結果失敗: {e}")

            rule = cache_rules.get(ctype) or CacheRule("path|source_text")
            cache_key = rule.make_key({"path": pth, "source_text": src})
            try:
                add_to_cache(ctype, cache_key, src, txt)
            except Exception as e:
                log_info(f"[SharedLM] 新增快取失敗: {e}")'''

if old_callback in content:
    content = content.replace(old_callback, new_callback)
    print('Fix 2: _untranslated now skips on_translated_item callback')
else:
    print('Fix 2: Pattern not found!')
    idx = content.find('if it.get("_untranslated"):')
    if idx >= 0:
        print('Found _untranslated at index:', idx)
        print(repr(content[idx-300:idx+200]))

# === Fix 3: remaining slicing needs to use expected which is now defined earlier ===
# The line "remaining = remaining[expected:]" should still work since expected is now defined earlier
old_remaining = '        remaining = remaining[expected:]'
# Check if this still exists
if old_remaining in content:
    print('Fix 3: remaining slicing stays at end (expected is now defined earlier)')
else:
    print('Fix 3: remaining slicing - checking...')
    idx = content.find('remaining = remaining[')
    if idx >= 0:
        print('Found:', repr(content[idx:idx+50]))

with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)
print('File saved!')
