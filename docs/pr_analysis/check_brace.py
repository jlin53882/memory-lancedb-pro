import subprocess

r = subprocess.run(['git', '-C', r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro', 'show', 'origin/jlin53882:index.ts'], capture_output=True, timeout=30)
content = r.stdout.decode('utf-8', errors='replace')
our_lines = content.split('\n')

# Find ALL occurrences of autoCapture !== false
print('=== autoCapture guards in origin/jlin53882 ===')
for i, l in enumerate(our_lines):
    if 'autoCapture !== false' in l:
        print(f'Line {i+1}: {l.strip()[:100]}')

print('\n=== Context around before_prompt_build end (line ~3140) ===')
for i in range(3135, 3175):
    if i < len(our_lines):
        print(f'{i+1}: {our_lines[i]}')

print('\n=== Phase 1 markers and next sections ===')
for i, l in enumerate(our_lines):
    if 'Proposal A Phase 1' in l or 'Integrated Self-Improvement' in l or 'Integrated Memory Reflection' in l:
        print(f'Line {i+1}: {l.strip()[:100]}')
