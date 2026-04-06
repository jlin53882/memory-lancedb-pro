# PRs Created for Issue #445 (Proposal A & B Implementation)

## Overview

Based on AliceLJY's reviewer feedback in Issue #445 Comment: https://github.com/CortexReach/memory-lancedb-pro/issues/445#issuecomment-4175916232

Two PRs have been created to implement the recommended fixes:

---

## PR 1: Phase 1 B-1 Scope-Aware BM25 Neighbor Expansion

**PR URL**: https://github.com/jlin53882/memory-lancedb-pro/pull/3

**Branch**: `feat/proposal-b1-neighbor-expansion`

**Files Changed**: `src/reflection-slices.ts`

### Changes

Added `loadAgentReflectionSlicesWithBm25Expansion()` function that:

1. Takes reflection slice entries and performs BM25 search for each
2. **Key Fix**: Uses `scopeFilter: [entry.scope]` instead of `scopeFilter: undefined` (global expansion)
3. Finds topK=2 neighbors per entry (configurable)
4. Filters by minimum BM25 score (default: 0.1)
5. Merges and deduplicates original entries with neighbors

### Config Options

| Option | Default | Description |
|--------|---------|-------------|
| `topK` | 2 | Number of neighbor results per entry |
| `minScore` | 0.1 | Minimum BM25 score threshold |

### Issue Reference

- Closes #445 (Comment: https://github.com/CortexReach/memory-lancedb-pro/issues/445#issuecomment-4175916232)

---

## PR 2: Phase 2/3 Dynamic Importance Feedback Signals (Proposal A)

**PR URL**: https://github.com/jlin53882/memory-lancedb-pro/pull/4

**Branch**: `feat/proposal-a-feedback-signal`

**Files Changed**: `index.ts`

### Changes

#### Phase 2: Importance Boost for Used Memories

- When a recalled memory is actually used in the response, boost importance by `importanceBoostPerUse` (default: +0.05)
- Detected via `agent_end` hook after message processing

#### Phase 3: Importance Penalty for Unused Memories (with min_recall_count guard)

- When a memory is recalled but not used, apply penalty by `importancePenaltyPerMiss` (default: -0.03)
- **Protected by `minRecallCountForPenalty` guard** (default: 2)
- Only penalizes memories that have been recalled at least `minRecallCountForPenalty` times
- This prevents new memories from being penalized before they've been given a fair chance

### Configuration

Added `config.feedbackSignal` to `PluginConfig` interface:

```typescript
feedbackSignal?: {
  /** Boost per successful use (default: 0.05) */
  importanceBoostPerUse?: number;
  /** Boost per user confirmation (default: 0.15) */
  importanceBoostPerConfirmation?: number;
  /** Penalty per miss (default: 0.03) */
  importancePenaltyPerMiss?: number;
  /** Minimum recall count before applying penalty (default: 2) */
  minRecallCountForPenalty?: number;
};
```

### Issue Reference

- Closes #445 (Comment: https://github.com/CortexReach/memory-lancedb-pro/issues/445#issuecomment-4175916232)

---

## Summary of Fixes Applied

| Fix | Description | File | Status |
|-----|-------------|------|--------|
| Phase 1 B-1 | Changed `scopeFilter: undefined` to `scopeFilter: [entry.scope]` for scope-aware BM25 expansion | `src/reflection-slices.ts` | ✅ Complete |
| Phase 2 | Made magnitude values configurable (`importanceBoostPerUse`, etc.) | `index.ts` | ✅ Complete |
| Phase 3 | Added `min_recall_count` threshold before negative adjustment | `index.ts` | ✅ Complete |

---

## Notes

- PRs are created from fork `jlin53882/memory-lancedb-pro` to upstream `CortexReach/memory-lancedb-pro`
- Both PRs target `master` branch
- Write access to upstream was denied, so PRs are submitted from fork

---

##待確認事項 (Pending Confirmation)

1. **Phase 1**: 需要確認 `loadAgentReflectionSlicesWithBm25Expansion` 是否需要在 `reflection-slices.ts` 中 export，或只是在 `index.ts` 中作為內部使用
2. **Phase 2/3**: `agent_end` hook 中讀取 `__recalledMemoryIds` 的方式是否與 auto-recall hook 的實現一致
3. **User Confirmation Signal**: Phase 2 extension for explicit user confirmation is a placeholder - 需要確認如何檢測用戶確認

---

*Generated: 2026-04-02*
