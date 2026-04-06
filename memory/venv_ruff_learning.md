# Ruff 套件學習筆記

> 來源：Minecraft_translator_flet venv  
> 版本：0.15.5  
> 日期：2026-03-15

---

## 套件概述

Ruff 是一個**極速的 Python linter 與 code formatter**，核心由 Rust 寫成。這個 Python 套件只是一個**包裝器**，用於找到並執行 Rust 二進制檔案。

- **官網**：https://docs.astral.sh/ruff/
- **GitHub**：https://github.com/astral-sh/ruff
- **支援 Python**：3.7 ~ 3.14

---

## 模組結構

```
ruff/
├── __init__.py        # 導出 find_ruff_bin
├── __main__.py        # 命令行執行入口 (_run)
└── _find_ruff.py     # 核心：尋找 ruff 二進制檔案
```

---

## 主要 API

### 1. find_ruff_bin() → str

**用途**：找出 ruff 二進制執行檔的路徑

```python
from ruff import find_ruff_bin

ruff_path = find_ruff_bin()  # 例如：C:\Users\admin\Desktop\...\\ Scripts\\ruff.exe
```

**實作邏輯**（`_find_ruff.py`）：
1. 构造ruff_exe名稱（Windows: `ruff.exe`，Unix: `ruff`）
2. 按優先順序搜尋以下位置：
   - 目前Python的scripts目錄
   - base_prefix的scripts目錄
   - 套件根目錄的上層（`Lib/site-packages/ruff` → `Scripts`）
   - 套件根目錄的相鄰目錄（`ruff/bin`）
   - 使用者個人目錄（`~/.local/bin`）
3. 若都找不到，拋出 `RuffNotFound`

---

### 2. RuffNotFound

**用途**：找不到 ruff 二進制檔案時拋出的例外

```python
from ruff._find_ruff import RuffNotFound

try:
    ruff_path = find_ruff_bin()
except RuffNotFound as e:
    print(e)  # 顯示所有搜尋過的路徑
```

---

### 3. 命令列執行（__main__.py）

**用途**：直接執行 `python -m ruff` 時的入口

```python
# 內部邏輯
def _run() -> None:
    ruff = find_ruff_bin()
    if sys.platform == "win32":
        subprocess.run([ruff, *sys.argv[1:]])
    else:
        os.execvp(ruff, [ruff, *sys.argv[1:]])
```

---

## 內部函數（_find_ruff.py）

| 函數 | 簽名 | 說明 |
|------|------|------|
| `_module_path()` | `() → str \| None` | 取得目前套件路徑 |
| `_matching_parents(path, match)` | `(str \| None, str) → str \| None` | 從路徑末端移除匹配的目錄部分 |
| `_join(path, *parts)` | `(str \| None, *str) → str \| None` | 安全地連接路徑 |
| `_user_scheme()` | `() → str` | 取得使用者目錄配置（`nt_user` / `posix_user` / `osx_framework_user`） |

---

## 重點筆記

1. **這個套件只是包裝**：真正的 linter 邏輯在 Rust 二進制檔案中，Python 層只負責找到並呼叫它
2. **跨平台路徑處理**：
   - Windows：搜尋 `Scripts` 目錄
   - Unix：搜尋 `bin` 目錄
3. **多種安裝情境支援**：
   - pip install
   - uv run --with
   - pip install --target

---

## 使用情境

如果你需要在 Python 程式裡呼叫 ruff：

```python
import subprocess
from ruff import find_ruff_bin

def run_ruff_check(path: str) -> subprocess.CompletedProcess:
    """執行 ruff linter 檢查"""
    ruff_bin = find_ruff_bin()
    return subprocess.run([ruff_bin, "check", path])

def run_ruff_format(path: str) -> subprocess.CompletedProcess:
    """執行 ruff 格式化"""
    ruff_bin = find_ruff_bin()
    return subprocess.run([ruff_bin, "format", path])
```
