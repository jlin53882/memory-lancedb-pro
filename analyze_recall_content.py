# 用 lance-db 讀取真實 LanceDB entry 長度
import subprocess, sys, os

# 確認 Node.js 可用
result = subprocess.run(["node", "--version"], capture_output=True, text=True)
print(f"Node: {result.stdout.strip()}")

# 嘗試用 lancedb python client
try:
    import lancedb
    print("lancedb Python client 可用")
    
    db_path = os.path.expanduser(r"~/.openclaw/memory/lancedb-pro-jina1024")
    print(f"嘗試開啟: {db_path}")
    
    db = lancedb.connect(db_path)
    print(f"Table names: {db.table_names()}")
    
    for tbl_name in db.table_names():
        tbl = db.open_table(tbl_name)
        df = tbl.to_pandas()
        if "text" in df.columns:
            texts = df["text"].tolist()
            lens = sorted([len(str(t)) for t in texts if t])
            if lens:
                total = len(lens)
                print(f"\n=== {tbl_name} ===")
                print(f"總數: {total}")
                print(f"長度: min={lens[0]}, P10={lens[int(total*0.1)]}, P25={lens[int(total*0.25)]}, "
                      f"P50={lens[int(total*0.5)]}, P75={lens[int(total*0.75)]}, P90={lens[int(total*0.9)]}, max={lens[-1]}")
                print(f"平均: {sum(lens)//total}")
                
                print(f"\n各 autoRecallPerItemMaxChars 截斷率:")
                for limit in [120, 150, 180, 200, 250, 300, 350, 400, 500, 600]:
                    truncated = sum(1 for l in lens if l > limit)
                    pct = truncated / total * 100
                    bar = "█" * int(pct / 2)
                    print(f"  {limit:4d}: {truncated:4d}/{total} ({pct:5.1f}%) {bar}")
                
                print(f"\n前5筆範例:")
                for t in texts[:5]:
                    print(f"  [{len(str(t))}字] {str(t)[:100]!r}...")
        else:
            print(f"  {tbl_name}: 無 text 欄位，欄位={list(df.columns)}")
            
except ImportError:
    print("lancedb Python client 不可用，嘗試 pip install...")
    subprocess.run([sys.executable, "-m", "pip", "install", "lancedb", "--quiet"])
    print("已安裝，請重新執行")
except Exception as e:
    print(f"錯誤: {e}")
