#!/usr/bin/env python3
"""修補 lm_translator_shared_loop.py 的 C-3 和 C-1 問題"""
import sys

file_path = r'C:\Users\admin\Desktop\minecraft_translator_flet\translation_tool\core\lm_translator_shared_loop.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add _untranslated check before add_to_cache (C-3 fix)
old_cache = '''            try:
                add_to_cache(ctype, cache_key, src, txt)
            except Exception as e:
                log_info(f"[SharedLM] 新增快取失敗: {e}")

        # C-1 修復：使用原始批次大小切片，而非實際處理的數量'''

new_cache = '''            # C-3 修復：若此項目被標記為未翻譯（批次縮減時的原項目），則跳過快取寫入
            if it.get("_untranslated"):
                log_info(f"[SharedLM] 略過未翻譯項目的快取寫入: {pth}")
            else:
                try:
                    add_to_cache(ctype, cache_key, src, txt)
                except Exception as e:
                    log_info(f"[SharedLM] 新增快取失敗: {e}")

        # C-1 修復：使用原始批次大小切片，而非實際處理的數量'''

if old_cache in content:
    content = content.replace(old_cache, new_cache)
    print('Fix 1 (C-3): _untranslated check added')
else:
    print('Fix 1 (C-3): Pattern not found')
    idx = content.find('add_to_cache(ctype, cache_key, src, txt)')
    if idx >= 0:
        print('Found at index:', idx)
        print(repr(content[idx-200:idx+100]))

# Fix 2: Add protection for API returning MORE than expected (C-1 enhancement)
old_c1 = '''        if actual_processed_in_this_batch < expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量低於預期（預期 {expected}，實際 {actual_processed_in_this_batch}）"
            )
        remaining = remaining[expected:]'''

new_c1 = '''        # C-1 增強：若翻譯 API 回傳多於預期（模型串接錯誤/JSON截斷污染），多出的項目會被永久跳過
        if len(safe_translated) > expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量異常多於預期 ({len(safe_translated)} > {expected})，"
                f"拒絕處理以防資料遺失，只取前 {expected} 項"
            )
            safe_translated = safe_translated[:expected]
        if actual_processed_in_this_batch < expected:
            log_info(
                f"[SharedLM] ⚠️ API 回傳數量低於預期（預期 {expected}，實際 {actual_processed_in_this_batch}）"
            )
        remaining = remaining[expected:]'''

if old_c1 in content:
    content = content.replace(old_c1, new_c1)
    print('Fix 2 (C-1 enhancement): API over-run protection added')
else:
    print('Fix 2 (C-1): Pattern not found')
    idx = content.find('actual_processed_in_this_batch < expected')
    if idx >= 0:
        print('Found at index:', idx)
        print(repr(content[idx-50:idx+300]))

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved')
