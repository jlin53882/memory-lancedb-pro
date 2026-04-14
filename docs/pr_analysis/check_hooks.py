import re

with open(r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro\index.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find hooks registrations
for i, line in enumerate(lines):
    if 'api.on("agent_end"' in line or 'api.on("before_prompt' in line or 'api.on("session_end"' in line:
        start = max(0, i-10)
        end = min(len(lines), i+5)
        print(f'\n=== Hook at line {i+1} ===')
        for j in range(start, end):
            marker = '>>>' if j == i else '   '
            print(f'{marker} {j+1:4d}: {lines[j]}', end='')
