import os

root = r'C:\Users\admin\Desktop\two_project'
patterns = [
    'page.open(', 'page.close(', 'scroll=', 'prefix_text=', 'on_change=',
    'on_result=', 'pick_date(', 'show_dialog(', 'pop_dialog(', 'show_snack_bar(',
    'ElevatedButton', 'border.all(', 'padding.symmetric(', 'padding.only(', 'border_radius.only('
]

for dirpath, _, filenames in os.walk(root):
    if '.venv' in dirpath or 'node_modules' in dirpath:
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            txt = open(path, 'r', encoding='utf-8').read()
        except Exception:
            continue
        hits = [p for p in patterns if p in txt]
        if hits:
            print(path)
            for h in hits:
                print('  HIT', h)
