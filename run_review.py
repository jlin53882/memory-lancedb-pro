#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

prompt = """你是 code review 專家，請用繁體中文回覆。

請 review 以下 commit（hash: 1bac9e6）的改動，專注於 src/smart-extractor.ts 中 stripEnvelopeMetadata 函式的 regex 修改：

改動摘要：
原本 regex: `You are running as a subagent.*?`
修改後: `You are running as a subagent\\b.*?`
（加入了 word boundary `\\b` 防止貪心匹配）

完整 regex:
/^\\[(?:Subagent Context|Subagent Task)\\]\\s*(?:You are running as a subagent\\b.*?(?:$|(?<=\\.)\\s+)|Results auto-announce to your requester\\.?\\s*|do not busy-poll for status\\.?\\s*|Reply with a brief acknowledgment only\\.?\\s*|Do not use any memory tools\\.?\\s*)?/gim

請確認：
1. 這個 fix 的邏輯是否正確？加入 `\\b` 的目的是什麼？
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
