# memory-lancedb-pro 記憶分類、邊界與意圖系統深度分析報告

> 分析目標：C:\Users\admin\.openclaw\memory-lancedb-pro  
> 分析日期：2026-04-02  
> 分析語系：繁體中文

---

## 一、記憶分類系統（memory-categories.ts）

### 1.1 六類記憶的定義與邊界

本系統定義了 **六類相互獨立但有生命週期關聯的記憶類別**：

| 類別 | 用途定位 | 內容特徵 |
|------|----------|----------|
| **profile** | 使用者背景資訊 | 時區、代詞、協作風格、語言偏好等靜態屬性 |
| **preferences** | 使用者偏好 | 飲食習慣、工具偏好、互動風格等動態偏好 |
| **entities** | 實體資訊 | 姓名、專案名稱、團隊成員、產品等具名實體 |
| **events** | 事件記錄 | 上線、部署、發布、incident 等時間線事件 |
| **cases** | 案例/對話上下文 | 特定對話的問題、解決方案、踩坑記錄 |
| **patterns** | 模式/慣例 | 程式碼風格、命名慣例、決策模式等可复用的模式 |

### 1.2 跨類別重疊的處理策略

系統透過 **四種不同的生命週期策略** 來處理類別間的邊界模糊問題：

#### (1) ALWAYS_MERGE（強制合併）
```typescript
export const ALWAYS_MERGE_CATEGORIES = new Set<MemoryCategory>(["profile"]);
```
- `profile` 類別永遠不保留歷史版本
- 新提取的 profile 資訊直接覆蓋舊版本
- **防止重複**：避免時區從 "Asia/Taipei" 變成 "America/NewYork" 時產生兩筆衝突記錄

#### (2) TEMPORAL_VERSIONED（時間版本化）
```typescript
export const TEMPORAL_VERSIONED_CATEGORIES = new Set<MemoryCategory>([
  "preferences",
  "entities",
]);
```
- 支援 `supersede` 決策（取代）而非刪除歷史
- 保留變更軌跡但標記最新事實
- **範例**：使用者說「我討厭吃香菜」→ 舊記錄標為 superseded，新記錄作為 active

#### (3) APPEND_ONLY（僅附加）
```typescript
export const APPEND_ONLY_CATEGORIES = new Set<MemoryCategory>([
  "events",
  "cases",
]);
```
- 不允許 MERGE，僅支援 CREATE 或 SKIP
- 事件與案例是時間序列，合併會喪失時序資訊
- **範例**：兩次部署 incident 不能合併，必須各自獨立記錄

#### (4) MERGE_SUPPORTED（可合併）
```typescript
export const MERGE_SUPPORTED_CATEGORIES = new Set<MemoryCategory>([
  "preferences",
  "entities",
  "patterns",
]);
```
- 允許 LLM 輸出 MERGE 決策進行去重
- 但非強制，由 LLM 判斷是否真的需要合併

### 1.3 去重決策類型

```typescript
type DedupDecision =
  | "create"      // 新建立
  | "merge"       // 與現有合併
  | "skip"        // 跳過（與現有完全重複）
  | "support"     // 補充支援現有記憶
  | "contextualize" // 為現有記憶提供上下文
  | "contradict"  // 與現有記憶矛盾
  | "supersede";  // 取代舊有事實
```

這個設計的巧妙之處在於：**並非所有類別都使用同一套去重邏輯**，而是由類別特性決定行為。

---

## 二、USER.md 邊界管控（workspace-boundary.ts）

### 2.1 設計理念

USER.md 是使用者資訊的 **Single Source of Truth（單一真相來源）**。系統透過邊界管控防止：
1. **記憶污染**：不讓 LanceDB 中的使用者資訊覆蓋 USER.md
2. **資訊不一致**：強制路由特定類別的記憶回到 USER.md
3. **檢索洩漏**：recall 時過濾掉應由 USER.md 壟斷的資訊

### 2.2 邊界槽位（Boundary Slots）

```typescript
type UserMdExclusiveSlot = "profile" | "name" | "addressing";
```

三個專屬槽位：
- **profile**：所有與使用者背景相關的資訊（時區、代詞、工作方式）
- **name**：使用者的姓名/自稱
- **addressing**：使用者偏好的稱呼方式

### 2.3 邊界觸發條件

```typescript
function isUserMdExclusiveMemory(params, workspaceBoundary) {
  const slots = new Set<UserMdExclusiveSlot>();
  
  // 觸發條件 1：明確標記為 profile 類別
  if (params.memoryCategory === "profile") {
    slots.add("profile");
  }
  
  // 觸發條件 2：透過 identity-addressing 分析偵測 name/addressing
  const semantics = classifyIdentityAndAddressingMemory(params);
  if (semantics.slots.has("name")) slots.add("name");
  if (semantics.slots.has("addressing")) slots.add("addressing");
  
  // 觸發條件 3：正則表達式探針（PROFILE_HINT_PATTERNS）
  const probe = [params.text, params.abstract, params.overview, params.content]
    .filter(...).join("\n");
  if (PROFILE_HINT_PATTERNS.some(pattern => pattern.test(probe))) {
    slots.add("profile");
  }
  
  // 只要命中任一 enabled 路由，就視為 USER.md 獨占
  return (config.routeProfile && slots.has("profile")) ||
         (config.routeCanonicalName && slots.has("name")) ||
         (config.routeCanonicalAddressing && slots.has("addressing"));
}
```

### 2.4 邊界行為

| 行為 | 說明 |
|------|------|
| **routeProfile** | profile 類別的候選記憶不寫入 LanceDB，保留給 USER.md |
| **routeCanonicalName** | 姓名資訊不寫入 LanceDB，保留給 USER.md |
| **routeCanonicalAddressing** | 稱謂偏好不寫入 LanceDB，保留給 USER.md |
| **filterRecall** | recall 時過濾掉這些獨占資訊，避免重複暴露 |

### 2.5 防止記憶污染的機制

1. **寫入時過濾**：`isUserMdExclusiveEntry()` 在候選記憶寫入前攔截
2. **檢索時過濾**：`filterUserMdExclusiveRecallResults()` 在 recall 回傳前篩選
3. **雙軌驗證**：即使 USER.md 缺失，也有 identity-addressing 作為 fallback 偵測

---

## 三、身份與稱謂語意分類（identity-addressing.ts）

### 3.1 設計目標

將 **自然語言中表達姓名與稱謂偏好** 的各種方式統一映射到標準化的記憶格式。

### 3.2 支援的表達模式

#### 姓名表達（NAME_PATTERNS）
```typescript
// 中文
/(?:我的名字是|我(?:现在)?叫|本名是)\s*([^\s，。,.!！?？"'""''「」『』]+)/iu

// 英文
/calls?\s+themselves\s+['"]([^'"]+)['"]/i
/name\s+is\s+['"]?([^'".,\n]+)['"]?/i
```

#### 稱謂偏好表達（ADDRESSING_PATTERNS）
```typescript
// 中文
/(?:以后你叫我|以后请叫我|请叫我|以后称呼我(?:为)?|称呼我(?:为)?|称呼其为|称呼他为)\s*([^\s，。,.!！?？"'""''「」『』]+)/iu

// 英文
/Preferred address(?: is)?|be addressed as|addressed as\s*['"]?([^'".,\n]+)['"]?/i
```

### 3.3 標準化輸出格式

無論原始表達如何，都轉換為統一的候選記憶格式：

```typescript
// 姓名 → entities 類別
{
  category: "entities",
  abstract: `姓名：${alias}`,
  overview: `## Identity\n- Name: ${alias}`,
  content: `用户当前姓名/自称为"${alias}"。原始表述：${sourceText}`
}

// 稱謂偏好 → preferences 類別
{
  category: "preferences",
  abstract: `称呼偏好：${alias}`,
  overview: `## Addressing\n- Preferred form of address: ${alias}`,
  content: `用户希望以后被称呼为"${alias}"。原始表述：${sourceText}`
}
```

### 3.4 事實鍵（Fact Key）標準化

```typescript
export const CANONICAL_NAME_FACT_KEY = "entities:姓名";
export const CANONICAL_ADDRESSING_FACT_KEY = "preferences:称呼偏好";
```

使用 `entities:欄位名` 和 `preferences:欄位名` 的語意化鍵名，方便後續檢索與比對。

### 3.5 去重與正規化邏輯

```typescript
function canonicalizeIdentityAndAddressingCandidate(candidate) {
  // 1. 如果候選記憶已是 entities 類別
  if (candidate.category === "entities") {
    // 嘗試提取姓名
    const name = extractFirst(NAME_PATTERNS, combined);
    if (name) return makeCandidate("name", name, ...);
    
    // 嘗試提取稱謂（可能混在一起）
    const addressing = extractFirst(ADDRESSING_PATTERNS, combined);
    if (addressing) return makeCandidate("addressing", addressing, ...);
  }
  // ... 反向處理 preferences
}
```

這個設計確保了 **即使一開始分類錯誤，也能被修正**。

---

## 四、查詢意圖分析（intent-analyzer.ts）

### 4.1 設計理念

Intent Analyzer 是 **輕量級、規則驅動的意圖分類系統**，旨在：
- 不呼叫 LLM（避免延遲）
- 為每次檢索提供 **類別優先序 + 深度** 的信號
- 啟發自 OpenViking 的分層檢索架構

### 4.2 意圖類別與檢索目標的映射

```typescript
type MemoryCategoryIntent =
  | "preference"  // 偏好查詢
  | "fact"       // 知識/事實查詢
  | "decision"   // 決策/理由查詢
  | "entity"     // 實體/人物查詢
  | "other";    // 其他
```

注意：**"event" 不是儲存類別**，事件查詢會路由到 `entity + decision`（最可能包含時間線資料的類別）。

### 4.3 檢索深度（Recall Depth）

```typescript
type RecallDepth = "l0" | "l1" | "full";
```

| 深度 | 用途 | 輸出格式 |
|------|------|----------|
| **l0** | 極度壓縮 | 一行摘要（類別 + 80 字內） |
| **l1** | 中等詳細 | 類別 + scope + 300 字內 |
| **full** | 完整內容 | 完整原文 |

### 4.4 意圖規則優先順序

```typescript
const INTENT_RULES: IntentRule[] = [
  // 1. Preference / Style（最常見，先匹配）
  { label: "preference", categories: ["preference", "decision"], depth: "l0" },
  
  // 2. Decision / Rationale
  { label: "decision", categories: ["decision", "fact"], depth: "l1" },
  
  // 3. Entity / People / Project
  { label: "entity", categories: ["entity", "fact"], depth: "l1" },
  
  // 4. Event / Timeline（事件路由到 entity + decision）
  { label: "event", categories: ["entity", "decision"], depth: "full" },
  
  // 5. Fact / Knowledge
  { label: "fact", categories: ["fact", "entity"], depth: "l1" },
];
```

**匹配策略**：First-match-wins，按特異性排序（高置信度規則置頂）。

### 4.5 意圖如何影響檢索排序

```typescript
function applyCategoryBoost(results, intent, boostFactor = 1.15) {
  const prioritySet = new Set(intent.categories);
  
  return results.map(r => {
    if (prioritySet.has(r.entry.category)) {
      // 匹配的類別，boost 分數
      return { ...r, score: Math.min(1, r.score * boostFactor) };
    }
    return r;
  }).sort((a, b) => b.score - a.score);
}
```

**關鍵設計**：
- **不過濾**：保留所有結果，只是調整排序
- **boost 而非替換**：分數加成限於 1.15x，避免完全覆蓋向量相似度
- **低置信度時 bypass**：若 `intent.confidence === 'low'`，直接返回原始排序

### 4.6 輸出格式與注入上下文

```typescript
function formatAtDepth(entry, depth, score, index, extra?) {
  // l0: - [preference] 偏好內容... (85%)
  // l1: - [preference:workspace] 中等詳細內容... (85%, vector+BM25)
  // full: - [preference:workspace] 完整內容... (85%)
}
```

注入時自動攜帶：
- 類別標籤
- scope 範圍
- 分數百分比
- 來源標記（vector / BM25 / reranked）

---

## 五、偏好槽位推斷（preference-slots.ts）

### 5.1 設計目標

從非結構化的自然語言偏好描述中，結構化地提取 **品牌-品項** 的原子偏好槽位。

### 5.2 支援的表達模式

#### 中文品牌-品項模式
```typescript
/(?:^|[\s，,。；;！!？?])(?:我|用户)?(?:很|更|还)?(?:喜欢|爱吃|偏爱|常吃|想吃)(?:吃|喝|用|买)?
(?<brand>[\p{Script=Han}A-Za-z0-9&·'\-]{1,24})
的(?<items>[\p{Script=Han}A-Za-z0-9&·'\-\s、,，和及与/]{1,80})/u
```

#### 英文品牌-品項模式
```typescript
/\b(?:i|user)?\s*(?:really\s+|still\s+|also\s+)?(?:like|love|prefer|enjoy)\s+
(?<items>[a-z0-9'&\-\s]{1,80})\s+from\s+
(?<brand>[a-z0-9'&\-\s]{1,40})/iu
```

### 5.3 推斷結果格式

```typescript
interface AtomicBrandItemPreferenceSlot {
  type: "brand-item";
  brand: string;   // 品牌名
  item: string;   // 具體品項
}
```

### 5.4 推斷邏輯流程

```
1. 正規化文字（去除角色前綴 [用戶]）
     ↓
2. 比對 BRAND_ITEM_PREFERENCE_PATTERNS
     ↓
3. 提取 brand + items 群組
     ↓
4. 分割 items（按 、,，/ 及 和 and 等分隔符）
     ↓
5. 正規化每個 item（去除冠詞、空白）
     ↓
6. 若為單一 item → 產出 AtomicBrandItemPreferenceSlot
   若為多項 items → 視為 aggregate（需要 further processing）
```

### 5.5 關鍵正規化步驟

```typescript
function normalizePreferenceToken(value: string): string {
  return value
    .replace(ROLE_PREFIX_RE, "")           // 去除 [用戶] 等前綴
    .replace(/^[""'`'']+|[""'`''。！？,，；;:：]+$/gu, "")  // 去除引號標點
    .replace(/\b(?:the|a|an)\s+/giu, "")  // 去除英文冠詞
    .replace(/\s+/g, "")                  // 去除空白
    .toLowerCase();                       // 統一小寫
}
```

### 5.6 應用場景

此槽位推斷主要用於：
- **偏好比對**：當使用者說「我想喝星巴克的咖啡」時，快速匹配「星巴克」+ 「咖啡」的槽位
- **偏好聚合**：收集多個品牌-品項的 atomic slots，構成完整的使用者偏好地圖
- **檢索 boost**：可在 recall 時針對特定 slot 進行加權

---

## 六、系統整合視角

### 6.1 資料流總覽

```
User Input
    ↓
┌─────────────────────────┐
│ 1. Intent Analyzer      │ ← 決定檢索類別 + 深度
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 2. LanceDB Recall      │ ← 向量 + BM25 檢索
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 3. Category Boost       │ ← 根據意圖信號調整排序
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 4. USER.md Boundary    │ ← 過濾獨占記憶
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 5. Memory Extraction   │ ← LLM 產生候選記憶
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 6. Dedup & Categorize   │ ← 去重 + 分類決策
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 7. Preference Slots     │ ← 結構化偏好槽位
└─────────────────────────┘
    ↓
Write to LanceDB
```

### 6.2 關鍵設計原則

| 原則 | 實作方式 |
|------|----------|
| **類別自治** | 每類記憶有獨立的生命週期策略（merge / versioned / append-only） |
| **邊界保守** | USER.md 獨占資訊不寫入 LanceDB，確保 Single Source of Truth |
| **意圖驅動** | 規則驅動的意圖分類，影響檢索排序而非過濾 |
| **原子化偏好** | 將自然語言偏好轉為結構化 slot，便於比對與聚合 |
| **零 LLM 延遲** | Intent Analyzer 和 Preference Slots 都是 pure regex，無需 API 呼叫 |

---

## 七、分析總結

memory-lancedb-pro 的這五個模組構成了一套 **自給自足的記憶管理系統**：

1. **memory-categories.ts** 定義了清晰的類別邊界，透過生命週期策略處理跨類別重疊
2. **workspace-boundary.ts** 確保 USER.md 作為使用者資訊的唯一來源，防止記憶污染
3. **identity-addressing.ts** 將姓名與稱謂的各種表達方式標準化
4. **intent-analyzer.ts** 提供輕量級的意圖分類，影響檢索結果的呈現方式
5. **preference-slots.ts** 將非結構化偏好轉為結構化槽位，便於後續應用

這套系統的設計哲學是：**在記憶提取時盡可能結構化，在檢索呈現時保持彈性**。透過規則驅動的意圖分析 + 類別導向的 boost 策略，達到「少噪音、精準排序」的效果，同時保持系統的輕量與高效。

---

*報告結束*
