#!/usr/bin/env python3
import subprocess

proj = r'C:\Users\admin\Desktop\minecraft_translator_flet'

# Stage
r1 = subprocess.run(['git', '-C', proj, 'add', '-A'], capture_output=True, text=True)
print('git add:', r1.returncode)

msg = """fix(audit): C-1/C-3 深層 bug 修補 + 2 個 regression test

James 發現深層問題並親自驗證：

C-1 深層 bug：
- 原本 safe_translated[:expected] 在 loop (line 139) 之後才截斷 (line 177)
- 2 筆 batch 回 3 筆時，callback 真的會吃到第 3 筆
- 修復：將截斷提前到 loop 之前，確保多餘項目永不進入處理流程

C-3 深層 bug：
- 原本 _untranslated 只在 cache 寫入前檢查，但 on_translated_item() 先被呼叫了
- FTB/KubeJS/MD callback 直接把 text 寫回輸出，原文混入輸出沒有被堵住
- 修復：_untranslated 項目在 on_translated_item 之前就 continue

Regression tests:
- test_api_returns_more_than_batch_callback_called_only_for_batch_size
- test_untranslated_item_skips_on_translated_item_callback

Refs #65"""

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
