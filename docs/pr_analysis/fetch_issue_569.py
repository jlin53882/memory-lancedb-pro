import json, subprocess

def gh_json(endpoint):
    r = subprocess.run(["gh", "api", endpoint], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

# Get issue body
issue = gh_json("repos/CortexReach/memory-lancedb-pro/issues/569")
print(f"Title: {issue['title']}")
print(f"State: {issue['state']}")
print(f"Author: {issue['user']['login']}")
print(f"Created: {issue['created_at']}")
print(f"\nBody:\n{issue['body']}")
print(f"\n--- Comments ---")

comments = gh_json("repos/CortexReach/memory-lancedb-pro/issues/569/comments")
for c in comments:
    print(f"\n[{c['user']['login']}] ({c['created_at']}):")
    print(c['body'])
