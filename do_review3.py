#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts")
from opencode_task import OpenCodeAPI

client = OpenCodeAPI(timeout=120)

prompt = """你是 code review 專家（繁體中文回覆）。

以下是一個 fix commit 的 diff，請確認：
1. 邏輯是否正確（當 this.decayEngine 存在時，recencyBoosted = mapped，跳過 applyRecencyBoost 以避免重複加成）
2. 是否有副作用或 regression
3. 程式碼風格是否一致

【原始程式碼】：
const recencyBoosted = this.applyRecencyBoost(mapped);

【修改後程式碼】：
const recencyBoosted = this.decayEngine
  ? mapped
  : this.applyRecencyBoost(mapped);

【註解】：
// Bug 7 fix: when decayEngine is active, skip applyRecencyBoost here because
// decayEngine already handles temporal scoring; avoid double-boost.

回覆格式（只選一種）：
- 完全沒問題：LGTM
- 有問題：ISSUES: [說明問題及修復方式]
"""

try:
    sid = client.create_session(title="Code Review 736eae1")
    print(f"Session: {sid}")
    
    response = client.send_message(
        prompt=prompt,
        session_id=sid,
        model="minimax/MiniMax-M2.7",
        reasoning="high"
    )
    
    # Check for errors in response
    info = response.get("info", {})
    if info.get("error"):
        print(f"API Error: {info['error']}")
    
    text = client.extract_text(response)
    print(f"Review result:\n{text}")
    
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
