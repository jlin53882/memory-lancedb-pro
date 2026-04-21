# -*- coding: utf-8 -*-
with open(r'C:\Users\admin\.openclaw\extensions\memory-lancedb-pro\scripts\ci-test-manifest.mjs', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
print('import-markdown in manifest:', 'import-markdown' in content)
import re
tests = re.findall(r"'(test/[^']+)'", content)
print('All tests in manifest:')
for t in sorted(tests):
    print(' ', t)
