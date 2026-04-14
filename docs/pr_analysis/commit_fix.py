import subprocess

# Read commit message
with open(r'C:\Users\admin\.openclaw\workspace-dc-channel--1476866394556465252\docs\pr_analysis\commit_msg.txt', 'r', encoding='utf-8') as f:
    msg = f.read()

# Git add and commit
result = subprocess.run(
    ['git', '-C', r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro', 'add', 'index.ts'],
    capture_output=True, text=True
)
print(f"git add: {result.returncode}")

result = subprocess.run(
    ['git', '-C', r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro', 'commit', '-F', '-'],
    input=msg, capture_output=True, text=True, encoding='utf-8'
)
print(f"git commit: {result.returncode}")
print(result.stdout)
print(result.stderr[:500] if result.stderr else '')
