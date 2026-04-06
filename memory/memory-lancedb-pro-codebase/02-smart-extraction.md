# Smart Extraction 深度分析報告

**目標檔案：** `src/smart-extractor.ts`、`src/extraction-prompts.ts`、`src/batch-dedup.ts`
**分析日期：** 2026-04-02
**分析的程式碼庫：** memory-lancedb-pro

---

## 一、Pipeline 總覽

```
conversation text
      │
      ▼
┌─────────────────────────────────────┐
│ 1. stripEnvelopeMetadata()          │  去除 OpenClaw channel 注入的 metadata
│    - System: [timestamp] Channel[]  │
│    - Conversation info (JSON)       │
│    - Sender (JSON)                  │
│    - Replied message (JSON)         │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│ 2. LLM extractCandidates()          │  單次 LLM call，6-category 萃取
│    - buildExtractionPrompt()        │  回傳最多 5 筆 CandidateMemory
│    - validate & normalize           │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│ 3. batchDedup() (批次內 cosine)     │  萃取後候選人之間的向量去重
│    - SIMILARITY_THRESHOLD = 0.7     │  (用於 vector search 預過濾)
│    - threshold = 0.85 (cosine dedup)│
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│ 4. Admission Control (governance)   │  可選的 LLM 驅動 admission gate
│    - utility / confidence / novelty │
│    - recency / typePrior            │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│ 5. deduplicate() (兩階段)           │  Stage 1: vector search (0.7)
│    - preference-slot guard          │  Stage 2: LLM dedup decision
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│ 6. processCandidate() → store       │  create/merge/skipped/support/
│                                     │  contextualize/contradict/supersede
└─────────────────────────────────────┘
```

---

## 二、6 類別萃取邏輯

### 2.1 六類別定義（`memory-categories.ts`）

| 類別 | 定義 | 測試句式 | 行為 |
|------|------|----------|------|
| `profile` | 使用者身份（靜態屬性） | "User is..." | **永遠 merge**，跳過 dedup，直接 upsert profile |
| `preferences` | 使用者偏好（傾向） | "User prefers/likes..." | 支援 MERGE/SUPERSEDE（時間版本化） |
| `entities` | 持續存在的名詞 | "XXX's state is..." | 支援 MERGE/SUPERSEDE（時間版本化） |
| `events` | 發生的事件 | "XXX did/completed..." | **僅 append**（CREATE 或 SKIP） |
| `cases` | 問題-解法 pair | 含 "problem → solution" | **僅 append**（CREATE 或 SKIP） |
| `patterns` | 可複用的流程 | 可用於「類似情境」 | 支援 MERGE |

### 2.2 萃取 Prompt 設計（`buildExtractionPrompt`）

萃取 Prompt 的核心原則：

- **Target Output Language: auto** — 由 LLM 自動偵測對話語言
- **最大 5 筆記憶 per extraction**（`MAX_MEMORIES_PER_EXTRACTION = 5`）
- **三層結構**：L0 abstract（一行 index）、L1 overview（類別專用 Markdown）、L2 content（完整敘事）
- **Merge key 格式**：`[Merge key]: [Description]` — 用於 mergeable 類別

萃取時的噪聲過濾（`extractCandidates` 內）：

```typescript
// 三層驗證
1. normalizeCategory()       → 無效 category 直接拋棄
2. abstract.length < 5      → 過短 abstract 拋棄
3. isNoise(abstract)        → noise-filter.ts 比對拋棄
```

### 2.3 LLM 回應格式

```json
{
  "memories": [
    {
      "category": "profile|preferences|entities|events|cases|patterns",
      "abstract": "One-line index",
      "overview": "Structured Markdown summary",
      "content": "Full narrative"
    }
  ]
}
```

---

## 三、萃取品質確保機制

### 3.1 Admission Control（governance gate）

`AdmissionController` 在 dedup 之前對每個 candidate 做**五維度加權評分**：

| 維度 | 權重（balanced） | 說明 |
|------|-----------------|------|
| `typePrior` | **60%** | 類別先驗：profile(0.95) > preferences(0.9) > patterns(0.85) > cases(0.8) > entities(0.75) > events(0.45) |
| `novelty` | 10% | 與現有記憶的最大相似度（1 - maxSimilarity） |
| `confidence` | 10% | ROUGE-Like F1 + token coverage（來自 conversation 支撐度） |
| `utility` | 10% | LLM 評估「未來實用性」（可關閉） |
| `recency` | 10% | 半衰期衰減（距離上次同類記憶的時間） |

**門檻設計（balanced preset）：**
- `rejectThreshold: 0.45` — 分數低於此值 → **reject**（不入庫）
- `admitThreshold: 0.6` — 分數高於此值 + novelty < 0.55 → hint = **"add"**

**三種Preset對比：**

| Preset | rejectThreshold | admitThreshold | 風格 |
|--------|----------------|----------------|------|
| `balanced` | 0.45 | 0.6 | 預設值 |
| `conservative` | 0.52 | 0.68 | **更嚴格**，events 幾乎不進 |
| `high-recall` | 0.34 | 0.52 | **更寬鬆**，減少 false negative |

**Admission 的獨特價值：**
- 不只是「相似度去重」，而是評估這筆記憶**是否值得保存**（utility、confidence）
- 可寫入持久化的 rejection audit（`admission-audit/rejections.jsonl`），用於日後分析
- `hint` 欄位提供給 dedup pipeline 額外信號（"add" vs "update_or_merge"）

### 3.2 噪聲反饋學習

當 LLM 回傳**零筆候選**時（最強的噪聲信號），`learnAsNoise()` 會：
1. 取 conversation 末 300 字
2. 對其 embedding
3. 寫入 `NoisePrototypeBank`

此為**被動學習**：從失敗中學習，不主動擴展噪聲庫。

### 3.3 提取時的 validation

萃取完成後，`extractCandidates` 還會做：
- **invalidCategoryCount** — 無效類別計數
- **shortAbstractCount** — abstract < 5 字元計數
- **noiseAbstractCount** — `isNoise()` 命中計數

---

## 四、Envelope Metadata 過濾

### 4.1 `stripEnvelopeMetadata()` 的四層過濾

```typescript
// 第一層：System: [timestamp] Channel[account] DM | ou_xxx...
text.replace(/^System:\s*\[[\d\-: +GMT]+\]\s+\S+\[.*?\].*$/gm, "")

// 第二層：標記型 JSON metadata 區塊
/(?:Conversation info|Sender|Replied message)\s*\(untrusted[^)]*\):\s*```json\s*\{[\s\S]*?\}\s*```/g

// 第三層：殘餘的 message_id + sender_id JSON blocks
/```json\s*\{[^}]*"message_id"\s*:[^}]*"sender_id"\s*:[^}]*\}\s*```/g

// 第四層：折疊 excessive blank lines
/\n{3,}/g → "\n\n"
```

### 4.2 為何需要過濾？

這些 metadata 由 OpenClaw channel（Discord、Feishu 等）在轉發對話時自動注入。若讓 LLM 看見：
- **qwen 等較弱模型**會把 metadata 當作對話內容萃取，汙染記憶
- System 行的 channel 資訊會被當作「使用者在討論某 channel」
- JSON 結構會破壞 prompt 的結構化輸出預期

### 4.3 觸發位置

在 `extractCandidates()` 內，**在呼叫 LLM 之前**就執行，確保送入的 prompt 永遠是乾淨的對話文字：

```typescript
const cleaned = stripEnvelopeMetadata(truncated);
const prompt = buildExtractionPrompt(cleaned, user);
```

---

## 五、Cosine Dedup 機制

### 5.1 兩階段 Dedup

#### Stage 1: Vector Pre-filter（`SIMILARITY_THRESHOLD = 0.7`）

```typescript
const activeSimilar = await this.store.vectorSearch(
  candidateVector,
  5,           // top-5
  0.7,         // SIMILARITY_THRESHOLD
  scopeFilter,
  { excludeInactive: true },  // 不取 superseded/invalidated 記錄
);
```

若無相似結果 → 直接 **CREATE**。

#### Stage 2: LLM Decision（`buildDedupPrompt`）

將候選記憶 + top-3 相似記憶送入 LLM，LLM 輸出七種決策之一：

| 決策 | 意義 | 適用類別 |
|------|------|----------|
| `CREATE` | 完全新資訊 | 全部 |
| `MERGE` | 新增細節到現有記憶 | preferences, entities, patterns |
| `SKIP` | 與現有重複或資訊退化 | 全部 |
| `SUPERSEDE` | 可變事實已更新 | preferences, entities |
| `SUPPORT` | 在特定 context 強化現有記憶 | preferences, entities, patterns |
| `CONTEXTUALIZE` | 增加情境 nuance | preferences, entities, patterns |
| `CONTRADICT` | 在特定 context 否定現有記憶 | preferences, entities, patterns |

**events / cases 類別限制**：這兩類是**append-only**，LLM 只能輸出 `CREATE` 或 `SKIP`，嚴禁輸出其餘五種決策（Prompt 層面 enforce）。

### 5.2 批次內 Cosine 去重（`batch-dedup.ts`）

**位置**：在 LLM dedup 之前，候選人內部彼此比對。

```typescript
// smart-extractor.ts
const dedupResult = batchDedup(abstracts, vectors);
// threshold = 0.85（預設）
// 演算法：O(n²) pairwise cosine，n ≤ 5
// 策略：後者標記為 duplicate of 較早者
```

**為何需要？**
- 萃取 LLM 可能一次回傳多個相關記憶（如「user 喜歡 Python」和「user 偏好 Python type-hint-free」）
- 這些在萃取時已同時產生，相似度極高，進 LLM dedup 會浪費昂貴的 API call
- **節省成本**：批次內去除，不需要再呼叫一次 `dedupPrompt`

**Threshold 0.85 的意義：**
- 0.85 > 0.7（vector pre-filter 的門檻）
- 代表「明顯重複」才去除，保留「語義接近但不相同」的候選
- 避免過度 aggressive 去重導致資訊丢失

### 5.3 Preference Slot Guard（額外保護）

```typescript
// preferences 類別特殊邏輯
if (candidate.category === "preferences") {
  const candidateSlot = inferAtomicBrandItemPreferenceSlot(candidate.content);
  if (sameBrand && differentItem) {
    return { decision: "CREATE" }; // 同一品牌、不同商品，永不 merge
  }
}
```

**範例**：
- 「喜歡麥當勞的板燒雞腿堡」
- 「喜歡麥當勞的麥辣雞翅」

→ 同一品牌、不同商品 → 兩筆分開儲存，不 merge。

### 5.4 Destructive Decision 安全機制

```typescript
// supersede / contradict 需要精確的 match_index
// 若 LLM 未提供有效 index，降級為 CREATE（避免錯誤替換）
const destructiveDecisions = new Set(["supersede", "contradict"]);
if (destructiveDecisions.has(decision) && !hasValidIndex) {
  return { decision: "CREATE" };
}
```

---

## 六、與 Claude Code Extraction 的差異

> 以下對比對象為 Claude Code 的記憶萃取機制（概念對比，非精確實作比對）

| 維度 | memory-lancedb-pro | Claude Code |
|------|-------------------|-------------|
| **萃取觸發** | 對話結束後主動 extract | 在特定 context window 截止時被動觸發 |
| **類別模型** | 6 類別（profile/preferences/entities/events/cases/patterns） | 主要 2-3 類（fact/preference/entity） |
| **去重層次** | 3 層（批次 cosine → admission → LLM dedup） | 較少，通常僅向量相似度 |
| **Governance** | Admission Control（5 維度加權評分） | 無明確 governance gate |
| **Metadata 過濾** | `stripEnvelopeMetadata()` 主動過濾 System/Sender/JSON | 無專門 envelope 過濾（假設乾淨輸入） |
| **時間版本化** | SUPERSEDE 保留歷史、標記 invalidated_at | 傾向直接覆寫 |
| **Merge 策略** | LLM merge prompt（保留三層結構） | 簡單覆寫或簡單附加 |
| **Audit 能力** | 完整 admission audit + rejection audit | 無持久化 audit |
| **Rate Limiting** | `ExtractionRateLimiter`（sliding window 30/hr） | 無內建 rate limiter |
| **Noise Learning** | 零萃取時學習為噪聲 | 無噪聲學習機制 |
| **Preference Slot** | 品牌-商品顆粒度保護 | 無顆粒度保護 |
| **Scope 過濾** | `scopeFilter` 支援多 scope 讀取限制 | 無 scope 概念 |

---

## 七，重要設計亮點

### 7.1 admission control 領先之處

傳統的 extraction 系統只要 LLM「萃取得出來」就入庫。`AdmissionController` 的價值在於：

1. **utility scoring** — 不是「能萃取」就好，而是「未來有用」才行
2. **confidence scoring** — 候選記憶是否有對話內容支撐（ROUGE-Like F1）
3. **typePrior 佔 60%** — 預設信任 profile/preferences，懷疑 events（符合長期記憶價值邏輯）
4. **rejection audit 持久化** — 可分析系統的 false negative 模式

### 7.2 三層記憶結構的價值

```
L0 abstract  →向量搜尋的 text（簡短、精確）
L1 overview  →結構化摘要（category-specific Markdown）
L2 content   →完整敘事（背景、細節）
```

優點：
- 搜尋時只 embed L0，但呈現 L1 + L2 的豐富度
- Merge 時保留三層完整性，不破壞結構
- 不同 consumer 可取用不同層級

### 7.3 `excludeInactive: true` 的重要性

```typescript
const activeSimilar = await this.store.vectorSearch(
  candidateVector, 5, 0.7, scopeFilter,
  { excludeInactive: true },  // 排除 superseded/invalidated
);
```

確保被 SUPERSEDE 的舊記憶**不會喧賓奪主**遮擋當前事實，讓新候選有公平比較的機會。

---

## 八、潛在觀察點

1. **Admission Control 預設關閉**：`enabled: false`（balanced preset），需主動開啟才能生效
2. **utilityMode 預設 "standalone"**：不與 novelty/confidence 維度互動，單獨評估實用性
3. **零萃取時的噪聲學習**：只取末 300 字，可能不足以捕捉完整噪聲特徵
4. **batchDedup 的 threshold (0.85) 與 vectorSearch (0.7) 差距**：代表萃取候選間的重複標準比與歷史記憶的標準更嚴格（同一批萃取的內容更可能真正重複）
5. **SLOTH（events/cases）的 APPEND_ONLY 限制**：在 dedup prompt 層面 enforce，但若 LLM prompt injection 可能繞過，程式碼層有 `APPEND_ONLY_CATEGORIES` set 可供查詢但未見主動阻擋

---

*本報告由 Subagent 分析 memory-lancedb-pro 程式碼庫產出*
