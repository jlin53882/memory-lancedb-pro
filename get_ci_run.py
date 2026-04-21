# -*- coding: utf-8 -*-
import urllib.request, json, os

def gh_api(url):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

# Get the run details
run = gh_api('https://api.github.com/repos/CortexReach/memory-lancedb-pro/actions/runs/24723015451')
print('Run name:', run.get('name'))
print('Head commit:', run.get('head_commit', {}).get('message', ''))
print('Head sha:', run.get('head_sha', ''))

# Get the check runs for the commit
checks = gh_api('https://api.github.com/repos/CortexReach/memory-lancedb-pro/commits/b87f858/check-runs')
print('\nCheck runs:')
for c in checks.get('check_runs', []):
    print(f"  {c['name']}: {c['conclusion']} - {c.get('output', {}).get('title', '')}")
    # Print annotations/errors
    for ann in c.get('output', {}).get('annotations', []):
        print(f"    Annotation [{ann['annotation_level']}]: {ann['message']}")
        print(f"      at {ann['path']}:{ann['start_line']}")
