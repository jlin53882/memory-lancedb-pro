#!/usr/bin/env python3
"""
Obsidian Task Board 初始化腳本
建立 Kanban 看板 + Dataview 儀表板

用法:
    python setup_tasks.py <vault-path> [--folder <name>] [--columns "Backlog,Todo,In Progress,Review,Done"]
"""
import os
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Initialize Obsidian Task Board")
    parser.add_argument("vault_path", help="Path to Obsidian vault root")
    parser.add_argument("--folder", default="Tasks", help="Task folder name (default: Tasks)")
    parser.add_argument("--columns", default="Backlog,Todo,In Progress,Review,Done",
                        help="Comma-separated Kanban columns")
    args = parser.parse_args()

    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"ERROR: Vault path does not exist: {vault}", file=sys.stderr)
        sys.exit(1)

    task_dir = vault / args.folder
    task_dir.mkdir(exist_ok=True)
    print(f"[OK] Created folder: {task_dir}")

    columns = [c.strip() for c in args.columns.split(",")]

    # === Board.md ===
    board_lines = [
        "---",
        "kanban-plugin: basic",
        "---",
        "",
        f"# {args.folder} Board",
        "",
    ]
    for col in columns:
        board_lines.append(f"## {col}")
        board_lines.append("")
        board_lines.append("- ")

    board_md = task_dir / "Board.md"
    board_md.write_text("\n".join(board_lines), encoding="utf-8")
    print(f"[OK] Created: {board_md}")

    # === Dashboard.md ===
    dashboard_lines = [
        "# Task Dashboard",
        "",
        "## P1 緊急任務",
        "```dataview",
        "TABLE status, category, due",
        f'FROM "{args.folder}"',
        'WHERE priority = "P1" AND status != "done"',
        "SORT due ASC",
        "```",
        "",
        "## 逾期任務",
        "```dataview",
        "TABLE priority, category",
        f'FROM "{args.folder}"',
        "WHERE due AND due < date(today) AND status != \"done\"",
        "```",
        "",
        "## 最近完成",
        "```dataview",
        "TABLE category",
        f'FROM "{args.folder}"',
        'WHERE status = "done"',
        "SORT file.mtime DESC",
        "LIMIT 10",
        "```",
        "",
        "## 全部未完成",
        "```dataview",
        "TABLE status, priority, category, due",
        f'FROM "{args.folder}"',
        'WHERE status != "done"',
        "SORT priority ASC, due ASC",
        "```",
    ]

    dashboard_md = task_dir / "Dashboard.md"
    dashboard_md.write_text("\n".join(dashboard_lines), encoding="utf-8")
    print(f"[OK] Created: {dashboard_md}")

    # === .gitkeep ===
    gitkeep = task_dir / ".gitkeep"
    gitkeep.touch()

    print()
    print("✅ Task board initialized!")
    print(f"   Folder: {task_dir}")
    print(f"   Please install 'Kanban' and 'Dataview' Obsidian community plugins.")


if __name__ == "__main__":
    main()
