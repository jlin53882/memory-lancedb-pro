import subprocess, json

r = subprocess.run(['gh', 'api', 'repos/CortexReach/memory-lancedb-pro/actions/runs/24327095712/jobs'], capture_output=True, timeout=30)
data = json.loads(r.stdout)
for job in data.get('jobs', []):
    print(f"{job['name']}: {job['conclusion']}")