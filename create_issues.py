#!/usr/bin/env python3
"""建立 GitHub Issues for 程式碼稽核報告"""
import subprocess
import os
import sys

GH_OWNER = "jlin53882"
GH_REPO = "Minecraft-translate"
PROJ_DIR = r"C:\Users\admin\Desktop\minecraft_translator_flet"

def run_gh(title, body_text, labels):
    """使用 gh issue create 建立 issue"""
    cmd = ["gh", "issue", "create",
           "--repo", f"{GH_OWNER}/{GH_REPO}",
           "--title", title]
    
    # Write body to temp file to avoid encoding issues
    body_file = os.path.join(os.environ.get('TEMP', '/tmp'), 'issue_body.md')
    with open(body_file, 'w', encoding='utf-8') as f:
        f.write(body_text)
    cmd.extend(["--body-file", body_file])
    
    for label in labels:
        cmd.extend(["--label", label])
    
    result = subprocess.run(cmd, capture_output=True, cwd=PROJ_DIR, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout.strip()

# Issue 1: CRITICAL
critical_title = "[CRITICAL] 程式碼稽核 - 資料遺失與安全性問題（11項）"
critical_body = """## 稽核報告
本 Issue 收錄 11 項 CRITICAL 等級問題，來自 對抗式程式碼稽核報告（最終驗證版 2026-04-07）。

## 🔴 CRITICAL 問題清單

### C-1｜API 回傳少於批次量時，資料永久遺失
- **檔案**：`translation_tool/core/lm_translator_shared_loop.py:169`
- **問題**：`remaining = remaining[actual_processed_in_this_batch:]` 若 API 回傳 3 項（批次 10 項），剩餘 7 項被永久移除
- **修復**：`remaining = remaining[len(batch):]`，數量不符時拋出警告

### C-2｜`call_gemini_requests` 完全無 Retry 機制
- **檔案**：`translation_tool/core/lm_api_client.py:68-73`
- **問題**：`requests.post()` 只有一次呼叫，無任何 retry
- **修復**：實作指數退避重試（3 次 + jitter）

### C-3｜批次縮減時原文混入輸出
- **檔案**：`translation_tool/core/lm_translator_main.py:855-857`
- **問題**：`all_results.extend(current_batch)` 將原文直接混入譯文
- **修復**：縮減後的原始項目應標記或拋出警告

### C-4｜路徑遍歷
- **檔案**：`translation_tool/core/jar_processor_extract.py:128-134`
- **問題**：`assets/../../../etc/passwd` 可寫入 `output_root` 外
- **修復**：寫入前呼叫 `os.path.abspath()` 並驗證在 `output_root` 內

### C-5~C-10｜ZIP bomb 防護缺失（6 處）
- **位置**：
  1. `lang_merge_zip_io.py:35` — 只驗 header `file_size`
  2. `jar_processor_extract.py:119` — 直接 `zf.open().read()`
  3. `jar_browser.py:73` — `zf.read().decode()` 無防護
  4. `icon_index.py:58,119` — 8 threads 並行讀 ZIP 無大小限制
  5. `icon_preview_view.py`（6+ 處）— 多處 `zf.read()` 無防護
  6. `lang_merge_content_copy.py:76` — 遍歷整個 ZIP 無大小檢查
- **修復**：所有 `zf.read()` 前加大小限制

### C-11｜`while pending_items:` 無限期迴圈
- **檔案**：`translation_tool/utils/cache_shards.py:176`
- **問題**：若 `capacity == 0` 且寫入失敗，`pending_items` 不縮減
- **修復**：加 `if not pending_items: break` 保護

---
**關聯 PR**：待建立
"""

# Issue 2: HIGH
high_title = "[HIGH] 程式碼稽核 - 文件與邏輯不一致問題（5項）"
high_body = """## 稽核報告
本 Issue 收錄 5 項 HIGH 等級問題，來自 對抗式程式碼稽核報告（最終驗證版 2026-04-07）。

## 🟠 HIGH 問題清單

### H-1｜`rotate_api_key()` docstring 誤導
- **檔案**：`translation_tool/core/lm_translator_main.py:131-171`
- **問題**：Docstring 說「Raises: RuntimeError」，實作只有 `return False`。`except RuntimeError` 是死碼
- **修復**：統一 docstring 與實作

### H-2｜`value_fully_translated` 文件與實作不符
- **檔案**：`translation_tool/core/lm_config_rules.py:304-334`
- **問題**：Docstring 說呼叫 `needs_translation_text()`，實作只做 `!= ""` 檢查
- **後果**：空字串被當成「未翻譯」，cache 命中失敗
- **修復**：實作符合文件，或修正文件

### H-3｜Checkpoint 與 remaining 切片同步問題
- **檔案**：`translation_tool/core/lm_translator.py:710,737`
- **問題**：`remaining = remaining[actual_processed:]` 在第 710 行，checkpoint 在第 737 行傳入已切片值
- **後果**：crash 後可能重複翻譯部分項目
- **修復**：checkpoint 寫入前建立 `remaining` 的 deep copy

### H-4｜Cache key 三個不同名稱，命中率不一致
- **檔案**：`translation_tool/core/lm_translator_shared_cache.py:21-27,55-63`
- **問題**：`make_key` 只用 `source_text`，`_is_valid_hit` 嘗試三個 fallback
- **後果**：cache 誤判未命中，浪费 API quota
- **修復**：統一 key 策略

### H-5｜寫入中途 crash 無法恢復（temp+atomic replace 非 WAL）
- **檔案**：`translation_tool/utils/cache_shards.py:40-60`
- **問題**：使用 `temp+atomic replace`，不是真正 WAL；crash 時可能遺失最後一筆
- **修復**：實作 WAL 或加 fsync 保護

---
**關聯 PR**：待建立
"""

# Issue 3: MEDIUM
medium_title = "[MEDIUM] 程式碼稽核 - 實作細節與邊界處理（4項）"
medium_body = """## 稽核報告
本 Issue 收錄 4 項 MEDIUM 等級問題，來自 對抗式程式碼稽核報告（最終驗證版 2026-04-07）。

## 🟡 MEDIUM 問題清單

### M-1｜`export_cache_only=True` 回傳空陣列
- **檔案**：`translation_tool/core/lm_translator_main.py:164-166`
- **問題**：直接 `return [], "EXPORT_CACHE_ONLY"`，註解說是過渡實作
- **修復**：儘快實作完整功能

### M-2｜Shard rotation TOCTOU
- **檔案**：`translation_tool/utils/cache_shards.py:203-218`
- **問題**：解鎖後 `_rotate_shard_if_needed` 在無鎖狀態執行，另一程序可能同時寫入
- **修復**：改為鎖內旋轉，或用目錄 atomic rename

### M-4｜429/503 解析時 `except Exception` 吞噬 AttributeError
- **檔案**：`translation_tool/core/lm_translator_main.py:714-715`
- **問題**：當 `e.response` 為 `None` 時，`.json()` 和 `.text` 都拋 `AttributeError`，被 `except Exception` 吞噬
- **修復**：加 `if hasattr(e, 'response') and e.response` 檢查

### M-6｜`os.walk` 無 symlink 保護
- **檔案**：`translation_tool/core/ftb_translator.py:111`
- **問題**：`os.walk(input_dir)` 無 `followlinks=False`，可遍历 symlink 到意外位置
- **修復**：加 `followlinks=False` 並驗證路徑

---
**關聯 PR**：待建立
"""

print("建立 GitHub Issues...")
print("=" * 60)

# Issue #65 was already created for CRITICAL
print("\n[CRITICAL] Issue #65 已建立: https://github.com/jlin53882/Minecraft-translate/issues/65")

# Create HIGH issue
print("\n[2/3] 建立 HIGH Issue...")
high_url = run_gh(high_title, high_body, ["high", "documentation", "bug"])
if high_url:
    print(f"✅ HIGH: {high_url}")
else:
    print("❌ HIGH Issue 建立失敗")

# Create MEDIUM issue
print("\n[3/3] 建立 MEDIUM Issue...")
medium_url = run_gh(medium_title, medium_body, ["medium", "enhancement"])
if medium_url:
    print(f"✅ MEDIUM: {medium_url}")
else:
    print("❌ MEDIUM Issue 建立失敗")

print("\n" + "=" * 60)
print("Issue 建立完成！")
print("\nIssue 清單：")
print("  CRITICAL: https://github.com/jlin53882/Minecraft-translate/issues/65")
if high_url:
    print(f"  HIGH: {high_url}")
if medium_url:
    print(f"  MEDIUM: {medium_url}")
