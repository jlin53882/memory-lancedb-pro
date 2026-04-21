import subprocess, json

result = subprocess.run(
    ['gh', 'api', 'repos/CortexReach/memory-lancedb-pro/commits', '--paginate', '--slurp'],
    capture_output=True
)
data = json.loads(result.stdout.decode('utf-8', errors='ignore'))
for c in data[:30]:
    print(c['sha'][:8], c['commit']['message_headline'][:100])
