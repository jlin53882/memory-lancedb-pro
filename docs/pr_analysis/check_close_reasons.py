import json, subprocess

def gh_json(endpoint):
    r = subprocess.run(["gh", "api", endpoint], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", errors="replace"))

# Check issue #445 comments for close reasons
print("=== Issue #445 Comments ===")
comments = gh_json("repos/CortexReach/memory-lancedb-pro/issues/445/comments")
for c in comments:
    body = c.get("body", "")[:600]
    user = c.get("user", {}).get("login", "?")
    created = c.get("created_at", "?")
    print(f"[{user}] {created}:")
    print(body[:600])
    print("---")

# Check PR reviews for close reasons
print("\n=== PR #507 Reviews ===")
reviews = gh_json("repos/CortexReach/memory-lancedb-pro/pulls/507/reviews")
for r in reviews:
    body = r.get("body", "")[:600]
    user = r.get("user", {}).get("login", "?")
    state = r.get("state", "?")
    created = r.get("submitted_at", "?")
    print(f"[{user}] ({state}) {created}:")
    print(body[:600])
    print("---")
