# 09-metadata-governance.md

> **分析日期**：2026-04-02  
> **目標資料夾**：`C:\Users\admin\.openclaw\memory-lancedb-pro`  
> **分析檔案**：`smart-metadata.ts`、`admission-control.ts`、`admission-stats.ts`、`self-improvement-files.ts`

---

## 一、Smart Metadata Schema 設計分析

### 1.1 完整欄位分類

`SmartMemoryMetadata` 是整個系統的核心元資料結構，共含 **25+ 個欄位**，分為六大類：

#### A. 身份識別（Identity）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `l0_abstract` | `string` | 一行摘要（用於向量搜尋的關鍵詞來源） |
| `l1_overview` | `string` | 短概述（fallback 為 `defaultOverview(l0)`） |
| `l2_content` | `string` | 完整內容 |
| `memory_category` | `MemoryCategory` | 記憶類別（profile/preferences/entities/events/cases/patterns） |
| `fact_key` | `string \| undefined` | 時間版本類別的唯一識別鍵，格式為 `category:normalized_topic` |

#### B. 等級與狀態（Tier / State / Layer）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `tier` | `MemoryTier` | 衰減層級（core / working / peripheral），與 Decay Engine 連動 |
| `state` | `MemoryState` | 生命週期狀態（pending → confirmed → archived） |
| `memory_layer` | `MemoryLayer` | 存放層（durable / working / reflection / archive） |

**Layer 推導邏輯**（`deriveDefaultLayer`）：
- `source === "reflection" || "session-summary"` → `reflection`
- `state === "archived"` → `archive`
- `category === profile / preferences / events` → `durable`
- 其餘 → `working`

#### C. 存取與信心（Access & Confidence）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `access_count` | `number` | 被取出使用的次數 |
| `confidence` | `number (0-1)` | 信心水準，預設 0.7，由 ContextualSupport 增強 |
| `last_accessed_at` | `number` | 上次存取的時間戳 |

#### D. 時間有效性（Temporal Validity）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `valid_from` | `number` | 記憶生效時間（對應時間版本類別） |
| `invalidated_at` | `number \| undefined` | 失效時間（需 ≥ valid_from） |

`isMemoryActiveAt()` 用於判斷記憶在指定時間是否有效。

#### E. 關係鏈（Relationship Chain）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `supersedes` | `string \| undefined` | 此筆記取代哪筆記 |
| `superseded_by` | `string \| undefined` | 此筆記被哪筆記取代 |
| `relations` | `MemoryRelation[]` | 外部關係（type + targetId），最多 16 筆 |

#### F. 出處與注入（Provenance & Injection）

| 欄位 | 型別 | 用途 |
|------|------|------|
| `source_session` | `string \| undefined` | 原始 session ID |
| `source` | `MemorySource` | 來源類型（manual / auto-capture / reflection / session-summary / legacy） |
| `injected_count` | `number` | 被注入進對話的次數 |
| `last_injected_at` | `number \| undefined` | 上次注入時間 |
| `last_confirmed_use_at` | `number \| undefined` | 上次**確認有用**的時間（可用於動態 importance） |

#### G. 治理字段（Governance）⭐

| 欄位 | 型別 | 用途 |
|------|------|------|
| `bad_recall_count` | `number` | 這筆記億被取出但**內容錯誤**的次數 |
| `suppressed_until_turn` | `number` | 對話輪次號，在此之前不得被取出 |

#### H. 上下文支援（Contextual Support，V2）⭐

```typescript
interface ContextualSupport {
  context: SupportContext;       // e.g. "morning", "work", "evening"
  confirmations: number;          // 在此 context 下被證實的次數
  contradictions: number;         // 在此 context 下被推翻的次數
  strength: number;               // confirmations / (confirmations + contradictions)
  last_observed_at: number;
}

interface SupportInfoV2 {
  global_strength: number;        // 所有 slice 的加權平均
  total_observations: number;     // confirmations + contradictions 總和
  slices: ContextualSupport[];   // 最多 MAX_SUPPORT_SLICES = 8
}
```

---

### 1.2 Schema 設計特點

1. **雙向 Legacy 橋接**：`reverseMapLegacyCategory()` 將舊系統的 `preference/fact/entity/decision` 映射到新的 `MemoryCategory`，同時照顧既有資料。
2. **事實鍵自動推導**：`deriveFactKey()` 自動從 `l0_abstract` 提取 `category:topic` 格式的事實鍵，支援 `：:` 和 `->/=>` 分隔符。
3. **JSON 總量上限**：寫入前會截斷 `relations`（≤16）、`history`（≤50）、`sources`（≤20），防止 metadata 無限膨脹。
4. **V1 → V2 支援**：`parseSupportInfo()` 自動將舊格式 `{confirmations, contradictions, strength}` 遷移到 V2 的 slices 格式。

---

## 二、`ContextualSupport.strength` 計算方式

### 2.1 Per-Slice Strength

```typescript
strength = (confirmations + contradictions > 0)
  ? confirmations / (confirmations + contradictions)
  : 0.5   // 無任何觀察時的預設值
```

**意義**：在特定上下文（如「早上」、「工作」）下，這筆記億被事後**確認正確**（confirmations）vs. **被推翻**（contradictions）的比例。

### 2.2 Global Strength

```typescript
global_strength = (totalConf + totalContra > 0)
  ? totalConf / (totalConf + totalContra)
  : 0.5
```

其中 `totalConf` / `totalContra` 包含**所有活躍 slice 的evidence**，以及**已被截斷丟棄的 slice 的 evidence**（在 `updateSupportStats` 中額外累計 `droppedConf` / `droppedContra`）。

### 2.3 截斷行為（Slice Cap at 8）

當 slices 超過 `MAX_SUPPORT_SLICES=8` 時：
1. 按 `last_observed_at` 排序，保留最近的 8 個
2. 丟棄的 slices 的 evidence **不會消失**，而是被累計進 `totalConf` / `totalContra`
3. 這意味著 `total_observations` 會**超過**目前 slices 的簡單加總，而 `global_strength` 準確反映了所有歷史 evidence

### 2.4 Context 正規化

`normalizeContext()` 支援中英文別名映射：
- 「早上/上午/早晨」→ `morning`
- 「晚上/傍晚」→ `evening`
- 「工作/上班」→ `work`
- 未匹配的自定義標籤保留原樣

---

## 三、`bad_recall_count` / `suppressed_until_turn` 觸發時機

### 3.1 欄位性質

這兩個欄位是**由外部 caller 寫入的 governance 信號**，Schema 本身只提供儲存格，實際遞增邏輯在 store 层或 recall 层：

- `bad_recall_count`：當一次 `recall` 取出記憶後，**應用端發現記憶內容與事實不符**時遞增
- `suppressed_until_turn`：當 `bad_recall_count` 超過某個閾值時，寫入一個對話輪次號，在該輪次之前這筆記億不會被召回

### 3.2 讀取行為

`parseSmartMetadata()` 與 `buildSmartMetadata()` 對這兩個欄位做 `clampCount(value, 0)` 標準化（確保非負整數），但**不會主動計算或推導**。實際的觸發邏輯（例如「多少次 bad_recall 後開始 suppression」）需要在 recall pipeline 中實作。

### 3.3 與 Admission Control 的關係

目前 admission-control.ts 的 `evaluate()` **不看** `bad_recall_count` 或 `suppressed_until_turn`，因為 admission 發生在**寫入前**，而 bad_recall 發生在**寫入後的召回環節**。兩者構成互補的反饋迴路：

```
寫入前 → Admission Controller（決定是否准許寫入）
寫入後 → Recall + Governance（決定是否召回 / 抑制）
```

---

## 四、Admission Control 寫入決策機制

### 4.1 評分模型（AMAC — Admission Model with Audit & Control）

`AdmissionController.evaluate()` 對每個 `CandidateMemory` 計算一個 **0-1 的 admission score**：

```
score = w_utility * utility
      + w_confidence * confidence
      + w_novelty * novelty
      + w_recency * recency
      + w_typePrior * typePrior
```

其中五個分數各自獨立計算（0-1 區間），權重加總為 1.0。

### 4.2 各分數計算方式

| 分數 | 計算方式 | 含義 |
|------|---------|------|
| **utility** | LLM prompt 評估「這筆記億對未來跨 session 交互的實用性」| 0.5 = 預設值（LLM 失敗時）|
| **confidence** | ROUGE-like F1（候選文本 vs. 對話文本） × 0.7 + token coverage × 0.3 − unsupported_ratio × 0.25 | 候選內容在對話中是否有充分根據 |
| **novelty** | `1 - maxSimilarity`（cosine similarity vs. 既有可能候選）| 與現有記憶越不像，分數越高 |
| **recency** | 指數衰減：`1 - exp(-λ * gapDays)`，halfLife 可配置（預設 14 天）| 越久沒更新過的類似記憶，越值得寫入新版本 |
| **typePrior** | 查表：profile=0.95, preferences=0.9, patterns=0.85, entities=0.75, cases=0.8, events=0.45 | 記憶類型的基本重要性prior |

### 4.3 決策邏輯

```
if score < rejectThreshold        → "reject"（寫入磁盤rejections.jsonl）
else if score >= admitThreshold AND maxSimilarity < 0.55  → "add"（全新記憶）
else                               → "update_or_merge"（與現有記憶合併）
```

`"reject"` 的 candidate **不會寫入**，但會留下完整的 audit trail。

### 4.4 三種預設配置

| 預設 | 用途場景 | rejectThreshold | admitThreshold | 特點 |
|------|---------|-----------------|----------------|------|
| `balanced` | 一般用途 | 0.45 | 0.60 | 預設值，typePrior=0.6 最高 |
| `conservative` | 高精度需求 | 0.52 | 0.68 | 降低 events prior（0.28），提高 novelty/recency 權重 |
| `high-recall` | 高覆蓋需求 | 0.34 | 0.52 | 降低所有閾值，events prior 提高到 0.58 |

### 4.5 審計追蹤

每次評估都會產生 `AdmissionAuditRecord`（寫入記憶的 metadata 或 `rejections.jsonl`）：
- `version: "amac-v1"`
- `decision` / `hint`（add / update_or_merge）
- `score` + `thresholds` + `weights`
- `feature_scores`（五個分數細項）
- `matched_existing_memory_ids`（相似度 ≥ 0.55 的既有可能記憶 ID）
- `compared_existing_memory_ids`（全部比對過的 ID）
- `max_similarity`（與最相似記憶的 cosine 值）
- `utility_reason`（LLM 的文字說明）

### 4.6 Novelty 的 Cosine Threshold

`matchedIds`（進入 `AdmissionAuditRecord.matched_existing_memory_ids`）的門檻是 **0.55**。這不是 admission 閾值，而是「是否視為重複」的 threshold：
- `maxSimilarity < 0.55` → 可惜 `add` hint
- `maxSimilarity ≥ 0.55` → `update_or_merge` hint

---

## 五、Admission Stats 統計系統

`admission-stats.ts` 提供 admission 後的**回溯統計**，讓 operator 理解 admission 行為：

### 5.1 資料來源

1. **通過的记忆**：`store.list()` 讀取，通過 metadata 中的 `admission_control.decision === "pass_to_dedup"` 識別
2. **被拒的记忆**：`rejections.jsonl`（JSONL 格式，每次拒絕追加一行）

### 5.2 統計維度

| 維度 | 說明 |
|------|------|
| `byCategory` | 每個記憶類別的被拒數量 |
| `byScope` | 每個 scope 的被拒數量 |
| `topReasons` | 被拒原因的文字雲（從 `utility_reason` 或 `audit.reason` 提取）|
| `windows` | 24小時 / 7天 兩個時間窗口的 admit/reject 數量與拒絕率 |
| `categoryBreakdown` | 每個類別的 admit count / reject count / reject rate |

### 5.3 Rejection Reason 正規化

`normalizeReasonKey()` 將理由字串中的具體數字替換為 `#`，例如：
- `"Admission rejected (0.234 < 0.450)"` → `"admission rejected (# < #)"`
- 用於將相同模式的不同具體分數**分組計數**。

---

## 六、Self-Improvement 學習檔案寫入

### 6.1 檔案結構

```
baseDir/.learnings/
├── LEARNINGS.md   # 學習條目（LRN-YYYYMMDD-NNN）
└── ERRORS.md      # 錯誤條目（ERR-YYYYMMDD-NNN）
```

### 6.2 寫入格式

每個條目結構：
```
## [LRN-20260402-001] best_practice

**Logged**: 2026-04-02T...
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
...

### Details
...

### Suggested Action
...

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---
```

### 6.3 併發安全機制

`withFileWriteQueue()` 為每個檔案維護一個 Promise 鏈，確保：
- 同一檔案不會同時被多個請求寫入（避免 JSONL 交錯損壞）
- 不同檔案（LEARNINGS.md vs ERRORS.md）可並發寫入
- 使用 `appendFile` 而非 `writeFile`，避免覆蓋

### 6.4 ID 生成邏輯

ID = `{prefix}-{date}-{count}`，其中 count = 當日該前綴在檔案中出現的次數（正規表達式計數）。因此 ID 跨 session 遞增，不會重複。

---

## 七、與 #445 Proposal A（動態 Importance）的關聯分析

### 7.1 現有 Importance 來源

Admission Control **不直接處理 importance**，`CandidateMemory.importance` 是傳入的既有值。Admission 評估的是**候選是否值得寫入**，而非重要性排名。

### 7.2 潛在連結：Admission → 動態 Importance

```
CandidateMemory.importance（初始值）
    ↓
AdmissionController.evaluate()（決定是否寫入）
    ↓
寫入後 → actual use（injected_count↑、last_confirmed_use_at 更新）
    ↓
Decay Engine（根據 importance + decay rate 調整）
    ↓
ContextualSupport（bad_recall_count↑ → confidence↓ → 可能被抑制）
```

Admission 與 Decay/Governance 形成互補：
- **Admission**：控制什麼可以寫入（gatekeeper）
- **Decay**：控制已寫入的記憶如何隨時間淡化（degradation）
- **Governance**（bad_recall / suppressed）：控制已寫入記憶的即時可用性（recall suppression）

### 7.3 `last_confirmed_use_at` 的關鍵角色

`last_confirmed_use_at` 追蹤記憶**最後一次被確認有用的時間**。這個欄位可以作為 Proposal A 動態 importance 的輸入信號之一：
- 高頻確認使用 → importance 應提高
- 長期未確認使用 → importance 自然衰減
- 多次 bad_recall → importance 應降低並觸發 suppression

### 7.4 尚未實現的環節

 Admission Control 的 `auditMetadata: true` 寫入 audit 資料到 metadata，但**目前未連動到 Decay Engine**。具體來說：
- `injected_count` 和 `last_confirmed_use_at` 在 admission 時是否更新，取決於 caller 的實作
- `bad_recall_count` 的寫入時機和閾值也需要 caller 實作
- Decay Engine 目前需要主動呼叫者傳入 `importance`，沒有從 metadata 自動讀取 `last_confirmed_use_at` 來動態調整

---

## 八、總結架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    CandidateMemory                           │
│  (importance, category, abstract, content, vector, ...)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │  AdmissionController     │  ← admission-control.ts
        │  .evaluate()             │
        │                          │
        │  5-D scoring:            │
        │  utility (LLM)          │
        │  confidence (ROUGE F1)  │
        │  novelty (cosine)       │
        │  recency (exp decay)    │
        │  typePrior (table)       │
        │                          │
        │  decision:               │
        │  reject → rejections.jsonl│
        │  pass_to_dedup → hint:   │
        │    add / update_or_merge │
        └──────────┬───────────────┘
                   │ write
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 SmartMemoryMetadata                           │
│  core identity: l0/l1/l2, category, tier, state, layer     │
│  provenance: source, source_session, injected_count        │
│  governance: bad_recall_count, suppressed_until_turn        │
│  support: SupportInfoV2 { global_strength, slices[] }       │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴────────────┐
          │                        │
          ▼                        ▼
   [Recall Pipeline]       [Decay Engine]
   bad_recall_count↑      importance + decay rate
   suppressed_until_turn   → tier / active_state
```

---

## 九、關鍵設計决策總覽

| 決策 | 選擇 | 理由 |
|------|------|------|
| Admission Score 權重設計 | `typePrior` 預設佔 60% | 記憶類型是最穩定的先驗信號 |
| Novelty 閾值 | cosine similarity ≥ 0.55 才算「重複」| 兼顾召回率與去重效果 |
| Support Strength 預設 | 無 evidence 時為 0.5（中性）| 避免無中生有的高/低信心 |
| Governance 字段位置 | 存在 metadata 而非獨立 table | 減少 JOIN，保持自足的治理上下文 |
| Rejection 持久化 | JSONL 追加（append-only）| 適合大量寫入且易於日後分析 |
