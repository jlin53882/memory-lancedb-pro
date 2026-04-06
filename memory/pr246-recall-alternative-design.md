# `recalledMemoryIds` 替代方案分析

> 日期：2026-04-02
> 背景：SDK 驗證確認 `ctx.session.recalledMemoryIds` **不存在**於 `PluginHookAgentContext`，須重新設計 Phase 2 的 hook 資料流

---

## 一、recalledMemoryIds 的事實查核

### 1.1 設計文件 v8 的錯誤描述

設計文件 v8 聲稱：

> `recalledMemoryIds` 由 **OpenClaw core recall pipeline** 在 `before_prompt_build` 執行完後寫入（寫入時機在 injection 結果產生之後、agent response 之前），plugin 無需自行維護。

### 1.2 SDK 驗證結果

**❌ 錯誤。** `recalledMemoryIds` 欄位在 `PluginHookAgentContext` 中**不存在**。

驗證方式：在 `memory-lancedb-pro` 原始碼（`index.ts`）中搜索 `recalledMemoryIds`，結果為 **0 處引用**。該欄位從未在任何 hook callback 的 `ctx` 物件中被使用。

---

## 二、實際 Memory Injection 發生位置

### 2.1 Injection 發生在 `before_prompt_build` 內部

從 `index.ts` 的 `before_prompt_build` hook（`config.autoRecall === true` 分支）：

```typescript
api.on("before_prompt_build", async (event: any, ctx: any) => {
  // ...
  const recallWork = async (): Promise<{ prependContext: string } | undefined> => {
    // 1. 決定 accessibleScopes
    const accessibleScopes = resolveScopeFilter(scopeManager, agentId);

    // 2. 執行 recall（整個函式在 hook 內部執行）
    const results = filterUserMdExclusiveRecallResults(await retrieveWithRetry({
      query: recallQuery,
      limit: retrieveLimit,
      scopeFilter: accessibleScopes,
      source: "auto-recall",
      signal: recallAbortController.signal,
    }), config.workspaceBoundary);

    // 3. Governance 過濾 → selected[] → prependContext
    const selected = [...]; // selected[].id 包含所有被 injection 的 memory IDs

    return {
      prependContext:
        `<relevant-memories>\n` +
        `[UNTRUSTED DATA — historical notes from long-term memory...]\n` +
        `${memoryContext}\n` +
        `[END UNTRUSTED DATA]\n` +
        `</relevant-memories>`,
    };
  };

  const result = await Promise.race([recallWork()..., timeout...]);
  return result; // 回傳 { prependContext }
}, { priority: 10 });
```

**關鍵觀察**：
- Recall 發生在 `recallWork()` 函式內部，**整個過程封裝在 `before_prompt_build` hook 裡面**
- `selected[].id`陣列包含所有被 injection 的 memory IDs
- Hook 最後 `return` 一個 `{ prependContext: string }`，**這個回傳值只帶文字，不帶 ID 列表**

### 2.2 沒有任何 SDK 機制在 hook 間傳遞 recall IDs

當 `before_prompt_build` 回傳 `{ prependContext }` 時：
- OpenClaw core 將 `prependContext` 文字拼接進 prompt
- **沒有任何 SDK 機制**將 `selected[].id` 傳遞給後續的 `agent_end` 或 `session_end` hook
- `ctx.session` 中不存在 `recalledMemoryIds` 欄位

---

## 三、替代方案分析

### 方案 A：Plugin 內部維護 `Map<sessionId, recallInfo>`（推薦）

**做法**：在 `before_prompt_build` 的 `recallWork()` 執行完、return 之前，將 `selected[].id` 存入模組級別的 `Map`。

```typescript
// 模組級別（plugin 實例內，process 生命周期持久）
const pendingRecallBySession = new Map<string, {
  recallIds: string[];
  responseText: string;
  injectedAt: number;
}>();

// ============================================================
// before_prompt_build：攔截並記住
// ============================================================
api.on("before_prompt_build", async (event: any, ctx: any) => {
  const sessionId = ctx?.sessionId || "default";
  const recallResult = await recallWork(); // 執行 recall

  if (recallResult && recallResult.prependContext) {
    // 記住這輪 injection 的 IDs（在 return 之前）
    const selectedIds = selected.map(item => item.id); // selected[] 是 recallWork 內部變數
    pendingRecallBySession.set(sessionId, {
      recallIds: selectedIds,
      injectedAt: Date.now(),
      responseText: "", // responseText 等 agent_end 時填入
    });
  }

  return recallResult;
}, { priority: 10 });

// ============================================================
// agent_end：取用並清除
// ============================================================
api.on("agent_end", async (event: any, ctx: any) => {
  const sessionId = ctx?.sessionId || "default";
  const pending = pendingRecallBySession.get(sessionId);
  if (!pending) return;

  const responseText = event.messages?.at(-1)?.content ?? "";
  pending.responseText = responseText;

  // 現在可以用 pending.recallIds + pending.responseText 實作 feedback signal
  // ...
  pendingRecallBySession.delete(sessionId);
});

// ============================================================
// session_end：防止洩漏（額外安全網）
// ============================================================
api.on("session_end", async (_event: any, ctx: any) => {
  pendingRecallBySession.delete(ctx?.sessionId || "default");
}, { priority: 20 });
```

**優點**：
- Plugin 自行維護，不依賴 SDK 任何變更
- 準確：知道哪些 ID 是這輪 injection 的（因為是在同一個 hook instance 內操作）
- 簡單：只有一個 Map，無需 IPC 或檔案 I/O

**缺點**：
- 如果 OpenClaw 在不同 process 中運行 plugin（re-spawn），Map 會丟失 → 但實際上 plugin 是同一個 node_modules singleton，Map 會保持
- 長時間運行的 process（> RAM 上限）Map 可能累積 → 可用 `pruneMapIfOver()` 處理

**風險評估**：🟢 低風險

---

### 方案 B：利用 SDK 內部機制（不可行）

`ctx.session` 中**沒有**任何可用欄位儲存 recall IDs。嘗試利用 SDK 內部機制需要 SDK 團隊支援，目前沒有任何文件或 API 暗示這種機制存在。

**結論**：❌ 不可行

---

### 方案 C：在 `before_prompt_build` 回傳值中夾帶 ID（需要 SDK 支援）

理論上，如果 SDK 的 `before_prompt_build` 回傳值除了 `prependContext` 還能接受 `metadata` 欄位，就可以把 ID 藏在 metadata 裡。但目前 SDK 不支援。

**結論**：❌ 目前 SDK 不支援，需等待 SDK 擴展

---

### 方案 D：延後讀取——用 `sessionId` + `injectedAt` 在 `agent_end` 重新查詢

**做法**：`before_prompt_build` 只記住 `sessionId` + `injectedAt`，`agent_end` 時重新从 store 查詢最近 injection 的記錄（透過 `injected_count` 或 `last_injected_at` 欄位）。

```typescript
// before_prompt_build：只記住 sessionId + injectedAt
const autoRecallInjectionLog = new Map<string, number>(); // sessionId → injectedAt

api.on("before_prompt_build", async (event: any, ctx: any) => {
  const sessionId = ctx?.sessionId || "default";
  const result = await recallWork();
  if (result) {
    autoRecallInjectionLog.set(sessionId, Date.now());
  }
  return result;
});

// agent_end：查詢 last_injected_at 接近的記憶
api.on("agent_end", async (event: any, ctx: any) => {
  const sessionId = ctx?.sessionId || "default";
  const injectedAt = autoRecallInjectionLog.get(sessionId);
  if (!injectedAt) return;

  // 查詢所有 last_injected_at 在 [injectedAt - 1000, injectedAt + 2000] 的記憶
  // （因為 metadata 裡有 last_injected_at + injected_count）
  const candidates = await store.list(accessibleScopes, undefined, 20, 0);
  const recalledIds = candidates
    .filter(e => {
      const meta = parseSmartMetadata(e.metadata, e);
      return meta.last_injected_at >= injectedAt - 1000
          && meta.last_injected_at <= injectedAt + 2000
          && meta.injected_count > 0;
    })
    .map(e => e.id);

  // ...
});
```

**優點**：
- 不需要 plugin 內部 Map（狀態存在 LanceDB 裡）
- Session 重啟也能找回

**缺點**：
- 需要精確的時間窗口，時間可能漂移
- 準確度低：候選範圍需要很大（injected_count 可能有其他來源的 injection）
- 需要重新查詢整個 store（昂貴）

**結論**：❌ 準確度過低，不推薦

---

## 四、推薦方案：A（Plugin 內部 Map）

**方案 A 是唯一可行的實作路徑**。

實作時的唯一細節：`before_prompt_build` 內部的 `selected[]` 陣列（包含 `id` 欄位）需要在 return 之前被提取出來，存入 Map。

```typescript
// recallWork() 內部，在構建 prependContext 之後、return 之前：
const injectedIds = selected.map(item => item.id).join(",") || "(none)";
api.logger.debug?.(`injectedIds=${injectedIds}`);

// 同時存入 Map（由 module-level pendingRecallBySession 提供）
if (sessionId && injectedIds !== "(none)") {
  pendingRecallBySession.set(sessionId, {
    recallIds: selected.map(item => item.id),
    injectedAt: Date.now(),
    responseText: "",
  });
}

return { prependContext: ... };
```

---

## 五、修正後的 Hook 執行順序與資料流

```
┌─────────────────────────────────────────────────────────────────────┐
│  Hook 執行順序（Phase 2 相關）                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. message_received (priority default)                              │
│     → 緩存 raw user message 到 lastRawUserMessage Map              │
│                                                                      │
│  2. before_prompt_build (priority 10, auto-recall)                  │
│     → 執行 recallWork() → 取得 selected[].id                        │
│     → 存入 pendingRecallBySession[sessionId] ← 關鍵！               │
│     → return { prependContext: string }                             │
│     → OpenClaw core 拼接 prependContext 到 prompt                   │
│                                                                      │
│  3. before_prompt_build (priority 12, reflection inheritance)       │
│     → 執行 reflection slice injection                               │
│     → return { prependContext: string }（可能覆蓋或追加）            │
│                                                                      │
│  4. [Agent 生成回應]                                                 │
│                                                                      │
│  5. agent_end (auto-capture)                                        │
│     → 取出 pendingRecallBySession[sessionId]                       │
│     → 取得 responseText                                             │
│     → 執行 isRecallUsed() 判斷回應是否使用了記憶                     │
│     → 寫入 last_confirmed_use_at / bad_recall_count                │
│     → pendingRecallBySession.delete(sessionId)                     │
│                                                                      │
│  6. session_end (priority 20, reflection cleanup)                  │
│     → pendingRecallBySession.delete(sessionId)（安全網）             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**重要修正**：`before_prompt_build` 的回傳值只是字串，**沒有 ID 攜帶機制**。所有 ID 追蹤必須透過 plugin 內部 Map 完成。

---

## 六、附：Proposal A Phase 2 實作程式碼（修正版）

```typescript
// ============================================================
// Phase 2 實作：替代 ctx.session.recalledMemoryIds
// ============================================================

// 模組級別 Map（plugin 實例內持久，process 生命周期）
const pendingRecallBySession = new Map<string, {
  recallIds: string[];
  responseText: string;
  injectedAt: number;
}>();

// prune 防止記憶體無限增長
function prunePendingRecall(maxEntries = 2000) {
  if (pendingRecallBySession.size <= maxEntries) return;
  const excess = pendingRecallBySession.size - maxEntries;
  const keys = [...pendingRecallBySession.keys()];
  for (let i = 0; i < excess; i++) {
    pendingRecallBySession.delete(keys[i]);
  }
}

// ============================================================
// agent_end：儲存這輪 injection 的 recall IDs 和 agent 回應
// ============================================================
api.on("agent_end", async (event: any, ctx: any) => {
  const sessionId = ctx?.sessionId || "default";
  const pending = pendingRecallBySession.get(sessionId);
  if (!pending || pending.recallIds.length === 0) return;

  const responseText = event.messages?.at(-1)?.content ?? "";
  pending.responseText = responseText;

  // isRecallUsed 邏輯（與 v8 設計相同）
  for (const id of pending.recallIds) {
    const entry = await store.get(id);
    if (!entry) continue;

    const meta = parseSmartMetadata(entry.metadata, entry);
    const used = isRecallUsed(entry.text, responseText);

    if (used) {
      await store.patchMetadata(id, {
        last_confirmed_use_at: Date.now(),
        bad_recall_count: 0,
      }, accessibleScopes);
    } else {
      await store.patchMetadata(id, {
        bad_recall_count: (meta.bad_recall_count ?? 0) + 1,
      }, accessibleScopes);
    }
  }

  pendingRecallBySession.delete(sessionId);
});

// ============================================================
// before_prompt_build：將 selected IDs 存入 Map
// ============================================================
// （在現有 auto-recall 邏輯的「selected」建構完成後、return 之前加入）
// 位置：index.ts, before_prompt_build hook 內, recallWork() 的尾端
//
// const selectedIds = selected.map(item => item.id);
// if (sessionId && selectedIds.length > 0) {
//   pendingRecallBySession.set(sessionId, {
//     recallIds: selectedIds,
//     injectedAt: Date.now(),
//     responseText: "",
//   });
// }

// ============================================================
// session_end：安全網，防止 pendingRecall 洩漏
// ============================================================
api.on("session_end", async (_event: any, ctx: any) => {
  pendingRecallBySession.delete(ctx?.sessionId || "default");
}, { priority: 20 });
```

---

## 七、結論

| 方案 | 可行性 | 風險 | 備註 |
|------|--------|------|------|
| A：Plugin 內部 Map | ✅ 推薦 | 🟢 低 | 唯一準確的實作方式 |
| B：SDK 內部機制 | ❌ 不可行 | — | 沒有任何可用欄位 |
| C：回傳值夾帶 | ❌ SDK 不支援 | — | 需 SDK 團隊擴展 |
| D：時間窗口重新查詢 | ❌ 準確度低 | — | 時間漂移問題 |

**設計文件 v8 中關於 `recalledMemoryIds` 的描述需要全部修正**。
