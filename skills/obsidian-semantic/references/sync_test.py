#!/usr/bin/env python3
"""
Phase 2 Sync - 批次 embedding 版本
使用 Ollama /v1/embeddings API 批次處理
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import requests

# 路徑設定
OPENCLAW_ROOT = Path(r"C:\Users\admin\.openclaw")
OBSIDIAN_VAULT = Path(r"C:\Users\admin\.hermes-knowledge")
OBSIDIAN_INDEX = OPENCLAW_ROOT / "workspace/tmp/obsidian_index/embeddings.json"
OLLAMA_URL = "http://localhost:11434/v1/embeddings"
MODEL = "jina-v5-retrieval-test"

def embed_batch(texts: list) -> list:
    """批次取得 embedding（使用 /v1/embeddings）"""
    if not texts:
        return []
    
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "input": texts},
            timeout=120
        )
        if resp.status_code == 200:
            data = resp.json()
            # 按 index 排序回傳
            results = [None] * len(texts)
            for item in data.get("data", []):
                results[item["index"]] = item["embedding"]
            return results
    except Exception as e:
        print(f"Batch embed error: {e}", file=sys.stderr)
    return [None] * len(texts)

def embed_single(text: str) -> list:
    """單一 embedding"""
    results = embed_batch([text])
    return results[0] if results else None

def find_related_files(content: str, top_k: int = 3) -> list:
    """用現有 index + 批次 embedding 找相關檔案"""
    emb = embed_single(content[:500])
    if not emb:
        return []
    
    if not OBSIDIAN_INDEX.exists():
        return []
    
    with open(OBSIDIAN_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 只取前 50 個候選做比對
    files = data['files'][:50]
    embeddings = data['embeddings'][:50]
    
    candidates = []
    for f, e in zip(files, embeddings):
        a, b = np.array(emb), np.array(e)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        if norm > 0:
            sim = np.dot(a, b) / norm
            candidates.append({'title': f['title'], 'path': f['path'], 'score': float(sim)})
    
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:top_k]

def get_all_workspaces():
    ws = []
    for d in OPENCLAW_ROOT.iterdir():
        if d.is_dir() and d.name.startswith("workspace"):
            ws.append(d)
    return ws

def scan_workspace(workspace_path: Path) -> list:
    files = []
    for f in workspace_path.glob("*.md"):
        if not f.name.startswith("."):
            files.append(f)
    for dir_name in [".learnings", "memory", "docs"]:
        dir_path = workspace_path / dir_name
        if dir_path.exists():
            for f in dir_path.rglob("*.md"):
                if "__pycache__" not in str(f):
                    files.append(f)
    return files

def convert_to_obsidian(content: str, title: str, workspace: str, tags: list = None) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    tags_str = ", ".join([f'"{t}"' for t in (tags or ["openclaw", "sync"])])
    
    frontmatter = f"""---
date: {date}
source: {workspace}
tags: [{tags_str}]
---

"""
    
    if not content.strip().startswith('#'):
        content = f"# {title}\n\n{content}"
    
    return frontmatter + content

def generate_wikilinks(related_files: list) -> str:
    if not related_files:
        return ""
    
    lines = ["\n## 相關筆記\n"]
    for f in related_files[:3]:
        if f['score'] > 0.3:
            lines.append(f"- [[{f['title']}]]")
    return "\n".join(lines)

def detect_tags(content: str, workspace: str) -> list:
    tags = ["openclaw", workspace.replace("workspace-", "")]
    content_lower = content.lower()
    if "memory" in content_lower: tags.append("記憶")
    if "learn" in content_lower or "error" in content_lower: tags.append("學習")
    if "pr" in content_lower: tags.append("PR")
    if "issue" in content_lower: tags.append("Issue")
    return list(set(tags))[:4]

def sync_file(source_path: Path, workspace_name: str, dry_run: bool = True) -> dict:
    result = {'source': str(source_path), 'workspace': workspace_name, 'status': 'pending'}
    
    try:
        title = source_path.stem
        output_path = OBSIDIAN_VAULT / "系統/OpenClaw/工作區" / workspace_name / f"{title}.md"
        result['output'] = str(output_path)
        
        # 檢查是否需要同步
        if output_path.exists():
            if source_path.stat().st_mtime <= output_path.stat().st_mtime:
                result['status'] = 'skip'
                return result
        
        content = source_path.read_text(encoding='utf-8')
        
        # 找相關檔案（批次 embedding）
        related = find_related_files(content)
        
        tags = detect_tags(content, workspace_name)
        obsidian_content = convert_to_obsidian(content, title, workspace_name, tags)
        obsidian_content += generate_wikilinks(related)
        
        if dry_run:
            print(f"[DRY] {source_path.name}")
            result['status'] = 'dry'
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(obsidian_content, encoding='utf-8')
            print(f"[SYNC] {source_path.name}")
            result['status'] = 'ok'
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def main(dry_run=True):
    print("=== Phase 2 Sync - 批次 Embedding 版 ===\n")
    
    workspaces = get_all_workspaces()
    print(f"Workspaces: {len(workspaces)}")
    
    all_files = []
    for ws in workspaces:
        files = scan_workspace(ws)
        all_files.extend([(f, ws.name) for f in files])
    
    print(f"總檔案: {len(all_files)}\n")
    
    stats = {'total': len(all_files), 'skip': 0, 'sync': 0, 'error': 0}
    
    for i, (f, ws_name) in enumerate(all_files, 1):
        result = sync_file(f, ws_name, dry_run)
        
        if result['status'] == 'skip':
            stats['skip'] += 1
        elif result['status'] == 'ok':
            stats['sync'] += 1
        elif result['status'] == 'error':
            stats['error'] += 1
        
        if i % 300 == 0:
            print(f"進度: {i}/{len(all_files)} | 同步: {stats['sync']} | 跳過: {stats['skip']}")
    
    print(f"\n=== 結果 ===")
    print(f"總計: {stats['total']}")
    print(f"同步: {stats['sync']}")
    print(f"跳過: {stats['skip']}")
    print(f"錯誤: {stats['error']}")
    
    return stats

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=not args.no_dry_run)