# Issue #445 — PR #246 Proposal A & B 實作分析（v8 定稿）

> 日期：2026-04-02
> 基於：memory-lancedb-pro 原始碼分析 + Claude Code 實作借鑒
> 更新：v8 — 修正 Phase 3 矛盾、recalledMemoryIds 填入責任、store 取得方式、TTL fallback、Phase 1 品質驗收
> 更新：v9 — 修正 `isRecallUsed` text.length=20-24 邏輯缺口（`> 90` → `> 24`），修正 `bm25Search` 參數名（`scope` → `scopeFilter`）

---

## 驗證結果摘要

| 問題 | 答案 |
|------|------|
| getSlices 插入點 | `extractReflectionSlicesWithSanitizer` → `return { invariants, derived }` 的前一瞬間；derived slices 產生後、return 之前插入擴展邏輯 |
| bm25Search 函式名 | ✅ `bm25Search`（`store.ts:522`，`Store` 類別方法） |
| bm25Search scope 參數名 | ⚠️ 應為 `scopeFilter?: string[]`（陣列），非 `scope: 'same'` |
| text.length=20-24 問題 | ✅ 已修復（threshold `> 90` 改為 `> 24`，見 2.2 備註）|

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
| `bad_recall_count` | `smart-metadata.ts` | **欄位存在但未使用** | **Phase 3 觀察依據** | - |
| `recalledMemoryIds` | session context | **Phase 2 關鍵依賴** | 由 OpenClaw core recall pipeline 填入 | - |

**`recalledMemoryIds` 填入責任說明**：此欄位由 **OpenClaw core recall pipeline** 在 `before_prompt_build` 執行完後寫入（寫入時機在 injection 結果產生之後、agent response 之前），plugin 無需自行維護。若實作時發現此欄位不存在，應先確認 SDK 版本是否支援，必要時向 core 提 issue 或實作 feature request。

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
 *   - 短文本（≤ 90字）使用全段策略，減少 false negative
 */
function isRecallUsed(recallText: string, responseText: string): boolean {
  const text = recallText.trim();
  if (text.length < 20) return false;

  let snippet: string;
  if (text.length > 24) {
    // 長文本（> 24字）：取第 20~70 字作為核心段（避開固定前綴）
    // 閾值為 24 而非 90：確保短文本（20~24字）全部作為核心段，
    // 避免 text.slice(20, 70) 產生 0~4 字空片段被 guard 誤判
    snippet = text.slice(20, 70);
  } else {
    // 短文本（20~24字）：全部作為核心段
    snippet = text;
  }

  if (snippet.length < 5) return false;
  if (/^[\s\p{P}]+$/u.test(snippet)) return false;

  return responseText.toLowerCase().includes(snippet.toLowerCase());
}
```

### 2.3 跨 Turn 狀態保存（實作核心）

#### TypeScript Interface 擴展

```typescript
// 使用 module augmentation 擴展 SDK 型別
declare module 'openclaw-sdk' {
  interface Session {
    /** OpenClaw core recall pipeline 在 injection 完成後自動寫入 */
    recalledMemoryIds?: string[];
  }
}
```

#### 實作程式碼

```typescript
// ============================================================
// store 取得方式：ctx.store（由 OpenClaw SDK 在 api.on() callback 的 ctx 物件中注入）
// 用法：const store = ctx.store;
// ============================================================

const pendingRecall = new Map<string, {
  recallIds: string[];
  responseText: string;
  injectedAt: number;
}>();

// ============================================================
// agent_end：儲存這輪 injection 的 recall IDs 和 agent 回應
// ============================================================
api.on("agent_end", async (event, ctx) => {
  const sessionId = ctx.session.id;
  const responseText = ctx.messages.at(-1)?.content ?? "";

  const recallIds = ctx.session.recalledMemoryIds;
  if (!recallIds || !Array.isArray(recallIds) || recallIds.length === 0) {
    // 常態：並非每個 session 都會 recall memory，沒有是正常的，不算錯誤
    return;
  }

  pendingRecall.set(sessionId, { recallIds, responseText, injectedAt: Date.now() });
});

// ============================================================
// before_prompt_build：比對並寫入 metadata
// ============================================================
api.on("before_prompt_build", async (event, ctx) => {
  const sessionId = ctx.session.id;
  const pending = pendingRecall.get(sessionId);
  pendingRecall.delete(sessionId); // 取完立即刪除

  if (!pending || pending.recallIds.length === 0) return;

  const { recallIds, responseText } = pending;
  const sessionMessages = ctx.messages ?? [];
  const store = ctx.store; // ✅ 從 ctx 取得

  for (const id of recallIds) {
    const recallEntry = await store.get(id);
    if (!recallEntry) continue;

    const currentCount = recallEntry.bad_recall_count ?? 0;
    const userResponse = extractUserResponseAfter(sessionMessages, pending.injectedAt);
    const textToCheck = userResponse ?? responseText;
    const used = isRecallUsed(recallEntry.text, textToCheck);

    if (used) {
      await store.update(id, {
        last_confirmed_use_at: Date.now(),
        bad_recall_count: 0  // 一次原諒全部：被使用即代表記憶仍然有效
      });
    } else {
      await store.update(id, { bad_recall_count: currentCount + 1 });
    }
  }
});

// ============================================================
// session_end：防止 pendingRecall 記憶洩漏
// ============================================================
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
 *   - 若 messages 沒有 timestamp，永遠回傳 null，fallback 到 responseText。
 *   - 此 fallback 在無 timestamp 的環境下是預期行為，日誌無需標記。
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
const expanded: ReflectionSlice[] = [];

for (const slice of derivedSlices) {
  // ⚠️ `bm25Search` 為 `store` 實例方法，非自由函式
  // scopeFilter: string[] — 只擴展同 strictKey 的 reflection items（同 invariant group）
  // ⚠️ 注意：design doc 早期版本誤用 `scope: 'same'`，應為 `scopeFilter: [slice.strictKey]`
  const neighbors = await store.bm25Search(slice.text, /* limit */ 2, [slice.strictKey]);
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
- **驗收標準**：
  - **量**：Reflection injection 結果數量增加
  - **質**（人工抽查）：隨機抽 3-5 個 case，確認鄰居 items 與原 slice 主題相關

### Phase 2：`last_confirmed_use_at` 寫入機制【可平行 Phase 1】
- **實作位置**：`agent_end` + `before_prompt_build` + `session_end` 三 hook
- **實作前確認**：`agent_end`、`before_prompt_build`、`session_end` 三 hook 是否存在於 SDK 版本；`ctx.session.recalledMemoryIds` 是否由 core 填入
- **TTL fallback**（若 `session_end` hook 不可用）：在 plugin 初始化時加 `setInterval(() => { const now = Date.now(); for (const [k, v] of pendingRecall) if (now - v.injectedAt > 5 * 60 * 1000) pendingRecall.delete(k); }, 60_000);`（每分鐘清除 5 分鐘前殘留項目）
- **驗收標準**：`last_confirmed_use_at` 每日寫入率 > 0，`bad_recall_count` 有遞增記錄

### Phase 3：Importance 直接調整【依賴 Phase 2 數據】
- **觸發條件**：`last_confirmed_use_at` 每日寫入率連續 7 天 > 10 筆
- **`bad_recall_count` 的角色**：作為 Phase 3 的主要**觀察依據**（而非觸發門檻）。當累積樣本足夠時，可用於分析「被使用但 importance 低」或「未被使用但 importance 高」的異常 patterns，輔助判斷幅度是否需要調整。
- **觸發者**：人工確認（自動化只做日誌 alert）
- **⚠️ Phase 3 潛在陷阱**：Phase 3 若要在 `agent_end` 裡直接寫 `importance`，同樣需要 `const store = ctx.store;`，`before_prompt_build` 的取法須一併帶入。

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
5. ✅ Phase 3：`bad_recall_count` 改為「觀察依據」（非觸發門檻），是否接受？
6. ✅ `recalledMemoryIds` 由 OpenClaw core recall pipeline 填入，文件已說明，是否有異議？
