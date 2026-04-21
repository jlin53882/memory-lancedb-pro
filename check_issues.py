import subprocess, json

result = subprocess.run(
    ["gh", "api", "repos/CortexReach/memory-lancedb-pro/issues", "--paginate"],
    capture_output=True, text=True
)
issues = json.loads(result.stdout)
keywords = ["Unable to update lock", "stale threshold", "update lock within"]
for issue in issues:
    body = issue.get("body", "") or ""
    if any(k.lower() in body.lower() for k in keywords):
        print(f"#{issue['number']} [{issue['state']}] {issue['title']}")
