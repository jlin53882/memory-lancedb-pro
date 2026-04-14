# [BUG] Ollama 0.20.5+ Embedding API 相容性問題 — /v1/embeddings 回傳空陣列

## 問題摘要

使用 Ollama 0.20.5 作為 embedding provider 時，`embedder.ts` 透過 OpenAI-compatible endpoint (`/v1/embeddings`) 呼叫 Ollama，**所有 embedding 都回傳空陣列**，導致 memory recall 完全失效。

---

## 問題詳述

### 環境
- **Ollama 版本**：0.20.5（2026-04-14 最新穩定版）
- **受影響模型**：
  - `jina-v5-retrieval-test`（原生 1024 dims）
  - `nomic-embed-text`（原生 768 dims）
  - `mxbai-embed-large`（原生 1024 dims）
- **Plugin 版本**：memory-lancedb-pro（master branch）
- **設定**：
  ```json
  "embedding": {
    "provider": "openai-compatible",
    "apiKey": "ollama-local",
    "baseURL": "http://localhost:11434/v1",
    "dimensions": 1024,
    "model": "jina-v5-retrieval-test",
    "normalized": true,
    "taskPassage": "retrieval.passage",
    "taskQuery": "retrieval.query"
  }
  ```

### 錯誤現象
```
memory-lancedb-pro: recall failed: Error: Failed to generate embedding from Ollama: This operation was aborted
```

### 根本原因
`src/embedder.ts` 的 `embedWithNativeFetch()` 方法使用 `/v1/embeddings` endpoint，但 **Ollama 0.20.5 的 `/v1/embeddings` 有 bug，所有參數（`input`、`prompt`）都回傳空陣列**。

### API 測試結果

| Endpoint | 參數 | jina-v5-retrieval-test | nomic-embed-text |
|----------|------|-------------------------|------------------|
| `/v1/embeddings` | `input` | EMPTY (0 dims) ❌ | EMPTY (0 dims) ❌ |
| `/v1/embeddings` | `prompt` | EMPTY (0 dims) ❌ | EMPTY (0 dims) ❌ |
| `/api/embeddings` | `input` | EMPTY (0 dims) ❌ | EMPTY (0 dims) ❌ |
| `/api/embeddings` | `prompt` | **1024 dims** ✅ | **768 dims** ✅ |

**結論**：只有 `/api/embeddings` + `prompt` 參數能正常運作。

---

## README 不需要調整

```
Ollama（本地）    nomic-embed-text    http://localhost:11434/v1    取決於模型
```

這段文件是對的——`http://localhost:11434/v1` 是 Ollama 官方的正確建議，**問題不在文件而在 code**。

| 層面 | 對錯 | 說明 |
|------|------|------|
| **README 文件** | ✅ 正確 | 告訴用戶用 `/v1` endpoint 是對的 |
| **Ollama 官方建議** | ✅ 正確 | `/v1` 是 Ollama 官方的 OpenAI-compatible API |
| **plugin code** | ❌ 有 bug | `embedWithNativeFetch` 在 Ollama 0.20.5 上失效 |

---

## 修復方式

### 檔案：`src/embedder.ts`
### 方法：`embedWithNativeFetch()`

**修改內容**：

```typescript
// 修改前（問題程式碼）
private async embedWithNativeFetch(payload: any, signal?: AbortSignal): Promise<any> {
  if (!this._baseURL) {
    throw new Error("embedWithNativeFetch requires a baseURL");
  }
  
  // 問題點：使用 baseURL（通常是 http://127.0.0.1:11434/v1）
  // 拼接後變成 /v1/embeddings，但 Ollama 0.20.5 的 /v1/embeddings 有 bug
  const endpoint = this._baseURL.replace(/\/$/, "") + "/embeddings";
  
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
    body: JSON.stringify(payload),  // ← payload.input 在這，但 Ollama 不吃
    signal: signal,
  });
  
  const data = await response.json();
  return data; // OpenAI-compatible shape: { data: [{ embedding: number[] }] }
}

// 修改後（修復程式碼）
private async embedWithNativeFetch(payload: any, signal?: AbortSignal): Promise<any> {
  if (!this._baseURL) {
    throw new Error("embedWithNativeFetch requires a baseURL");
  }
  
  // 使用 legacy /api/embeddings endpoint（Ollama 0.20.5 /v1/embeddings 有 bug）
  const base = this._baseURL.replace(/\/$/, "").replace(/\/v1$/, "");
  const endpoint = base + "/api/embeddings";

  const apiKey = this.clients[0]?.apiKey ?? "ollama";

  // Ollama 的 /api/embeddings 需要 "prompt" 參數，而非 "input"
  const ollamaPayload = {
    model: payload.model,
    prompt: payload.input,
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
    body: JSON.stringify(ollamaPayload),
    signal: signal,
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(`Ollama embedding failed: ${response.status} ${response.statusText} ??${body.slice(0, 200)}`);
  }

  const data = await response.json();
  
  // 將 Ollama 格式轉換為 OpenAI 格式
  return { data: [{ embedding: data.embedding }] };
}
```

### 修復關鍵點

1. **Endpoint**：從 `/v1/embeddings` 改為 `/api/embeddings`
2. **參數**：從 `input` 改為 `prompt`
3. **回應格式轉換**：Ollama `/api/embeddings` 回傳 `{embedding: [...]}`，需轉換成 OpenAI format `{data: [{embedding: [...]}]}`

---

## 影響範圍

- 所有使用 Ollama 作為 embedding provider 的用戶（特別是使用 `/v1` baseURL 的）
- 症狀：auto-recall 完全失效，每次嘗試 recall 都會得到 "Failed to generate embedding from Ollama: This operation was aborted" 錯誤
- 初期可能看不出問題（因為 LRU cache），但 cache 過期後就會失敗

---

## 標籤

bug, embedding, ollama

---

## 相關檔案

- `src/embedder.ts` — `embedWithNativeFetch()` 方法
