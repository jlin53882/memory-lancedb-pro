# 分析記憶體長度分布，評估最佳 autoRecallMaxChars / autoRecallPerItemMaxChars
import json, glob, os, sys

workspace = os.path.dirname(os.path.abspath(__file__))
memory_dir = os.path.join(workspace, "memory")

lengths = []
categories = {}
file_samples = {}  # category -> list of (filename, length, preview)

for root, dirs, files in os.walk(memory_dir):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__')]
    for fname in files:
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, encoding="utf-8") as fh:
                content = fh.read().strip()
            if not content:
                continue
            l = len(content)
            rel = os.path.relpath(fpath, workspace)
            lengths.append((l, rel, content[:80]))
            
            # categorize
            cat = "other"
            if "decision" in fname: cat = "decision"
            elif "preference" in fname: cat = "preference"
            elif "entity" in fname: cat = "entity"
            elif "reflection" in fname: cat = "reflection"
            elif "fact" in fname: cat = "fact"
            elif "learnings" in fname: cat = "learnings"
            elif "daily" in rel: cat = "daily"
            elif "journal" in rel: cat = "journal"
            elif "cases" in rel: cat = "cases"
            elif "patterns" in rel: cat = "patterns"
            categories[cat] = categories.get(cat, 0) + 1
        except Exception as e:
            pass

# 也掃 .jsonl
journal_dir = os.path.join(memory_dir, "journal")
if os.path.exists(journal_dir):
    for fpath in glob.glob(os.path.join(journal_dir, "*.jsonl")):
        try:
            with open(fpath, encoding="utf-8") as fh:
                for line in fh:
                    obj = json.loads(line.strip())
                    text = obj.get("text", "")
                    if text:
                        lengths.append((len(text), os.path.basename(fpath), text[:80]))
        except:
            pass

if not lengths:
    print("找不到任何記憶體")
    sys.exit(1)

lengths.sort(key=lambda x: x[0])
total = len(lengths)
char_lens = [l[0] for l in lengths]

def pct(p):
    idx = max(0, min(len(char_lens)-1, int(total * p)))
    return char_lens[idx]

print(f"=== 記憶體分析 ===")
print(f"總數量: {total}")
print(f"")
print(f"長度分佈:")
print(f"  最小:   {char_lens[0]}")
print(f"  P10:    {pct(0.10)}")
print(f"  P25:    {pct(0.25)}")
print(f"  P50:    {pct(0.50)}")
print(f"  P75:    {pct(0.75)}")
print(f"  P90:    {pct(0.90)}")
print(f"  P95:    {pct(0.95)}")
print(f"  最大:   {char_lens[-1]}")
print(f"  平均:   {sum(char_lens)//total}")
print(f"")

print(f"類別分布:")
for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {cnt}")

print(f"")
print(f"=== 不同 autoRecallPerItemMaxChars 下的截斷率 ===")
print(f"(假設 recall 回來的 item 會被 truncateText 截到這個長度)")
for limit in [120, 150, 180, 200, 250, 300, 350, 400, 500, 600]:
    truncated = sum(1 for l in char_lens if l > limit)
    pct_val = truncated / total * 100
    bar = "█" * int(pct_val / 2)
    print(f"  {limit:4d}: {truncated:4d}/{total} ({pct_val:5.1f}%) {bar}")

print(f"")
print(f"=== 不同 autoRecallMaxChars 預算能容納多少筆記憶 ===")
print(f"(假設每筆 = autoRecallPerItemMaxChars，不含 prefix 開銷)")
for max_chars in [400, 600, 800, 1000, 1200, 1500, 2000]:
    for per_item in [150, 180, 200, 250, 350]:
        items = max_chars // per_item
        overhead = max(0, items - 1) * 2  # \n separator estimate
        actual = items if items * per_item + overhead <= max_chars else items - 1
        if per_item == 150:
            print(f"  maxChars={max_chars}: {actual} 筆 @{per_item}字 (開銷~{overhead})")
            break
