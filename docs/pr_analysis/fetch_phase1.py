import json, subprocess

def gh_json(endpoint):
    r = subprocess.run(["gh", "api", endpoint], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

# Compare Phase 1 branch against OFFICIAL master
print("=== Comparing feat/proposal-a-v3-clean vs official CortexReach/master ===")
compare = gh_json("repos/jlin53882/memory-lancedb-pro/compare/CortexReach:master...feat/proposal-a-v3-clean")
print(f"Ahead by: {compare['ahead_by']}")
print(f"Behind by: {compare['behind_by']}")
print(f"\nFiles changed ({len(compare['files'])}):")
for f in compare['files']:
    additions = f.get('additions', 0)
    deletions = f.get('deletions', 0)
    print(f"  {f['status']:12} {f['filename']} (+{additions}/-{deletions})")

print("\n=== Last 5 commits ===")
for c in compare['commits'][:5]:
    msg = c['commit']['message'].split('\n')[0]
    print(f"  {c['sha'][:8]} - {msg}")
