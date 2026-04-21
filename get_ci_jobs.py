# -*- coding: utf-8 -*-
import urllib.request, json, os

url = 'https://api.github.com/repos/CortexReach/memory-lancedb-pro/actions/runs/24723015451/jobs'
headers = {'Accept': 'application/vnd.github.v3+json'}
token = os.environ.get("GITHUB_TOKEN", "")
if token:
    headers['Authorization'] = f'token {token}'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())

for job in data.get('jobs', []):
    if job.get('conclusion') == 'failure':
        print(f'FAILED: {job["name"]}')
        print(f'  HTML: {job["html_url"]}')
        # Get raw log URL
        print(f'  Log URL: {job.get("logs_url", "N/A")}')
        # Get runner info
        print(f'  Runner: {job.get("runner_name", "N/A")}')
        print()
