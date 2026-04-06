# memory-lancedb-pro 資料儲存層深度分析報告

> 分析目標：LanceDB 儲存層 CRUD、多範圍隔離管理、長文本分塊處理
> 分析日期：2026-04-02

---

## 1. LanceDB Table Schema 設計

### 1.1 資料模型（MemoryEntry）

```typescript
interface MemoryEntry {
  id: string;                    // UUID（可接受前綴查詢，8+ hex chars）
  text: string;                 // 記憶文本內容
  vector: number[];              // Embedding 向量
  category: "preference" | "fact" | "decision" | "entity" | "other" | "reflection";
  scope: string;                // 範圍標籤（預設 "global"）
  importance: number;           // 重要性分數（0-1）
  timestamp: number;            // Unix timestamp（毫秒）
  metadata?: string;            // JSON 字串（可擴展元資料）
}
```

### 1.2 索引策略

| 索引類型 | 欄位 | 用途 |
|---------|------|------|
| **Vector Index** | `vector` | 餘弦相似度搜尋（`distanceType: 'cosine'`） |
| **FTS Index** | `text` | BM25 全文搜尋（使用 LanceDB `Index.fts()`） |
| **Scalar** | `scope`, `category`, `timestamp` | WHERE 子句過濾 |

### 1.3 關鍵設計要點

1. **向量化維度驗證**：初始化時比對配置維度與表中現有維度，不匹配則拋錯
2. **FTS 回退機制**：若 FTS 建立失敗，降級到 `lexicalFallbackSearch()`（應用層關鍵字比對）
3. **空陣列回傳**：`list()` 不回傳 vector 欄位以提升效能；需要向量時用 `fetchForCompaction()`

---

## 2. Multi-Scope 隔離實現

### 2.1 內建 Scope 模式

| 模式 | 格式 | 用途 |
|------|------|------|
| `global` | `"global"` | 全域共享知識 |
| `agent:{id}` | `"agent:dc-channel-..."` | Agent 私有記憶 |
| `user:{id}` | `"user:user123"` | 使用者範圍 |
| `project:{id}` | `"project:myproject"` | 專案範圍 |
| `custom:{name}` | `"custom:team-alpha"` | 自訂範圍 |
| `reflection:agent:{id}` | `"reflection:agent:dc-channel-..."` | Agent 自我反思 |

### 2.2 存取控制三層语义

| 回傳值 | Store 行為 | 適用情境 |
|--------|------------|----------|
| `undefined` | 無過濾（全 bypass） | 保留 ID（system/undefined）|
| `[]` | 拒絕所有讀取 | 明確空過濾器 |
| `["global", "agent:xxx", ...]` | 限縮至列出範圍 | 正常 Agent 存取 |

### 2.3 權限繼承邏輯

```typescript
// getAccessibleScopes() 邏輯
if (isSystemBypassId(agentId)) {
  return this.getAllScopes();  // 系統任務全存取
}

const explicitAccess = config.agentAccess[agentId];
if (explicitAccess) {
  return [...explicitAccess, `reflection:agent:${agentId}`];
}

// 預設：global + 自己的 agent scope
return ["global", `agent:${agentId}`, `reflection:agent:${agentId}`];
```

### 2.4 Scope Filter 應用

所有搜尋方法（`vectorSearch`, `bm25Search`, `list`, `delete`, `update`）都接受 `scopeFilter?: string[]` 參數：

```typescript
// 向量搜尋中的 scope 過濾
if (scopeFilter && scopeFilter.length > 0) {
  const conditions = scopeFilter
    .map(scope => `scope = '${escapeSqlLiteral(scope)}'`)
    .join(" OR ");
  query = query.where(`(${conditions}) OR scope IS NULL`);
}
```

**注意**：`scope IS NULL` 處理向後兼容性（舊資料可能無 scope 欄位）。

---

## 3. Chunker 疊加視窗機制

### 3.1 預設配置

```typescript
const DEFAULT_CHUNKER_CONFIG = {
  maxChunkSize: 4000,     // 最大字元數
  overlapSize: 200,      // 疊加區域（200 chars）
  minChunkSize: 200,     // 最小 chunk（除最後一個外）
  semanticSplit: true,   // 語意分詞（句 > 行 > 空白）
  maxLinesPerChunk: 50,  // 最大行數限制
};
```

### 3.2 疊加視窗移動邏輯

```typescript
// 核心迴圈
while (pos < text.length) {
  const end = findSplitEnd(text, pos, maxEnd, minEnd, config);
  const { chunk, meta } = sliceTrimWithIndices(text, pos, end);
  
  chunks.push(chunk);
  metadatas.push(meta);
  
  // 關鍵：疊加視窗向前滑動
  const nextPos = Math.max(end - config.overlapSize, pos + 1);
  pos = nextPos;
}
```

**疊加效果示意**：
```
Chunk 1: [0....................4000]
Chunk 2:          [3800...................8000]  ← 200 字元重疊
Chunk 3:                    [7800............12000]
```

### 3.3 語意分詞優先級

1. **句結尾**：`[.!?。！？]` → 在標點後 Include trailing whitespace
2. **換行符**：`\n` → 段落邊界
3. **空白字元**：`\s` → 最後手段

### 3.4 Smart Chunking 動態調整

```typescript
export function smartChunk(text: string, embedderModel?: string): ChunkResult {
  const base = EMBEDDING_CONTEXT_LIMITS[embedderModel] ?? 8192;
  
  // CJK 檢測：CJK 字符約 2-3 tokens each
  const cjkHeavy = getCjkRatio(text) > 0.3;
  const divisor = cjkHeavy ? 2.5 : 1;
  
  const config = {
    maxChunkSize: Math.floor(base * 0.7 / divisor),  // 70% 安全邊界
    overlapSize: Math.floor(base * 0.05 / divisor),
    minChunkSize: Math.floor(base * 0.1 / divisor),
    ...
  };
  
  return chunkDocument(text, config);
}
```

### 3.5 CJK 特殊處理

```typescript
const CJK_RE = /[\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF\uF900-\uFAFF]/;

function getCjkRatio(text: string): number {
  // 計算 CJK 字符佔比
  // 若 > 30%，則觸發 token 數量除 divisor（2.5）
}
```

**理由**：一個中文字 ≈ 2-3 tokens，若用相同 char limit 會超出模型 token 預算。

---

## 4. 資料遷移（migrate.ts）實作

### 4.1 遷移來源

```typescript
function getDefaultLegacyPaths(): string[] {
  return [
    join(home, ".openclaw", "memory", "lancedb"),
    join(home, ".claude", "memory", "lancedb"),
  ];
}
```

### 4.2 遷移流程

```
1. findSourceDatabase() → 掃描預設路徑，找 .lance 目錄
2. loadLegacyData() → 讀取 legacy table schema
3. migrateEntries() → 轉換並寫入新 table
   - 保留 original id
   - 映射 category
   - 預設 scope = "global"
   - metadata 標記 { migratedFrom, originalId, originalCreatedAt }
```

### 4.3 向後兼容 Migration

```typescript
// store.ts 中的表初始化邏輯
const missingColumns = [];
if (!fieldNames.has("scope"))    missingColumns.push({ name: "scope", valueSql: "'global'" });
if (!fieldNames.has("timestamp")) missingColumns.push({ name: "timestamp", valueSql: "CAST(0 AS DOUBLE)" });
if (!fieldNames.has("metadata"))  missingColumns.push({ name: "metadata", valueSql: "'{}'" });

if (missingColumns.length > 0) {
  await table.addColumns(missingColumns);  // 新增欄位
}
```

### 4.4 遷移驗證

```typescript
async verifyMigration(sourceDbPath?: string): Promise<{
  valid: boolean;
  sourceCount: number;
  targetCount: number;
  issues: string[];
}> {
  // 檢查 target >= source（允許 skipExisting）
}
```

---

## 5. 檔案鎖定與並發安全

### 5.1 Cross-Process Lock

```typescript
private async runWithFileLock<T>(fn: () => Promise<T>): Promise<T> {
  const lockPath = join(this.config.dbPath, ".memory-write.lock");
  const release = await lockfile.lock(lockPath, {
    retries: { retries: 5, factor: 2, minTimeout: 100, maxTimeout: 2000 },
    stale: 10000,
  });
  try { return await fn(); } 
  finally { await release(); }
}
```

### 5.2 Update 序列化

```typescript
private async runSerializedUpdate<T>(action: () => Promise<T>): Promise<T> {
  // 每個 store 實例的 update 排隊，避免並發 delete+add 競爭
  this.updateQueue = previous.then(() => lock);
  await previous;
  return action();
}
```

### 5.3 錯誤回滾機制

```typescript
await this.table!.delete(`id = '${resolvedId}'`);
try {
  await this.table!.add([updated]);
} catch (addError) {
  const current = await this.getById(original.id);
  if (current) throw new Error("write failed, but existing record preserved");
  // 嘗試回滾
  await this.table!.add([rollbackCandidate]);
}
```

---

## 6. 搜尋策略對比

| 方法 | 索引 | 分數計算 | 適用情境 |
|------|------|----------|----------|
| `vectorSearch` | Vector Index | `1 / (1 + cosine_distance)` | 語意相似度 |
| `bm25Search` | FTS Index | `sigmoid(rawBM25 / 5)` | 關鍵字精確匹配 |
| `lexicalFallback` | 無 | `scoreLexicalHit()` | FTS 失敗時回退 |

**疊加權重**（lexical fallback）：
```typescript
const score = scoreLexicalHit(query, [
  { text: entry.text, weight: 1 },
  { text: metadata.l0_abstract, weight: 0.98 },
  { text: metadata.l1_overview, weight: 0.92 },
  { text: metadata.l2_content, weight: 0.96 },
]);
```

---

## 7. 小結

| 元件 | 設計重點 |
|------|----------|
| **Store** | 向量 + FTS 雙索引；檔案鎖 cross-process 安全；update 失敗回滾 |
| **Scopes** | 內建 6 種模式；bypass/deny-all 明確區分；自動繼承 reflection scope |
| **Chunker** | 200 chars 重疊；Smart 調適 model limits；CJK 字符 special handling |
| **Migrate** | 自動偵測 legacy 路徑；欄位不足時動態補齊；dry-run 支援 |

本分析涵蓋 `store.ts`、`scopes.ts`、`chunker.ts`、`migrate.ts` 四個核心模組的設計與實現细节。