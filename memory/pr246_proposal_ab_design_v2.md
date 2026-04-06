# Issue #445 — PR #246 Proposal A & B 實作分析

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒

---

## 一、現有系統能力盤點

### 1.1 現有的 Importance/Boost 機制

| 機制 | 檔案 | 說明 | 與 Proposal A 關係 |
|------|------|------|-------------------|
| 靜態 Importance | `store.ts` | 寫入時預設 0.7，寫入後固定不變 | Proposal A 要動態更新 |
| Weibull Decay | `decay-engine.ts` | importance 調制半衰期 | 現有系統自然受益 |
| Frequency Reinforcement | `access-tracker.ts` | 高頻存取 → 半衰期延長（最多 3x）| 獨立運作，不衝突 |
| Tier 分層 | `tier-manager.ts` | Core/Working/Peripheral | Proposal A 觸發晉升/降級 |
| Importance Weight 檢索 | `retriever.ts` | `score *= (0.7 + 0.3 × importance)` | 動態更新自然生效 |
| last_confirmed_use_at | `smart-metadata.ts` | **欄位存在但未使用** | 關鍵橋接欄位 |
| bad_recall_count | `smart-metadata.ts` | **欄位存在但未使用** | 關鍵橋接欄位 |

**關鍵發現**：`last_confirmed_use_at` 和 `bad_recall_count` 已經有 schema，但**從未被寫入或讀取**。這是 Proposal A 的核心切入點。

### 1.2 現有 Frequency Reinforcement 極限

從 `access-tracker.ts` 分析：

```typescript
// 現有 frequency reinforcement：
effectiveHL = baseHL + baseHL × reinforcementFactor × log1p(effectiveAccessCount)
```

這只是「用越多越慢衰減」，**不是**根據使用品質調整 importance 本身。兩個機制是互補的。

---

## 二、Proposal A 分析

### 2.1 核心設計方向

**目標**：讓 `importance` 從「寫入時固定」變成「使用後動態調整」。

### 2.2 Feedback Signal 設計

| 信號 | 捕捉時機 | 調整方式 |
|------|---------|---------|
| 被引用進回應 | agent_end → 比對 recall 結果與回應 | `importance += 0.05`，上限 1.0 |
| user 明確確認正確 | user 說「對」「沒錯」| `importance += 0.15`，上限 1.0 |
| user 標記錯誤 | user 說「不對」「錯了」| `importance -= 0.10`，下限 0.1 |
| 召回後沒被用到（2次）| 下次 recall 檢查 | `importance -= 0.03` |
| 長期未使用（>30天）| 現有 decay 自然處理 | 不需額外邏輯 |

### 2.3 實作切入點

**最佳時機**：`before_prompt_build` hook（早於 `agent_end`，可取得 recall 結果）

```typescript
// 在 before_prompt_build 中：
// 1. 讀取這次 injection 的 items IDs
// 2. 留到下一個 before_prompt_build 或 agent_end 比對
// 3. 根據 feedback 更新 importance
```

### 2.4 風險分析

| 風險 | 嚴重度 | 說明 |
|------|--------|------|
| Feedback Signal 判斷不可靠 | 高 | 純文本比對 high false positive/negative |
| Context Loss | 高 | `agent_end` 時 session 結束，難以取得完整 recall→回應對應 |
| 效能 overhead | 中 | 每 session 做額外 embedding similarity 比對 |
| 欄位未同步 | 低 | `last_confirmed_use_at` 現有 schema，可直接寫入 |

### 2.5 方案 A 內部分歧

| 方向 | Pros | Cons |
|------|------|------|
| 直接改 `importance` | 立即見效 | 對 decay 有非線性影響 |
| 透過 `last_confirmed_use_at` 間接觸發 | 更安全：現有 decay 邏輯不變 | 需要 decay engine 主動讀取此欄位 |

**建議**：Phase 1 採用間接方式（寫入 `last_confirmed_use_at`，decay engine 自動受益），Phase 2 再評估是否直接改 `importance`。

---

## 三、Proposal B 分析

### 3.1 B-1：Reflection 系統鄰居擴展（推薦先行）

```typescript
// 在 loadAgentReflectionSlicesFromEntries() 後：
// 對每個 derived slice 做鄰居擴展：
// 1. bm25Search(text, topK=2, scope=same)
// 2. Merge + deduplicate
// 3. Cap: max 2 neighbors per recalled memory
```

| 評估 | 分數 |
|------|------|
| 改動範圍 | 限於 `reflection-store.ts` 或 `reflection-slices.ts` |
| 風險 | 🟢 低（只影響 reflection 查詢）|
| 預估工時 | 1-2 天 |
| MMR 衝突 | N/A（不經過 retriever）|

### 3.2 B-2：全域 Retrieval 鄰居擴展

```typescript
// 在 retriever.ts 的 applyMMRDiversity() 前：
// applyNeighborExpansion(results)
```

| 評估 | 分數 |
|------|------|
| 改動範圍 | 需修改 `retriever.ts` 核心邏輯 |
| 風險 | 🟡 中-高 |
| 預估工時 | 3-5 天 |
| MMR 衝突 | ⚠️ 高（MMR 推遲相似項目，鄰居擴展又拉回來）|

**建議**：先做 B-1，穩定後再評估是否需要 B-2。

---

## 四、方案比較總表

### Proposal A

| 方案 | Pros | Cons | 風險 |
|------|------|------|------|
| 直接改 importance | 立即見效、實作簡單 | 對 decay 有非線性影響 | 中 |
| 間接（last_confirmed_use_at）| 安全、backward compatible | Phase 2 才能完整 | 低 |
| BM25 相似度比對 | 可量化 | 高計算成本 | 高 |
| LLM 判斷 feedback quality | 最準確 | 每 session 呼叫 LLM，昂貴 | 中 |

### Proposal B

| 方案 | Pros | Cons | 風險 |
|------|------|------|------|
| B-1 Reflection 先行 | 低風險、 contained、立即見效 | 只影響 reflection | 低 |
| B-2 全域 retrieval | 更全面 | MMR 衝突、需要更多測試 | 中-高 |
| B-1 + B-2 最終 | 最完整 | 實作時間長 | 中 |

---

## 五、最終推薦方案

### Phase 1：輕量化快速見效
1. **Proposal B-1**：Reflection 鄰居擴展
   - 實作位置：`reflection-slices.ts`
   - 風險：極低
   - 效果：reflection injection 品質提升

### Phase 2：核心功能
2. **Proposal A 間接版本**：寫入 `last_confirmed_use_at`
   - 實作位置：`before_prompt_build` 或 `agent_end` hook
   - 風險：低（只是寫入一個已有欄位）
   - 效果：decay engine 自動受益，不需要直接改 importance

### Phase 3：完整功能（可選）
3. **Proposal A 直接版本**：直接改 `importance`
   - 需要更精確的 feedback signal 判斷
   - 建議：先用弱信號（agent 直接引用），再逐步複雜化

### Phase 4：全面增強（可選）
4. **Proposal B-2**：全域鄰居擴展
   - 基於 B-1 穩定後的實際效果決定

---

## 六、借鑒 Claude Code 的設計

Claude Code 的 `/compact` 指令採用**三軌壓縮**：

| 層次 | 觸發時機 | 策略 |
|------|---------|------|
| SNIP Compact | API 413 error | 移除最後一條訊息 |
| Micro Compact | 每 N 回合 | 折疊連續同角色訊息 |
| Auto Compact | 90% token budget | LLM summarization |

memory-lancedb-pro 的 `session-compressor.ts` 已有類似的**評分 + greedy 選擇**機制（`scoreText` 根據 tool_call/correction/decision 給予高/低分）。

**啟示**：Proposal A 的 feedback signal 可以借鑒這個評分邏輯：
- 從 `session-compressor.ts` 的 `estimateConversationValue()` 取得 session 品質
- 高品質 session 的 recall 被使用 → 給予更高 importance boost

---

## 七、需作者確認的問題

1. Proposal A 的 feedback signal 如何可靠判斷？（作者意圖）
2. B-1 先行可以接受嗎？
3. Phase 2 的 indirect 方式（`last_confirmed_use_at`）是否是作者想要的？
4. 直接改 `importance` 的調整幅度（+0.05 / +0.15 / -0.10）是否合理？
