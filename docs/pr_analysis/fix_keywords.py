import re

with open(r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro\index.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Find confirmKeywords and errorKeywords lines
import re

# More robust pattern
pattern1 = r'const confirmKeywords = fb\.confirmKeywords \?\? \[.*?\];'
pattern2 = r'const errorKeywords = fb\.errorKeywords \?\? \[.*?\];'

new_confirm = 'const confirmKeywords = fb.confirmKeywords ?? ["correct", "right", "yes", "confirmed", "exactly", "對", "沒錯", "正確", "確認", "好的"];'
new_error = 'const errorKeywords = fb.errorKeywords ?? ["wrong", "incorrect", "not right", "that\'s wrong", "error", "mistake", "fix it", "change that", "改成", "改為", "不是這樣", "不對", "錯了"];'

# Replace both patterns
content = re.sub(pattern1, new_confirm, content)
content = re.sub(pattern2, new_error, content)

with open(r'C:\Users\admin\Desktop\jlin53882-memory-lancedb-pro\index.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated confirm/error keywords')