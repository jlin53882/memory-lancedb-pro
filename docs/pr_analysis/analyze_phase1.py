import json, subprocess

def gh_json(endpoint):
    r = subprocess.run(["gh", "api", endpoint], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

# Get all commits on Phase 1 branch
print("=== All Phase 1 commits ===")
commits = gh_json("repos/jlin53882/memory-lancedb-pro/commits?per_page=30&sha=feat/proposal-a-v3-clean")
for i, c in enumerate(commits):
    msg_lines = c['commit']['message'].split('\n')
    print(f"{i+1}. {c['sha'][:8]} - {msg_lines[0]}")

# Get the PR reviews for #507 to see what AliceLJY's CHANGES_REQUESTED said
print("\n=== PR #507 Reviews ===")
reviews = gh_json("repos/CortexReach/memory-lancedb-pro/pulls/507/reviews")
for r in reviews:
    print(f"\n[{r['user']['login']}] ({r['state']}) - {r['submitted_at']}:")
    body = r.get('body', '')[:800]
    if body:
        print(body[:800])
