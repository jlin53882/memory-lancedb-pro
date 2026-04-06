import os, glob

paths_to_check = [
    os.path.expanduser("~/.opencode/"),
    os.path.expanduser("~/AppData/Roaming/opencode/"),
    os.path.expanduser("~/.config/opencode/"),
    "C:/Users/admin/.opencode/",
]

for p in paths_to_check:
    if os.path.exists(p):
        print(f"\n=== {p} ===")
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                print(fp)
