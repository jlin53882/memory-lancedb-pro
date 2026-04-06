import os

# Check if the opencode-api skill scripts exist
skill_path = 'C:/Users/admin/.openclaw/workspace-dc-channel--1476866394556465252/skills/opencode-api/scripts'
print(f'Skill path: {skill_path}')
print(f'Exists: {os.path.exists(skill_path)}')

if os.path.exists(skill_path):
    for f in os.listdir(skill_path):
        print(f'  {f}')

# Also check the workspace skills directory
workspace_skills = 'C:/Users/admin/.openclaw/workspace/skills/opencode-api/scripts'
print(f'\nWorkspace skill path: {workspace_skills}')
print(f'Exists: {os.path.exists(workspace_skills)}')
if os.path.exists(workspace_skills):
    for f in os.listdir(workspace_skills):
        print(f'  {f}')
