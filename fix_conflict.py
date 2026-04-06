import json

with open('openclaw.plugin.json', encoding='utf-8') as f:
    content = f.read()

if '<<<<<<<' not in content:
    print('NO CONFLICT - already resolved')
    exit(0)

# uiHints conflict in openclaw.plugin.json
old = '''    "autoRecallMaxQueryLength": {
      "label": "Auto-Recall Max Query Length",
      "help": "Maximum character length of the auto-recall query before truncation. Default: 2000.",
=======
    "autoRecallTimeoutMs": {
      "label": "Auto-Recall Timeout (ms)",
      "help": "Timeout for each auto-recall retrieval call in milliseconds. Prevents slow retrieval from blocking responses.",
>>>>>>> 6a5ee85 (fix: add autoRecallTimeoutMs to openclaw.plugin.json schema)
      "advanced": true
    },'''

new = '''    "autoRecallMaxQueryLength": {
      "label": "Auto-Recall Max Query Length",
      "help": "Maximum character length of the auto-recall query before truncation. Default: 2000.",
      "advanced": true
    },
    "autoRecallTimeoutMs": {
      "label": "Auto-Recall Timeout (ms)",
      "help": "Timeout for each auto-recall retrieval call in milliseconds. Prevents slow retrieval from blocking responses.",
      "advanced": true
    },'''

if old in content:
    content = content.replace(old, new)
    with open('openclaw.plugin.json', 'w', encoding='utf-8') as f:
        f.write(content)
    print('FIXED!')
else:
    print('Pattern not found. Dumping around autoRecallMaxQueryLength:')
    idx = content.find('autoRecallMaxQueryLength')
    if idx >= 0:
        print(repr(content[idx:idx+600]))
    else:
        print('NOT FOUND')
