import subprocess, json

for pr in ['367', '365']:
    r = subprocess.run(
        ['gh','pr','view',pr,'--repo','CortexReach/memory-lancedb-pro',
         '--json','state,title,mergeable,reviews,additions,deletions,changedFiles,headRefName'],
        capture_output=True, text=True, encoding='utf-8'
    )
    data = json.loads(r.stdout)
    print(f'PR #{pr}: {data["title"]}')
    print(f'  Branch: {data["headRefName"]}')
    print(f'  State: {data["state"]}, Mergeable: {data["mergeable"]}')
    print(f'  Files: {data["changedFiles"]}, +{data["additions"]} -{data["deletions"]}')
    for rv in data.get('reviews', []):
        print(f'  Review by {rv["author"]["login"]}: {rv["body"][:80]}...')
    print()
