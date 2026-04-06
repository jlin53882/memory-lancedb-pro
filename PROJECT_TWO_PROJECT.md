# two_project — Flet 桌面接案與練琴管理系統

## 基本資訊

| 欄位 | 內容 |
|------|------|
| **路徑** | `C:\Users\admin\Desktop\two_project` |
| **用途** | Windows 桌面應用，管理接案工作（Work）、練琴（Practice）、作品集（Portfolio）、報價單（Quote）、待辦（Todo），並提供 PDF/CSV 匯出功能 |
| **技術棧** | Flet 0.82.2（桌面 UI）、Python 3.12+、reportlab（PDF 匯出）、Pillow（圖片處理） |
| **依賴管理** | uv（`uv sync` 安裝，`uv.lock` 版本鎖定） |
| **維運者** | James（家豪） |
| **最後維護** | 2026-03-25 |

---

## 專案結構

```
C:\Users\admin\Desktop\two_project\
├── src/                          # 主要程式碼
│   ├── main.py                   # 入口點（呼叫 ft.run(main=run)）
│   ├── app.py                    # AppShell（AppBar + 底部導覽列 + content area）
│   ├── app_context.py
│   │
│   ├── views/                    # UI 頁面（5 個主要頁面）
│   │   ├── dashboard.py         # 總覽：行事曆、本週摘要、快捷新增
│   │   ├── work_view.py         # 工作管理：列表、篩選、Master-Detail
│   │   ├── quote_view.py        # 報價單：表單輸入 → 計算 → PDF/CSV 匯出
│   │   ├── portfolio_view.py    # 作品集：Grid 縮圖牆 + 圖片燈箱
│   │   └── practice_view.py      # 練習計時器 + 歷史記錄
│   │
│   ├── components/               # 可复用 UI 元件
│   │   ├── card.py              # 通用卡片樣式
│   │   └── nav_bar.py           # 底部導覽列元件
│   │
│   ├── controllers/              # 資料整理層（過濾/排序/分頁）
│   │   └── data_manager.py      # 管理各頁面的資料準備邏輯
│   │
│   ├── services/                 # 跨頁商業流程
│   │   ├── quote_service.py     # 報價計算 + Snapshot 機制
│   │   ├── portfolio_service.py # 作品集圖片處理（縮圖/複製）
│   │   ├── practice_service.py  # 練習記錄 CRUD
│   │   └── migration_service.py  # 資料遷移工具
│   │
│   ├── repositories/             # 資料存取層（統一路由）
│   │   └── records_repo.py      # 讀寫 records.json，隔離 UI 與儲存
│   │
│   ├── models/                   # 領域模型（資料結構定義）
│   │   ├── work.py
│   │   ├── portfolio.py
│   │   ├── music.py
│   │   └── course.py
│   │
│   ├── infra/                    # 基層設施（與框架無關）
│   │   └── json_store.py        # atomic write + file lock 實作
│   │
│   ├── state/                    # 全域 UI 狀態
│   │   └── ui_feedback.py       # SnackBar / busy state 統一管理
│   │
│   ├── theme/                    # 主題樣式
│   │   ├── colors.py            # 色彩定義（PRIMARY 等）
│   │   └── tokens.py            # token/size/spacing 等
│   │
│   ├── utils/                    # 工具函式
│   │   ├── async_runner.py      # 背景任務標準化（非同步 + page.call_from_thread）
│   │   ├── responsive.py        # 響應式佈局（桌面 ≥1000px vs App <1000px）
│   │   ├── debug_overlay.py     # 開發用除錯浮層
│   │   ├── debug_trace.py       # 追蹤工具
│   │   └── error_log.py         # 錯誤日誌
│   │
│   └── data/                     # 資料檔案（JSON + 圖片）
│       ├── records.json         # 主資料庫（含 file lock）
│       ├── records.lock         # 鎖檔
│       ├── records.json.lock
│       └── picture/
│           ├── originals/        # 原始圖片
│           └── thumbs/          # 縮圖（Grid 只讀這個）
│
├── tests/                        # 測試（pytest）
│   ├── conftest.py
│   ├── repositories/
│   │   ├── test_data_manager.py
│   │   └── test_records_repo.py
│   ├── services/
│   │   ├── test_portfolio_service.py
│   │   ├── test_practice_service.py
│   │   └── test_quote_service.py
│   └── views/
│       ├── test_dashboard_view.py
│       ├── test_portfolio_view.py
│       ├── test_practice_view.py
│       ├── test_quote_view.py
│       └── test_work_view.py
│
├── docs/                         # 規格文件
│   ├── PROJECT_INDEX.md          # 專案索引
│   ├── SPEC_v3.md                # 詳細規格文件
│   ├── UI_DESIGN_v2.md           # UI 設計規範
│   └── flet_rules.md             # Flet 開發規範
│
├── scripts/                       # 工具腳本
├── assets/                        # 靜態資源
├── exports/                       # 匯出檔案（PDF/CSV）
├── pyproject.toml                # 專案設定（uv）
├── uv.lock                       # 依賴版本鎖
├── .python-version               # Python 版本指定
├── README.md                     # 主專案文件
└── run.log                      # 執行日誌
```

---

## 啟動方式

### 開發模式（推薦）

```bash
# 在專案根目錄執行
cd C:\Users\admin\Desktop\two_project
uv sync              # 安裝/更新依賴（若未執行過）
uv run src/main.py   # 啟動應用程式
```

### 生產模式

```bash
uv run python -m flet run src/main.py --production
```

### 必要環境

| 項目 | 版本 |
|------|------|
| Python | ≥ 3.12 |
| Flet | 0.82.2 |
| 關鍵依賴 | reportlab≥4.4.7, pillow≥10.4.0 |
| 工具 | uv（依賴管理）|

---

## 核心概念

### 這個工具做什麼？

一個 Windows 桌面應用，幫助自由接案者（家豪）管理日常工作與練習記錄：

1. **工作（Work）**：記錄接案工作項目（日期、名稱、類型、金額）、支援篩選與列表/卡片檢視
2. **練習（Practice）**：鋼琴練習計時器 + 歷史記錄
3. **作品集（Portfolio）**：圖片作品記錄，含自動縮圖 + 原圖燈箱
4. **報價（Quote）**：表單化報價單輸入 → 計算建議價/最低價 → PDF/CSV 匯出（背景執行不卡 UI）
5. **總覽（Dashboard）**：行事曆、本週摘要、快捷新增待辦/工作

### 主要使用流程

```
啟動 → AppShell（底部導覽列固定）
  ├── 總覽：看今日/本週摘要
  ├── 工作：新增/檢視/篩選案件
  ├── 報價：填表 → 算價 → 匯出 PDF/CSV
  ├── 作品集：上傳圖片 + 瀏覽 Grid
  └── 練習：開始計時 → 結束 → 自動儲存
```

### 重要資料結構

**records.json** 根結構（由 `RecordsRepo` 統一管理）：

```json
{
  "works":    [...],
  "practice": [...],
  "portfolio": [...],
  "todos":   [...],
  "quotes":  [...],
  "settings": {
    "quote": {
      "tax_rate": 0.0,
      "deposit_rate": 0.3
    }
  }
}
```

**Quote Snapshot 機制**（不可變舊報價）：
- `input_snapshot`：建立時的輸入值
- `pricing_snapshot`：建立時的計價規則
- `result_snapshot`：計算後的結果
- 舊 Quote 永遠唯讀，設定改動只影響新 Quote

---

## 架構分層（由上到下）

```
views/          → UI 層（ft.Control），只負責「呈現」與「觸發動作」
controllers/    → 資料整理（過濾/排序/分頁）
services/       → 跨頁商業邏輯（Quote 計算、Portfolio 圖片處理）
repositories/   → 統一資料存取（RecordsRepo，隔離 JSON）
infra/          → 底層設施（JsonStore：atomic write + file lock）
```

### 關鍵模組

| 模組 | 職責 | 溝通對象 |
|------|------|---------|
| `AppShell` | 頁面框架（AppBar + NavBar）| 所有 views |
| `RecordsRepo` | JSON 讀寫，隔離資料存取 | services / controllers |
| `JsonStore` | atomic write + file lock | RecordsRepo |
| `QuoteService` | 報價計算 + Snapshot | views/quote_view |
| `PortfolioService` | 圖片縮圖/複製 | views/portfolio_view |
| `async_runner` | 背景任務統一化 | 所有 views 的耗時操作 |

---

## 響應式設計（寬度分級）

| 視窗寬度 | 模式 | 行為 |
|---------|------|------|
| < 1000px | App 模式 | 單欄、大卡片、觸控友善 |
| ≥ 1000px | 桌面模式 | 卡片縮排、inline 資訊、Master-Detail |

---

## 開發須知

### 已知的坑

1. **Flet 0.82.2 元件數量膨脹**：List/Grid 預設只渲染前 50/100 筆，其餘分頁或逐步載入（由 controller 先切資料）
2. **JSON 存取**：所有讀寫必須走 `RecordsRepo`，嚴禁 views 直接碰 JSON
3. **async_runner 必要性**：PDF 匯出、圖片複製/縮圖等耗時操作必須背景化，否則 UI 會卡住
4. **刪除無確認/Undo**：目前刪除直接生效，待補（Phase 3）
5. **編輯功能未完成**：目前只支援新增/刪除，待補編輯（Phase 3）
6. **圖片 Grid**：Portfolio 的 Grid 永遠只讀縮圖（`data/picture/thumbs/`），點擊才載原圖

### 開發規範

1. **禁止 views 直接碰 JSON**：一律透過 `RecordsRepo` 存取
2. **耗時操作必須背景化**：用 `async_runner`，禁止同步阻塞 UI thread
3. **刪除前先建立** `__pycache__` 備份：`*.py.bak` 檔案保留修改前版本
4. **檔案鎖定**：JSON 寫入時 `JsonStore` 自動處理 file lock，理論上不需手動管理
5. **桌面模式需支援鍵盤**：Tab 切欄位、Enter 確認、Esc 取消
6. **所有新增功能需先寫「Done 定義」與「不做清單」**

### Phase 進度（摘要）

| Phase | 內容 | 狀態 |
|-------|------|------|
| Phase 1 | UI 骨架、主題、桌面雙欄 | 部分完成 |
| Phase 2 | Repo 分層、非同步標準化、Quote Snapshot | 核心完成 |
| Phase 3 | 刪除撤銷、編輯、測試 | 待實作 |

---

## 快速參考

### 常用指令

```bash
# 安裝依賴
uv sync

# 啟動開發
uv run src/main.py

# 執行測試
cd C:\Users\admin\Desktop\two_project
python -m pytest tests/ -v

# 清除快取（懷疑問題來自快取時）
Remove-Item "C:\Users\admin\Desktop\two_project\src" -Recurse -Force -Include "__pycache__","*.pyc"
```

### 測試方式

```bash
cd C:\Users\admin\Desktop\two_project
python -m pytest tests/ -v
```

測試檔案位於 `tests/` 目錄，使用 `pytest` + `pytest-asyncio`。
`.venv` 內有完整套件，**全域環境沒有**，務必 `cd` 進專案後用 `uv run python -m pytest`。

### 除錯方法

1. **Debug Overlay**：`src/utils/debug_overlay.py` 可開啟除錯浮層
2. **錯誤日誌**：`run.log` 記錄執行期間的錯誤
3. **圖片問題**：確認 `data/picture/originals/` 與 `thumbs/` 兩目錄都存在且有權限
4. **JSON 鎖定**：若 `records.json.lock` 未正常刪除，程式可能無法啟動，手動刪除即可
5. **__pycache__ 問題**：測試失敗時先清除 `__pycache__`

### 切換視窗大小測試響應式

在 `app.py` 或 `main.py` 中手動調整 `ft.Page` 的初始寬度（預設 1280×960），
或拖曳視窗邊緣穿越 1000px 界線，驗證桌面/App 模式切換。

---

*文件版本：v1.0（2026-03-25）*
*建立者：Agent（doc-two-project-arch subagent）*
