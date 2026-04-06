# Issue #445 — PR #246 Proposal A & B 實作分析（v7 定稿）

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒
> 更新：v7 — 修正 TypeScript augmentation、store 宣告來源、session_end hook 驗證

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

---

## 二、Proposal A — 動態 Importance

### 2.1 Feedback Signal 設計

| 信號 | 捕捉時機 | 調整幅度 | 到達邊界需幾次 |
|------|---------|---------|--------------|
| 被引用進回應 | Phase 2 雙 hook 搭配（見 2.3）| **+0.05**，上限 1.0 | 6 次（0.7→1.0） |
| user 明確確認正確 | agent_end 解析 | **+0.15**，上限 1.0 | 2 次（0.7→1.0） |
| user 標記錯誤 | agent_end 解析 | **-0.20**，下限 0.1 | 3 次（0.7→0.1）|
| 召回後沒被用到（連續2次）| 下次 `before_prompt_build` | **-0.03** | —（溫和） |

### 2.2 Feedback Signal 的可靠判斷方式

```typescript
/**
 * 判斷 recall 的記憶是否被 agent 回應使用。
 * 方法：取記憶的中段（避開固定前綴），與回應做 substring match。
 *
 * 局限性：
 *   - False negative 高（記憶被意譯就不匹配）：刻意接受，保守代價低
 *   - False positive 低：已用中段取樣緩解
 *   - 短文本（< 90字）使用全段策略，減少 false negative
 */
function isRecallUsed(recallText: string, responseText: string): boolean {
  const text = recallText.trim();
  if (text.length < 20) return false;

  let snippet: string;
  if (text.length > 90) {
    // 長文本：取前20-70字的核心段，避開固定前綴
    snippet = text.slice(20, 70);
  } else {
    // 短文本：取全部作為核心段
    snippet = text;
  }

  if (snippet.length < 5) return false;
  if (/^[\s\p{P}]+$/u.test(snippet)) return false;

  return responseText.toLowerCase().includes(snippet.toLowerCase());
}
```

### 2.3 跨 Turn 狀態保存（實作核心）

#### TypeScript Interface 擴展（Module Augmentation）

```typescript
// ✅ 使用 module augmentation 擴展 SDK 型別（而非 type alias）
// 若 SDK 不支援 module augmentation，則改用註釋標注「等 SDK 型別更新後移除 cast」
declare module 'openclaw-sdk' {
  interface Session {
    /** 此次 injection 所使用的 recall 記憶 IDs */
    recalledMemoryIds?: string[];
  }
}
```

#### 實作程式碼

```typescript
// ============================================================
// 前置宣告
// ============================================================
// store 來源：plugin 內部 singleton（由 OpenClaw SDK 注入，plugin 初始化時取得）
// 以下程式碼直接使用，不重複 import
// import { store } from './store';

// pendingRecall：module-level Map，key 為 sessionId（不怕 GC）
const pendingRecall = new Map<string, {
  recallIds: string[];
  responseText: string;
  injectedAt: number;
}>();

// ============================================================
// agent_end：儲存這輪 injection 的 recall IDs 和 agent 回應
// ============================================================
// ⚠️ 實作前確認：agent_end hook 是否存在於目前 OpenClaw API 版本
api.on("agent_end", async (event, ctx) => {
  const sessionId = ctx.session.id;
  const responseText = ctx.messages.at(-1)?.content ?? "";

  const recallIds = ctx.session.recalledMemoryIds; // ✅ 已由 augmentation 擴展，不再需要 cast
  if (!recallIds || !Array.isArray(recallIds) || recallIds.length === 0) {
    console.warn(`[ProposalA] agent_end: recalledMemoryIds not found or empty for session ${sessionId}`);
    return;
  }

  pendingRecall.set(sessionId, { recallIds, responseText, injectedAt: Date.now() });
});

// ============================================================
// before_prompt_build：比對並寫入 metadata
// ============================================================
// ⚠️ 實作前確認：before_prompt_build hook 是否存在於目前 OpenClaw API 版本
api.on("before_prompt_build", async (event, ctx) => {
  const sessionId = ctx.session.id;
  const pending = pendingRecall.get(sessionId);
  pendingRecall.delete(sessionId); // 取完立即刪除

  if (!pending || pending.recallIds.length === 0) return;

  const { recallIds, responseText } = pending;
  const sessionMessages = ctx.messages ?? [];

  for (const id of recallIds) {
    const recallEntry = await store.get(id);
    if (!recallEntry) continue;

    const currentCount = recallEntry.bad_recall_count ?? 0;
    const userResponse = extractUserResponseAfter(sessionMessages, pending.injectedAt);
    const textToCheck = userResponse ?? responseText; // fallback：無 user 回應時取 agent response
    const used = isRecallUsed(recallEntry.text, textToCheck);

    if (used) {
      // 設計說明：一次原諒全部。
      // 理由：一旦被使用，代表這條記憶仍然有效；
      // 之前的 bad_recall_count 是「誤判未用」（query 不精確），非記憶本身有問題
      await store.update(id, {
        last_confirmed_use_at: Date.now(),
        bad_recall_count: 0
      });
    } else {
      await store.update(id, { bad_recall_count: currentCount + 1 });
    }
  }
});

// ============================================================
// session_end：防止 pendingRecall 記憶洩漏
// ============================================================
// ⚠️ 實作前確認：session_end hook 是否存在於目前 OpenClaw API 版本
//   若不存在，改用 TTL-based cleanup（寫入時記錄 injectedAt，定期清除 > 5 分鐘的殘留項目）
api.on("session_end", async (event, ctx) => {
  pendingRecall.delete(ctx.session.id);
});

// ============================================================
// extractUserResponseAfter：找 user 回應
// ============================================================
/**
 * 從 session messages 中找出 agent 回應時間戳之後的 user 回應文字。
 *
 * ⚠️ 時限假設：
 *   - 若 messages 沒有 timestamp（m.timestamp ?? 0 === 0），永遠回傳 null，
 *     會 fallback 到 responseText。這個 fallback 是合理的，應在日誌中標記發生次數。
 */
function extractUserResponseAfter(
  messages: Array<{ role: string; content: string; timestamp?: number }>,
  afterTimestamp: number
): string | null {
  const userMsg = messages.find(
    m => m.role === "user" && (m.timestamp ?? 0) > afterTimestamp
  );
  return userMsg?.content ?? null;
}
```

---

## 三、Proposal B — 鄰居擴展

### 3.1 B-1：Reflection 系統鄰居擴展（推薦先行）

```typescript
// 切入點：reflection-slices.ts 的 loadAgentReflectionSlicesFromEntries() 後

// ✅ 明確型別
const expanded: ReflectionSlice[] = [];

for (const slice of derivedSlices) {
  // scope: 'same' — 只擴展同 strictKey 的 reflection items（同 invariant group）
  const neighbors = await bm25Search(slice.text, { topK: 2, scope: 'same' });
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
- **驗收標準**：Reflection injection 結果數量增加

### Phase 2：`last_confirmed_use_at` 寫入機制【可平行 Phase 1】
- **實作位置**：`agent_end` + `before_prompt_build` + `session_end` 三 hook
- **實作前確認**：`agent_end`、`before_prompt_build`、`session_end` 三 hook 是否存在於目前 SDK 版本
- **驗收標準**：`last_confirmed_use_at` 每日寫入率 > 0，`bad_recall_count` 有遞增記錄

### Phase 3：Importance 直接調整【依賴 Phase 2 數據】
- **觸發條件**：`last_confirmed_use_at` 每日寫入率連續 7 天 > 10 筆
- **觸發者**：人工確認（自動化只做日誌 alert）
- **建議**：`bad_recall_count` 作為 Phase 3 觸發欄位

### Phase 4：B-2 全域擴展【依賴 Phase 1 穩定】
- **觸發條件**：Phase 1 運行 1 個月無異常

---

## 六、Claude Code 借鑒（附錄）

```typescript
const sessionValue = estimateConversationValue(messages ?? []);
const multiplier = 0.5 + sessionValue; // 0.5~1.5
const adjustedBoost = baseBoost * multiplier;

// clamp 由上層處理：
// Math.min(1.0, importance + adjustedBoost)  // 上限
// Math.max(0.1, importance - penalty)          // 下限
```

**時序**：在 `before_prompt_build` 評估「截至目前」的對話，是不完整的近似。實作後觀察再決定是否修正。

---

## 七、待作者確認

1. ✅ Feedback signal：中段 substring match + 短文本全段
2. ✅ 調整幅度：`+0.05` / `+0.15` / `-0.20` / `-0.03`
3. ✅ bad_recall_count 重置邏輯：一次原諒全部
4. ✅ Phase 2 驗收標準：每日寫入率 > 0 + bad_recall_count 有記錄
5. ✅ Module augmentation 是否可接受？（若 SDK 不支援，保留 cast 並加註）
