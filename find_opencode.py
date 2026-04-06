import os
import glob

paths_to_check = [
    os.path.expanduser('~/.opencode/'),
    'C:/Users/admin/AppData/Roaming/npm/node_modules/opencode/',
    'C:/Users/admin/AppData/Local/opencode/',
]

for p in paths_to_check:
    print(f'\n--- {p} ---')
    try:
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    fp = os.path.join(root, f)
                    print(fp)
                if len(list(os.walk(p))) > 100:
                    print('... (too many files)')
                    break
        else:
            print('(does not exist)')
    except Exception as e:
        print(f'Error: {e}')
