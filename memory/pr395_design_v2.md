# Issue #395 / #447 — Reflection Resolution Mechanism 設計方案

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒

---

## 一、問題背景

Reflection pipeline 是單向的：extract → store → decay → inject。沒有 resolve → invalidate → suppress 路徑。

一旦 reflection item 被寫入，會持續被 injection 直到 maxAgeDays 自然過期（Invariant 預設 45 天，Derived 預設 7 天）。

**範例**：
- Session A：Rerank 設定問題 → 萃取 6 條 derived lessons
- Session B：Rerank 已確認正常
- Sessions C, D, E...：這 6 條過時 item 繼續 injection，最多持續 45 天

**現有缺口**：
- `filterByMaxAge()` 存在（`reflection-store.ts` 第 377 行）
- 但沒有 `filterByResolved()`（不存在 `resolvedAt` 欄位）
- 也沒有 `memory_reflection_resolve` tool

---

## 二、現有程式碼分析結論

### 現有 Reflection Pipeline

```
reflection-store.ts
  │
  ├── loadAgentReflectionSlices() ──→ 回傳 {invariants: string[], derived: string[]}
  │                                    │
  │   filterByMaxAge() 在這裡（recall 時自然套用）
  │
  └── storeReflectionToLanceDB()
        │
        ├── reflection-event-store.ts ──→ 每次事件一筆記錄（不含 item）
        │
        └── reflection-item-store.ts
              ├── InvariantItem：半衰期 45 天（k=0.22, midpoint=45天）
              └── DerivedItem：半衰期 7 天（k=0.65, midpoint=7天）
```

### 現有 ReflectionItemMetadata Schema

```typescript
interface ReflectionItemMetadata {
  strictKey?: string;       // 問題叢集 ID（用於分組）
  quality?: number;          // 萃取品質（0-1）
  confidence?: number;       // 置信度
  injectedCount?: number;    // 被 injection 次數
  eventId?: string;         // 關聯的事件 ID
  // ⚠️ 沒有 resolvedAt / resolvedBy / resolutionNote
}
```

---

## 三、方案比較

### 方案 A：resolvedAt field + memory_reflection_resolve tool（推薦）

在 `ReflectionItemMetadata` 新增可選欄位：

```typescript
interface ReflectionItemMetadata {
  // ... 現有欄位 ...
  resolvedAt?: number;       // Unix ms timestamp
  resolvedBy?: string;       // agentId
  resolutionNote?: string;    // 可選備註
}
```

新增 filter 和 tool：

```typescript
// filterByResolved() — 在 filterByMaxAge() 之後呼叫
function filterByResolved(items: ReflectionItem[]): ReflectionItem[] {
  return items.filter(item => item.metadata.resolvedAt === undefined);
}

// memory_reflection_resolve tool
memory_reflection_resolve({
  query?: string,   // BM25 match → 解決所有匹配
  id?: string,      // 直接 ID → 解決一筆
  note?: string,    // 備註（可選）
})
```

| Pros | Cons |
|------|------|
| 完全 backward compatible（欄位可選）| schema migration：歷史 items 無 resolvedAt |
| 實作簡單：只加 filter + tool | 需提供 migration script |
| 不改變既有 decay 流程 | 需作者確認 strictKey 共 resolve 行為 |
| 低風險：不影響其他模組 | - |

### 方案 B：cross-pipeline suppression

基於 semantic similarity 抑制相似的 reflection items。

| Pros | Cons |
|------|------|
| 更聰明：自動找出相似 items | 需 semantic similarity 分類，高複雜度 |
| 不需要 explicit resolve | 準確度難以保證 |

**排除理由**：複雜度過高，準確度不明顯優於方案 A。

### 方案 C：Full status schema migration

將 `status: 'active' | 'resolved' | 'superseded'` 列為正式欄位。

| Pros | Cons |
|------|------|
| 最嚴謹：狀態明確 | 需要 schema migration（破壞性變更）|
| | 過度設計：目前不需要 |

**排除理由**：過度複雜，方案 A 已經足夠。

---

## 四、最終推薦方案

**採用方案 A，並加入以下細節：**

### 4.1 strictKey 一起 resolve（建議默認行為）

當 resolve 時，如果提供了 `strictKey`，則**所有同 strictKey 的 items 都一併標記為 resolved**：

```typescript
memory_reflection_resolve({ query, strictKey, note }) {
  let toResolve: string[];

  if (id) {
    toResolve = [id];
  } else if (query) {
    // BM25 search → 取出匹配的 items
    const results = await bm25Search(query, { scope, limit: 20 });
    toResolve = results.map(r => r.id);
  }

  // 如果有 strictKey，擴展範圍
  if (strictKey) {
    const sameKey = await findByStrictKey(strictKey);
    toResolve = [...new Set([...toResolve, ...sameKey])];
  }

  // 批量更新
  await store.updateMany(toResolve, {
    resolvedAt: Date.now(),
    resolvedBy: currentAgentId,
    resolutionNote: note,
  });

  return `Resolved ${toResolve.length} items`;
}
```

### 4.2 新增工具

```typescript
// memory_reflection_resolve({ query?, id?, strictKey?, note? })
// memory_reflection_stats({ scope?, status?: 'active' | 'resolved' | 'all' })
// memory_reflection_list({ scope?, status?: 'active' | 'resolved' | 'all', limit?: 20 })
```

### 4.3 Migration Script

```typescript
// 對所有歷史 items（無 resolvedAt）自動視為 active：
// 不需要 migration，只是查詢時預設只取 resolvedAt === undefined
```

---

## 五、實作順序建議

| 順序 | 內容 | 理由 |
|------|------|------|
| 1 | `resolvedAt` 等欄位加到 ReflectionItemMetadata interface | 最基礎變更 |
| 2 | `filterByResolved()` 在 recall 時呼叫 | 立即見效：已解決的不再 injection |
| 3 | `memory_reflection_resolve` tool | 讓 agent 主動標注 |
| 4 | `memory_reflection_list` + `memory_reflection_stats` | 讓 agent 可審視現有 items |
| 5 | Migration script（可選）| 清理歷史資料 |

**所有步驟都是 additive**（不破壞既有功能）。

---

## 六、需作者確認的問題

1. `strictKey` 共 resolve 是預設行為嗎？還是需要 explicit flag？
2. `memory_reflection_list` 是否會暴露過多 internal details？
3. resolved items 的 retention policy（多久後可刪除）？

---

## 七、借鑒 Claude Code 的設計

Claude Code 的 reflection 系統（`extractMemories/`）採用：
- **Fork 萃取 agent**：主 agent 有寫入 → 萃取 agent 跳過；主 agent 未寫入 → 萃取 agent 補足
- **互斥機制**：避免重複萃取同一 session

這個互斥模式可以用在 resolved items：當一個 item 被 resolved 之後，萃取 agent 應該知道跳過這個 topic。
