# 分析 LanceDB 內真實記憶體長度分布
import json, sqlite3, os, glob

# 找到 LanceDB 路徑
possible_paths = [
    r"C:\Users\admin\.openclaw\extensions\memory-lancedb-pro",
    os.path.expanduser(r"~/.openclaw\extensions\memory-lancedb-pro"),
    r"C:\Users\admin\.openclaw",
]
config_path = os.path.join(r"C:\Users\admin\.openclaw\openclaw.json")
db_path = None

if os.path.exists(config_path):
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)
    plugins = cfg.get("plugins", {})
    mem_cfg = plugins.get("entries", {}).get("memory-lancedb-pro", {})
    config = mem_cfg.get("config", {})
    db_path = config.get("dbPath")
    print(f"dbPath from config: {db_path}")

# 嘗試從 lance.db 讀取
lance_db = None
if db_path:
    candidates = [
        db_path,
        os.path.join(db_path, "lance.db"),
        os.path.join(db_path, ".lance"),
    ]
    for c in candidates:
        if os.path.exists(c):
            lance_db = c
            break

# 如果找不到，從擴展目錄找
if not lance_db:
    ext_dir = r"C:\Users\admin\.openclaw\extensions\memory-lancedb-pro"
    for root, dirs, files in os.walk(ext_dir):
        for f in files:
            if "lance" in f.lower() or ".sqlite" in f.lower():
                print(f"Found DB candidate: {os.path.join(root, f)}")

# 找 memory-lancedb-pro 的 lance 目錄
base = r"C:\Users\admin\.openclaw"
print(f"\n搜尋 LanceDB 目錄...")
for root, dirs, files in os.walk(base):
    # 跳过明顯不是的目錄
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.venv', 'venv', 'cache', 'logs')]
    for d in dirs:
        if "lance" in d.lower() or "memory" in d.lower():
            full = os.path.join(root, d)
            print(f"  {full}")

# 也看看 config 是否有自訂路徑
print(f"\n嘗試找 lance.db...")
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.venv', 'venv', 'cache', 'logs')]
    if 'lance.db' in files:
        print(f"  Found: {os.path.join(root, 'lance.db')}")
    if '.lance' in dirs:
        print(f"  Found dir: {os.path.join(root, '.lance')}")
