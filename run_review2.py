#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

prompt = """你是 code review 專家，請用繁體中文回覆。

請 review commit 1bac9e6 的改動，專注於 stripEnvelopeMetadata 函式中的 regex 修改：

原始版本: You are running as a subagent followed by non-greedy match .*?
修改後版本: You are running as a subagent with word boundary, then non-greedy match

（即在 subagent 後面加了反斜槓b word boundary，防止 .*? 貪心匹配到非預期的內容）

請確認：
1. 這個 fix 的邏輯是否正確？
2. 是否有副作用或 regression 風險？
3. 程式碼風格是否一致？
4. 這個修改是否完全解決了貪心匹配的問題？

回覆格式：LGTM 或 ISSUES: ...（如有問題請詳細說明）
"""

result = run_opencode_task(
    prompt=prompt,
    model="minimax/MiniMax-M2.7",
    reasoning="high",
    timeout=180,
)
print(f"OK: {result.ok}")
print(f"Text: {result.text}")
print(f"Session: {result.session_id}")
print(f"Error: {result.error}")
