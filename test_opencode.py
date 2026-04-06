#!/usr/bin/env python3
import sys
sys.path.insert(0, "C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts")
from opencode_task import run_opencode_task

# Simple test first
result = run_opencode_task(
    prompt="Say hello in one word",
    model="minimax/MiniMax-M2.7",
    reasoning="none",
    timeout=60,
)
print(f"OK: {result.ok}")
print(f"Text: {result.text}")
print(f"Error: {result.error}")
