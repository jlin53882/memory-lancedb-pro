#!/usr/bin/env python3
"""
測試記憶截斷對不同內容位置的影響
autoRecallMaxChars=600 / perItem=180 / truncate=tail（從尾巴截斷）
"""

def make_memory(label: str, front: str, middle: str, back: str) -> str:
    return f"[{label}] 前段：{front}。中段：{middle}。後段：{back}"

PAD_MEDIUM = "填充文字重複區塊。" * 60   # ~1200字
PAD_LONG   = "填充文字重複區塊。" * 300  # ~6000字

TEST_MEMORIES = [
    # 短記憶（<180，几乎不截斷）
    {"id": "短記憶", "text": make_memory("短", "蘋果是紅色水果", "含維生素C", "可助消化"), "head": "蘋果", "tail": "消化"},
    # 中記憶，重點在頭（~1200字）
    {"id": "中記憶_頭", "text": make_memory("中", "【答案42】這是結論在開頭", PAD_MEDIUM, "結尾廢話段落"), "head": "答案42", "tail": "結尾"},
    # 中記憶，重點在尾（~1200字）
    {"id": "中記憶_尾", "text": make_memory("中", "開頭背景無用資訊", PAD_MEDIUM, "【答案42】結論在最後"), "head": "背景", "tail": "答案42"},
    # 長記憶，重點在頭（~6000字）
    {"id": "長記憶_頭", "text": make_memory("長", "【答案42】最重要結論在這裡", PAD_LONG, "結尾廢話一堆"), "head": "答案42", "tail": "廢話"},
    # 長記憶，重點在尾（~6000字）
    {"id": "長記憶_尾", "text": make_memory("長", "開頭背景說明", PAD_LONG, "【答案42】結論在最後一行很重要"), "head": "背景", "tail": "答案42"},
    # 長記憶，頭尾都重要（都在180字內）
    {"id": "長記憶_頭尾", "text": make_memory("長", "【答案甲42】開頭結論", PAD_LONG, "【答案乙99】結尾結論"), "head": "答案甲42", "tail": "答案乙99"},
]

def truncate_text(text: str, max_chars: int) -> str:
    """tools.ts:95 行為：從尾巴截斷"""
    if len(text) <= max_chars:
        return text
    clipped = text[:max(1, max_chars - 1)].rstrip()
    return clipped + "�K"

def simulate_injection(text: str, per_item_max: int = 180) -> dict:
    truncated = truncate_text(text, per_item_max)
    return {"text": truncated, "length": len(truncated)}

print("=" * 70)
print("記憶截斷測試｜perItem=180 / truncate=tail")
print("=" * 70)
print()

total_chars = 0
total_budget = 600
fail_count = 0

for mem in TEST_MEMORIES:
    original_len = len(mem["text"])
    inj = simulate_injection(mem["text"])
    truncated_text = inj["text"]

    head_in = mem["head"] in truncated_text
    tail_in = mem["tail"] in truncated_text

    head_verdict = "✅" if head_in else "❌"
    tail_verdict = "❌" if (not tail_in and original_len > 200) else ("✅" if tail_in else "⚠️")

    print(f"[{mem['id']}]")
    print(f"  原始: {original_len} 字 → 截斷後: {inj['length']} 字")
    print(f"  前段重點「{mem['head']}」: {head_verdict}")
    if original_len > 200:
        print(f"  尾段重點「{mem['tail']}」: {tail_verdict}")
    print(f"  截斷後文字: {truncated_text[:100]}...")
    print()

    total_chars += inj["length"]
    if original_len > 200 and not tail_in:
        fail_count += 1

print("=" * 70)
print("結果總結")
print("=" * 70)
print(f"{'類型':<20} {'原始':>6} {'注入':>6} {'頭保留':>8} {'尾保留':>8}")
print("-" * 70)
for mem in TEST_MEMORIES:
    orig = len(mem["text"])
    inj = simulate_injection(mem["text"])
    head_ok = mem["head"] in inj["text"]
    tail_ok = mem["tail"] in inj["text"]
    print(f"{mem['id']:<20} {orig:>6} {inj['length']:>6} {'✅' if head_ok else '❌':>8} {'✅' if tail_ok else '❌':>8}")
print("-" * 70)
print(f"總注入: {total_chars}/{total_budget} 字")
if total_chars > total_budget:
    print(f"⚠️  超過預算！還會再被裁 {total_chars - total_budget} 字（由外向內砍）")
print()
print(f"尾段重點丢失: {fail_count} 筆記得（當長度>200字時）")
print()
print("【核心發現】")
print("1. truncateText 永遠從尾巴截 → 結尾內容100%丢失")
print("2. 當結論在記憶尾端（不管多短），截斷後永遠看不到")
print("3. 總預算600字，若inject多筆 → 最外圍的記憶被再多砍一輪")
