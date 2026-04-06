# Memory-LanceDB-Pro Reflection 系統深度分析

> 分析日期：2026-04-02
> 目標版本：memory-lancedb-pro (latest)

---

## 一、系統總覽

Reflection 系統是 memory-lancedb-pro 的核心模組，負責將 agent 執行後的自我檢討（reflection）文字，轉化為可inject、可搜尋、可衰減的記憶體。整個系統由五個核心模組構成：

| 檔案 | 職責 |
|------|------|
| `reflection-store.ts` | 協調儲存、載入、排名 |
| `reflection-slices.ts` | Markdown 解析 → 可注入切片 |
| `reflection-item-store.ts` | Item payload 建構（衰減模型） |
| `reflection-event-store.ts` | Event payload 建構 |
| `reflection-ranking.ts` | 分數計算（Logistic 函數） |

---

## 二、Decay 模型設計（Invariant vs Derived）

### 2.1 預設參數

| 類型 | midpointDays | k (陡峭度) | baseWeight | quality | 設計意圖 |
|------|---------------|------------|------------|---------|----------|
| **Invariant** | 45 天 | 0.22 | 1.1 | 1.0 | 長期穩定規則，衰減極緩慢 |
| **Derived** | 7 天 | 0.65 | 1.0 | 0.95 | 短期變動，衰減較快 |

### 2.2 Logistic 衰減函數

```typescript
// reflection-ranking.ts
function computeReflectionLogistic(ageDays: number, midpointDays: number, k: number): number {
  return 1 / (1 + Math.exp(k * (ageDays - midpointDays)));
}
```

- **midpointDays**：曲線中點，ageDays = midpointDays 時，score = 0.5
- **k**：曲線陡峭程度，k 越大，衰減越劇烈
- **baseWeight**：基礎權重，Invariant 為 1.1，Derived 為 1.0
- **quality**：品質因子，Invariant 固定 1.0，Derived 為 0.95
- **usedFallback**：若使用 fallback 模式，分數額外乘 0.75

### 2.3 設計意圖分析

| 特性 | Invariant | Derived |
|------|------------|---------|
| **典型內容** | 永遠的規則、偏好、约束 | 這次執行學到的教訓、下次要調整的 |
| **生命週期** | 45 天後仍有較高分數 | 7 天後快速衰減 |
| **適用場景** | SOUL.md、AGENTS.md 等持久規則 | 單次踩坑、修復記錄 |

**設計邏輯**：Invariant 代表「長期不變的知識」，即使經過 45 天也應該保持高權重；Derived 代表「這次才有的新知識」，隨時間推移逐漸失去相關性。

---

## 三、Markdown 解析 → Injectable Slices

### 3.1 切片萃取流程

```
Reflection Markdown
       │
       ▼
┌──────────────────┐
│ extractSection  │  擷取 ## Invariants / ## Derived 等章節
│   Markdown      │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ parseSection    │  解析 `- ` 開頭的 bullet points
│   Bullets       │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ sanitizeLines   │  移除 placeholder、空行、標題行
│   (基本清理)    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│   Pattern       │  進一步分類：isInvariantRuleLike
│   Matching      │  / isDerivedDeltaLike
└──────────────────┘
       │
       ▼
   ReflectionSlices
   { invariants, derived }
```

### 3.2 Pattern Matching 規則

```typescript
// isInvariantRuleLike - 符合以下任一條件視為 Invariant
/^(always|never|when\b|if\b|before\b|after\b|prefer\b|avoid\b|require\b|only\b|do not\b|must\b|should\b)/i
// 或包含 must|should|never|always|prefer|avoid|required

// isDerivedDeltaLike - 符合以下任一條件視為 Derived
/^(this run|next run|going forward|follow-up|re-check|retest|verify|confirm|avoid repeating|adjust|change|update|retry|keep|watch)\b/i
// 或包含 delta|change|adjust|retry
```

### 3.3 兩套萃取器

| 函式 | 用途 | 過濾規則 |
|------|------|----------|
| `extractReflectionSlices` | 一般儲存用 | 僅移除 placeholder |
| `extractInjectableReflectionSlices` | 供 injection 用 | **額外過濾unsafe patterns** |

### 3.4 Injectable 安全性過濾

```typescript
// 禁止注入的危險 patterns (reflection-slices.ts)
const INJECTABLE_REFLECTION_BLOCK_PATTERNS = [
  // 試圖忽略/覆寫系統指令
  /^\s*(?:(?:next|this)\s+run\s+)?(?:ignore|disregard|forget|override|bypass)\b[\s\S]{0,80}\b(?:instructions?|guardrails?|policy|developer|system)\b/i,
  
  // 試圖取得 system prompt
  /\b(?:reveal|print|dump|show|output)\b[\s\S]{0,80}\b(?:system prompt|developer prompt|hidden prompt|full prompt|prompt verbatim|secrets?|keys?|tokens?)\b/i,
  
  // HTML/XML 標籤
  /<\s*\/?\s*(?:system|assistant|user|tool|developer|inherited-rules|derived-focus)\b[^>]*>/i,
  
  // 行首標籤
  /^(?:system|assistant|user|developer|tool)\s*:/i,
];
```

---

## 四、Injection 去重機制

### 4.1 儲存時去重（storeReflectionToLanceDB）

```typescript
// 當 kind === "combined-legacy" 時觸發去重檢查
if (payload.kind === "combined-legacy") {
  const existing = await params.vectorSearch(vector, 1, 0.1, [params.scope]);
  if (existing.length > 0 && existing[0].score > dedupeThreshold) {
    continue;  // 跳過儲存
  }
}
```

- **dedupeThreshold**: 0.97（極高相似度才跳過）
- 只針對 legacy combined payload 進行去重
- Item-level payload 不去重（因為每條 invariant/derived 已經是獨立的）

### 4.2 載入時排名（loadAgentReflectionSlicesFromEntries）

```typescript
// 聚合相同內容（normalize → Map key）
const key = normalizeReflectionLineForAggregation(candidate.line);
// key = line.trim().replace(/\s+/g, " ").toLowerCase()

// 同一 key 的多筆記錄：分數疊加 + 取最新 timestamp
current.score += score;
if (timestamp > current.latestTs) {
  current.latestTs = timestamp;
  current.line = candidate.line;  // 保留最新版本
}
```

**去重策略總結**：
1. **儲存階段**：legacy combined payload 用 vector similarity 去重（0.97）
2. **載入階段**：相同 normalized line 合併，分數累加，取最新內容
3. **載入限制**：最多返回 8 條 invariant、10 條 derived

---

## 五、與 #395/447 設計提案對照

### 5.1 提案背景

GitHub Issue #395/447 提出了以下設計概念：
- **resolvedAt field**：標記 reflection 何時被「解決」（不再需要 injection）
- **memory_reflection_resolve tool**：允許 agent 主動標記 reflection 為已解決

### 5.2 現有實作 vs 提案差異

| 面向 | 現有實作 | #395/447 提案 |
|------|----------|---------------|
| **生命週期控制** | Logistic decay（45天/7天） | 主動標記 resolvedAt |
| **解決機制** | 隨時間自然衰減（被新reflection擠出） | 人工/ agent 主動標記 |
| **重複檢測** | vectorSearch (0.97) + normalized aggregation | 尚未實作 |
| **衝突處理** | 分數疊加 + 最新 timestamp | 尚未明確定義 |

### 5.3 實作觀察

1. **現有系統沒有 resolvedAt**：沒有任何 field 標記 reflection 是否已被解決
2. **現有系統純粹依賴時間衰減**：透過 logistic 函數讓舊 reflection 自然退出 top-N
3. **沒有 memory_reflection_resolve tool**：agent 無法主動標記某條 reflection 為「已解決」

### 5.4 潛在問題與改進建議

| 問題 | 現有行為 | 建議改進 |
|------|----------|----------|
| **過期 reflection 仍佔名額** | 45天後 invariant 仍有 score，但仍會被新進擠出 | 支援 resolvedAt，主動移除 |
| **Agent 無法主動清理** | 只能等自然衰減 | 新增 resolve tool |
| **Decay 參數是固定值** | 寫死在 code 中 | 考慮開放設定，或根據內容類型動態調整 |

---

## 六、資料流總結

### 6.1 儲存流程（Write Path）

```
Agent Reflection Markdown
         │
         ▼
extractInjectableReflectionSlices()
         │
         ▼
buildReflectionStorePayloads()
   ├── buildReflectionEventPayload()     → event (kind: "event")
   ├── buildReflectionItemPayloads()     → items (kind: "item-invariant" / "item-derived")
   └── buildLegacyCombinedPayload()      → combined (kind: "combined-legacy")
         │
         ▼
storeReflectionToLanceDB()
   ├── embedPassage(text) → vector
   ├── vectorSearch() → 去重檢查（僅 combined）
   └── store() → LanceDB
```

### 6.2 載入流程（Read Path）

```
LanceDB entries (filtered by agentId + category=reflection)
         │
         ▼
loadAgentReflectionSlicesFromEntries()
   ├── buildInvariantCandidates() / buildDerivedCandidates()
   │       └── 讀取 decayMidpointDays, decayK, baseWeight, quality
   │
   ▼
rankReflectionLines()
   ├── computeReflectionScore() = logistic * baseWeight * quality * fallbackFactor
   ├── normalizeReflectionLineForAggregation() → Map key
   └── 分數疊加 + 取最新 timestamp
         │
         ▼
{ invariants: string[], derived: string[] }
```

---

## 七、關鍵常數速查

| 常數 | 值 | 用途 |
|------|-----|------|
| `REFLECTION_INVARIANT_DECAY_MIDPOINT_DAYS` | 45 | Invariant 衰減中點 |
| `REFLECTION_INVARIANT_DECAY_K` | 0.22 | Invariant 衰減陡峭度 |
| `REFLECTION_DERIVED_DECAY_MIDPOINT_DAYS` | 7 | Derived 衰減中點 |
| `REFLECTION_DERIVED_DECAY_K` | 0.65 | Derived 衰減陡峭度 |
| `DEFAULT_REFLECTION_DERIVED_MAX_AGE_MS` | 14 天 | Derived 最大年齡限制 |
| `REFLECTION_FALLBACK_SCORE_FACTOR` | 0.75 | Fallback 模式分數折損 |
| `dedupeThreshold` | 0.97 | Vector 去重閾值 |

---

## 八、結論

Memory-lancedb-pro 的 Reflection 系統是一個**設計嚴謹的記憶體蒸餾系統**：

1. **Decay 模型**：使用 logistic 函數，Invariant（45天）vs Derived（7天）的設計合理，符合「長期規則 vs 短期教訓」的直覺
2. **安全性**：injectable 版本有完整的 unsafe pattern 過濾，防止 injection 攻擊
3. **去重機制**：結合 vector similarity（儲存時）與 normalized aggregation（載入時）雙重保護
4. **缺口**：相較於 #395/447 提案，缺少 resolvedAt 主動解決機制與 memory_reflection_resolve tool

**與提案對照**：現有系統更傾向「被動衰減」而非「主動解決」。若要實作 #395/447，需要在 metadata 中新增 `resolvedAt?: number` field，並新增對應的工具讓 agent 可標記已解決的 reflection。