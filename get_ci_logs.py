# -*- coding: utf-8 -*-
import urllib.request, json, os

token = os.environ.get("GITHUB_TOKEN", "")

def get_job(job_id):
    url = f'https://api.github.com/repos/CortexReach/memory-lancedb-pro/actions/jobs/{job_id}'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def get_job_logs(job_id):
    url = f'https://api.github.com/repos/CortexReach/memory-lancedb-pro/actions/jobs/{job_id}/logs'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"Error fetching logs: {e}"

# Check core-regression
print("=== core-regression (72316523418) ===")
data = get_job(72316523418)
print('Conclusion:', data.get('conclusion'))
for step in data.get('steps', []):
    print(f"  Step: {step.get('name')} -> {step.get('conclusion')}")
print()

# Get logs for core-regression
print("=== core-regression logs (last 5000 chars) ===")
logs = get_job_logs(72316523418)
print(logs[-5000:])

print()
print("=== packaging-and-workflow (72316523421) ===")
data2 = get_job(72316523421)
print('Conclusion:', data2.get('conclusion'))
for step in data2.get('steps', []):
    print(f"  Step: {step.get('name')} -> {step.get('conclusion')}")
