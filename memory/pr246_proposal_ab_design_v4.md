# Issue #445 — PR #246 Proposal A & B 實作分析（v4）

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒
> 更新：v4 — 修正不對稱矛盾、跨 turn 狀態保存、isRecallUsed 前50字風險、附錄 clamp

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
| `bad_recall_count` | `smart-metadata.ts` | **欄位存在但未使用** | **Phase 3 觸發欄位** | - |

**關鍵發現**：`last_confirmed_use_at` 和 `bad_recall_count` 已有 schema 但從未被寫入或讀取。

---

## 二、Proposal A — 動態 Importance

### 2.1 Feedback Signal 設計

#### 數字推算與不對稱性說明

**設計意圖澄清**：
- 「懲罰幅度 > 獎勵幅度」的意義是：**每次犯錯的代價高**，而非「錯誤比正確快很多到達終點」
- 這個設計選擇是故意的：錯誤記憶的單次危害 > 正確記憶的單次確認效益
- 如果要讓錯誤「更快」降到 0.1，需將 `-0.10` 改為 `-0.20`（3步到0.1），但這會讓體驗過於劇烈

**調整幅度（修定）**：

| 信號 | 捕捉時機 | 調整幅度 | 到達 0.1/1.0 需幾次 |
|------|---------|---------|-------------------|
| 被引用進回應 | Phase 2 雙 hook 搭配（見 2.3）| **+0.05**，上限 1.0 | 6 次（0.7→1.0） |
| user 明確確認正確 | agent_end 解析 | **+0.15**，上限 1.0 | 2 次（0.7→1.0） |
| user 標記錯誤 | agent_end 解析 | **-0.20**，下限 0.1 | 3 次（0.7→0.1）|
| 召回後沒被用到（連續2次）| 下次 `before_prompt_build` | **-0.03** | —（溫和） |

**不對稱調整後**：錯誤記憶 3 步降到底，正確記憶 6 步升到頂，代價不對稱體現於「每次犯錯殺傷力更大」。

### 2.2 Feedback Signal 的可靠判斷方式

**核心問題**：如何可靠知道 agent 回應「用到」了哪條 recall 的記憶？

**採用：substring match + 中段取樣**

```typescript
/**
 * 判斷 recall 的記憶是否被 agent 回應使用。
 * 方法：取記憶的中段（避開固定前綴），與回應做 substring match。
 * 局限性：
 *   - False negative 高（記憶被意譯就不匹配）：刻意接受，保守代價低
 *   - False positive 低（通用前綴匹配）：已透過中段取樣緩解
 */
function isRecallUsed(recallText: string, responseText: string): boolean {
  const text = recallText.trim();
  if (text.length < 20) return false; // 太短不靠譜

  // 取中段核心內容（前20-70字），避開固定前綴（如時間戳、ID、通用描述頭）
  const snippet = text.slice(Math.min(20, text.length - 70), Math.min(70, text.length));

  // 如果中段都是標點/停用字，不靠譜
  if (/^[\s\p{P}]+$/u.test(snippet)) return false;

  return responseText.toLowerCase().includes(snippet.toLowerCase());
}
```

**侷限性說明**：
- False negative 高：是刻意設計，寧可少認定也不要誤判
- False positive 低：已用中段取樣緩解，但無法完全消除
- 最適合的場景：事後記住的結論、確切數值、具體名稱（這些不易被意譯）

### 2.3 跨 Turn 狀態保存（實作最關鍵處）

**為什麼需要兩個 hook 搭配**：

| Hook | 時機 | 做的事 |
|------|------|--------|
| `agent_end` | agent 產生回應後 | 存入這輪 injection 的 recall IDs + 回應文字 |
| `before_prompt_build` | 下一輪 prompt 建立前 | 取出上一輪儲存的 response，與這輪 injection 比對，寫入 metadata |

**狀態保存方式**：

```typescript
// 用 module-level WeakMap 儲存上一輪的 recall 結果（session scope）
const pendingRecall = new WeakMap<object, {
  recallIds: string[],
  responseText: string
}>();

// agent_end：儲存這輪 injection 的 recall IDs 和 agent 回應
api.on("agent_end", async (event, ctx) => {
  const responseText = ctx.messages.at(-1)?.content ?? "";
  const recallIds = ctx.session.recalledMemoryIds ?? []; // 假設有此資料

  pendingRecall.set(ctx.session, { recallIds, responseText });
});

// before_prompt_build：比對並寫入 metadata
api.on("before_prompt_build", async (event, ctx) => {
  const pending = pendingRecall.getAndDelete(ctx.session); // 取出並清除
  if (!pending || pending.recallIds.length === 0) return;

  const { recallIds, responseText } = pending;
  const sessionMessages = ctx.messages ?? [];

  for (const id of recallIds) {
    const recallEntry = await store.get(id);
    if (!recallEntry) continue;

    // 嘗試取得 user 回應（有時候 agent_end 到 before_prompt_build
    // 中間還有 user input，可以擴充這段邏輯）
    const userResponse = findUserResponseAfterAgent(sessionMessages, id);

    const used = isRecallUsed(recallEntry.text, userResponse ?? responseText);

    if (used) {
      await store.update(id, { last_confirmed_use_at: Date.now() });
    } else {
      const currentCount = (await store.get(id))?.bad_recall_count ?? 0;
      await store.update(id, { bad_recall_count: currentCount + 1 });
    }
  }
});
```

**時序假設與限制**：
- `estimateConversationValue()` 在 `before_prompt_build` 時只能評估「截至目前」的對話，這是可接受的近似（session 尾聲通常會有明確信號）
- `pendingRecall` 跨 session 不會残存（session 結束時自然失效）

---

## 三、Proposal B — 鄰居擴展

### 3.1 B-1：Reflection 系統鄰居擴展（推薦先行）

```typescript
// 切入點：reflection-slices.ts 的 loadAgentReflectionSlicesFromEntries() 後
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
| 風險 | 🟢 低 |
| 預估工時 | 1-2 天 |
| 效果範圍 | Reflection 系統（隔離）|
| 依賴關係 | **[可平行 Phase 2]** |

### 3.2 B-2：全域 Retrieval 鄰居擴展

| 評估 | 分數 |
|------|------|
| 改動範圍 | `retriever.ts` 核心邏輯 |
| 風險 | 🟡 中（MMR 衝突）|
| 預估工時 | 3-5 天 |
| 效果範圍 | 全域 retrieval（最大）|
| 依賴關係 | **[依賴 Phase 3 數據]** |

---

## 四、方案比較

### 為什麼 B-1 優先於 Proposal A？

| 維度 | B-1 | Proposal A |
|------|------|-----------|
| 實作複雜度 | 低 | 中 |
| 失敗風險 | 極低 | 中（feedback signal）|
| 驗證方式 | 直接觀察輸出差異 | 需長期數據累積 |
| 效果範圍 | Reflection 系統（隔離）| 全域 retrieval（最大）|
| 結論 | **先做 B-1，累積經驗再做 A** | - |

---

## 五、最終推薦方案（含依賴關係）

### Phase 1：B-1 鄰居擴展【可平行 Phase 2】
- **實作位置**：`reflection-slices.ts`
- **風險**：極低
- **驗證**：直接觀察 reflection injection 結果

### Phase 2：`last_confirmed_use_at` 寫入機制【可平行 Phase 1】
- **實作位置**：`agent_end` + `before_prompt_build` 雙 hook 搭配
- **做法**：寫入 `last_confirmed_use_at = Date.now()` 和 `bad_recall_count`
- **風險**：低
- **驗證**：觀察每日寫入率，預期穩定後 > 10 筆/天

### Phase 3：Importance 直接調整【依賴 Phase 2 數據】
- **觸發條件**（量化標準）：
  1. `last_confirmed_use_at` 每日寫入率連續 7 天 > 10 筆
  2. 觀察到有記憶的 `last_confirmed_use_at` 和 `decay_rate` 有明顯相關
- **做法**：根據 Phase 2 觀察到的數據，校正幅度數字後再實作
- **風險**：中
- **我們的建議**：`bad_recall_count` 作為 Phase 3 觸發欄位。理由：它已經是閒置欄位，可以直接用來追蹤「連續未被使用」的記憶，搭配 `importance -= 0.20` 可以快速降級壞記憶。

### Phase 4：B-2 全域擴展【依賴 Phase 1 穩定】
- **觸發條件**：Phase 1 運行 1 個月無異常
- **風險**：中

---

## 六、Claude Code 借鑒（附錄）

Claude Code 的 `session-compressor.ts` 有 `estimateConversationValue()` 可估算 session 品質（0-1）。

```typescript
const sessionValue = estimateConversationValue(messages ?? []);
const multiplier = 0.5 + sessionValue; // 0.5~1.5
const adjustedBoost = baseBoost * multiplier;

// 上層 clamp：Math.min(1.0, importance + adjustedBoost)
// 下層 clamp：Math.max(0.1, importance - penalty)
```

**時序說明**：`estimateConversationValue()` 在 `before_prompt_build` 評估的是「截至當下」的對話內容，是不完整的 session 近似。這在多數情況下是可接受的（session 尾聲會有明確信號如 user 確認/否定），但邊界情況（如 user 第一句就確認）可能導致 sessionValue 偏低。此限制應在實作後觀察資料再決定是否需要修正。

---

## 七、待作者確認

1. ✅ Feedback signal 判斷：**中段 substring match** 作為 Phase 2 的做法可以嗎？（接受高 false negative）
2. ✅ 調整幅度修正：`+0.05` / `+0.15` / `-0.20` / `-0.03`，錯誤記憶 3 步到 0.1，正確記憶 6 步到 1.0
3. ✅ `bad_recall_count` 作為 Phase 3 觸發欄位，理由已補充，是否採用？
4. Phase 2 的「穩定」量化標準：每日寫入率 > 10 筆連續 7 天，是否合理？
