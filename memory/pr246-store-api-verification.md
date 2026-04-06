# PR246 Phase 2 Store API 實作驗證報告

**目標目錄**：`C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test\src\`

---

## 1. `store.ts` — 驗證結果摘要

| 問題 | 答案 |
|------|------|
| `store.update` 支援 partial update | **是**。使用 `??`（nullish coalescing）合併： `updates.text ?? original.text`，未傳的欄位保留原值 |
| `last_confirmed_use_at` 型別 | `number`（Unix ms，無時區） |
| `bad_recall_count` 型別 | `number`（整數，由 `clampCount()` 確保） |
| 寫入是否需要轉換 | **不需要**。直接寫 `Date.now()`（ms）即可，`normalizeOptionalTimestamp` 內部只做 `Math.floor(n)` |
| schema 是否 strict | **否**。LanceDB 是 schemaless，無 strict 模式；額外欄位透過 `metadata` JSON string 儲存 |

### 詳細分析

#### `update()` 方法簽名與實作

```typescript
// store.ts 第 ~行
async update(
  id: string,
  updates: {
    text?: string;
    vector?: number[];
    importance?: number;
    category?: MemoryEntry["category"];
    metadata?: string;   // <-- 這裡沒有 last_confirmed_use_at / bad_recall_count
  },
  scopeFilter?: string[],
): Promise<MemoryEntry | null>
```

實作邏輯（delete + re-add 模式）：
```typescript
const updated: MemoryEntry = {
  ...original,
  text: updates.text ?? original.text,        // partial: 保留原值
  vector: updates.vector ?? original.vector,  // partial: 保留原值
  category: updates.category ?? original.category, // partial: 保留原值
  scope: rowScope,
  importance: updates.importance ?? original.importance, // partial
  timestamp: original.timestamp, // preserve original
  metadata: updates.metadata ?? original.metadata, // partial
};
```

**結論**：`update()` 直接支援 partial update，且底層是讀取→合併→刪除→重寫，而非覆寫。

#### 如何更新 `last_confirmed_use_at`（不走 `update` 直接欄位）

`last_confirmed_use_at` 不在 `update()` 的 `updates` 參數中，因為它是 `metadata` JSON 內的欄位。
正確做法是透過 `patchMetadata()`：

```typescript
// store.ts 第 ~行
async patchMetadata(
  id: string,
  patch: MetadataPatch,  // e.g. { last_confirmed_use_at: Date.now() }
  scopeFilter?: string[],
): Promise<MemoryEntry | null> {
  const existing = await this.getById(id, scopeFilter);
  if (!existing) return null;
  const metadata = buildSmartMetadata(existing, patch); // 合併 patch 到現有 metadata
  return this.update(id, { metadata: stringifySmartMetadata(metadata) }, scopeFilter);
}
```

`buildSmartMetadata()` 中對 `last_confirmed_use_at` 的處理：
```typescript
last_confirmed_use_at:
  patch.last_confirmed_use_at === undefined
    ? base.last_confirmed_use_at
    : normalizeOptionalTimestamp(patch.last_confirmed_use_at),
```

#### `normalizeOptionalTimestamp()` 轉換規則

```typescript
function normalizeOptionalTimestamp(value: unknown): number | undefined {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n) || n <= 0) return undefined;
  return Math.floor(n);  // 直接取整數，不除以 1000
}
```

**寫入方式**：直接傳 `Date.now()`（回傳 ms），不需要 `/1000`。

---

## 2. `smart-metadata.ts` — 驗證結果摘要

| 問題 | 答案 |
|------|------|
| `store.update` 支援 partial update | 不適用（此檔案無 `update` 方法）|
| `last_confirmed_use_at` 型別 | `number \| undefined`（Unix ms） |
| `bad_recall_count` 型別 | `number`（整數，預設 0，由 `clampCount()`） |
| 寫入是否需要轉換 | **不需要**，`normalizeOptionalTimestamp` 接受 `Date.now()` |
| schema 是否 strict | **否**，所有額外欄位都存在 `metadata` JSON 字串中 |

### 詳細分析

`SmartMemoryMetadata` 介面（所有欄位）：
```typescript
export interface SmartMemoryMetadata {
  l0_abstract: string;
  l1_overview: string;
  l2_content: string;
  memory_category: MemoryCategory;
  tier: MemoryTier;
  access_count: number;
  confidence: number;
  last_accessed_at: number;
  valid_from: number;
  invalidated_at?: number;
  fact_key?: string;
  supersedes?: string;
  superseded_by?: string;
  relations?: MemoryRelation[];
  source_session?: string;
  state: MemoryState;
  source: MemorySource;
  memory_layer: MemoryLayer;
  injected_count: number;
  last_injected_at?: number;
  last_confirmed_use_at?: number;  // <-- Unix ms
  bad_recall_count: number;         // <-- 整數計數
  suppressed_until_turn: number;
  canonical_id?: string;
  [key: string]: unknown;           // <-- 允許額外欄位
}
```

**注意**：所有 `*_at` 欄位都是 Unix ms（`number`），不需要除以 1000。`bad_recall_count` 是普通整數。

---

## 3. `memory-upgrader.ts` — 驗證結果摘要

| 問題 | 答案 |
|------|------|
| `store.update` 支援 partial update | 不適用（此檔案無 `update` 方法）|
| `last_confirmed_use_at` 型別 | 不直接處理（透過 `buildSmartMetadata`） |
| `bad_recall_count` 型別 | 不直接處理（預設 0） |
| 寫入是否需要轉換 | 不適用 |
| schema 是否 strict | **否** |

### 詳細分析

此檔案負責將 legacy memories 升級到新格式，不涉及 `last_confirmed_use_at` 或 `bad_recall_count` 的直接寫入。升級流程：

1. `isLegacyMemory()` — 檢測是否缺少 `memory_category` 欄位
2. `upgradeEntry()` — 產生 L0/L1/L2 摘要，更新 `metadata`
3. 最後呼叫 `store.update(entry.id, { text, metadata })` 寫入

---

## 總結：對 Phase 2 recall recall 流程的影響

### 如何更新 `last_confirmed_use_at`

```typescript
// 正確做法：透過 patchMetadata
await store.patchMetadata(id, {
  last_confirmed_use_at: Date.now(),  // 直接傳 ms，不需要 /1000
});
```

**不要**這樣做：
```typescript
// ❌ 錯誤：直接呼叫 update() 的 metadata 參數（底層會完全覆蓋）
await store.update(id, { metadata: '{"last_confirmed_use_at": Date.now()}' });
// 這會丟失其他 metadata 欄位！
```

### 如何遞增 `bad_recall_count`

```typescript
// 讀取 → 修改 → 寫回
const existing = await store.getById(id);
if (!existing) return;
const meta = parseSmartMetadata(existing.metadata, existing);
const updated = buildSmartMetadata(existing, {
  bad_recall_count: meta.bad_recall_count + 1,
});
await store.update(id, { metadata: stringifySmartMetadata(updated) });
```

### 寫入時需要除以 1000 嗎？

**不需要。** 所有 `*_at` 欄位都是 Unix 毫秒（與 `Date.now()` 一致），`clampCount` 對 `bad_recall_count` 也是直接取整數。
