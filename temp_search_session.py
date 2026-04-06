import json

path = r"C:\Users\admin\.openclaw\agents\dc-channel--1476866394556465252\sessions\2026-03-24T15-31-22-262Z_efc4c56f-acb6-4594-abb0-e791ccb84486.jsonl"

with open(path, encoding="utf-8") as f:
    content = f.read()

print(f"File size: {len(content)} bytes")
print(f"First 500 chars: {content[:500]}")
