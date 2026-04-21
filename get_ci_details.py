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

for job_id, name in [(72316523418, 'core-regression'), (72316523421, 'packaging-and-workflow')]:
    print(f"=== {name} ({job_id}) ===")
    job = gh_api(f'https://api.github.com/repos/CortexReach/memory-lancedb-pro/actions/jobs/{job_id}')
    print('Conclusion:', job.get('conclusion'))
    print('Failure message:', job.get('failure_message', 'N/A'))
    # Get annotations
    annotations_url = job.get('annotations_url', '')
    if annotations_url:
        ann_data = gh_api(annotations_url)
        for ann in ann_data:
            print(f"  [{ann.get('annotation_level')}] {ann.get('message')}")
            print(f"    File: {ann.get('path')}:{ann.get('start_line')}")
    print()
