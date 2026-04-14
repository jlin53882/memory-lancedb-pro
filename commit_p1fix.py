#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

r1 = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)
print('git add:', r1.returncode)

msg = """fix(audit): 修補 James 發現的 2 個額外 P1 問題

P1-1: icon_preview_view.py - Phase 1 的 _check_size 失敗時不再 abort
- 原本：Phase 1 找到 icon 但 PNG 過大時，RuntimeError 向上傳播，導致 Phase 2/3 fallback 完全無法執行
- 修復：Phase 1 包在 try-except 中，_check_size 失敗時記錄並繼續 Phase 2/3

P1-2: jar_processor_extract.py - fallback 路徑加入 10MB 文字檔大小限制
- 原本：jar_browser 跳過的大型文字檔（path in jar_results but None），
  在 fallback 直接讀 ZIP 時只有 100MB binary 限制，繞過了 10MB 文字檔限制
- 修復：檢測 is_jar_browser_skipped，在 fallback 時套用保守的 10MB 限制

Ref #65
"""

r2 = subprocess.run(['git', '-C', proj, 'commit', '-m', msg], capture_output=True, text=True)
print('git commit:', r2.returncode)
if r2.returncode != 0:
    print('STDERR:', r2.stderr)

r3 = subprocess.run(['git', '-C', proj, 'push', 'origin', 'fix/audit-critical', '--force'], capture_output=True, text=True)
print('git push:', r3.returncode)
if r3.returncode != 0:
    print('STDERR:', r3.stderr)
else:
    print('Done!')
