# Task Board — Kanban + Dataview 設定指南

## 必要插件

1. **Kanban** — 社群插件，安裝後建立看板
2. **Dataview** — 社群插件，用於儀表板查詢

## 初始化任務看板

```bash
python scripts/setup_tasks.py /path/to/vault [--folder Tasks] [--columns "Backlog,Todo,In Progress,Review,Done"]
```

會建立：
- `Tasks/Board.md` — Kanban 看板
- `Tasks/Dashboard.md` — Dataview 儀表板

## Board.md 格式（Kanban 插件）

```markdown
---
kanban-plugin: basic
---

# 任務看板

## Backlog
- [ ] [[Task Title]] 🟢 P3 @{created-date}

## Todo
- [ ] [[Task Title]] 🟡 P2 @{created-date}

## In Progress
- [ ] [[Task Title]] 🔴 P1 @{created-date}

## Review
- [ ] [[Task Title]] 🔴 P1 @{due-date}

## Done
- [x] [[Task Title]] ✅ @{completed-date}
```

## 任務筆記格式

```markdown
---
status: todo
priority: P1
category: project
created: 2026-04-17
due: 2026-04-20
parked_until:
---

# 任務標題

詳細描述。

## 參考文獻
- [[相關筆記|顯示名稱]]

## 狀態
- [x] 子步驟完成
- [ ] 子步驟待處理
```

## Frontmatter 欄位

| 欄位 | 選項 | 必要 |
|------|------|------|
| status | backlog, todo, in-progress, review, done | ✅ |
| priority | P1, P2, P3 | ✅ |
| category | 任意文字 | ✅ |
| created | YYYY-MM-DD | ✅ |
| due | YYYY-MM-DD | ❌ |
| parked_until | YYYY-MM-DD | ❌ |

## Dataview 查詢

### 儀表板主查詢（全部未完成）
```dataview
TABLE status, priority, category, due
FROM "Tasks"
WHERE status != "done"
SORT priority ASC, due ASC
```

### 緊急任務（P1）
```dataview
TABLE status, category, due
FROM "Tasks"
WHERE priority = "P1" AND status != "done"
SORT due ASC
```

### 逾期任務
```dataview
TABLE priority, category
FROM "Tasks"
WHERE due AND due < date(today) AND status != "done"
SORT due ASC
```

### 最近完成
```dataview
TABLE category
FROM "Tasks"
WHERE status = "done"
SORT file.mtime DESC
LIMIT 10
```

### 依分類統計
```dataview
TABLE length(rows) AS count
FROM "Tasks"
GROUP BY category
```

## 看板同步規則

> ⚠️ **永遠同時更新 Board.md 和任務筆記 frontmatter**

1. **建立任務**：建立 `.md` 檔 + 在 Board.md 適當欄位新增一行
2. **移動任務**：更新 frontmatter `status` + 移動 Board.md 中的行
3. **完成任務**：設 `status: done` + 移到 Done 欄位 + 標記為 `[x]`

## 優先級對應

| 優先級 | 看板 Emoji | 意義 |
|--------|------------|------|
| P1 | 🔴 | 緊急，盡快處理 |
| P2 | 🟡 | 正常優先級 |
| P3 | 🟢 | 暫存/低優先級 |
