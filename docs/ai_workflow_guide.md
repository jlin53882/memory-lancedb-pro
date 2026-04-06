# AI 工作流程助手指南

> 版本：2026-03-18  
> 適用：OpenClaw Main Agent  
> 情境：家豪叫我稽核專案時的指導原則

---

## 一、專案背景

### 1.1 我負責的專案

| 專案 | 路徑 | 技術棧 |
|------|------|--------|
| Minecraft Translator Flet | `C:\Users\admin\Desktop\minecraft_translator_flet` | Flet 0.28.3 + Python |
| Stock Trading | `C:\Users\admin\Desktop\Stock_trading` | Python + Yahoo API + Gemini API |

### 1.2 專案稽核重點

| 項目 | 檢查方式 |
|------|----------|
| Bare except | `rg "except:" --glob "*.py"` |
| API Key 硬編碼 | `rg "password\|api_key\|secret" --glob "*.py"` |
| Hardcoded 路徑 | `rg "C:\\\\\\\\"` |
| 測試覆蓋 | `uv run pytest --collect-only` |
| 未使用函數 | AST 分析 + 交叉驗證 |

---

## 二、6 大核心原則

### 原則 1：驗證優先於假設

```
❌ 「應該是...」
❌ 「通常這種情況是...」

✅ 用工具驗證事實
✅ 不確定時說「推測」
```

### 原則 2：依賴用 uv 處理

```
✅ uv sync              # 同步依賴
✅ uv run python       # 執行
❌ pip install         # 破壞環境
```

### 原則 3：修改前必備份

```
✅ cp config.json config.json.bak
✅ 先備份再改動
```

### 原則 4：測試是最終驗證

```
任何修改後：
✅ uv run pytest
✅ python -m py_compile <file>
```

### 原則 5：批次修改的風險 ⚠️

```
❌ 避免用批次腳本修改 Python
   - f-string、正則容易被破壞
   - 難以調試

✅ 正確方式：
   每次只改 1-2 處
   改完立即 py_compile 驗證
```

### 原則 6：回報要有結構

```
在 Discord 回報時：
- 做了什麼（具體動作）
- 關鍵決策（為什麼這樣做）
- 結果（測試數據）
- 建議下一步
```

---

## 三、常見任務流程

### 3.1 專案稽核流程

```
1. 探索結構
   → Get-ChildItem -Recurse -Filter "*.py"
   → 列出目錄組織

2. 靜態分析
   → rg 搜尋關鍵字
   → AST 分析函數

3. 問題檢查
   → Bare except
   → API Key 硬編碼
   → Hardcoded 路徑

4. 依賴檢查
   → uv run pytest --collect-only

5. API 驗證
   → import 模組測試
   → hasattr() 檢查

6. 測試驗證
   → uv run pytest -q
```

### 3.2 程式修改流程

```
1. 閱讀理解
   → read 工具完整讀取
   → 理解邏輯

2. 備份
   → Copy-Item file.py file.py.bak

3. 小幅修改
   → 每次 1-2 處

4. 驗證
   → python -m py_compile <file>
   → uv run python <file>
   → pytest

5. Git + 回報
```

### 3.3 環境設定流程

```
1. 確認版本
   → uv python list
   → pyproject.toml requires-python

2. 建立環境
   → uv python pin <版本>
   → uv sync

3. 驗證
   → import 關鍵模組
   → pytest 確認
```

---

## 四、驗證 SOP

### 4.1 語法驗證

```bash
# 單一檔案
python -m py_compile <file>.py

# 多個檔案
python -m py_compile file1.py file2.py file3.py
```

### 4.2 執行驗證

```bash
# 直接執行
uv run python <file>.py

# 模組測試
uv run python -c "import <module>"
```

### 4.3 測試驗證

```bash
# 收集測試
uv run pytest --collect-only

# 執行測試
uv run pytest -q

# 執行特定測試
uv run pytest tests/<file>.py -v
```

---

## 五、GitHub PR 自動化

### 5.1 常用指令

```bash
# 查詢狀態
gh status

# 建立 PR
gh pr create --title "..." --body "..."

# 查看 PR
gh pr view <number>

# 追蹤 Issue
gh issue list --repo <owner/repo>
```

### 5.2 Issue 追蹤

```
gh-issues skill 可用：
  --repo "owner/repo"
  --label bug
  --limit 5
  --milestone v1.0
```

---

## 六、溝通原則

### 6.1 語言

- 使用**繁體中文**
- 技術術語保留原文

### 6.2 風格

- 直接、簡潔
- 先給結論，再補充細節
- 不說「當然」「很好」這類廢話

### 6.3 等待指令

- 等待明確指令才執行
- 不自己亂改

### 6.4 回報格式

```
📋 任務摘要
- 做了什麼
- 關鍵決策
- 結果
- 下一步建議
```

---

## 七、常用指令速查

### 7.1 uv / Python

| 任務 | 指令 |
|------|------|
| 安裝依賴 | `uv sync` |
| 執行 | `uv run python <file>` |
| 確認版本 | `uv python list` |
| 語法檢查 | `python -m py_compile <file>` |

### 7.2 搜尋

| 任務 | 指令 |
|------|------|
| 搜尋程式碼 | `rg "pattern" --glob "*.py"` |
| 搜尋並列行號 | `rg -n "pattern" --glob "*.py"` |
| 排除資料夾 | `rg "pattern" --glob "!node_modules"` |

### 7.3 檔案

| 任務 | 指令 |
|------|------|
| 列出檔案 | `Get-ChildItem -Recurse -Filter "*.py"` |
| 備份 | `Copy-Item file.py file.py.bak` |
| 讀取 | `Get-Content <file>` |

### 7.4 Git

| 任務 | 指令 |
|------|------|
| 狀態 | `git status` |
| 新增 | `git add .` |
| 提交 | `git commit -m "..."` |
| 推送 | `git push` |

---

## 八、其他重要知識

### 8.1 常見問題修復

| 問題 | 修復方式 |
|------|----------|
| Log 不寫入 | config.py 新增 log_print/log_error/log_warning |
| API Key 硬編碼 | 改為 os.getenv() + .env |
| Bare except | 改為 except Exception as e: |
| API 回傳類型不穩定 | 新增 safe_get_first() 函數 |

### 8.2 日誌函數模板

```python
# config.py

def log_error(module: str, message: str):
    logger = get_logger(module)
    logger.error(message)

def log_warning(module: str, message: str):
    logger = get_logger(module)
    logger.warning(message)

def log_info(module: str, message: str):
    logger = get_logger(module)
    logger.info(message)

def log_print(module: str, message: str):
    print(message)
    logger = get_logger(module)
    logger.info(message)
```

### 8.3 安全原則

- 不外洩私密資料
- 破壞性操作先確認
- 不確定就先問

### 8.4 Flet 設計規則（2026-03-18 教訓）

#### Flet 設計前檢查清單
```
□ 讀 FLET_FIXES.md
□ 讀 flet-ui-0283-design-audit.md
□ 搜尋現有程式碼確認模式
□ 驗證 API 存在性
```

#### 設計稿產出清單
```
□ 每個類別的 super().__init__() 在最後
□ 用 self._page_ref 而非 self.page（避免觸發 framework property）
□ 所有定義的屬性有讀寫
□ import 的模組有使用
□ 寫完後 py_compile 驗證
```

#### 同步/非同步確認
```
□ 搜尋現有程式碼用 threading 還是 asyncio
□ 不要假設，用證據說話
```

#### 常見錯誤避免

| 錯誤 | 避免方式 |
|------|----------|
| 捏造 API | 先用 `python -c "import flet as ft; print('xxx' in dir(ft.Page))"` 驗證 |
| super() 前存取 self.page | 用 `self._page_ref` 暫存，super() 後再用 |
| 死碼 | 定義的屬性一定要有讀寫 |
| 方法放錯類別 | 每複製一個方法，確認它屬於哪個類別 |

### 8.5 程式碼修改規則（Stock Trading 教訓）

#### 禁止批次文字替換
```
❌ 禁止：用 sed/replace 批次替換 Python 程式碼
✅ 允許：用正規表示式 + 測試
✅ 允許：用 AST 分析 + 程式化修改
✅ 允許：手動修改關鍵檔案
```

#### 任何修改後必驗證
```
修改前 → 備份
修改後 → python -m py_compile 驗證
驗證失敗 → 立即還原
```

#### 日誌函數標準
```
✅ log_error(module, message)   - 錯誤
✅ log_warning(module, message) - 警告
✅ log_info(module, message)    - 資訊
✅ log_print(module, message)   - 輸出+記錄
```

---

*本指南基於 2026-03-18 實戰經驗撰寫*
*未來處理稽核任務時依此執行*
