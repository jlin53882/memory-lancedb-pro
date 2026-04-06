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

**關鍵發現**：`last_confirmed_use_at` 和 `bad_recall_count` 已有 schema 但從未被寫入或讀取。

---

## 二、Proposal A — 動態 Importance

### 2.1 Feedback Signal 設計

#### 數字推算與不對稱性說明

**設計意圖**：錯誤記憶單次危害 > 正確記憶單次確認效益，懲罰幅度大於獎勵幅度。

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
 *
 * ⚠️ 注意：短文本（< 90字）的取樣策略與長文本不同，見下方實作
 */
function isRecallUsed(recallText: string, responseText: string): boolean {
  const text = recallText.trim();
  if (text.length < 20) return false;

  let snippet: string;
  if (text.length > 90) {
    // 長文本：取前20-70字的核心段，避開固定前綴
    snippet = text.slice(20, 70);
  } else {
    // 短文本：取全部（text.length ≤ 90時，start=0, end=text.length）
    // 此時視為「全段皆為核心」，減少短記憶的 false negative
    snippet = text.slice(0, text.length);
  }

  if (snippet.length < 5) return false;
  if (/^[\s\p{P}]+$/u.test(snippet)) return false;

  return responseText.toLowerCase().includes(snippet.toLowerCase());
}
```

### 2.3 跨 Turn 狀態保存（實作核心）

#### 雙 Hook 搭配流程

| Hook | 時機 | 做的事 |
|------|------|--------|
| `agent_end` | agent 產生回應後 | 存入這輪 injection 的 recall IDs + 回應文字 |
| `before_prompt_build` | 下一輪 prompt 建立前 | 取出上一輪 response，與這輪 injection 比對並寫入 metadata |
| `session_end` | session 結束時 | 清理 pendingRecall，防止 leak |

#### TypeScript Interface 擴展

```typescript
// ⚠️ 長期風險管理：補完介面後應將 as any 移除
interface SessionWithRecall {
  id: string;
  recalledMemoryIds?: string[];
  // ...其餘 Session 原有用欄位
}

type Session = SessionWithRecall; // 覆蓋原名稱，實際使用時直接用 Session
```

#### 實作程式碼

```typescript
// 用 module-level Map 儲存上一輪的 recall 結果
// key: sessionId（字串），不怕 GC 問題
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

  // ✅ 用正式介面型別（移除 as any）
  const recallIds = (ctx.session as SessionWithRecall).recalledMemoryIds;
  if (!recallIds || !Array.isArray(recallIds) || recallIds.length === 0) {
    console.warn(`[ProposalA] agent_end: recalledMemoryIds not found or empty for session ${sessionId}`);
    return;
  }

  pendingRecall.set(sessionId, {
    recallIds,
    responseText,
    injectedAt: Date.now()
  });
});

// ============================================================
// before_prompt_build：比對並寫入 metadata
// ============================================================
api.on("before_prompt_build", async (event, ctx) => {
  const sessionId = ctx.session.id;
  const pending = pendingRecall.get(sessionId);

  // ✅ 取完立即刪除
  pendingRecall.delete(sessionId);

  if (!pending || pending.recallIds.length === 0) return;

  const { recallIds, responseText } = pending;
  const sessionMessages = ctx.messages ?? [];

  for (const id of recallIds) {
    const recallEntry = await store.get(id);
    if (!recallEntry) continue;

    const currentCount = recallEntry.bad_recall_count ?? 0;

    const userResponse = extractUserResponseAfter(
      sessionMessages,
      pending.injectedAt
    );

    // ✅ fallback 到 responseText（user 沒回應時）
    const textToCheck = userResponse ?? responseText;
    const used = isRecallUsed(recallEntry.text, textToCheck);

    if (used) {
      // ✅ 設計說明：一次原諒全部。
      // 理由：一旦被使用，代表這條記憶仍然有效，
      // 即使之前有 bad_recall_count，也代表那些是「誤判未用」（query 不精確）而非記憶本身有問題
      await store.update(id, {
        last_confirmed_use_at: Date.now(),
        bad_recall_count: 0
      });
    } else {
      await store.update(id, {
        bad_recall_count: currentCount + 1
      });
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
 * @param messages — session message 陣列
 * @param afterTimestamp — agent_end 的時間戳（injectedAt）
 *
 * ⚠️ 時限假設：
 *   - 如果 messages 沒有 timestamp（m.timestamp ?? 0 === 0），
 *     此函數永遠回傳 null，會 fallback 到 responseText。
 *   - 這個 fallback 是合理的：沒有時間戳時，取 responseText 是最接近的替代。
 *   - 實作者應確保 session messages 有 timestamp，或在日誌中標記此 fallback 發生次數。
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

// ✅ 明確型別（避免 TS 推斷為 never[]）
const expanded: ReflectionSlice[] = [];

for (const slice of derivedSlices) {
  // scope: 'same' — 只擴展同 strictKey 的 reflection items
  // （same = 同 invariant group，確保擴展的鄰居與原 slice 高度相關）
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
- **驗收標準**：Reflection injection 結果有更多鄰近 items（可觀察輸出數量增加）

### Phase 2：`last_confirmed_use_at` 寫入機制【可平行 Phase 1】
- **實作位置**：`agent_end` + `before_prompt_build` + `session_end` 三 hook
- **實作前確認**：`recalledMemoryIds` 欄位存在性（見 2.3）
- **驗收標準**（可觀測指標）：
  - `last_confirmed_use_at` 每日寫入率 > 0
  - `bad_recall_count` 有遞增記錄（日誌可見）

### Phase 3：Importance 直接調整【依賴 Phase 2 數據】
- **觸發條件**（量化標準，需同時滿足）：
  1. `last_confirmed_use_at` 每日寫入率連續 7 天 > 10 筆
  2. `bad_recall_count >= 3` 的記憶樣本（人工抽樣確認有意義）
- **觸發者**：人工確認（自動化只做日誌 alert，不做自動實作切換）
- **建議**：`bad_recall_count` 作為 Phase 3 觸發欄位

### Phase 4：B-2 全域擴展【依賴 Phase 1 穩定】
- **觸發條件**：Phase 1 運行 1 個月無異常

---

## 六、Claude Code 借鑒（附錄）

Claude Code 的 `session-compressor.ts` 有 `estimateConversationValue()` 可估算 session 品質（0-1）。

```typescript
const sessionValue = estimateConversationValue(messages ?? []);
const multiplier = 0.5 + sessionValue; // 0.5~1.5
const adjustedBoost = baseBoost * multiplier;

// 上層 clamp（寫入前保護）：
// Math.min(1.0, importance + adjustedBoost)  // 上限
// Math.max(0.1, importance - penalty)          // 下限
```

**時序說明**：`estimateConversationValue()` 在 `before_prompt_build` 時只能評估「截至目前」的對話，是不完整的近似。邊界情況（如 user 第一句就確認）可能偏低，此限制應在實作後觀察資料再決定是否修正。

---

## 七、待作者確認

1. ✅ Feedback signal 判斷：**中段 substring match + 短文本全段策略**
2. ✅ 調整幅度：`+0.05` / `+0.15` / `-0.20` / `-0.03`
3. ✅ `bad_recall_count` 重置邏輯：一次原諒全部，理由已說明
4. ✅ Phase 2 驗收標準：改為可觀測指標（每日寫入率 > 0 + bad_recall_count 有記錄）
