#!/usr/bin/env python3
"""修補 icon_preview_view.py 和 jar_processor_extract.py 的兩個 P1 問題"""
import re

# ============================================================
# Fix 1: icon_preview_view.py - Phase 1 大小檢查失敗時要繼續 fallback
# ============================================================
fp1 = r'C:\Users\admin\Desktop\minecraft_translator_flet\app\views\icon_preview_view.py'
with open(fp1, 'r', encoding='utf-8', errors='replace') as f:
    c1 = f.read()

old_phase1 = '''            # ===== Phase 1: Model JSON 解析（最高優先）=====
            result = _try_extract_mod_icon_from_model(jar_path, modid, zf, names, key=key)
            if result:
                tex_val, png_path = result
                _check_size(zf, png_path, _MAX_ICON_SIZE)
                icon_data = zf.read(png_path)
                icon_cache_root.mkdir(parents=True, exist_ok=True)
                out_path = icon_cache_root / f"{modid}_{jar_path.stem}_{_safe_filename_key(key)}.png"
                out_path.write_bytes(icon_data)
                log_info(f"[IconPreview] Model JSON icon: {modid} → {png_path} (tex={tex_val})")
                return out_path'''

new_phase1 = '''            # ===== Phase 1: Model JSON 解析（最高優先）=====
            # P1 修復：若 PNG 大小超過限制，不拋錯而是用 continue 讓 Phase 2/3 接手
            # 否則 Phase 1 的過大 PNG 會導致整個 extraction abort
            try:
                result = _try_extract_mod_icon_from_model(jar_path, modid, zf, names, key=key)
                if result:
                    tex_val, png_path = result
                    _check_size(zf, png_path, _MAX_ICON_SIZE)
                    icon_data = zf.read(png_path)
                    icon_cache_root.mkdir(parents=True, exist_ok=True)
                    out_path = icon_cache_root / f"{modid}_{jar_path.stem}_{_safe_filename_key(key)}.png"
                    out_path.write_bytes(icon_data)
                    log_info(f"[IconPreview] Model JSON icon: {modid} → {png_path} (tex={tex_val})")
                    return out_path
            except RuntimeError as ex:
                log_info(f"[IconPreview] Phase 1 失敗（{ex}），繼續 Phase 2...")'''

if old_phase1 in c1:
    c1 = c1.replace(old_phase1, new_phase1)
    print('Fix 1 (icon_preview): Phase 1 wrapped in try-except')
else:
    print('Fix 1: Pattern not found!')
    idx = c1.find('Phase 1: Model JSON 解析')
    if idx >= 0:
        print(repr(c1[idx-5:idx+500]))

with open(fp1, 'w', encoding='utf-8', errors='replace') as f:
    f.write(c1)

# ============================================================
# Fix 2: jar_processor_extract.py - fallback 路徑也要檢查大小
# ============================================================
fp2 = r'C:\Users\admin\Desktop\minecraft_translator_flet\translation_tool\core\jar_processor_extract.py'
with open(fp2, 'r', encoding='utf-8', errors='replace') as f:
    c2 = f.read()

old_fallback = '''                # Binary 檔案或 jar_browser 未找到：直接讀 ZIP
                    # C-6 修復：讀取前先檢查成員的 header file_size，防止大型 binary 檔案耗盡記憶體
                    _MAX_BINARY_SIZE = 100 * 1024 * 1024  # 100MB
                    if member.file_size > _MAX_BINARY_SIZE:
                        log_warning(
                            f"[jar_extract] ⚠️ 拒絕讀取過大檔案：{normalized_path}"
                            f"（{member.file_size / 1024 / 1024:.1f}MB > 100MB）"
                        )
                        continue
                    with zf.open(member) as source:
                        source_data = source.read()'''

new_fallback = '''                # Binary 檔案或 jar_browser 未找到：直接讀 ZIP
                    # C-6 修復：讀取前先檢查成員的 header file_size，防止大型 binary 檔案耗盡記憶體
                    # P1 修復：若 jar_browser 因大小限制跳過了文字檔（path in jar_results but None），
                    #          fallback 直接讀 ZIP 時也必須檢查大小（用保守的 10MB 閾值）
                    _MAX_BINARY_SIZE = 100 * 1024 * 1024  # 100MB
                    _MAX_FALLBACK_SIZE = 10 * 1024 * 1024  # 10MB，fallback 保守限制
                    # jar_browser 跳過的大型文字檔也會出現在 jar_results 中（值為 None）
                    is_jar_browser_skipped = (
                        normalized_path in jar_results and jar_results[normalized_path] is None
                    )
                    if is_jar_browser_skipped or normalized_path not in jar_results:
                        # fallback 讀取：套用保守的 10MB 限制（適用於文字檔）
                        if member.file_size > _MAX_FALLBACK_SIZE:
                            log_warning(
                                f"[jar_extract] ⚠️ 拒絕讀取過大檔案（fallback）：{normalized_path}"
                                f"（{member.file_size / 1024 / 1024:.1f}MB > 10MB）"
                            )
                            continue
                    elif member.file_size > _MAX_BINARY_SIZE:
                        log_warning(
                            f"[jar_extract] ⚠️ 拒絕讀取過大檔案：{normalized_path}"
                            f"（{member.file_size / 1024 / 1024:.1f}MB > 100MB）"
                        )
                        continue
                    with zf.open(member) as source:
                        source_data = source.read()'''

if old_fallback in c2:
    c2 = c2.replace(old_fallback, new_fallback)
    print('Fix 2 (jar_extract): fallback size check added')
else:
    print('Fix 2: Pattern not found!')
    idx = c2.find('Binary 檔案或 jar_browser 未找到')
    if idx >= 0:
        print(repr(c2[idx-50:idx+400]))

with open(fp2, 'w', encoding='utf-8', errors='replace') as f:
    f.write(c2)

print('All fixes applied!')
