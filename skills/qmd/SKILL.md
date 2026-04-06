---
name: qmd
description: "本地知識庫搜尋引擎。使用 QMD (Query Markup Documents) 搜尋 workspace 中的 Markdown 文檔。支援三種模式：BM25 關鍵字搜尋（最快）、向量語意搜尋、混合搜尋+AI重排序（最準）。已索引 memory/、docs/、workspace/ 共 70+ 文檔。適用於查找過往筆記、技術文檔、決策記錄。"
---

# QMD - 本地知識庫搜尋

## 何時使用

- 查找過往筆記、決策、技術文檔
- 搜尋 Flet、two_project、minecraft_translator_flet 相關資料
- 查找 bug 修復記錄、SOP 文檔
- 檢索 memory/ 中的每日記憶

## 已索引的 Collections

- **memory** (10 檔案) — 每日記憶、決策記錄
- **docs** (11 檔案) — 技術文檔、SOP
- **workspace** (49 檔案) — 專案筆記、AGENTS.md、SOUL.md 等

## 三種搜尋模式

### 1. 關鍵字搜尋（最快，<1s）

**適用場景：**已知關鍵字、精確匹配

```bash
.\qmd.cmd search "關鍵字" -n 5
```

**範例：**
```bash
.\qmd.cmd search "Flet 灰畫面" -n 3
# 結果：flet-gray-screen-debug-checklist.md (87%)
```

---

### 2. 語意搜尋（中速，~3s）

**適用場景：**概念性查詢、不確定關鍵字

```bash
.\qmd.cmd vsearch "概念描述" -n 5
```

**範例：**
```bash
.\qmd.cmd vsearch "如何處理 UI 更新問題" -n 3
# 結果：reload-regression-sop.md (74%) — 自動理解語意
```

---

### 3. 混合搜尋 + AI 重排序（最準，~10-20s）

**適用場景：**重要查詢、需要最佳結果

```bash
.\qmd.cmd query "複雜問題" -n 5
```

**範例：**
```bash
.\qmd.cmd query "two_project 的 UI 重構規劃" -n 3
# 結果：memory/2026-02-13.md (75%) — AI 智能排序
```

---

## 常用指令

### 查看狀態
```bash
.\qmd.cmd status
```

### 列出 collections
```bash
.\qmd.cmd collection list
```

### 手動更新索引
```bash
.\qmd.cmd update
```

### 重建向量索引
```bash
.\qmd.cmd embed
```

### 獲取特定文檔
```bash
.\qmd.cmd get "memory/2026-02-13.md"
```

### 批量獲取（glob pattern）
```bash
.\qmd.cmd multi-get "memory/2026-02-*.md" -l 50
```

---

## 輸出格式

### 預設格式（片段 + 評分）
```bash
.\qmd.cmd search "query"
```

### JSON 格式（程式化處理）
```bash
.\qmd.cmd search "query" --json
```

### 僅文件列表（快速掃描）
```bash
.\qmd.cmd search "query" --files
```

### 完整內容（深入閱讀）
```bash
.\qmd.cmd search "query" --full
```

---

## 搜尋選項

| 選項 | 說明 | 範例 |
|------|------|------|
| `-n <數量>` | 返回結果數 | `-n 10` |
| `--min-score <分數>` | 最低相似度 | `--min-score 0.5` |
| `-c <collection>` | 僅搜尋特定 collection | `-c memory` |
| `--all` | 返回所有匹配（配合 --min-score） | `--all --min-score 0.3` |
| `--full` | 完整文檔內容 | `--full` |
| `--json` | JSON 輸出 | `--json` |
| `--files` | 僅文件路徑 | `--files` |

---

## 使用範例

### 查找 Flet 相關問題
```bash
.\qmd.cmd search "Flet 灰畫面 debug" -c docs -n 5
```

### 語意搜尋 UI 問題
```bash
.\qmd.cmd vsearch "如何解決 UI 不更新的問題" -n 5
```

### 查找近期決策（JSON 格式）
```bash
.\qmd.cmd query "two_project 重構決策" -c memory --json -n 5
```

### 獲取最近一週的記憶
```bash
.\qmd.cmd multi-get "memory/2026-02-*.md" --json
```

---

## 注意事項

1. **首次查詢會下載模型**（僅一次）：
   - Embedding 模型：328MB
   - Reranker 模型：1.28GB
   - Generation 模型：639MB

2. **速度對比**：
   - `search`：<1 秒
   - `vsearch`：~3 秒
   - `query`：~10-20 秒（首次較慢）

3. **自動更新**：
   - 每天早上 9:00 自動更新索引（cron job）
   - 手動更新：`.\qmd.cmd update`

4. **索引範圍**：
   - 當前索引：70 個文檔，82 個 chunks
   - 新增文檔後需要 `update` + `embed`

---

## 整合建議

### 與 memory_search 對比

| 功能 | memory_search | QMD |
|------|--------------|-----|
| 速度 | 快 | 中～慢 |
| 準確度 | 中 | 高 |
| 語意理解 | 基本 | 強 |
| AI 重排序 | ❌ | ✅ |
| 適用場景 | 快速召回 | 深度查詢 |

**建議策略：**
- 快速查詢 → 用 `memory_search`
- 重要查詢 → 用 QMD `query`
- 概念查詢 → 用 QMD `vsearch`

---

## 腳本位置

- **Wrapper 腳本**：`C:\Users\admin\.openclaw\workspace\qmd.cmd`
- **原始入口**：`C:\Users\admin\.bun\install\global\node_modules\qmd\src\qmd.ts`
- **索引資料庫**：`C:\tmp\.cache\qmd\index.sqlite`
- **模型快取**：`C:\Users\admin\.cache\qmd\models\`

---

## 更新日誌

- **2026-02-14**：初次安裝，建立 3 個 collections（memory、docs、workspace）
- **2026-02-14**：設定每日自動更新 cron job（9:00 AM）
- **2026-02-14**：整合到 OpenClaw skill 系統
