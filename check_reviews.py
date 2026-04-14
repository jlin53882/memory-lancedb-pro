import subprocess, json, sys

def gh_json(endpoint):
    r = subprocess.run(['gh', 'api', endpoint], capture_output=True, encoding='utf-8', errors='replace')
    try:
        return json.loads(r.stdout) if r.stdout.strip() else []
    except:
        return {'stdout': r.stdout[:500], 'stderr': r.stderr[:200]}

# Get full review details for PR 516
print('=== PR #516 Full Reviews ===')
reviews = gh_json('repos/CortexReach/memory-lancedb-pro/pulls/516/reviews')
if isinstance(reviews, list):
    for i, rv in enumerate(reviews):
        print(f"\n--- Review {i+1} ---")
        print(f"User: {rv.get('user',{}).get('login')}")
        print(f"State: {rv.get('state')}")
        body = rv.get('body', '')
        print(f"Body ({len(body)} chars):\n{body}")
else:
    print(reviews)

# Get PR 516 timeline
print('\n\n=== PR #516 Timeline ===')
events = gh_json('repos/CortexReach/memory-lancedb-pro/issues/516/timeline?per_page=50')
if isinstance(events, list):
    for ev in events:
        print(f"  {ev.get('event', 'unknown')}: {ev.get('actor',{}).get('login','?')} | {str(ev.get('created_at',''))[:10]} | {str(ev)[:100]}")
else:
    print(events)

# Check if PR 516 was closed and reopened
print('\n\n=== PR #516 Status Events ===')
stat_events = gh_json('repos/CortexReach/memory-lancedb-pro/pulls/516/events?per_page=50')
if isinstance(stat_events, list):
    for ev in stat_events:
        print(f"  {ev.get('event')}: {ev.get('actor',{}).get('login','?')} | {str(ev.get('created_at',''))[:10]}")
