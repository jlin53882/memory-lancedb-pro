import json, sys

try:
    with open(r"C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\all_prs.json", "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    prs = json.loads(content)
    
    for p in prs:
        title = p.get('title', '')
        if any(kw in title.lower() for kw in ['proposal', 'feedback', 'dynamic importance', 'recall used']):
            print(f"#{p['number']} | {p['title']} | state={p['state']} | user={p['user']['login']} | head={p['head']['ref']} | base={p['base']['ref']}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print(f"File size: {len(content) if 'content' in dir() else 'N/A'}", file=sys.stderr)
