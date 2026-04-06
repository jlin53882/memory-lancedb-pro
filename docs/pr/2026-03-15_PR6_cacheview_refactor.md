# PR #6：CacheView 重構拆分

## 1. 概述

將超過 2000 行的 CacheView 拆分成多個獨立模組，提升可維護性。

## 2. 設計目標

- 將 CacheView 拆分為多個 Panel
- 每個 Panel 控制在 300 行以內
- 採用 MVP 模式分離關注點
- 不改變現有功能

## 3. 實作方式

### 3.1 目錄結構

```
app/views/cache_manager/
├── __init__.py
├── cache_controller.py    # 協調器
├── cache_presenter.py    # 呈現邏輯
├── cache_state.py        # 狀態管理
├── panels/
│   ├── __init__.py
│   ├── overview_panel.py    # 總覽
│   ├── query_panel.py       # 查詢
│   ├── shard_panel.py       # 分片
│   └── history_panel.py     # 歷史
└── cache_actions.py         # 既有保留
```

### 3.2 MVP 模式

- **Model**: 資料結構定義
- **View**: 各 Panel UI
- **Presenter**: 業務邏輯

### 3.3 拆分原則

- 每個 Panel 負責一個主要功能區塊
- Panel 間透過 Controller 協調
- 保持現有的資料流不變

## 4. 驗收標準

- [ ] CacheView 程式碼行數減少至 800 行以內
- [ ] 各 Panel 獨立功能正常
- [ ] 現有操作不受影響
- [ ] 易於新增功能

## 5. 風險

- 拆分過程複雜 → 分多次 PR 逐步完成
- 現有功能破壞 → 每個拆分後進行完整測試
