# PR #246 — Proposal A & B 詳細分析報告

> 分析日期：2026-04-02
> 分析範圍：C:\Users\admin\Desktop\memory-lancedb-pro-import-markdown-test
> 分析方式：Sub-agent 分批閱讀 36 個核心檔案 + 主文件分析

---

## 一、現有系統能力盤點

### 1.1 現有的 Importance/Boost 機制

| 機制 | 檔案 | 說明 |
|------|------|------|
| **靜態 Importance** | `store.ts` | 寫入時預設 `0.7`，寫入後固定不變 |
| **Weibull Decay** | `decay-engine.ts` | `importance` 調制半衰期長度：`effectiveHL = halfLife × exp(μ × importance)`， importance 越高衰減越慢 |
| **Frequency Reinforcement** | `access-tracker.ts` | 高頻訪問 → 半衰期延長（最多 3x），`effectiveHL = baseHL + baseHL × reinforcementFactor × log1p(effectiveAccessCount)` |
| **Tier 分層** | `tier-manager.ts` | Core（β=0.8，最慢衰減）/ Working（β=1.0）/ Peripheral（β=1.3，最快衰減）|
| **Importance Weight 在檢索時** | `retriever.ts` | `applyImportanceWeight()`：`score *= (0.7 + 0.3 × importance)`，但寫入後靜態 |
| **Confirmed Use 追蹤** | `smart-metadata.ts` | `last_confirmed_use_at` 欄位已存在，但**目前未被用於動態調整** |
| **Bad Recall 抑制** | `smart-metadata.ts` | `bad_recall_count` / `suppressed_until_turn` 已存在，但**未被主動觸發** |
| **Reflection Quality Weight** | `reflection-store.ts` | `quality × logistic(age) × baseWeight`，已實現動態衰減 |

**結論**：系統有 frequency reinforcement（頻率強化），但**沒有根據「記憶被引用/確認正確/標錯」來動態調整 importance 的機制**。

---

### 1.2 Proposal B 可切入的現有基礎

| 現有能力 | 檔案 | 與 Proposal B 的關係 |
|----------|------|---------------------|
| **MMR Diversity** | `retriever.ts` | 相似記憶只會被延後，不會被擴展 |
| **Reflection Lines** | `reflection-store.ts` | 已有 `loadAgentReflectionSlicesFromEntries()`，輸出時取 top-8/10，可做鄰居擴展 |
| **Chunk Overlap** | `chunker.ts` | 200 chars 重疊，勉強算粗糙的鄰居上下文 |
| **Support/Contradiction Tracking** | `smart-metadata.ts` | `ContextualSupport.strength` 存在，但不用於 recall 排序 |
| **LLM Merge/Skip Dedup** | `memory-categories.ts` | `create/merge/skip/support/contradict` decision 已有類似關係建模，但僅用於寫入時去重 |

**結論**：Proposal B 的鄰居擴展在 retrieval 階段**沒有現成架構**，reflection 有類似機制但用途不同。

---

### 1.3 關鍵缺口

| 缺口 | 說明 |
|------|------|
| **LanceDB `importance` 寫入後靜態** | `store.ts` 的 `importance` 欄位只在寫入時設定，沒有根據使用行為動態更新的路徑 |
| **`last_confirmed_use_at` 有欄位無邏輯** | metadata 追蹤了「記憶被真正用到」的時間，但 decay/boost 計算不看這個欄位 |
| **`bad_recall_count` 未被觸發** | 錯誤召回抑制機制已定義，但沒有實際的觸發寫入點 |
| **Reflection 與主 Retrieval 脫鉤** | `loadAgentReflectionSlicesFromEntries()` 有自己的衰減評分，但主 recall 不會對結果再做鄰居擴展 |
| **Chunk Averaging 無重要性感知** | 多 chunk 文本的 embedding 只做平均，沒有根據 chunk 重要性加權 |

---

## 二、Proposal A — 動態 Importance 設計

### 2.1 核心設計方向

**目標**：讓 `importance` 從「寫入時固定」變成「使用後動態調整」。

**現有頻率強化的極限**（`access-tracker.ts`）：
```
effectiveHL = baseHL + baseHL × reinforcementFactor × log1p(effectiveAccessCount)
```
這只是「用越多越慢衰減」，不是「根據使用品質調整 importance 本身」。

### 2.2 建議的 Feedback Signal 與調整幅度

| 信號 | 捕捉時機 | 調整方式 |
|------|---------|---------|
| **被引用進回應** | agent 回應後，檢查是否包含 recall 結果的內容 | `importance += 0.05`，上限 1.0 |
| **user 明確確認正確** | user 說「對」「沒錯」| `importance += 0.15`，上限 1.0 |
| **user 標記錯誤** | user 說「不對」「錯了」| `importance -= 0.10`，下限 0.1 |
| **召回後沒被用到** | 連續 2 次被召回但都沒被引用 | `importance -= 0.03` |
| **長期未使用** | 超過 30 天未有任何 access | `importance` 慢慢回歸預設值（被 decay 自然稀釋）|

### 2.3 實作切入點

**最自然的 hook 點**：`agent_end` Hook（`index.ts` 已存在）
```
agent_end 事件
  → 取出本輪 auto-recall 的結果
  → 比對 agent 回應內容
  → 根據 feedback 信號更新對應記憶的 importance
  → 寫回 LanceDB（透過 store.patchMetadata 或 store.update）
```

**為什麼用 `agent_end` 而不是別的時機**：
- `before_agent_start` 發生在 recall 之後，此時無法判斷回應是否真的用了記憶
- `agent_end` 已有完整的 `event.messages`，可以比對 recall 結果和最終回應
- 不需要新增 lifecycle trigger，只需要在現有的 `agent_end` 流程中加一個後處理步驟

### 2.4 與現有系統的整合

| 現有元件 | 整合方式 |
|---------|---------|
| `decay-engine.ts` | **不需要改**。decay 已經吃 `importance` 做半衰期調制，importance 變了他自然會重新計算 |
| `tier-manager.ts` | Core 晉升條件：`importance >= 0.8`。動態調整的 importance 會自然觸發或阻止晉升 |
| `store.ts` | 用 `patchMetadata()` 或 `update()` 局部更新 importance 欄位 |
| `smart-metadata.ts` | `last_confirmed_use_at` 和 `bad_recall_count` 可以同步更新 |
| `access-tracker.ts` | **不需要改**。頻率追蹤和 importance 調整是兩條獨立路徑，互補不衝突 |

### 2.5 風險與對策

| 風險 | 對策 |
|------|------|
| Importance 反覆調整造成震盪 | 加入 `importanceUpdatedAt` 欄位，每次調整後冷卻 3 輪對話 |
| 錯誤的 negative feedback 造成記憶被汙染 | 設置下限：`importance` 最低 0.1，不會降到零而被 decay 完全淘汰 |
| 沒有明確的 positive/negative 信號時怎麼辦 | 預設「召回等於引用」：有被 recall 就算一次正向，隨時間衰減 |

---

## 三、Proposal B — Attention-Like Neighbor Enrichment 設計

### 3.1 核心設計方向

**目標**：當某條記憶被 recall 回來時，主動去找它的「鄰居」記憶，一起帶進上下文。

**與 Proposal A 的關係**：Proposal B 是獨立的，不需要 Proposal A。但 Proposal A 產生的動態 importance 可以讓 B 的鄰居選擇更精準。

### 3.2 兩種實作路徑

#### 路徑 B-1（推薦）：在 reflection recall 時擴展

Reflection 已有完整的鄰居建模機制（`loadAgentReflectionSlicesFromEntries()`），只需在輸出 top-8/10 之後，多做一圈鄰居搜尋：

```
loadAgentReflectionSlicesFromEntries() → 輸出 N 條
  → 對每條做 bm25Search(entry.text, topK=3, scope=同scope)
  → 合併去重
  → 輸出（原有 + 鄰居）→ 帶進上下文
```

**優點**：
- 只影響 reflection recall，不影響主 retrieval 延遲
- 現有 `reflection-store.ts` 的衰減模型可以直接複用
- 不需要新增基礎架構

**缺點**：
- 只對 reflection 記憶有效，不影響普通 memories 表

#### 路徑 B-2（完整版）：在 retriever 输出後做 neighbor boost

在 `retriever.ts` 的 `retrieve()` 完成後、返回結果前：

```
retrieve() → [記憶A, 記憶B, 記憶C]
  → 對每條做 vectorSearch(text, topK=3, scope=同scope)
  → 鄰居們加入候選池
  → 依相似度 + importance 重新排序
  → 輸出（原本 + 重要鄰居）
```

**優點**：對所有記憶類型都有效。

**缺點**：
- 對每條 recall 結果多做一次 vector 搜尋，延遲增加
- 需要限制擴展深度（建議最多 1 hop + 每條取 top-2）
- 可能把不相關的記憶帶進來

### 3.3 實作切入點

**最自然的 hook 點**：在 `retriever.ts` 的 `retrieve()` 方法末尾，在 MMR diversity 之後、返回結果之前，插入 neighbor enrichment 步驟。

### 3.4 與現有系統的整合

| 現有元件 | 整合方式 |
|---------|---------|
| `retriever.ts` | `retrieve()` 後處理 chain 可插入鄰居擴展 |
| `store.ts` | `bm25Search()` 和 `vectorSearch()` 已經可以直接呼叫，不需要新增 API |
| `smart-metadata.ts` | `access_count` 和 `importance` 可以用於控制擴展深度（高 importance 的記憶擴展多一點）|
| MMR Diversity | **可能衝突**：MMR 會把相似記憶延後，與 neighbor enrichment 方向相反。需要調整 MMR 邏輯 |

### 3.5 風險與對策

| 風險 | 對策 |
|------|------|
| 記憶數量膨脹，上下文爆炸 | 限制：每條 recall 結果最多擴展 2 個鄰居，總輸出上限 20 條 |
| 引入不相關記憶 | 只擴展 `scope` 相同的記憶 |
| MMR 與 neighbor 方向衝突 | 調整 MMR 順序：先做 neighbor enrichment，再做 MMR diversity |

---

## 四、為什麼不做 Proposal C

Proposal C 需要一個「場景分類器」在 recall 前墊一層，根據當前對話屬於哪個領域（交易/技術/閒聊）動態調整權重。

**不做的原因**：

1. **分類機制做出來容易，做準很難**。目前系統沒有任何 session-level 的領域分類能力。需要額外訓練或 prompt-based 分類，都會增加延遲和成本。

2. **分類錯了代價高**：錯誤的場景分類會讓不該出現的記憶被加權、該出現的反而被稀釋，比不做還差。

3. **Proposal A + B 已經覆蓋主要需求**：A 讓重要的記憶更長壽，B 讓上下文更豐富。兩者結合已能大幅提升記憶系統的品質。

4. **Proposal C 的效益不確定**：沒有明確的使用者回饋證明「場景感知 recall」比「統一路徑 recall」更好。

**建議**：等有明確的場景判斷需求（例如明確定義了 3~5 個使用場景）再投入。

---

## 五、A + B 整合後的 Recall 流程

```
使用者 query
  ↓
shouldSkipRetrieval() — adaptive gate（已有）
  ↓
向量搜尋 + BM25 → fusion → rerank
  ↓
length norm → importance weight → time decay（Proposal A: importance 已是動態的）
  ↓
noise filter → MMR diversity
  ↓
[NEW] Neighbor Enrichment（Proposal B）
  → 對每條結果做鄰居擴展
  → 合併 + 重新排序
  ↓
返回記憶結果
  ↓
[NEW] agent_end Feedback Loop（Proposal A）
  → 分析回應是否引用了記憶
  → 根據 feedback 更新 importance
  → 寫回 LanceDB
```

---

## 六、優先順序建議

| 順序 | 項目 | 理由 |
|------|------|------|
| 1 | **Proposal A Phase 1**：在 `agent_end` 加入簡單的 feedback loop | 只需要一個新的 Hook 後處理，不動現有 decay/tier 邏輯 |
| 2 | **Proposal B 路徑 B-1**：Reflection recall 時的鄰居擴展 | 封閉在 `reflection-store.ts` 內，風險低 |
| 3 | **Proposal A Phase 2**：加入 `last_confirmed_use_at` 和 `bad_recall_count` 的實際觸發邏輯 | 讓 feedback 信號更精準 |
| 4 | **Proposal B 路徑 B-2**：主 retrieval 的 neighbor enrichment | 最後再做，風險最高 |

---

## 七、對現有架構的侵入性分析

| 項目 | 侵入性 | 說明 |
|------|--------|------|
| Proposal A Phase 1 | **低** | 只加一個 `agent_end` 後處理，不改任何現有模組 |
| Proposal A Phase 2 | **中** | 修改 `smart-metadata.ts` 的 feedback 寫入邏輯 |
| Proposal B-1 | **低** | 只修改 `retriever.ts` 的 reflection 输出部分 |
| Proposal B-2 | **中** | 需要修改 `retriever.ts` 的主 retrieval chain |

**沒有任何一個 proposal 需要修改 `decay-engine.ts`、`tier-manager.ts` 或 `store.ts` 的核心邏輯**，全部是新層疊加。
