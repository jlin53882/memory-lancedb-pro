# minecraft_translator_flet — Minecraft 翻譯工具

> 讓任何 agent 拿到此檔後能立即上手。

---

## 基本資訊

| 項目 | 內容 |
|------|------|
| **GitHub** | `https://github.com/jlin53882/Minecraft-translate` |
| **本地路徑** | `C:\Users\admin\Desktop\minecraft_translator_flet` |
| **用途** | 將 Minecraft 模組包從簡體中文／英文批量翻譯為繁體中文（台灣用語） |
| **技術棧** | Python >= 3.12、Flet（桌面 GUI）、ftb-snbt-lib、Gemini API、OpenCC、pandas、SQLite FTS5 |
| **維運者** | James（家豪）/ jlin53882 |
| **目前版本** | v0.6.0 |
| **最近測試** | 834 passed（2026-03-16）|

---

## 專案結構

```
minecraft_translator_flet/
├── main.py                      # 應用程式入口（Flet Page 啟動）
├── app/
│   ├── services.py              # QC/checkers 所需 façade（非主線）
│   ├── services_impl/           # 主線 canonical services（PR28a/b 遷移完成）
│   │   ├── config_service.py
│   │   ├── logging_service.py
│   │   ├── cache/               # 快取服務（cache_services.py）
│   │   └── pipelines/           # 各類任務管線
│   │       ├── bundle_service.py
│   │       ├── extract_service.py
│   │       ├── ftb_service.py
│   │       ├── kubejs_service.py
│   │       ├── lm_service.py
│   │       ├── lookup_service.py
│   │       ├── md_service.py
│   │       ├── merge_service.py
│   │       ├── _pipeline_logging.py
│   │       └── _task_runner.py
│   ├── ui/
│   │   ├── components.py        # UI 元件抽取（PR68）
│   │   ├── theme.py             # 主題系統（PR69）
│   │   ├── view_wrapper.py
│   │   ├── keyboard_shortcuts.py
│   │   └── quick_jump.py
│   └── views/                   # 11 個主 View + 子模組
│       ├── config_view.py       # 設定
│       ├── rules_view.py        # 替換規則
│       ├── cache_view.py        # 快取管理（QueryPanel / ShardPanel）
│       ├── qc_view.py           # 品質檢查
│       ├── lookup_view.py       # 查詢
│       ├── icon_preview_view.py # 圖示預覽
│       ├── bundler_view.py      # 打包輸出 ZIP
│       ├── translation_view.py  # 翻譯任務（FTB / KubeJS / Markdown）
│       ├── extractor_view.py   # JAR 提取
│       ├── lm_view.py           # 機器翻譯（Gemini）
│       └── merge_view.py        # 檔案合併
│       # 子模組（views/ 下再細分）
│       ├── cache_manager/       # cache 子模組（panels/overview/query/shard）
│       ├── config/              # config 子模組（config_form/actions）
│       ├── extractor/           # extractor 子模組（extractor_panels/actions/state）
│       ├── rules/               # rules 子模組（rules_table/actions/state）
│       └── translation/         # translation 子模組（translation_panels/actions/state）
├── translation_tool/            # 核心翻譯邏輯（legacy, 仍被部分服務引用）
│   ├── core/
│   │   ├── lang_merger.py      # 語言檔合併核心
│   │   ├── lang_merge_*.py     # 合併策略模組
│   │   ├── lm_translator_main.py  # Gemini 批次翻譯主邏輯
│   │   ├── lm_translator_shared*.py  # 共用翻譯工具
│   │   ├── ftb_translator*.py  # FTB SNBT 翻譯
│   │   ├── kubejs_translator*.py  # KubeJS 翻譯
│   │   ├── md_translation*.py  # Markdown 翻譯
│   │   ├── jar_processor*.py   # JAR 檔處理
│   │   ├── output_bundler.py   # ZIP 打包
│   │   ├── icon_*.py           # 圖示解析
│   │   └── lm_api_client.py    # Gemini API 客戶端
│   ├── checkers/                # QC 檢查器
│   │   ├── untranslated_checker.py
│   │   ├── english_residue_checker.py
│   │   ├── color_char_checker.py
│   │   └── variant_comparator.py
│   ├── plugins/                 # 插件目錄（待確認用途）
│   └── utils/
│       └── cache_search.py      # SQLite FTS5 全文搜尋（2026-03-16 優化：49s→4s）
├── tests/                       # pytest 測試（834 個）
│   ├── conftest.py
│   ├── fixtures/                # 測試 fixture
│   └── test_*.py               # 單元/ characterization 測試
├── docs/
│   ├── pr/                     # PR 設計文件
│   ├── changelog/
│   └── *.md                    # 各種技術文件
├── config.example.json          # 設定範例
├── config.json                 # 實際設定（含 API Key，已加入 .gitignore）
├── pyproject.toml
├── uv.lock
└── ITERATION_SOP.md             # Claw 疊代作業標準流程

```

---

## 啟動方式

### 開發模式（從 repo 根目錄）

```powershell
cd C:\Users\admin\Desktop\minecraft_translator_flet

# 基本 smoke test
uv run python -c "import main; print('ok')"

# 全量測試（834 個）
uv run pytest -q
```

### 生產模式

```powershell
uv run python main.py
```

啟動後開啟 Flet 桌面 GUI，左側導覽列可切換 11 個功能頁面。

### 必要環境

- **Python**: >= 3.12
- **套件管理器**: `uv`（必要）
- **主要套件**（詳見 `pyproject.toml`）:
  - `flet[all]==0.28.3`（桌面 GUI）
  - `ftb-snbt-lib>=0.4.1`（SNBT 解析）
  - `google-genai>=1.56.0`（Gemini API）
  - `opencc-python-reimplemented>=0.1.7`（簡繁轉換）
  - `pandas>=2.3.3`
  - `orjson>=3.11.3`（高效 JSON）
  - `pytest>=9.0.2`
  - `wikipedia>=1.4.0`（生物學名查詢）

### 必要設定

```powershell
# 首次需複製設定檔
cp config.example.json config.json
# 編輯 config.json，填入 Gemini API Key
```

### ⚠️ Windows 環境注意

若遇到 `WinError 5`（使用者目錄快取/暫存權限），建議改用 repo 內路徑：

```powershell
$env:UV_CACHE_DIR = ".uv-cache"
$env:TMP = ".tmp"
$env:TEMP = ".tmp"
uv run pytest -q --basetemp=.pytest-tmp\full -o cache_dir=.pytest-cache\full
```

---

## 翻譯流程（核心）

### 主要處理階段（Pipeline Stages）

```
raw → clean → pending → translate → final
```

| 階段 | 說明 |
|------|------|
| **raw** | 從 JAR 提取的原始語言檔（en_us.json / zh_cn.json） |
| **clean** | 清理格式、標準化內容 |
| **pending** | 待翻譯條目（增量合併策略決定哪些需要翻） |
| **translate** | 透過 Gemini API 批次翻譯 |
| **final** | 最終產出（zh_tw.json、資源包 ZIP） |

### 語言合併邏輯（`lang_merger.py`）

依 `en_us.json` / `zh_cn.json` / `zh_tw.json` 組合決定合併策略：
- **JSON 語言檔**：增量更新（保留已翻譯內容）
- **內容檔（如 Patchouli）**：覆寫策略

### 支援的翻譯來源格式

| 格式 | 說明 |
|------|------|
| `lang/*.json` | Minecraft 標準語言檔 |
| `patchouli_books/` | Patchouli 手冊 JSON |
| `ftbquests/*.snbt` | FTB Quests 任務檔 |
| `kubejs/*.js` | KubeJS Tooltip 腳本 |
| `*.md` | Markdown 文件 |

### 快取機制

翻譯結果會寫入 SQLite FTS5 快取（`translation_tool/utils/cache_search.py`），支援：
- 全文搜尋
- 模糊比對
- 相似詞推薦
- 版本歷史

**2026-03-16 優化後**：重建時間 49秒 → 4秒（提升 91%）

---

## 重要模組

### 1. `app/services_impl/pipelines/` — 主線任務管線

所有主線業務邏輯集中於此（PR28a/b 遷移後的 canonical 位置）：

| 服務 | 職責 |
|------|------|
| `extract_service.py` | 從 JAR 檔提取語言資源 |
| `merge_service.py` | 語言檔智慧合併 |
| `lm_service.py` | Gemini 批次翻譯 |
| `ftb_service.py` | FTB SNBT 處理 |
| `kubejs_service.py` | KubeJS 翻譯 |
| `md_service.py` | Markdown 翻譯 |
| `bundle_service.py` | ZIP 資源包打包 |
| `lookup_service.py` | 快取查詢 |
| `_pipeline_logging.py` | 管線統一日誌 |
| `_task_runner.py` | 任務執行框架 |

### 2. `app/services.py` — QC façade

非主線，專為 QC/checkers 保留的 façade 層（PR29 收斂後定位），**不應引入新依賴**。

### 3. `translation_tool/core/lm_translator_main.py` — Gemini 翻譯核心

批次送 Gemini，依錯誤類型做：
- 縮批（split batch on error）
- 重試（retry）
- 換 Key（key rotation）
- 節流（throttle）

### 4. `translation_tool/utils/cache_search.py` — SQLite FTS5 全文搜尋

快取讀寫與搜尋，2026-03-16 重大優化（SQLite PRAGMA、WAL、ThreadPoolExecutor、批次大小 5000→20000）。

### 5. `translation_tool/checkers/` — 品管檢查器

| 檢查器 | 職責 |
|------|------|
| `untranslated_checker.py` | 偵測未翻譯條目 |
| `english_residue_checker.py` | 偵測英文殘留 |
| `color_char_checker.py` | 顏色字元檢查 |
| `variant_comparator.py` | 變體比對（TSV） |

### 6. `app/ui/theme.py` — 主題系統（PR69）

統一的 Flet 主題配置。

---

## 開發須知

### 已知坑

1. **Flet 0.28.3** 為固定版本，不建議任意升級
2. **Windows 路徑權限**：`WinError 5` 需設定環境變數繞過（如上方環境說明）
3. **`page.on_error` 無法捕獲 UI handler 異常**：UI handler 的例外不會被 page 錯誤處理捕獲
4. **破壞性失敗必須 raise**：`return {}` 會吞掉 exception，嚴禁使用
5. **Python 版本**：專案強制 >= 3.12，別在更低版本上測試
6. **中文檔案寫入**：大量中文寫入時用 `write` tool（自動 UTF-8），嚴禁 PowerShell redirect

### PR 流程（重要）

> 依據 `ITERATION_SOP.md`，所有含「開 PR / 走 PR 流程」的任務：

1. **接工作前先讀 `docs/AI_WORKFLOW_MANUAL.md`**（確認工作原則與驗證 SOP）
2. **先建立 feature branch**，確認乾淨的 parent commit
3. 在 branch 內完成所有實作與驗證
4. 確認所有變更都在 branch 上，再建立 PR
5. **嚴禁先在 main/commit 完成實作，再試圖補 PR**（force push 與歷史汙染）
6. PR merge 前嚴禁刪除 source branch

### 測試方式

```powershell
# smoke test
uv run python -c "import main; print('ok')"

# 全量測試（834 個）
uv run pytest -q

# 單一測試檔
uv run pytest tests/test_cache_store.py -v
```

### Lint / 程式碼風格

```powershell
uv run ruff check .
```

---

## 快速參考

### 常用指令

```powershell
# 安裝依賴
uv sync

# 啟動 GUI
uv run python main.py

# Smoke test
uv run python -c "import main; print('ok')"

# 全量測試
uv run pytest -q

# Lint
uv run ruff check .

# Windows 權限問題繞過
$env:UV_CACHE_DIR = ".uv-cache"; $env:TMP = ".tmp"; $env:TEMP = ".tmp"
uv run pytest -q --basetemp=.pytest-tmp\full -o cache_dir=.pytest-cache\full
```

### config.json 主要區塊

| 區塊 | 說明 |
|------|------|
| `logging` | 日誌等級與輸出目錄 |
| `translator` | 輸出資料夾、快取目錄、平行處理 worker 數 |
| `species_cache` | 生物學名快取（Wikipedia 查詢）|
| `lm_translator` | Gemini API Keys、模型設定、批次大小、System Prompt |
| `output_bundler` | 最終 ZIP 打包路徑 |
| `lang_merger` | 待翻譯與隔離資料夾命名 |

### 重要文件位置

| 檔案 | 用途 |
|------|------|
| `docs/PR_WORKFLOW.md` | PR 工作流說明 |
| `docs/ITERATION_SOP.md` | Claw 疊代作業標準流程 |
| `docs/pr/` | 各 PR 設計文件 |
| `docs/ROADMAP_CURRENT.md` | 目前 Roadmap |
| `docs/PROJECT_INDEX.md` | 專案文件索引 |

---

## 歷史參考（待確認）

- **PR28a/b**：主線 caller 遷移到 `app.services_impl.*`
- **PR29**：QC/checkers façade 收斂
- **PR62-71**：測試基礎設施、Docstring、UI 抽取、主題系統、廢棄清理
- **2026-03-16**：搜尋索引效能優化（49s → 4s）

---

*本文件由 agent 依據 2026-03-25 實際調查建立，若有資訊過時請更新。*
