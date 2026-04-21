#!/usr/bin/env python3
"""
Obsidian Semantic Search - CLI Interface
Enhanced with LLM Query Understanding, Summary and Wikilink
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path
import requests

import os
_DEFAULT_INDEX = r"C:\Users\admin\.openclaw\workspace\tmp\obsidian_index\embeddings.json"
DEFAULT_INDEX = os.environ.get("OBSIDIAN_INDEX", _DEFAULT_INDEX)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://172.31.224.1:11434/api/embeddings")
OLLAMA_CHAT_URL = os.environ.get("OLLAMA_CHAT_URL", "http://172.31.224.1:11434/api/chat")
RERANKER_URL = os.environ.get("RERANKER_URL", "http://172.31.224.1:19999/v1/rerank")
# MiniMax API for LLM understanding
MINIMAX_API_URL = os.environ.get("MINIMAX_API_URL", "https://api.minimax.io/anthropic/v1/messages")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_MODEL = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.1")

def embed_text(text: str) -> list:
    try:
        resp = requests.post(OLLAMA_URL, json={"model": "jina-v5-retrieval-test", "prompt": text[:1000]}, timeout=30)
        if resp.status_code == 200:
            return resp.json()["embedding"]
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return None

def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def understand_query(query: str) -> dict:
    """用 MiniMax LLM 理解查詢意圖並擴展上下文
    
    回傳格式：
    {
        'intent': str,           # 理解到的意圖
        'enhanced_query': str,    # 增強後的查詢
        'related_concepts': [],   # 相關概念
        'context_hints': []      # 上下文提示
    }
    
    錯誤處理：
    - 529: Rate Limit → 使用本地關鍵字增強
    - 其他錯誤 → 返回原始查詢
    """
    prompt = f"""你是一個搜尋理解助手。請分析以下查詢，並提供增強的搜尋建議。

查詢：「{query}」

請用以下 JSON 格式回覆（只回覆 JSON，不要其他文字）：
{{
    "intent": "理解到的使用者意圖（一句話）",
    "enhanced_query": "增強後的搜尋查詢，包含同義詞和相關術語",
    "related_concepts": ["相關概念1", "相關概念2", "相關概念3"],
    "context_hints": ["上下文提示1", "上下文提示2"]
}}

只回覆 JSON："""
    
    # 嘗試 MiniMax API
    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        data = {
            "model": MINIMAX_MODEL,
            "max_tokens": 256,
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(MINIMAX_API_URL, json=data, headers=headers, timeout=60)
        
        # 529 Rate Limit → fallback 到本地處理
        if resp.status_code == 529:
            print(f"[MiniMax Rate Limit 529，使用本地關鍵字處理]", file=sys.stderr)
            return {
                'intent': query,
                'enhanced_query': query,
                'related_concepts': [],
                'context_hints': []
            }
        
        if resp.status_code == 200:
            result = resp.json()['choices'][0]['message']['content'].strip()
            # 嘗試解析 JSON
            try:
                # 移除可能的 markdown code block
                if result.startswith('```'):
                    lines = result.split('\n')
                    result = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
                return json.loads(result)
            except json.JSONDecodeError:
                # 如果解析失敗，返回預設值
                return {
                    'intent': query,
                    'enhanced_query': query,
                    'related_concepts': [],
                    'context_hints': []
                }
        else:
            print(f"MiniMax API error: {resp.status_code}", file=sys.stderr)
            
    except requests.exceptions.RequestException as e:
        print(f"MiniMax connection error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"MiniMax error: {e}", file=sys.stderr)
    
    return {
        'intent': query,
        'enhanced_query': query,
        'related_concepts': [],
        'context_hints': []
    }

def rerank(query: str, docs: list) -> list:
    try:
        resp = requests.post(RERANKER_URL, json={"model": "BAAI/bge-reranker-base", "query": query, "documents": docs, "top_n": len(docs)}, timeout=60)
        if resp.status_code == 200:
            return resp.json()['results']
    except Exception as e:
        print(f"Reranker error: {e}", file=sys.stderr)
    return None

def llm_summary(query: str, content: str, model: str = "llama3.2:latest") -> str:
    """用 LLM 生成摘要"""
    try:
        prompt = f"""根據以下查詢「{query}」，產生 50 字以內的簡短摘要：

內容：{content[:500]}

摘要："""
        resp = requests.post(OLLAMA_CHAT_URL, json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, timeout=30)
        if resp.status_code == 200:
            return resp.json().get('response', '').strip()
    except Exception as e:
        print(f"LLM error: {e}", file=sys.stderr)
    return None

def generate_wikilink(title: str) -> str:
    """產生 Obsidian Wikilink 格式"""
    return f"[[{title}]]"

def search(query: str, index_file: str = DEFAULT_INDEX, top_k: int = 5, with_summary: bool = True, with_llm_understand: bool = True) -> list:
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data['files']
    embeddings = data['embeddings']
    
    # Step 1: LLM 理解問題 - 用關鍵字強化
    query_understanding = {
        'intent': query,
        'enhanced_query': query,
        'related_concepts': [],
        'context_hints': []
    }
    
    if with_llm_understand:
        print(f"[LLM 理解中...]", file=sys.stderr)
        query_understanding = understand_query(query)
        print(f"[意圖] {query_understanding['intent']}", file=sys.stderr)
        print(f"[增強查詢] {query_understanding['enhanced_query']}", file=sys.stderr)
        if query_understanding['related_concepts']:
            print(f"[相關概念] {', '.join(query_understanding['related_concepts'][:3])}", file=sys.stderr)
    
    # 使用增強後的查詢
    enhanced_query = query_understanding['enhanced_query']
    
    # Step 2: Embedding 向量化
    query_emb = embed_text(enhanced_query)
    if not query_emb:
        return [], query_understanding
    
    # Step 3: 向量相似度搜尋
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
    
    # Step 4: Reranker 重新排序
    docs = [c['content'] for c in top_candidates]
    rerank_results = rerank(enhanced_query, docs)
    
    if rerank_results is None:
        # Fallback to vector only
        fallback = [(c['title'], c['path'], c['vector_score'], None, None) for c in candidates[:top_k]]
        return fallback, query_understanding
    
    # Step 5: LLM 摘要生成 + Wikilink
    final = []
    for r in rerank_results[:top_k]:
        c = top_candidates[r['index']]
        combined = c['vector_score'] * 0.3 + r['relevance_score'] * 0.7
        
        # 生成摘要
        summary = None
        wikilink = None
        if with_summary:
            summary = llm_summary(query, c['content'])
            wikilink = generate_wikilink(c['title'])
        
        final.append((c['title'], c['path'], combined, summary, wikilink))
    
    final.sort(key=lambda x: x[2], reverse=True)
    return final, query_understanding

def format_output(results: list, query: str, query_understanding: dict = None) -> str:
    """格式化輸出"""
    output = f"=== 搜尋結果: \"{query}\" ===\n\n"
    
    # 如果有 LLM 理解結果，先顯示
    if query_understanding and query_understanding.get('intent') != query:
        output += f"【理解意圖】{query_understanding['intent']}\n"
        if query_understanding.get('related_concepts'):
            output += f"【相關概念】{', '.join(query_understanding['related_concepts'][:3])}\n"
        if query_understanding.get('context_hints'):
            output += f"【上下文】{', '.join(query_understanding['context_hints'][:2])}\n"
        output += "\n"
    
    for i, (title, path, score, summary, wikilink) in enumerate(results, 1):
        output += f"[{i}] {title}\n"
        output += f"    分數: {score:.3f}\n"
        output += f"    路徑: {path}\n"
        if summary:
            output += f"    摘要: {summary}\n"
        if wikilink:
            output += f"    連結: {wikilink}\n"
        output += "\n"
    
    output += f"共找到 {len(results)} 個相關結果\n"
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-k", "--top-k", type=int, default=5)
    parser.add_argument("--no-summary", action="store_true", help="Skip LLM summary")
    parser.add_argument("--no-understand", action="store_true", help="Skip LLM query understanding")
    args = parser.parse_args()
    
    if not args.query:
        print("Usage: obsidian-semantic.py <query> [-k N] [--no-summary] [--no-understand]")
        sys.exit(1)
    
    results, query_understanding = search(
        args.query, 
        top_k=args.top_k, 
        with_summary=not args.no_summary,
        with_llm_understand=not args.no_understand
    )
    output = format_output(results, args.query, query_understanding)
    print(output)
