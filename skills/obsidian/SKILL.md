---
name: obsidian
description: Comprehensive Obsidian vault management via obsidian-cli. Covers vault discovery, daily notes, task management (Kanban + Dataview), note operations (create/search/move/delete), and two-way sync with obsidian-openclaw plugin. Use when working with Obsidian vaults, managing daily notes, creating task boards, or synchronizing notes with the AI workspace.
metadata:
  openclaw:
    emoji: "💎"
    requires:
      bins:
        - obsidian-cli
    install:
      - id: brew
        kind: brew
        label: Install obsidian-cli (macOS)
        formula: yakitrak/yakitrak/obsidian-cli
      - id: scoop
        kind: scoop
        label: Install obsidian-cli (Windows)
        bucket: https://github.com/yakitrak/scoop-obsidian-cli
        package: obsidian-cli
  config:
    VAULT_NAME:
      description: Obsidian vault name - set via obsidian-cli set-default
    ALLOWED_PATHS:
      description: Comma-separated whitelist of allowed folder paths. Agent will skip folders not in this list
    DAILY_FOLDER:
      description: Subfolder for daily notes. Leave empty for vault root
    TASKS_FOLDER:
      description: Subfolder for task board
---

# Obsidian Skill

Comprehensive Obsidian vault management. Obsidian vault = a normal folder on disk.

## ⚠️ Path Restriction (重要)

**Agent 只允許操作白名單中的路徑！**

設定 `ALLOWED_PATHS` 避免 agent 遍歷整個 vault：
- 格式：逗號分隔的資料夾名稱（如 `notes,memos,projects`）
- Agent 收到搜尋請求時，只在這些資料夾內搜尋
- 未設定時預設為全部資料夾

常見設定：
```
ALLOWED_PATHS=notes,daily,archive
DAILY_FOLDER=Daily Notes
TASKS_FOLDER=Tasks
VAULT_NAME=MyVault
```

## obsidian-cli Installation

**macOS:**
```bash
brew install yakitrak/yakitrak/obsidian-cli
```

**Windows (Scoop):**
```bash
scoop bucket add scoop-obsidian-cli https://github.com/yakitrak/scoop-obsidian-cli
scoop install obsidian-cli
```

**Verify:**
```bash
obsidian-cli --version
```

---

## Vault Discovery

### Find Active Vault

Obsidian tracks vaults in config. Read `obsidian.json` for the active vault:

**macOS:**
```bash
cat ~/Library/Application\ Support/obsidian/obsidian.json
```

**Windows:**
```bash
type "%APPDATA%\obsidian\obsidian.json"
```

Look for `"open": true` entry. Use that vault name.

### Set Default Vault

```bash
obsidian-cli set-default "VAULT_NAME"
obsidian-cli print-default --path-only  # verify
```

---

## Daily Notes

### Open/Create Today's Note

```bash
obsidian-cli daily
```

### Append Entry

```bash
obsidian-cli daily
obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "ENTRY_TEXT")" --append
```

### Read Daily Note

Today:
```bash
obsidian-cli print "$(date +%Y-%m-%d).md"
```

Yesterday:
```bash
obsidian-cli print "$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d).md"
```

### Date Formats

| Reference | Command |
|-----------|---------|
| Today | `date +%Y-%m-%d` |
| Yesterday | `date -d yesterday +%Y-%m-%d 2>/dev/null \|\| date -v-1d +%Y-%m-%d` |
| Last Friday | `date -d "last friday" +%Y-%m-%d 2>/dev/null \|\| date -v-friday +%Y-%m-%d` |
| 3 days ago | `date -d "3 days ago" +%Y-%m-%d 2>/dev/null \|\| date -v-3d +%Y-%m-%d` |

---

## Note Operations

### Create Note

```bash
obsidian-cli create "Folder/New note" --content "# Title\n\nContent here" --open
```

### Search Notes (Path Restricted)

**重要：Agent 必須尊重 `ALLOWED_PATHS` 設定！**

使用 `obsidian-cli search` 前，先確認查詢的資料夾在白名單內：
- ✅ 允許：`obsidian-cli search "query"` (預設 vault 範圍)
- ✅ 允許：手動指定白名單路徑搜尋
- ❌ 禁止：搜尋 vault 根目錄下所有非白名單資料夾

如果 vault 有多個資料夾但只有部分在白名單：
```bash
# 只搜尋允許的資料夾
obsidian-cli search-content "query" --path "notes/subfolder"
```

**當不確定路徑是否允許時，先問使用者確認。**

### Move/Rename (Safe Refactor)

```bash
obsidian-cli move "old/path/note" "new/path/note"
```
Automatically updates `[[wikilinks]]` and Markdown links across the vault.

### Delete

```bash
obsidian-cli delete "path/note"
```

---

## Task Management (Kanban + Dataview)

### Setup Task Board

Requires **Kanban** and **Dataview** Obsidian community plugins.

```bash
python scripts/setup_tasks.py <vault-path> [--folder Tasks] [--columns "Backlog,Todo,In Progress,Review,Done"]
```

This creates:
- `<folder>/Board.md` — Kanban board
- `<folder>/Dashboard.md` — Dataview dashboard

### Task Note Format

```markdown
---
status: todo
priority: P1
category: project
created: 2026-04-17
due: 2026-04-20
---

# Task Title

Description here.

## References
- [[supporting-note|Display Name]]
```

### Frontmatter Fields

| Field | Values | Required |
|-------|--------|---------|
| status | backlog, todo, in-progress, review, done | yes |
| priority | P1, P2, P3 | yes |
| category | free text | yes |
| created | YYYY-MM-DD | yes |
| due | YYYY-MM-DD | no |

### Move Tasks

Always update BOTH the task note frontmatter AND Board.md:
1. Set `status` in frontmatter
2. Move card line in Board.md to target column

### Priority Emoji on Board

- 🔴 P1 (urgent)
- 🟡 P2 (normal)
- 🟢 P3 (backlog)

### Dashboard Queries (Dataview)

```dataview
TABLE status, priority, due
FROM "Tasks"
WHERE status != "done"
SORT due ASC
```

```dataview
TABLE priority, category
FROM "Tasks"
WHERE due AND due < date(today) AND status != "done"
```

---

## Two-Way Sync (obsidian-openclaw)

Sync notes between Obsidian vault and AI workspace.

### Components

- **Backend**: `obsidian-sync` skill (sync-server.mjs)
- **Plugin**: [obsidian-openclaw](https://github.com/AndyBold/obsidian-openclaw) (Obsidian Community Plugin)

### Start Sync Server

```bash
SYNC_TOKEN="<gateway-token>" SYNC_WORKSPACE="<workspace-path>" node scripts/sync-server.mjs
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SYNC_PORT` | `18790` | Server port |
| `SYNC_BIND` | `localhost` | Bind address |
| `SYNC_WORKSPACE` | workspace root | Sync root |
| `SYNC_TOKEN` | (required) | Auth token |
| `SYNC_ALLOWED_PATHS` | `notes,memory` | Allowed subdirectories |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sync/status` | Health check |
| GET | `/sync/list?path=notes` | List markdown files |
| GET | `/sync/read?path=notes/x.md` | Read file + metadata |
| POST | `/sync/write?path=notes/x.md` | Write file |

### Install Obsidian Plugin

Via [BRAT](https://github.com/TfTHacker/obsidian42-brat):
1. Install BRAT community plugin
2. Add beta repo: `AndyBold/obsidian-openclaw`

### Expose via Tailscale

```bash
tailscale serve --bg --https=18790 http://localhost:18790
```

---

## Path Validation Helper

Agent 在執行任何搜尋或檔案操作前，應驗證路徑：

```python
# Python helper: 檢查路徑是否在白名單
def is_path_allowed(path: str, allowed_folders: list) -> bool:
    if not allowed_folders:  # 無白名單 = 全部允許
        return True
    for folder in allowed_folders:
        if folder in path:
            return True
    return False

# 使用範例
allowed = ["notes", "memos", "projects"]  # 從 ALLOWED_PATHS 讀取
path = "vault/notes/meeting.md"
if is_path_allowed(path, allowed):
    print("✅ 允許操作")
else:
    print("❌ 路徑不在白名單，拒絕操作")
```

## Detailed References

For detailed task setup script, Dataview queries, and sync server details, see:
- `references/daily-notes.md` — Full daily notes workflow
- `references/task-board.md` — Kanban + Dataview setup guide
- `references/sync-server.md` — Sync server configuration
