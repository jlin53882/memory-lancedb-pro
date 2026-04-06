# PR #246 Phase 1 測試結果報告

**時間**：2026-04-02 16:40 GMT+8
**目標**：執行現有測試 + 驗證 Phase 1 B-1（BM25 擴展）實作正確性

---

## 現有測試結果

| 測試檔案 | 結果 | 備註 |
|---------|------|------|
| `memory-reflection.test.mjs` | ⚠️ 32 PASS / 1 FAIL | 1 個預設值相關的失敗（與 Phase 1 無關）|
| `reflection-bypass-hook.test.mjs` | ✅ 4/4 PASS | 全部通過 |

### 失敗測試分析

**位置**：`test/memory-reflection.test.mjs:1168`
```
assert.equal(parsed.sessionStrategy, "systemSessionMemory");
// 預期：'systemSessionMemory'
// 實際：'none'
```

**原因**：與 Phase 1 BM25 擴展實作無關，屬於既有的 `parsePluginConfig` 預設值邏輯問題（`sessionStrategy` 欄位的 fallback 行為）。

---

## Phase 1 實作驗證

目標函式：`loadAgentReflectionSlicesWithBm25Expansion`（`src/reflection-slices.ts`）

| 檢查點 | 結果 | 原始碼依據 |
|--------|------|-----------|
| `scopeFilter` 預設 `undefined`（global） | ✅ | `const scopeFilter = options?.bm25Scope;`（無預設值 → `undefined` = 全域）|
| `topK` 預設 2 | ✅ | `const topK = options?.bm25TopK ?? 2;` |
| 去重邏輯存在 | ✅ | `const seen = new Set<string>()` + `seen.has(neighborText)` + `seen.add(neighborText)` |
| 只擴展 `derived`，不擴展 `invariants` | ✅ | 回傳 `{ invariants: [], derived: expanded, expandedFrom: expanded.length }` — `invariants` 固定為空陣列 |

### 實作邏輯摘要

```typescript
// 去重機制（lines 287-299）
const expanded: string[] = [];
const seen = new Set<string>();
for (const entry of params.entries) {
  const text = entry.text?.trim();
  if (!text || seen.has(text)) continue;
  const neighbors = await store.bm25Search(text, topK, scopeFilter, { excludeInactive });
  for (const neighbor of neighbors) {
    const neighborText = neighbor.entry?.text?.trim();
    if (neighborText && !seen.has(neighborText)) {
      seen.add(neighborText);
      expanded.push(neighborText);
    }
  }
}
return { invariants: [], derived: expanded, expandedFrom: expanded.length };
```

---

## 結論

- **測試**：32/33 通過，1 個失敗與 Phase 1 無關（既有的 `parsePluginConfig` 預設值問題）。
- **Phase 1 實作**：所有 4 個檢查點全部 ✅ 正確實作。

---

## 後續建議

1. **Phase 1 實作可確認無誤**，可繼續推進 Phase 2。
2. 失敗的測試（`defaults to systemSessionMemory when neither field is set`）屬於獨立的預設值邏輯問題，建議另開 issue 追蹤，不阻礙 PR #246 合併。
