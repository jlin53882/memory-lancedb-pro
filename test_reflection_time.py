#!/usr/bin/env python3
"""
測試 reflection prompt 的 LLM 生成時間
模擬 generateReflectionText 的實際行為
"""

import time
import subprocess
import json
import sys
import os

# 測試用的 mock conversation（16193 chars，符合 log 中的實際大小）
MOCK_CONVERSATION = """
[Session conversation content - truncated for this test]
""".strip()

def build_reflection_prompt(conversation: str, max_chars: int = 6000) -> str:
    """模擬 buildReflectionPrompt"""
    clipped = conversation[-max_chars:] if len(conversation) > max_chars else conversation

    tool_error_signals = []  # 這次測試不需要 error signals

    error_hints = "- (none)" if not tool_error_signals else "\n".join(
        f"{i+1}. [{e['toolName']}] {e['summary']} (sig:{e['sig'][:8]})"
        for i, e in enumerate(tool_error_signals)
    )

    return f"""You are generating a durable MEMORY REFLECTION entry for an AI assistant system.

Output Markdown only. No intro text. No outro text. No extra headings.

Use these headings exactly once, in this exact order, with exact spelling:
## Context (session background)
## Decisions (durable)
## User model deltas (about the human)
## Agent model deltas (about the assistant/system)
## Lessons & pitfalls (symptom / cause / fix / prevention)
## Learning governance candidates (.learnings / promotion / skill extraction)
## Open loops / next actions)
## Retrieval tags / keywords)
## Invariants
## Derived

Hard rules:
- Do not rename, translate, merge, reorder, or omit headings.
- Every section must appear exactly once.
- For bullet sections, use one item per line, starting with '- '.
- Do not wrap one bullet across multiple lines.
- If a bullet section is empty, write exactly: '- (none captured)'
- Do not paste raw transcript.
- Do not invent Logged timestamps, ids, file paths, commit hashes, session ids, or storage metadata unless they already appear in the input.
- If secrets/tokens/passwords appear, keep them as [REDACTED].

Section rules:
- Context / Decisions / User model / Agent model / Open loops / Retrieval tags / Invariants / Derived = bullet lists only.
- Lessons & pitfalls = bullet list only; each bullet must be one single line in this shape:
  - Symptom: ... Cause: ... Fix: ... Prevention: ...
- Invariants = stable cross-session rules only; prefer bullets starting with Always / Never / When / If / Before / After / Prefer / Avoid / Require.
- Derived = recent-run distilled learnings, adjustments, and follow-up heuristics that may help the next several runs, but should decay over time.
- Keep Invariants stable and long-lived; keep Derived recent, reusable across near-term runs, and decayable.
- Do not restate long-term rules in Derived.

Governance section rules:
- If empty, write exactly:
  - (none captured)
- Otherwise, do NOT use bullet lists there.
- Use one or more entries in exactly this format:

### Entry 1
**Priority**: low|medium|high|critical
**Status**: pending|triage|promoted_to_skill|done
**Area**: frontend|backend|infra|tests|docs|config|<custom area>
### Summary
<one concise candidate>
### Details
<short supporting details>
### Suggested Action
<one concrete next action>

Notes:
- Keep writer-owned metadata out of the output. The writer generates Logged and IDs.
- Prefer structured, machine-parseable output over elegant prose.

OUTPUT TEMPLATE (copy this structure exactly):
## Context (session background)
- ...

## Decisions (durable)
- ...

## User model deltas (about the human)
- ...

## Agent model deltas (about the assistant/system)
- ...

## Lessons & pitfalls (symptom / cause / fix / prevention)
- Symptom: ... Cause: ... Fix: ... Prevention: ...

## Learning governance candidates (.learnings / promotion / skill extraction)
- (none captured)

## Open loops / next actions
- ...

## Retrieval tags / keywords
- ...

## Invariants
- ...

## Derived
- ...

---

CONVERSATION TO ANALYZE (last {max_chars} chars):
{clipped}
"""


def test_ollama_reflection():
    """直接測試 Ollama 的 reflection 生成時間"""
    print("=" * 60)
    print("測試 Reflection Prompt LLM 生成時間")
    print("=" * 60)

    # 建立測試用的 conversation（模擬 16193 chars）
    test_conv = """
User: 嗨
Assistant: 嗨家豪！
User: 幫我看看這個問題
Assistant: 好的，我來幫你處理
User: 謝謝
Assistant: 不客氣！
""" * 200  # 重複產生足夠長度

    print(f"測試用 conversation 長度: {len(test_conv)} chars")
    print()

    # 建立 reflection prompt
    prompt = build_reflection_prompt(test_conv, max_chars=6000)
    print(f"Reflection prompt 長度: {len(prompt)} chars")
    print()

    # 測試 1: /api/embeddings (應該馬上回)
    print("測試 1: /api/embeddings 延遲（基準）...")
    start = time.time()
    try:
        resp = subprocess.run([
            "curl", "-s", "-X", "POST",
            "http://localhost:11434/api/embeddings",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"model": "jina-v5-retrieval-test", "prompt": "hello"})
        ], capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start
        print(f"  → {elapsed:.2f}s")
    except Exception as e:
        print(f"  → 錯誤: {e}")
    print()

    # 測試 2: /api/generate (reflection 實際用的 endpoint)
    print("測試 2: /api/generate 延遲（reflection 實際用這個）...")
    start = time.time()
    try:
        resp = subprocess.run([
            "curl", "-s", "-X", "POST",
            "http://localhost:11434/api/generate",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": "jina-v5-retrieval-test",
                "prompt": "Say 'hello' in one word only",
                "options": {"num_predict": 5}
            })
        ], capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start
        print(f"  → {elapsed:.2f}s")
    except Exception as e:
        print(f"  → 錯誤: {e}")
    print()

    # 測試 3: 完整的 reflection prompt 生成
    print("測試 3: 完整 reflection prompt 生成（6000 chars input）...")
    print("  [這個測試會需要比較久的時間，timeout=120s]")
    start = time.time()
    try:
        resp = subprocess.run([
            "curl", "-s", "-X", "POST",
            "http://localhost:11434/api/generate",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": "jina-v5-retrieval-test",
                "prompt": prompt,
                "options": {"num_predict": 500}  # 限制輸出長度
            })
        ], capture_output=True, text=True, timeout=125)
        elapsed = time.time() - start
        print(f"  → {elapsed:.2f}s")

        if resp.stdout:
            try:
                result = json.loads(resp.stdout)
                text = result.get("response", "")
                print(f"  → 生成文字長度: {len(text)} chars")
            except:
                pass
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"  → TIMEOUT after {elapsed:.2f}s")
    except Exception as e:
        print(f"  → 錯誤: {e}")
    print()

    print("=" * 60)
    print("測試完成")
    print("=" * 60)


if __name__ == "__main__":
    test_ollama_reflection()
