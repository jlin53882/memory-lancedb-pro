# Memory-Lancedb-Pro 檢索引擎深度分析報告

**分析對象：** `memory-lancedb-pro` — 混合檢索系統
**分析檔案：** `src/retriever.ts`、`src/retrieval-trace.ts`、`src/retrieval-stats.ts`、`src/adaptive-retrieval.ts`
**語言：** TypeScript（Node.js / Deno 環境）

---

## 一、架構總覽：檢索管線（Retrieval Pipeline）

整個檢索系統由四層組成，形成一個**多 stage 管線**：

```
Query 輸入
    │
    ▼
┌──────────────────────────────────────────────┐
│ Adaptive Gate（shouldSkipRetrieval）          │  ← 決定是否跳過
└──────────────────────────────────────────────┘
    │ (通過閘門)
    ▼
┌──────────────────────────────────────────────┐
│ 檢索模式分流                                 │
│  ├─ Tag 前綴查詢 → BM25-only + mustContain    │
│  ├─ 純向量模式 → Vector-only                  │
│  └─ 混合模式 → Hybrid (parallel_search)       │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ RRF Fusion（融合向量 + BM25 的排名）           │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 候選池過濾（minScore threshold）               │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ Rerank（Cross-Encoder 或 Cosine Fallback）    │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 時間 / 生命週期調整                           │
│  ├─ Recency Boost（加法 bonus，新記憶優先）    │
│  ├─ Importance Weight（乘法權重，重要記憶優先） │
│  ├─ Time Decay（乘法 penalty，舊記憶降分）     │
│  └─ Decay Engine（完整生命週期系統，可選）     │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 長度正規化（Length Normalization）             │
│  防止長文字靠關鍵字密度佔據排名                │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ Hard Cutoff（低於 hardMinScore 直接丟棄）     │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 噪聲過濾（Noise Filter）                      │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ MMR Diversity（MMR 啟發式去重）               │
└──────────────────────────────────────────────┘
    │
    ▼
最終 Top-K 結果
```

---

## 二、Hybrid Retrieval 實作分析

### 2.1 三種檢索模式

| 模式 | 觸發條件 | 實作 |
|------|----------|------|
| **BM25-only** | 查詢含 tag 前綴（`proj:`, `env:`, `team:`, `scope:`） | 純 BM25，並額外做 `mustContain` 過濾 |
| **Vector-only** | `config.mode === "vector"` 或 store 不支援 FTS | 純向量相似度搜尋 |
| **Hybrid** | 預設模式，且 store 有 FTS 支援 | 向量 + BM25 **並行**搜尋 |

**並行搜尋設計亮點：**
```typescript
// vectorOnlyRetrieval / bm25OnlyRetrieval 中
trace?.startStage("parallel_search", []);
const [vectorResults, bm25Results] = await Promise.all([
  this.runVectorSearch(queryVector, candidatePoolSize, scopeFilter, category),
  this.runBM25Search(query, candidatePoolSize, scopeFilter, category),
]);
```
並行搜尋的 timing 會記錄在同一個 `parallel_search` stage 下，不會錯誤地將兩次搜尋的延遲分開計算。

---

### 2.2 RRF Fusion（Reciprocal Rank Fusion）

**標準 RRF 公式：**
```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```
其中 `k` 為常數（預設 `k=60`），`rank_i(d)` 為文件 `d` 在第 `i` 個 ranking 中的排名。

**然而此實作並非直接用標準 RRF，而是採用 `weighted score fusion` + `BM25 keyword floor`：**

```typescript
// 向量加權融合
const weightedFusion = (vectorScore * this.config.vectorWeight)
                       + (bm25Score * this.config.bm25Weight);

// BM25 keyword floor：精確關鍵字匹配（如 API key、ticket 編號）
// 即使向量分數低，只要 BM25 >= 0.75 就保留 92% BM25 分數
const fusedScore = vectorResult
  ? clamp01(
      Math.max(
        weightedFusion,
        bm25Score >= 0.75 ? bm25Score * 0.92 : 0,
      ),
      0.1,
    )
  : clamp01(bm25Result!.score, 0.1);
```

**融合策略的兩個核心洞察：**

1. **加權線性融合（0.7/0.3 預設）**：兼顧語意向量和關鍵字精確匹配
2. **BM25 keyword floor**：當 BM25 ≥ 0.75 時，確保精確匹配（ID、ticket 編號、API key）不會被向量的語意相似度淹沒。這是一個非常實用的工程取捨。

**Ghost Entry 修補（FIX #15）：**
BM25 可能回傳已從向量資料庫刪除的「幽靈」記錄。Fusion 前會檢查 `store.hasId(id)`，若不存在則跳過：
```typescript
if (!vectorResult && bm25Result) {
  const exists = await this.store.hasId(id);
  if (!exists) continue; // Skip ghost entry
}
```

---

## 三、Cross-Encoder Rerank 實作分析

### 3.1 Rerank 觸發時機

| 條件 | 是否觸發 |
|------|----------|
| `config.rerank === "none"` | ❌ 不 rerank |
| `config.rerank === "cross-encoder"` 但無 API key | ❌ Fallback cosine |
| `config.rerank === "cross-encoder"` + API key | ✅ 嘗試 cross-encoder |
| Cross-encoder API 呼叫失敗 | ❌ Fallback cosine |
| Cross-encoder API Timeout | ❌ Fallback cosine |

**Fallback 鏈：Cross-Encoder → Cosine Similarity（輕量候選）**

### 3.2 多 Provider 適配器

支援 6 種不同格式的 Rerank API：

| Provider | Request 格式 | Response 格式 |
|----------|-------------|---------------|
| Jina / SiliconFlow | `{ model, query, documents: string[], top_n }` | `results[].relevance_score` |
| Voyage | 同上，但用 `top_k` 而非 `top_n` | `data[].relevance_score` |
| Pinecone | `{ model, query, documents: {text}[], rank_fields, top_n }` | `data[].score` |
| TEI | `{ query, texts: string[] }` | `results[]` 或 `data[]` 含 `score` |
| DashScope | `{ model, input: { query, documents } }` | `output.results[].relevance_score` |

實作採用**Provider Adapter Pattern**：每個 provider 有獨立的 request builder 和 response parser，隔離差異。

### 3.3 Rerank 分數混合

```typescript
// 60% cross-encoder 分數 + 40% 原始融合分數
const blendedScore = clamp01WithFloor(
  item.score * 0.6 + original.score * 0.4,
  floor,
);
```

**Preservation Floor（保障分數下限）：**

| BM25 分數 | 未返回（dropped）| 已返回 |
|-----------|----------------|--------|
| ≥ 0.75 | 100% 原分數 | 95% 原分數 |
| ≥ 0.6 | 95% 原分數 | 90% 原分數 |
| < 0.6 | 80% 原分數 | 50% 原分數 |

這個機制確保**精確關鍵字匹配**（BM25 ≥ 0.75）在 rerank 失敗或被降序時，不會完全消失。

### 3.4 Cosine Fallback

當 cross-encoder API 不可用時，使用 cosine similarity 做 lightweight rerank：
```typescript
const cosineScore = cosineSimilarity(queryVector, result.entry.vector);
const combinedScore = result.score * 0.7 + cosineScore * 0.3;
```
- Cosine similarity 只需查詢向量和文件向量，無需重新編碼文件
- 比例 70% fused score + 30% cosine，避免完全偏離原始排名

---

## 四、時間衰減與重要性權重分析

### 4.1 Recency Boost（加法 bonus）

**公式：**
```typescript
boost = Math.exp(-ageDays / recencyHalfLifeDays) * recencyWeight
finalScore = clamp01(originalScore + boost)
```

- 適用場景：新記憶比舊記憶略佔優勢，**當語意分數接近時**可以獲勝
- 預設 half-life = 14 天，weight = 0.1
- 為**加法**而非乘法，確保新記憶不會因為 boost 破壞原始分數的比例關係
- 14 天後 boost 降為 `e^(-1) * 0.1 ≈ 0.037`

### 4.2 Importance Weight（乘法權重）

**公式：**
```typescript
factor = baseWeight + (1 - baseWeight) * importance  // baseWeight = 0.7
finalScore = clamp01(originalScore * factor)
```

| Importance 值 | Factor | 效果 |
|---------------|--------|------|
| 1.0（最高） | 1.0 | 不變 |
| 0.7（預設） | 0.91 | ×0.91 |
| 0.5 | 0.85 | ×0.85 |
| 0.0 | 0.7 | ×0.7（最低保障） |

**乘法設計**：重要性影響分數的**相對比例**，而不只是固定加成。

### 4.3 Time Decay（乘法 penalty，與 Recency Boost 對比）

| 特性 | Recency Boost | Time Decay |
|------|---------------|------------|
| 類型 | 加法 bonus | 乘法 penalty |
| 方向 | 新記憶加分 | 舊記憶減分 |
| 預設值 | 14 天半衰期 / 0.1 weight | 60 天半衰期 |
| 最低 Floor | 無（可疊加） | 0.5x（永不低於 50%）|
| 與 Decay Engine 衝突？ | 只在無 Decay Engine 時啟用 | 只在無 Decay Engine 時啟用 |

**Time Decay 公式：**
```typescript
factor = 0.5 + 0.5 * Math.exp(-ageDays / effectiveHL)
finalScore = clamp01(originalScore * factor, originalScore * 0.5)
```

| 天數（60 天 half-life）| Factor |
|------------------------|--------|
| 0 天 | 1.00x（無 penalty）|
| 60 天（1 half-life）| ~0.68x |
| 120 天（2 half-life）| ~0.59x |
| 240 天（4 half-life）| ~0.52x |
| ∞（非常老）| → 0.5x（floor）|

**Access Reinforcement**：頻繁存取的記憶，effective half-life 會延長：
```typescript
const effectiveHL = computeEffectiveHalfLife(
  halfLife,            // 60 天
  accessCount,         // 存取次數
  lastAccessedAt,      // 上次存取時間
  reinforcementFactor, // 0.5
  maxHalfLifeMultiplier // 3x
);
```
被經常存取的記憶，half-life 可延長最多 3 倍（180 天），**防止「活躍記憶」被線性衰減消滅**。

---

## 五、Length Normalization 分析

**目標：** 防止長文字靠關鍵字密度壟斷排名

**公式：**
```typescript
factor = 1 / (1 + 0.5 * log2(charLen / anchor))  // anchor = 500
```

| 字元長度 | Factor | 說明 |
|----------|--------|------|
| ≤ 500 | ~1.0 | 無 penalty（短文小幅 boost）|
| 800 | ~0.75 | 輕微 penalty |
| 1000 | ~0.67 | |
| 1500 | ~0.56 | |
| 2000 | ~0.50 | 半衰 penalty |
| 4000 | ~0.38 | |

**對數衰減**：長度的 penalty 是對數而非線性的，長度增加 4 倍（500→2000），penalty 從 1.0→0.5，只衰減一半，比較溫和。

**設計取捨：** 對數 penalty 避免短文完全被長文淹沒，但也不會完全抹殺長文的價值。

---

## 六、Adaptive Retrieval Gate（自適應檢索閘門）

### 6.1 決策邏輯

```
shouldSkipRetrieval(query)
  │
  ├─ [FORCE 優先] 含 "remember/recall/forgot/memory/上次/你記得" → 不跳過
  │
  ├─ trimmed.length < 5 → 跳過
  │
  ├─ 匹配 SKIP_PATTERNS（問候語、斜線指令、純 emoji 等）→ 跳過
  │
  ├─ 有 minLength 參數時：
  │   ├─ 長度 < minLength 且不含問號 → 跳過
  │   └─ 否則 → 不跳過
  │
  ├─ 預設長度閾值：
  │   ├─ 含有 CJK 字符 → 閾值 = 6（含 CJK 的 query 語意密度高）
  │   └─ 純英文 → 閾值 = 15
  │   且不含問號 → 跳過
  │
  └─ 預設 → 不跳過（執行檢索）
```

### 6.2 CJK 特殊處理

```typescript
const hasCJK = /[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]/.test(trimmed);
const defaultMinLength = hasCJK ? 6 : 15;
```
這是合理的設計：CJK 字符承載的語意密度高，3 個中文字就能構成一個有意義的查詢，而英文需要更多字符。

### 6.3 OpenClaw Cron Prompt 正規化

```typescript
// 移除 OpenClaw 注入的中繼資料前綴
s = s.replace(/^\[cron:[^\]]+\]\s*/i, "");
s = s.replace(/^\[[A-Za-z]{3}\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s[^\]]+\]\s*/, "");
s = s.replace(/^(Conversation info|Sender) \(untrusted metadata\):[\s\S]*?\n\s*\n/gim, "");
```
防止 cron 自動化觸發時，帶有系統前綴的 prompt 被誤判為「命令式」而跳過檢索。

---

## 七、Pipeline 觀測性設計（Trace + Stats）

### 7.1 TraceCollector（單次查詢追蹤）

每個 stage 記錄：
- `inputCount` / `outputCount`：進出人數
- `droppedIds`：被過濾的 ID 列表
- `scoreRange[min, max]`：分數範圍
- `durationMs`：牆鐘時間

**零開銷設計：**
```typescript
const trace = this._statsCollector ? new TraceCollector() : undefined;
// 只有在 statsCollector 啟用時才建立 trace
```

### 7.2 RetrievalStatsCollector（彙總統計）

滾動視窗（預設 1000 筆記錄），計算：
- **延遲指標**：avg、p95
- **品質指標**：零結果率、rerank 使用率、noise filter 移除率
- **瓶頸分析**：topDropStages（哪些 stage 丟棄最多結果）

**`topDropStages` 的價值：** 可以發現系統瓶頸——例如若 `noise_filter` 經常大量刪除結果，可能表示 noise filter 太 aggressive。

---

## 八、可以借鑒到其他系統的設計

### 8.1 BM25 Keyword Floor（高價值）

```typescript
bm25Score >= 0.75 ? bm25Score * 0.92 : 0
```
這個模式確保**精確匹配（如 ID、代號、ticket 編號）**不被 semantic search 淹沒，是混合系統中非常實用的技巧。

### 8.2 Ghost Entry 修補

在 RRF 前驗證文件是否真正存在於 store 中，是防止 FTS index 和 vector store 不一致的好習慣。

### 8.3 Preservation Floor

Cross-encoder 降序時，保留一個 min 分數（而非直接刪除），並根據 BM25 分數高低決定保留程度。

### 8.4 MMR Diversity（MMR 啟發式）

```typescript
// 相似度 > 0.85 → defer（不刪除，移到最後）
const tooSimilar = selected.some(s => cosineSimilarity(sVec, cVec) > threshold);
if (tooSimilar) deferred.push(candidate);
```
**不刪除**相似項目，只**延後**，維持結果池大小的同時避免重複佔據 top-k。

### 8.5 Adaptive Gate 的 CJK 閾值

根據語言調整最短長度閾值，對多語言系統很有參考價值。

### 8.6 Access Reinforcement for Time Decay

結合存取頻率動態調整半衰期，防止活躍記憶被直線衰減消滅，是「用進廢退」概念的良好實作。

### 8.7 多 Provider Rerank Adapter

統一的 request builder / response parser 讓切換 rerank 服務商幾乎零成本，是好擴展性的典範。

### 8.8 分層分數調整（加法 vs 乘法）

| 調整類型 | 用途 | 範例 |
|----------|------|------|
| 加法（Recency Boost）| 微調、相對排名 | 新記憶略優先 |
| 乘法（Importance / Time Decay）| 縮放比例 | 重要記憶放大差距 |
| 乘法 + Floor（Time Decay）| 有下限的penalty | 舊記憶不會歸零 |

三種調整模式分層疊加，每層有明確的數學含義和工程意圖。

---

## 九、潛在觀察與限制

1. **RRF 參數 `k` 未暴露**：標準 RRF 的 `k=60` 是隱含常數，若能與 vectorWeight/bm25Weight 同等暴露為設定項，會更靈活。

2. **Rerank Fallback 順序**：Cosine fallback 依賴文件向量存在於 `entry.vector`，若向量資料庫有空洞會失效。建議 fallback 前加 `hasId` 檢查。

3. **MMR 相似度閾值（0.85）硬編碼**：雖然 MMR Diversity 是可選 stage，但相似度閾值寫死在程式碼中，未暴露為設定參數。

4. **Stats Collector 無持久化**：`_records` 在記憶體中，重啟後丢失。若需要長期趨勢分析，需額外寫入磁碟或外接監控系統。

5. **Time Decay 與 Decay Engine 二選一**：`if (this.decayEngine)` 邏輯說明兩者是互斥的，系統不支援同時使用。若 Decay Engine 存在，recency boost + time decay 都被跳過，由 Decay Engine 統一處理。

---

*報告生成時間：2026-04-02*
*分析工具：memory-lancedb-pro source code（TypeScript）*
