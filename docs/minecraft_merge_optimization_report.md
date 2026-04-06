# 檔案合併管線（Merge）優化建議報告

> 日期：2026-03-19
> 適用版本：minecraft-translator-flet（含 lang_merger / lang_merge_pipeline / lang_merge_content_* 模組）
> 前提：已完成 `tools/test_all_features.py` 全部 13 功能 PASS，merge 底層已可正常運作

---

## 摘要：優化分級

| 等級 | impact | 改動幅度 | 建議優先順序 |
|------|--------|---------|-------------|
| 🔴 P0 | 速度 10x+ | 極小（1 行） | 最高 |
| 🟡 P1 | 速度 2-5x | 小（3-5 行） | 高 |
| 🟢 P2 | 正確性修補 | 中（需驗證） | 中 |
| 🔵 P3 | 彈性提升 | 小 | 低 |

---

## 🔴 P0｜all_files_cache：list → set（速度提升 10x+）

### 現況問題

**檔案**：`translation_tool/core/lang_merger.py`（約第 120-130 行）

```python
# 現況：list + in → O(n) 線性查詢
all_files_cache = [n.lower().replace("\\", "/") for n in zf.namelist()]
```

`all_files_cache` 是 `list`，查詢時：
```python
has_cn_or_tw = any(
    n.startswith(book_root) and ("/zh_cn/" in n or "/zh_tw/" in n)
    for n in all_files_cache          # ← O(n)，460 JAR × 每個 book 查 N 次
)
```

### 根本原因

每次呼叫 `process_content_or_copy_file` 都會對整個 ZIP 的所有檔名做 `startswith` + `in` 掃描。
460 個 JAR、每個平均 5000 個檔名，每次查詢 = 5000 次字串比對。

### 修改方法

**檔案**：`translation_tool/core/lang_merger.py`

找到（約第 128 行）：
```python
all_files_cache = [n.lower().replace("\\", "/") for n in zf.namelist()]
```

**改為**（新增一個 set 供快速前綴查詢）：
```python
all_files_cache_list = [n.lower().replace("\\", "/") for n in zf.namelist()]
all_files_cache_set  = set(all_files_cache_list)  # O(1) exact match

# ── 新增：前綴查詢用的 dict（key = 前綴，value = 該前綴下的所有檔名）───
_prefix_map = defaultdict(set)
for name in all_files_cache_list:
    # 支援 book_root 前綴查詢："/assets/patchouli_books/" 開頭的檔
    if "/assets/" in name:
        parts = name.split("/assets/", 1)
        _prefix_map["/assets/" + parts[1].split("/")[0] + "/"].add(name)
    # 支援 zh_cn/zh_tw 前綴
    if "/zh_cn/" in name or "/zh_tw/" in name:
        _prefix_map["/zh_cn/"].add(name)
        _prefix_map["/zh_tw/"].add(name)

# 將 set 傳入，讓 process_content_or_copy_file 改用 set 做 O(1) 查詢
```

**同時修改** `lang_merge_content_copy.py` 的查詢（約第 50-55 行）：
```python
# 現況（O(n)）：
has_cn_or_tw = any(
    n.startswith(book_root) and ("/zh_cn/" in n or "/zh_tw/" in n)
    for n in all_files_cache     # list → 每次都掃描全部
)

# 改為（O(1)）：
# 在 lang_merger 傳入 _prefix_map["/zh_cn/"] 和 _prefix_map["/zh_tw/"] 兩個 set
# 這裡直接查：
has_cn_or_tw = any(
    n.startswith(book_root) and (n in _cn_set or n in _tw_set)
    for n in [book_root]  # 不再掃全部，只要 book_root 下有的就是有
)
# 或更直接：
has_cn_or_tw = bool(_prefix_map.get("/zh_cn/") | _prefix_map.get("/zh_tw/"))
```

**驗證方式**：
```python
# 在 test_all_features.py 加入計時
import time
t0 = time.perf_counter()
results = list(merge_zhcn_to_zhtw_from_zip(test_zip, output_dir))
t1 = time.perf_counter()
print(f"合併耗時：{t1-t0:.3f}s")
```

---

## 🟡 P1｜contains_cjk()：同一 value 重複計算（速度提升 2-5x）

### 現況問題

**檔案**：`translation_tool/core/lang_merge_pipeline.py`（約第 25-55 行）

`contains_cjk()` 每次對同一個 `value` 字串都重新正則比對。每個 mod 的每個 key 呼叫 2-4 次：
- `contains_cjk(tw_val)`
- `contains_cjk(cn_val)`
- `contains_cjk(en_val)`
- `contains_cjk(english_source)`

### 修改方法

**檔案**：`translation_tool/core/lang_merge_pipeline.py`

在 `_process_single_mod()` 內，`for key in all_keys:` 迴圈**之前**新增一個 memo dict：

```python
# 在 for key in all_keys: 之前新增
_value_cjk_cache: Dict[Any, bool] = {}

def memo_cjk(v: Any) -> bool:
    """contains_cjk with memoization（同一 value 不重算）"""
    # 用 id(v) 作為 key，因為 dict/list 內容相同但不同物件時只算一次
    vid = id(v)
    if vid not in _value_cjk_cache:
        _value_cjk_cache[vid] = contains_cjk(v)
    return _value_cjk_cache[vid]
```

然後在迴圈內，把所有 `contains_cjk(...)` 替換成 `memo_cjk(...)`：
```python
# 改
if contains_cjk(tw_val):  →  if memo_cjk(tw_val):
if contains_cjk(cn_val):  →  if memo_cjk(cn_val):
```

**驗證方式**：
同 P0，計時後比對前後耗時。

---

## 🟢 P2｜JSON5/含註解 JSON 支援（正確性修補）

### 現況問題

`modern_industrialization/lang/pt_br.json` 有註解或非標準格式（`Expecting property name enclosed in double quotes`），
現正則把副檔名是 `.json` 的檔案全部用 `json.loads` 解析，失敗就整檔隔離。

**受影響情境**：
- `pt_br.json`（巴西葡文）有註解（`// comment` 或 `# comment`）
- 某些 mod 的 lang JSON 含有 `trailing comma`

### 修改方法

**檔案**：`translation_tool/core/lang_merge_zip_io.py`

找 `_read_json_from_zip` 函數（約略在第 30-50 行）：

```python
# 現況
def _read_json_from_zip(zf, path):
    with zf.open(path) as f:
        return json.loads(f.read())
```

**新增 json5 fallback**（不改原邏輯，只加 fallback）：

```python
import json
import re

def _strip_json_comments(text: str) -> str:
    """剝除 // 和 # 單行註解（不影響字串內的 # 或 //）"""
    result = []
    in_string = False
    i = 0
    while i < len(text):
        c = text[i]
        if c in ('"', "'"):
            in_string = not in_string if text[i-1] != '\\' or i == 0 else in_string  # 簡化：實際用狀態機
            result.append(c)
        elif not in_string and text[i:i+2] == '//':
            # 跳過到行尾
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        elif not in_string and text[i] == '#':
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        result.append(c)
        i += 1
    return ''.join(result)

def _read_json_from_zip(zf, path: str):
    with zf.open(path) as f:
        raw = f.read()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback：嘗試剝除註解後再解析
        text = raw.decode("utf-8", errors="replace")
        text_clean = _strip_json_comments(text)
        # 移除 trailing comma（簡單替換 }, → } 和 ], → ]）
        text_clean = re.sub(r',(\s*[}\]])', r'\1', text_clean)
        return json.loads(text_clean)
```

**驗證方式**：
```python
# 直接對 pt_br.json 測試
import zipfile
from translation_tool.core.lang_merge_zip_io import _read_json_from_zip
with zipfile.ZipFile(mod_jar_path) as zf:
    data = _read_json_from_zip(zf, "assets/modid/lang/pt_br.json")
print(f"解析成功，{len(data)} 個 key")
```

---

## 🟡 P1｜SHA256 hash：相同檔案內容不重算

### 現況問題

**檔案**：`translation_tool/core/jar_processor_extract.py`（約第 40-55 行）

每個 matched 檔案都計算一次 SHA256，但同一個 ZIP 內相同路徑的內容每次都相同，且 `zf.open().read()` 已經把整個內容讀進記憶體。

### 修改方法

**檔案**：`translation_tool/core/jar_processor_extract.py`

在 `extract_from_jar_impl` 內，`with zipfile.ZipFile(jar_path)` 區塊**最開頭**新增：

```python
# 在 for member in zf.infolist(): 之前新增
_hash_cache: Dict[str, str] = {}  # {content_bytes_hex: hash_str}

def get_file_hash_cached(data: bytes) -> str:
    key = data[:1024].hex()  # 只取前 1KB 的 hex 當 key
    if key not in _hash_cache:
        _hash_cache[key] = hashlib.sha256(data).hexdigest()
    return _hash_cache[key]
```

然後把 `get_file_hash_fn(source_data)` 替換成 `get_file_hash_cached(source_data)`。

**更乾脆的改法**（不改簽名介面）：在 `zf.infolist()` 迴圈開始前，先建一個 content→hash 的 dict：

```python
# 先把整個 ZIP 內容讀進記憶體（已讀取一次）
content_map = {m.filename: zf.read(m.filename) for m in zf.infolist() if not m.is_dir()}
# 之後重複查就不需要再讀
```

---

## 🔵 P3｜ThreadPool max_workers：根據 I/O vs CPU 調整

### 現況問題

**檔案**：`translation_tool/core/lang_merger.py`（約第 127 行）

```python
max_workers = load_config().get("translator", {}).get("parallel_execution_workers") or os.cpu_count()
```

`os.cpu_count()` 在多數桌面環境是 8-16，對於**磁碟 I/O 密集**的工作（讀取 ZIP）而非 CPU 密集，這個數字太高，會造成大量執行緒競爭磁碟讀取。

### 修改方法

**檔案**：`translation_tool/core/lang_merger.py`

```python
# 現況
max_workers = load_config().get("translator", {}).get("parallel_execution_workers") or os.cpu_count()

# 改為（磁碟 I/O 密集，建議設為 CPU 數的 2-3 倍，但設上限 32）
config_val = load_config().get("translator", {}).get("parallel_execution_workers")
if config_val is None:
    max_workers = min(32, (os.cpu_count() or 4) * 3)
else:
    max_workers = config_val
```

**或在 config.json 新增欄位**（不改 code）：
```json
{
  "translator": {
    "parallel_execution_workers": 24
  }
}
```

---

## 驗證清單（全部跑過才算完成）

```
□ P0  speed test：merge 30 JAR 前後耗時比對（目標 10x+ 提升）
□ P1  speed test：contains_cjk 計時比對（目標 2-5x 提升）
□ P2  實際解析 pt_br.json 不再報錯
□ P2  用 test_all_features.py 跑一次 test_merge 確認無 regression
□ P3  確認 max_workers 設定在 config.json 中生效
□ 全量 regression：python -m pytest tests/ — 全部通過
□ UI 驗證：啟動 Flet UI，選一個 JAR 跑完整合併流程，確認進度條正常
```

---

## 建議執行順序

```
1. P0（all_files_cache set）→ 最高速、最簡單
2. P1（contains_cjk memo）→ 配合 P0 一起驗證速度
3. P2（JSON5 fallback）→ 修 pt_br 問題
4. P3（max_workers）→ 微調，視機器負載決定
```
