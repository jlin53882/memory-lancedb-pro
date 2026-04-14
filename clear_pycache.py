import shutil, os
root = r'C:\Users\admin\Desktop\minecraft_translator_flet'
count = 0
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith('.pyc') or '__pycache__' in d:
            path = os.path.join(d, f)
            try:
                os.remove(path)
                count += 1
            except:
                pass
            if '__pycache__' in d:
                try:
                    os.rmdir(d)
                    count += 1
                except:
                    pass
print(f'Re removed {count} files/dirs')
