# PR #246 Phase 1 實作報告 — B-1 鄰居擴展

## 實作摘要

已在 `reflection-slices.ts` 中新增 BM25 鄰居擴展相關函式。

### 修改內容

1. **新增 `loadAgentReflectionSlicesFromEntries`**（同步 wrapper）
   - 位置：第 330-352 行
   - 用途：提供同步介面（實際實作在 reflection-store.ts）

2. **新增 `loadAgentReflectionSlicesWithBm25Expansion`**（異步擴展）
   - 位置：第 354-419 行
   - 用途：對 derived slices 執行 BM25 鄰居擴展

### 函式簽名

```typescript
export async function loadAgentReflectionSlicesWithBm25Expansion(
  store: { bm25Search: (query: string, limit?: number, scopeFilter?: string[], options?: { excludeInactive?: boolean }) => Promise<Array<{ entry: { text: string } }>> },
  params: {
    entries: Array<{ text: string; metadata: Record<string, unknown>; timestamp: number }>;
    agentId: string;
    now?: number;
    deriveMaxAgeMs?: number;
    invariantMaxAgeMs?: number;
  },
  options?: {
    bm25TopK?: number;        // 預設 2
    bm25Scope?: string[] | undefined;  // undefined = global
    excludeInactive?: boolean; // 預設 true
  }
): Promise<{
  invariants: string[];
  derived: string[];
  expandedFrom?: number;
}>
```

### 實作邏輯

1. 接收已計算好的 derived slices（透過 entries 傳入）
2. 對每個 derived slice 執行 `store.bm25Search()`
3. 收集鄰居的 text內容
4. 去重（依 text內容 Set）
5. 回傳擴展後的 derived + expandedFrom 計數

---

## 待確認項目（⚠️ 需要 mlp-impl-a 驗證）

| 項目 | 假設內容 | 狀態 |
|------|---------|------|
| BM25 搜尋 scope 參數 | 支援 `scopeFilter?: string[]`，傳入 `['same']` 代表同 scope | ⚠️ 待確認 |
| 回傳格式 | `MemorySearchResult[]`，其中 `result.entry.text` 是記憶內文 | ⚠️ 待確認 |
| 去重策略 | 目前用 text 內容去重，是否需要依 id 或 hash？ | ⚠️ 待確認 |
| 擴展目標 | 僅擴展 derived？還是要連 invariants 一起擴展？ | ⚠️ 待確認 |

---

## 調用範例

```typescript
import { loadAgentReflectionSlicesFromEntries } from './reflection-store.js';
import { loadAgentReflectionSlicesWithBm25Expansion } from './reflection-slices.js';

// Step 1: 取得基礎 slices
const slices = loadAgentReflectionSlicesFromEntries({
  entries: reflectionEntries,  // 從 store.list()取得的 MemoryEntry[]
  agentId: 'agent:xxx',
});

// Step 2: BM25 擴展 derived
const expanded = await loadAgentReflectionSlicesWithBm25Expansion(store, {
  entries: reflectionEntries, // 需包含 text 欄位
  agentId: 'agent:xxx',
}, {
  bm25TopK: 2,
  bm25Scope: ['same'], // 假設支援 scope 篩選
});

console.log('derived 原始數:', slices.derived.length);
console.log('BM25 擴展後:', expanded.derived.length);
```

---

## 假設驗證清單

| 假設 | 來源依據 | 驗證狀態 |
|------|---------|---------|
| `store.bm25Search` 存在且簽名正確 | 從 store.ts 第 522 行確認存在 | ✅ 已確認 |
| `scopeFilter: ['same']` 能正確篩選同 scope 記憶 | 從 scopes.ts 分析推測 | ⚠️ 待確認 |
| 回傳結果有 `entry.text` 欄位 | 從 retriever.ts 第 493 行使用方式推測 | ⚠️ 待確認 |

---

## 檔案變更

- `src/reflection-slices.ts`：新增 2 個函式（約 90 行）

---

## 下一步

1. 等 mlp-impl-a 確認 BM25 搜尋的實際參數行為
2. 確認後回來修正 `bm25Scope` 參數用法
3. 整合到 index.ts 的 slices 載入流程

---

*最後更新：2026-04-02*