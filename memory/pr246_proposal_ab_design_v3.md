# Issue #445 — PR #246 Proposal A & B 實作分析（v3）

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒
> 更新：v3 — 修正 hook 不一致、數字依據、Phase 依賴關係

---

## 一、現有系統能力盤點

### 1.1 Importance/Boost 機制

| 機制 | 檔案 | 說明 | 與 Proposal A | 與 Proposal B |
|------|------|------|--------------|---------------|
| 靜態 Importance | `store.ts` | 寫入時預設 0.7，寫入後固定不變 | **要動態更新** | - |
| Weibull Decay | `decay-engine.ts` | importance 調制半衰期 | decay 自然受益 | - |
| Frequency Reinforcement | `access-tracker.ts` | 高頻存取 → 半衰期延長（最多 3x）| 互補不衝突 | - |
| Tier 分層 | `tier-manager.ts` | Core/Working/Peripheral | 動態 importance 觸發晉升/降級 | - |
| Importance Weight | `retriever.ts` | `score *= (0.7 + 0.3 × importance)` | 動態更新自然生效 | - |
| `last_confirmed_use_at` | `smart-metadata.ts` | **欄位存在但未使用** | **核心切入點** | - |
| `bad_recall_count` | `smart-metadata.ts` | **欄位存在但未使用** | **與 Phase 2 Phase 3 直接相關** | - |

**關鍵發現**：`last_confirmed_use_at` 和 `bad_recall_count` 已有 schema 但從未被寫入或讀取。這是 Proposal A 的最佳切入點。

### 1.2 Frequency Reinforcement 的極限

```typescript
// 現有：
effectiveHL = baseHL + baseHL × reinforcementFactor × log1p(effectiveAccessCount)
```

這只是「用越多越慢衰減」，**不是**根據使用品質調整 importance。兩個機制互補，頻率信號不等於品質信號。

---

## 二、Proposal A — 動態 Importance

### 2.1 Feedback Signal 設計

#### 數字推算依據

- **現狀**：importance 預設 `0.7`，上限 `1.0`，下限定義不明（建議 `0.1`）
- **從 0.7 到 1.0**：需要 6 次正向 feedback（每次 +0.05）
- **從 0.7 到 0.1**：需要 6 次負向 feedback（每次 -0.10）
- **不對稱合理性**：user 標記錯誤比確認正確更重要（錯誤記憶比遺漏正確記憶危害更大），所以懲罰幅度 > 獎勵幅度是合理的
- **召回未用 penalty（-0.03）**：比確認錯誤輕，因為「沒用到」可能是 query 不夠精確，不一定是記憶本身有問題

| 信號 | 捕捉時機 | 調整幅度 | 理由 |
|------|---------|---------|------|
| 被引用進回應 | `before_prompt_build` 比對 recall 結果與回應 | **+0.05**，上限 1.0 | 保守：需要累積多次才能確認真正有用 |
| user 明確確認正確 | agent_end 解析 user 回應 | **+0.15**，上限 1.0 | user 確認強信號，大步前進 |
| user 標記錯誤 | agent_end 解析 user 回應 | **-0.10**，下限 0.1 | 錯誤記憶應快速降級 |
| 召回後沒被用到（連續2次）| 下次 `before_prompt_build` | **-0.03** | 輕微提示，累計才有意義 |
| 超過 30 天未使用 | decay 自然處理 | 不需額外邏輯 | - |

### 2.2 Feedback Signal 的可靠判斷方式

這是最核心的問題：**如何可靠知道 agent 的回應「用到」了哪條 recall 的記憶？**

| 方向 | 做法 | 準確度 | 成本 |
|------|------|--------|------|
| 弱信號（推薦）| agent 直接引用記憶內容（如「根據之前記住的...」「上次我們決定...」）| 中 | 低 |
| 時間 proximity | recall 和回應時間接近就算「用到」| 低 | 極低 |
| LLM 判斷 | 每個回應送 LLM 判斷 | 高 | 高（昂貴）|

**推薦**：Phase 1 採用**弱信號 + 簡單關鍵字比對**
- 如果 agent 回應包含 recall 回傳的 memory text（substring match），則視為「用到」
- 這是最保守的判斷，false negative 高，false positive 低

```typescript
function isRecallUsed(recallText: string, responseText: string): boolean {
  // 取 recall text 的核心片段（前 50 字）
  const snippet = recallText.slice(0, 50).toLowerCase();
  return responseText.toLowerCase().includes(snippet);
}
```

### 2.3 實作切入點

**採用 `before_prompt_build` hook（確定）**

Phase 2 的推薦是 `before_prompt_build`（非 `agent_end`），理由：
- `agent_end` 時 session 已結束，context 可能不完整
- `before_prompt_build` 發生在 recall 結果已經產出之後，可以立即比對
- 比 `agent_end` 更適合做「寫入前的最後檢查」

```typescript
// Phase 2 實作
api.on("before_prompt_build", async (event, ctx) => {
  // 1. 從 ctx 取出這次 injection 的 recall results IDs
  // 2. 等下一輪 session 的 user 回應抵達時
  // 3. 在下一個 before_prompt_build 中比對 recall vs 回應
  // 4. 根據 feedback 更新 last_confirmed_use_at / bad_recall_count
});
```

---

## 三、Proposal B — 鄰居擴展

### 3.1 B-1：Reflection 系統鄰居擴展（推薦先行）

```typescript
// 切入點：reflection-slices.ts 的 loadAgentReflectionSlicesFromEntries() 後
// 對每個 derived slice 做鄰居擴展：
const expanded = [];
for (const slice of derivedSlices) {
  const neighbors = await bm25Search(slice.text, { topK: 2, scope: same });
  expanded.push(...neighbors);
}
return deduplicateById([...derivedSlices, ...expanded]);
```

| 評估 | 分數 |
|------|------|
| 改動範圍 | 限於 `reflection-slices.ts` |
| 風險 | 🟢 低（只影響 reflection）|
| 預估工時 | 1-2 天 |
| MMR 衝突 | N/A（不經過 retriever）|
| 依賴關係 | **[可平行 Phase 2]** |

### 3.2 B-2：全域 Retrieval 鄰居擴展

```typescript
// 切入點：retriever.ts — applyMMRDiversity() 前
```

| 評估 | 分數 |
|------|------|
| 改動範圍 | 需修改 `retriever.ts` 核心邏輯 |
| 風險 | 🟡 中（MMR 衝突）|
| 預估工時 | 3-5 天 |
| 依賴關係 | **[依賴 Phase 3 數據]** |

---

## 四、方案比較總表

### 為什麼 B-1 優先於 Proposal A？

| 維度 | B-1 | Proposal A |
|------|------|-----------|
| 實作複雜度 | 低 | 中 |
| 失敗風險 | 極低 | 中（feedback signal 判斷）|
| 驗證方式 | 可直接觀察輸出差異 | 需要長期數據累積 |
| 影響範圍 | reflection 系統隔離 | 全域 retrieval |
| 結論 | **先做 B-1，累積經驗再做 A** | - |

---

## 五、最終推薦方案（含依賴關係）

### Phase 1：B-1 鄰居擴展【可平行 Phase 2】
- **實作位置**：`reflection-slices.ts`
- **風險**：極低
- **驗證**：直接觀察 reflection injection 結果是否更完整

### Phase 2：`last_confirmed_use_at` 寫入機制【可平行 Phase 1】
- **實作位置**：`before_prompt_build` hook
- **做法**：每次 recall 被使用時寫入 `last_confirmed_use_at = Date.now()`
- **風險**：低（只是寫入一個閒置欄位）
- **驗證**：觀察 decay 是否對有確認使用的記憶更慢

### Phase 3：Feedback Signal 觸發 Importance 調整【依賴 Phase 2】
- **觸發條件**：Phase 2 穩定運行 2 週後
- **做法**：根據 Phase 2 觀察到的資料調整幅度數字，再實作直接改 `importance`
- **風險**：中（需要根據數據調整幅度）

### Phase 4：B-2 全域擴展【依賴 Phase 1 穩定】
- **觸發條件**：Phase 1 運行 1 個月無異常
- **風險**：中（MMR 衝突需特殊處理）

---

## 六、Claude Code 借鑒（附錄）

Claude Code 的 `session-compressor.ts` 有 `estimateConversationValue()` 可估算 session 品質（0-1）。這個分數可以用來加權 feedback signal 的調整幅度：

```typescript
// 如果整個 session 價值高（>0.7），則 feedback boost 幅度 ×1.5
// 如果 session 價值低（<0.3），則 feedback boost 幅度 ×0.5
const sessionValue = estimateConversationValue(messages);
const adjustedBoost = baseBoost * (0.5 + sessionValue);
```

**具體接入點**：`before_prompt_build` hook 內，在計算 feedback 後、寫入 metadata 前，乘以 session quality 加權。

---

## 七、待作者確認

1. ✅ Feedback signal 判斷：**弱信號（substring match）** 作為 Phase 1/2 的做法可以嗎？
2. ✅ 調整幅度（+0.05 / +0.15 / -0.10 / -0.03）：從 0.7 到 1.0 需 6 次正向確認，你認為這個速度合理嗎？
3. `bad_recall_count` 在 Phase 2 中用於追蹤「召回未用」，是否願意讓它成為真正的觸發點？
4. Phase 3 的觸發時機（Phase 2 運行 2 週後）是否合理？
