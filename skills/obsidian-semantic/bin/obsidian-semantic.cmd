#!/usr/bin/env python3
"""
Obsidian Semantic Search - CLI Interface
使用 Embedding + Reranker 語意搜尋 hermes-knowledge
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path
import requests

# 設定
DEFAULT_INDEX = r"C:\Users\admin\.openclaw\workspace\tmp\obsidian_index\embeddings.json"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
RERANKER_URL = "http://localhost:19999/v1/rerank"

def embed_text(text: str) -> list:
    """用 Ollama API 向量化"""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": "jina-v5-retrieval-test", "prompt": text[:1000]},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["embedding"]
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return None

def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def rerank(query: str, docs: list) -> list:
    """用 Reranker 重新排序"""
    try:
        resp = requests.post(
            RERANKER_URL,
            json={
                "model": "BAAI/bge-reranker-base",
                "query": query,
                "documents": docs,
                "top_n": len(docs)
            },
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()["results"]
    except Exception as e:
        print(f"Reranker error: {e}", file=sys.stderr)
    return None

def search(query: str, index_file: str = DEFAULT_INDEX, top_k: int = 5) -> list:
    """語意搜尋"""
    # 1. 載入索引
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data['files']
    embeddings = data['embeddings']
    
    # 2. 向量化問題
    print(f"Query: {query}", file=sys.stderr)
    query_emb = embed_text(query)
    if not query_emb:
        print("Failed to embed query", file=sys.stderr)
        return []
    
    # 3. 向量搜尋 (取 top 20 給 Reranker)
    candidates = []
    for i, (f, emb) in enumerate(zip(files, embeddings)):
        sim = cosine_sim(query_emb, emb)
        try:
            content = Path(f['path']).read_text(encoding='utf-8', errors='ignore')[:1000]
        except:
            content = ""
        candidates.append({
            'index': i,
            'title': f['title'],
            'path': f['path'],
            'content': content[:500],
            'vector_score': sim
        })
    
    candidates.sort(key=lambda x: x['vector_score'], reverse=True)
    top_candidates = candidates[:20]
    
    # 4. Reranker
    docs = [c['content'] for c in top_candidates]
    rerank_results = rerank(query, docs)
    
    if rerank_results is None:
        # Reranker 失敗，回傳向量結果
        return [(c['title'], c['path'], c['vector_score']) for c in candidates[:top_k]]
    
    # 5. 合併分數
    final = []
    for r in rerank_results:
        c = top_candidates[r['index']]
        combined = c['vector_score'] * 0.3 + r['relevance_score'] * 0.7
        final.append((c['title'], c['path'], combined))
    
    final.sort(key=lambda x: x[2], reverse=True)
    return final[:top_k]

def main():
    parser = argparse.ArgumentParser(description="Obsidian Semantic Search")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("-i", "--index", default=DEFAULT_INDEX, help="Index file path")
    args = parser.parse_args()
    
    if not args.query:
        print("Usage: obsidian-semantic <query>")
        sys.exit(1)
    
    results = search(args.query, args.index, args.top_k)
    
    print(f"=== Obsidian Semantic Search ===\n")
    for i, (title, path, score) in enumerate(results, 1):
        print(f"{i}. [{score:.3f}] {title}")
        print(f"   {path}\n")

if __name__ == "__main__":
    main()