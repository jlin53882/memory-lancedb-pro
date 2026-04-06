#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

prompt = """你是 code review 專家。

Commit 1bac9e6 修改了 stripEnvelopeMetadata 函式中的 regex：
把 "You are running as a subagent followed by non-greedy .*?" 
改成 "You are running as a subagent with word boundary, then non-greedy .*?"

請確認：
1. 邏輯正確嗎？
2. 有副作用嗎？
3. 程式碼風格一致嗎？

回覆格式：LGTM 或 ISSUES:
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
