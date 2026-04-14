import subprocess, json, sys

def gh_json(endpoint):
    r = subprocess.run(['gh', 'api', endpoint], capture_output=True, encoding='utf-8', errors='replace')
    try:
        return json.loads(r.stdout) if r.stdout.strip() else []
    except:
        return []

for num in [515, 516, 520, 521]:
    print(f'=== PR #{num} ===')
    info = gh_json(f'repos/CortexReach/memory-lancedb-pro/pulls/{num}')
    if isinstance(info, dict):
        print(f"  State: {info.get('state')}, Merged: {info.get('merged')}, User: {info.get('user',{}).get('login')}")
        print(f"  Title: {info.get('title','')}")
        print(f"  Closed at: {info.get('closed_at')}, Merged at: {info.get('merged_at')}")
        body = info.get('body', '')[:200]
        print(f"  Body: {body}")
    
    reviews = gh_json(f'repos/CortexReach/memory-lancedb-pro/pulls/{num}/reviews')
    if isinstance(reviews, list):
        for rv in reviews:
            print(f"  Review: {rv.get('user',{}).get('login')} | {rv.get('state')} | {str(rv.get('body',''))[:150]}")
    print()

# Also check issue 514
print('=== Issue #514 ===')
issue = gh_json('repos/CortexReach/memory-lancedb-pro/issues/514')
if isinstance(issue, dict):
    print(f"  State: {issue.get('state')}, User: {issue.get('user',{}).get('login')}")
    print(f"  Title: {issue.get('title','')}")
    print(f"  Body: {str(issue.get('body',''))[:300]}")
print()

# Check issue 492
print('=== Issue #492 ===')
issue = gh_json('repos/CortexReach/memory-lancedb-pro/issues/492')
if isinstance(issue, dict):
    print(f"  State: {issue.get('state')}, User: {issue.get('user',{}).get('login')}")
    print(f"  Title: {issue.get('title','')}")
print()
