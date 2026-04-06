# PR #246 測試環境建立報告

> 建立日期：2026-04-02
> 任務：建立 `memory-lancedb-pro-import-markdown-test` 測試環境

---

## 1. DB 位置確認

### LanceDB 來源位置

| 項目 | 內容 |
|------|------|
| **路徑** | `C:\Users\admin\.openclaw\memory\lancedb-pro-jina1024` |
| **Table 名稱** | `memories` |
| **總筆數** | 5,140 rows |
| **Vector 維度** | 1024（Jina v3 embeddings）|
| **Schema** | `id`, `text`, `vector[1024]`, `category`, `scope`, `importance`, `timestamp`, `metadata` |
| **總大小** | 7,100 MB（7.1 GB）|

### 為何採樣而非完整複製

原始 DB 為 **7.1 GB**，完整複製耗時且浪費資源。採用隨機採樣 500 筆（seed=42）建立測試 DB，足以覆蓋所有主要欄位類型與向量維度。

---

## 2. 測試資料庫（`.testdb/`）

### 建立方式

使用 Python `lancedb` + `pyarrow` 從原始 DB 中隨機採樣：

```python
# 流程
1. lancedb.connect(SRC) - 開啟原始 DB
2. src_table.to_arrow() - 載入完整 Arrow Table（5,140 rows）
3. np.random.choice(5140, size=500) - 隨機抽 500 筆（seed=42）
4. arrow_table.take(indices) - PyArrow take() 取出樣本
5. lancedb.connect(DST) - 建立新 DB
6. dst_db.create_table("memories", sampled_table) - 寫入
```

腳本位置：`scripts/create_test_db.py`

### 結果

| 項目 | 內容 |
|------|------|
| **目標路徑** | `C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test\.testdb` |
| **筆數** | 500 rows |
| **大小** | 2.57 MB |
| **Vector 維度** | 1024 |
| **耗時** | 1.4 秒 |
| **可重現性** | seed=42，每次執行結果相同 |

### 驗證

```python
# 第一筆記錄範例
id: 8469c17f-e062-4641-90df-0680ec6b9866
text: 132 chars
vector: [float x 1024]
```

---

## 3. Memory 資料複製

### 來源

| 項目 | 內容 |
|------|------|
| **路徑** | `C:\Users\admin\.openclaw\workspace\memory\` |
| **總檔案數** | 790 個檔案（含子目錄）|
| **總大小** | 9.33 MB |
| **副檔案** | `.md`, `.json`, `.jsonl`, `.html`, `.py` |

### 子目錄結構

```
memory/
  backups/
  english_vocab/
  evolution/
  reflect/
  reflections/
  reports/
  self-audit/
  self-improvement/
  stock_analysis/
  watchers/
```

### 複製後

| 項目 | 內容 |
|------|------|
| **目標路徑** | `C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test\.openclaw\memory\` |
| **總檔案數** | 790 個檔案 |
| **總大小** | 9.33 MB |
| **複製完整性** | 完全一致 |

---

## 4. 測試環境目錄結構

```
memory-lancedb-pro-import-markdown-test/
  .github/                  # GitHub workflows
  .openclaw/
    memory/               # 已複製（790 檔案, 9.33 MB）
  .testdb/                  # 已建立（500 筆, 2.57 MB）
    memories.lance/
      _transactions/
      _versions/
      data/
        lance data files
  docs/
  examples/
  memory-lancedb-pro-1.1.0-beta.10/
  scripts/
    create_test_db.py    # 新增：建立測試 DB 腳本
  skills/
  src/                      # 主要 TypeScript 原始碼
  test/
```

---

## 5. 快速啟動指令

### 重新建立測試 DB（Python）

```bash
cd C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test
python scripts\create_test_db.py
```

### 使用 Node.js 測試

```bash
node test_lancedb.mjs
# 修改 DB_PATH 指向 .testdb 可測試新 DB
```

### 驗證 Memory 檔案

```bash
# 確認檔案數量
Get-ChildItem .openclaw\memory -Recurse -File | Measure-Object
# 預期：790 個檔案
```

---

## 6. 環境狀態摘要

| 元件 | 狀態 | 來源到目標 | 大小 |
|------|------|-----------|------|
| LanceDB (memories) | 完成 | `memory\lancedb-pro-jina1024` to `.testdb` | 2.57 MB（採樣 500/5140 rows）|
| Memory Markdown 檔案 | 完成 | `workspace\memory` to `.openclaw\memory` | 9.33 MB（790 檔案）|
| 測試腳本 | 已建立 | scripts/create_test_db.py | - |
| 環境報告 | 已產出 | memory/pr246-test-env-setup.md | - |

---

## 7. 已知限制

1. **測試 DB 為採樣**：500 筆可能不足以覆蓋所有邊界情況
2. **Vector 維度固定**：僅支援 1024 維（Jina v3），若要測試其他 embedding 模型需要重新建立
3. **Scope/Category 多樣性**：實際資料中 scope/category 分佈需進一步確認
