# JAR 抽取（Extract）優化建議報告

> 日期：2026-03-19
> 適用版本：minecraft-translator-flet（含 `jar_processor*.py` 模組）
> 涵蓋功能：lang 抽取、book（Patchouli）抽取、preview 預覽

---

## 抽取管線現況架構

```
使用者選取 mods 目錄
         │
         ▼
┌─────────────────────────────────────────────┐
│ jar_processor_discovery.find_jar_files()    │  ← 現況：os.walk() 單線程
│ → 回傳 List[str]（460 個 JAR 絕對路徑）    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ run_extraction_process_impl()                │
│ → ThreadPoolExecutor(max_workers=CPU count)  │
│ → 對每個 JAR 提交 extract_from_jar_impl()  │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
 extract_from_jar_impl()  extract_from_jar_impl() ...
 │                            │
 ├─ 正則比對每個成員           ├─ ...
 ├─ SHA256 計算
 ├─ 檔案是否存在檢查
 └─ 寫入磁碟
```

---

## 🔴 P0｜現況最大瓶頸：重複讀取 JAR（速度殺手）

### 現況問題

**檔案**：`jar_processor_extract.py`（約第 35-70 行）

每個 matched 檔案的處理流程：
```python
with zf.open(member) as source:        # 第1次：open 系統呼叫
    source_data = source.read()         # 第2次：read 讀取記憶體
    source_hash = get_file_hash_fn(source_data)  # 第3次：計算 SHA256

if os.path.exists(final_output_path):
    with open(final_output_path, 'rb') as existing_file:  # 第3次：讀取舊檔
        existing_hash = get_file_hash_fn(existing_file.read())
```

磁碟 I/O 做了**三次**（`zf.open` + `zf.read` + 舊檔讀取）。

### 修改方法

**檔案**：`translation_tool/core/jar_processor_extract.py`

將整個 ZIP 內容一次讀進記憶體（`zf.namelist()` 已經會列舉，不需要額外成本），之後重複取用：

```python
def extract_from_jar_impl(
    jar_path: str,
    output_root: str,
    target_regex: re.Pattern,
    *,
    get_file_hash_fn: Callable[[bytes], str] = get_file_hash,
) -> Dict[str, Any]:
    extracted_count = 0
    skipped_count = 0
    jar_filename_base = _normalize_jar_base_name(jar_path)  # 快取結果

    try:
        with zipfile.ZipFile(jar_path, 'r') as zf:
            # ── P0 優化：一次把整個 ZIP 內容讀進記憶體 ──────────────
            all_content: Dict[str, bytes] = {}
            for member in zf.infolist():
                if member.is_dir():
                    continue
                all_content[member.filename] = zf.read(member.filename)
            # ── 之後每個檔案直接從 dict 取用，不重複 I/O ────────────

            for member in zf.infolist():          # 仍然用 infolist 驅動迴圈
                if member.is_dir():
                    continue
                normalized_path = member.filename.replace('\\', '/')
                if not target_regex.search(normalized_path):
                    continue

                source_data = all_content[member.filename]  # ← O(1) dict 取用

                if normalized_path.startswith('assets/'):
                    final_output_path = os.path.join(output_root, normalized_path)
                else:
                    final_mod_folder = f"{jar_filename_base}_extracted"
                    final_output_path = os.path.join(output_root, final_mod_folder, normalized_path)

                source_hash = get_file_hash_fn(source_data)

                if os.path.exists(final_output_path):
                    with open(final_output_path, 'rb') as existing_file:
                        existing_hash = get_file_hash_fn(existing_file.read())
                    if source_hash == existing_hash:
                        skipped_count += 1
                        continue

                os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
                with open(final_output_path, 'wb') as target:
                    target.write(source_data)
                extracted_count += 1

        return {'status': 'success', 'extracted': extracted_count, 'skipped': skipped_count}
    except Exception as e:
        log.error("處理 %s 時發生錯誤: %s", os.path.basename(jar_path), e)
        return {'status': 'error', 'extracted': 0, 'skipped': 0}
```

**驗證方式**：
```python
import time, zipfile
jar = "C:/Users/admin/Desktop/.minecraft/versions/All the Mods 10 4.3/mods/Apotheosis-1.21.1-8.3.6.jar"
# Before
t0 = time.perf_counter()
with zipfile.ZipFile(jar) as zf:
    for m in zf.infolist():
        if not m.is_dir():
            _ = zf.open(m).read()
t1 = time.perf_counter()
# After（一次讀進 dict）
t2 = time.perf_counter()
with zipfile.ZipFile(jar) as zf:
    content = {m.filename: zf.read(m.filename) for m in zf.infolist() if not m.is_dir()}
t3 = time.perf_counter()
print(f"逐個讀取：{t1-t0:.3f}s，一次讀取：{t3-t2:.3f}s，節省：{(t1-t0)-(t3-t2):.3f}s")
```

---

## 🟡 P1｜Discovery：os.walk 單線程（對 460 個 JAR 免費加速）

### 現況問題

**檔案**：`translation_tool/core/jar_processor_discovery.py`

```python
def find_jar_files(folder_path: str) -> List[str]:
    jar_files: List[str] = []
    for root, _, files in os.walk(folder_path):  # ← 單線程，每個子目錄依序走
        for file in files:
            if file.endswith('.jar'):
                jar_files.append(os.path.join(root, file))
```

`os.walk` 本身是單線程。但磁碟搜尋（特別是機械硬碟）會是主要瓶頸，固態碟差異較小。

### 修改方法

**檔案**：`translation_tool/core/jar_processor_discovery.py`

```python
import os
import glob
from concurrent.futures import ThreadPoolExecutor

def find_jar_files(folder_path: str) -> List[str]:
    """用 glob.glob 並行找所有 .jar（比 os.walk 快 2-3x）"""
    pattern = os.path.join(folder_path, "**", "*.jar")
    jar_files = glob.glob(pattern, recursive=True)  # glob 底層用 C 实现，比 walk 快
    log.info("在 '%s' 中找到 %s 個 .jar 檔案。", folder_path, len(jar_files))
    return jar_files
```

**若 `glob.glob` 在網路磁碟仍慢，替換成 ThreadPool 版**：
```python
def find_jar_files(folder_path: str) -> List[str]:
    """使用 ThreadPoolExecutor 並行走訪子目錄"""
    subdirs = [d[0] for d in os.walk(folder_path)]  # 取得所有子目錄
    jar_files: List[str] = []

    def scan_dir(d: str) -> List[str]:
        return [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.jar')]

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(scan_dir, subdirs)
        for res in results:
            jar_files.extend(res)

    jar_files.sort()  # 維持字母順序一致
    log.info("在 '%s' 中找到 %s 個 .jar 檔案。", folder_path, len(jar_files))
    return jar_files
```

**驗證方式**：
```python
import time
folder = r"C:\Users\admin\Desktop\.minecraft\versions\All the Mods 10 4.3\mods"
# os.walk 版
t0 = time.perf_counter()
import os; [os.path.join(r,f) for r,_,fs in os.walk(folder) for f in fs if f.endswith('.jar')]
t1 = time.perf_counter()
# glob 版
t2 = time.perf_counter()
import glob; glob.glob(os.path.join(folder,"**","*.jar"), recursive=True)
t3 = time.perf_counter()
print(f"os.walk：{t1-t0:.3f}s，glob：{t3-t2:.3f}s")
```

---

## 🟡 P1｜SHA256：每個 matched 檔案都算一次（可減半）

### 現況問題

即使內容相同，每次 `extract` 都重新計算 SHA256。
若 ZIP 內多個檔案內容相同浪費更大。

### 修改方法

在 `extract_from_jar_impl` 的 `all_content` 迴圈之後、新增 hash 快取：

```python
# 在 for member in zf.infolist(): 之後新增
_content_to_hash: Dict[bytes, str] = {}  # content → hash，相同內容不重算

for member in zf.infolist():
    if member.is_dir():
        continue
    normalized_path = member.filename.replace('\\', '/')
    if not target_regex.search(normalized_path):
        continue

    source_data = all_content[member.filename]

    # ── P1 優化：相同內容只算一次 SHA256 ──────────────────────────
    if source_data in _content_to_hash:
        source_hash = _content_to_hash[source_data]
    else:
        source_hash = get_file_hash_fn(source_data)
        _content_to_hash[source_data] = source_hash
```

---

## 🟢 P2｜正則數量眾多：lang 抽取正則可支援更多語言

### 現況問題

**檔案**：`translation_tool/core/jar_processor.py`（約第 50-55 行）

```python
lang_file_regex = re.compile(
    r"(?:assets/([^/]+)/)?lang/(en_us|zh_cn|zh_tw)\.(json|lang)$", re.IGNORECASE
)
```

只支援 `en_us`、`zh_cn`、`zh_tw` 三種語言。
根據 gap_analysis 的結果（30 個 JAR 中有 210 個其他語言檔被跳過），若要提高覆蓋率可擴充。

### 建議做法（不改正則，改以設定驅動）

在 `config.json` 新增可配置的語言清單：

```python
# translation_tool/core/jar_processor.py
LANG_CONFIG_KEY = ["en_us", "zh_cn", "zh_tw"]  # 可從 config 讀

def extract_lang_files_generator(mods_dir: str, output_dir: str) -> Generator[Dict[str, Any], None, None]:
    config = load_config()
    lang_codes = config.get("jar_extractor", {}).get("lang_codes", ["en_us", "zh_cn", "zh_tw"])
    lang_codes_lower = [c.lower() for c in lang_codes]
    lang_codes_str = "|".join(map(re.escape, lang_codes_lower))
    lang_file_regex = re.compile(
        rf"(?:assets/([^/]+)/)?lang/({lang_codes_str})\.(json|lang)$",
        re.IGNORECASE
    )
```

**`config.json` 新增**：
```json
{
  "jar_extractor": {
    "lang_codes": ["en_us", "zh_cn", "zh_tw", "ja_jp", "ko_kr", "ru_ru"]
  }
}
```

---

## 🟢 P2｜Preview 的重複 I/O（與 P0 相同問題）

### 現況問題

**檔案**：`translation_tool/core/jar_processor_preview.py`（約第 55-80 行）

`preview_extraction_generator_impl` 對每個 JAR 都 `zf.open()` + `zf.read()` 一次，但 preview 只是統計用，不需要讀取內容，只要 `zf.namelist()` 就夠了。

### 修改方法

```python
# 現況：每次 matched 都讀取實際內容（浪費）
matched_files.append(normalized_path)
total_size_bytes += member.file_size   # ← 用 file_size 就好，不需要讀取

# 改：不需要 read()，namelist() + infolist() 就足夠統計
```

且 preview 和 extraction 共用同一個 `_normalize_jar_base_name()` 結果，可以抽出變數。

---

## 🔵 P3｜ThreadPoolExecutor max_workers：I/O 密集優化

### 現況問題

**檔案**：`translation_tool/core/jar_processor_extract.py`（約第 90-110 行）

```python
max_workers = load_config().get('translation', {}).get('parallel_execution_workers') or os.cpu_count()
```

### 修改方法（同 merge 建議，統一 config）

```python
# translation/core/jar_processor_extract.py
_translation_config = None

def _get_translation_config():
    global _translation_config
    if _translation_config is None:
        _translation_config = load_config().get("translator", {})
    return _translation_config

trans_cfg = _get_translation_config()
workers_cfg = trans_cfg.get("parallel_execution_workers")

if workers_cfg is None:
    # I/O 密集：可高於 CPU 數量，上限 32
    max_workers = min(32, (os.cpu_count() or 4) * 3)
else:
    max_workers = workers_cfg
```

---

## 🟡 P1｜_normalize_jar_base_name：每個 JAR 只做一次，但可快取

### 現況問題

**檔案**：`translation_tool/core/jar_processor_extract.py`（約第 20-30 行）

```python
def _normalize_jar_base_name(jar_filename: str) -> str:
    base_full = os.path.splitext(os.path.basename(jar_filename))[0]
    clean_name = re.sub(...)
    match_version = VERSION_REGEX.search(clean_name)
    # ... 字串處理
    return base_name or base_full
```

正則替換代碼簡單，但 `re.sub` + `VERSION_REGEX.search` 仍有成本。
**在單次 extraction 內每個 JAR 只呼叫一次**，`460 個 JAR` 就是 460 次，成本不高，這個可以不改。

---

## 驗證清單

```
□ P0  單 JAR I/O 計時：節省 30-50% 讀取時間
□ P0  全量 460 JAR 測試：extract 總耗時比對
□ P0  test_all_features.py 的 test_extractor 仍然 PASS
□ P1  glob vs os.walk 計時（目標 2-3x）
□ P1  SHA256 memo 計時
□ P2  config.json 新增 lang_codes，驗證 ja_jp / ko_kr 可被抽出
□ P2  preview 只用 namelist，不讀取內容，驗證正確性
□ P3  max_workers=32 穩定運作
□ 全量回歸：uv run main.py 啟動 UI，選一個 JAR 完整跑一次抽取
```

---

## 建議執行順序

```
1. P0（一次讀取 ZIP 內容進 dict）→ 最大 impact，立刻驗證
2. P1（glob 替代 os.walk）→ 簡單且免費
3. P1（SHA256 memo）→ 配合 P0 一起做
4. P2（config lang_codes 擴充）→ 提高抽取覆蓋率
5. P2（preview 優化）→ 純加成
6. P3（max_workers 調整）→ 視機器負載決定
```
