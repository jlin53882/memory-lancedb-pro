import subprocess, json, os

msg = """Both issues fixed in commit 3d9f27d:

**P1 - autoCapture closing brace**: The `if (config.autoCapture !== false)` block (agent_end auto-capture, line 2625) was missing its closing brace. Added `}` after the Phase 1 before_prompt_build hook (priority 5) to properly close the block. Self-improvement, reflection, and lifecycle hooks now run independently of autoCapture.

**P2 - feedback config type coercion**: Added `Number()` coercion for all numeric feedback config values to prevent string concatenation."""

for comment_id in [3070848190, 3070848194]:
    tmp = os.path.expanduser('~/tmp_reply_' + str(comment_id) + '.json')
    payload = json.dumps({'body': msg})
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(payload)
    result = subprocess.run(
        ['gh', 'api', '--method', 'POST',
         'repos/CortexReach/memory-lancedb-pro/pulls/597/comments/' + str(comment_id) + '/replies',
         '--input', tmp],
        capture_output=True, timeout=30
    )
    print(f'Comment {comment_id}: return code {result.returncode}')
    if result.returncode != 0:
        print(f'stderr: {result.stderr}')
    os.remove(tmp)