---
name: obsidian-semantic
description: Unified semantic search for hermes-knowledge (Obsidian vault). Combines Embedding + Reranker + LLM understanding for accurate memory recall.
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins:
        - ollama
      models:
        - jina-v5-retrieval-test (embedding)
        - bge-reranker-base (reranker, port 19999)
        - MiniMax-M2.1 (LLM understanding, via API)
    install:
      - id: ollama
        kind: manual
        label: Install Ollama
        url: https://ollama.com
      - id: reranker
        kind: script
        label: Start Reranker server (port 19999)
  config:
    SOURCES:
      description: Comma-separated sources to search
      default: obsidian
    VECTOR_WEIGHT:
      description: Vector similarity weight (0-1)
      default: "0.3"
    RERANK_WEIGHT:
      description: Reranker score weight (0-1)
      default: "0.7"
    TOP_K:
      description: Number of results per source
      default: "3"
---

# obsidian-semantic

## 概述

Obsidian 語義搜尋工具，使用向量搜尋 + Reranker + LLM 理解提供準確的記憶召回。

## 核心功能

| 功能 | 說明 | 預設狀態 |
|------|------|----------|
| **Embedding 索引** | 3007 檔案已建立索引 | ✅ 開啟 |
| **向量相似度搜尋** | jina-v5-retrieval-test (1024 dims) | ✅ 開啟 |
| **Reranker 重新排序** | bge-reranker-base (port 19999) | ✅ 開啟 |
| **LLM 理解問題** | MiniMax-M2.1 強化搜尋關鍵字 | ✅ 開啟 |
| **LLM 摘要生成** | 對搜尋結果生成 50 字摘要 | ✅ 開啟 |
| **Wikilink 輸出** | Obsidian 格式連結 | ✅ 開啟 |

## 技術架構

```
使用者輸入查詢
     ↓
┌─────────────────────────┐
│  1. LLM 理解查詢意圖      │ ← MiniMax-M2.1（每次查詢即時處理）
│     （增強搜尋關鍵字）      │
└─────────────────────────┘
     ↓
┌─────────────────────────┐
│  2. 向量相似度搜尋        │ ← jina-v5-retrieval-test（已建立索引）
│     （在 3007 檔中搜尋）  │
└─────────────────────────┘
     ↓
┌─────────────────────────┐
│  3. Reranker 重新排序    │ ← bge-reranker-base（對 top-20 排序）
└─────────────────────────┘
     ↓
┌─────────────────────────┐
│  4. LLM 摘要生成        │ ← MiniMax-M2.1（對 top-5 生成摘要）
└─────────────────────────┘
     ↓
┌─────────────────────────┐
│  5. Wikilink 格式化     │ ← 輸出 [[標題]] 格式
└─────────────────────────┘
```

## 使用方式

### CLI 搜尋
```bash
python skills/obsidian-semantic/references/search.py "查詢關鍵字" -k 5
```

### 參數
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-k N` | 回傳結果數量 | 5 |
| `--no-summary` | 跳過 LLM 摘要生成 | 開啟 |
| `--no-understand` | 跳過 LLM 理解 | 關閉 |

### 範例輸出
```
=== 搜尋結果: "Carbon waitUntil" ===

【理解意圖】Carbon waitUntil
【增強查詢】Carbon waitUntil
【相關概念】waitUntil, Carbon, sub-agent

[1] carbon-waituntil-blocking
    分數: 0.830
    路徑: hermes-knowledge\系統\OpenClaw\技術\carbon-waituntil-blocking.md
    摘要: Carbon waitUntil 是 OpenClaw Carbon 框架中的...
    連結: [[carbon-waituntil-blocking]]

共找到 3 個相關結果
```

## LLM 模型選擇

### MiniMax-M2.1（預設）
- **優點**：對中文理解好、速度快、API 穩定
- **缺點**：需要 API key
- **錯誤處理**：529 Rate Limit 時自動 fallback 到原始查詢

### Llama3.2（備選）
- **優點**：本地運行、無需 API
- **缺點**：對特定術語（如 Carbon）理解較差
- **已廢棄**：理解能力不如 MiniMax-M2.1

## 錯誤處理

| 錯誤 | 處理方式 |
|------|----------|
| **529 Rate Limit** | 顯示訊息，使用原始查詢繼續 |
| **連線錯誤** | 顯示訊息，使用原始查詢繼續 |
| **API 逾時** | 顯示訊息，使用原始查詢繼續 |

## Phase 1 完成狀態

| 功能 | 狀態 | 備註 |
|------|------|------|
| Embedding 索引 | ✅ 完成 | 3007 檔案 |
| 向量相似度搜尋 | ✅ 完成 | jina-v5-retrieval-test |
| Reranker 重新排序 | ✅ 完成 | bge-reranker-base |
| LLM 理解問題 | ✅ 完成 | MiniMax-M2.1 |
| LLM 摘要生成 | ✅ 完成 | MiniMax-M2.1 |
| Wikilink 輸出 | ✅ 完成 | 格式：[[標題]] |

## 待處理（Phase 2）

- [ ] 合併 memory-lancedb-pro 搜尋
- [ ] 合併 session history 搜尋
- [ ] 自動化索引更新

## 學習記錄

### 2026-04-19
- **發現**：Llama3.2 把「Carbon」理解成化學元素，導致搜尋分數從 0.830 降到 0.187
- **解決**：切換到 MiniMax-M2.1，正確理解 OpenClaw 術語
- **錯誤處理**：加入 529 Rate Limit fallback 機制

### 測試結果對比

| 查詢 | Llama3.2 | MiniMax-M2.1 |
|------|----------|--------------|
| Carbon waitUntil | 0.187 ❌ | **0.830** ✅ |
| sub-agent 權限 | - | **0.821** ✅ |

## 檔案位置

- **搜尋腳本**：`skills/obsidian-semantic/references/search.py`
- **Embedding 索引**：`tmp/obsidian_index/embeddings.json`
- **Reranker**：`scripts/reranker_server.py`（port 19999）

## WSL 環境適配（2026-04-20）

從 WSL 呼叫時，所有 URL 必須用 Windows IP（`172.31.224.1`）而非 `localhost`：

| 服務 | Windows | WSL 需用 |
|------|---------|---------|
| Ollama | `localhost:11434` | `172.31.224.1:11434` |
| Reranker | `localhost:19999` | `172.31.224.1:19999` |

**環境變數**（在 `~/.hermes/.env` 有真實 key）：
```bash
export OBSIDIAN_INDEX="/mnt/c/Users/admin/.openclaw/workspace/tmp/obsidian_index/embeddings.json"
export OLLAMA_URL="http://172.31.224.1:11434/api/embeddings"
export RERANKER_URL="http://172.31.224.1:19999/v1/rerank"
export MINIMAX_API_KEY="sk-cp-q79Q-..."  # 從 ~/.hermes/.env 讀取
```

**Windows portproxy**：Ollama 直接 listen 0.0.0.0 不需 portproxy；但 reranker（獨立服務，若只 listen 127.0.0.1）需要：
```
netsh interface portproxy add v4tov4 listenport=19999 listenaddress=0.0.0.0 connectport=19999 connectaddress=127.0.0.1
```

**已修 Bug（2026-04-20）**：
1. MiniMax 回應格式：`content[0]['text']` → `choices[0]['message']['content']`
2. `llm_summary` 未定義 `LLM_URL` → 改用 `OLLAMA_CHAT_URL`
3. 所有 URL 預設值從 `localhost` → `172.31.224.1`
