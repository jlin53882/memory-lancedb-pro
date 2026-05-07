---
name: cluster-30
description: "Skill for the Cluster_30 area of memory-lancedb-pro. 22 symbols across 5 files."
---

# Cluster_30

22 symbols | 5 files | Cohesion: 76%

## When to Use

- Working with code in `src/`
- Understanding how vectorSearch, bm25Search, vectorOnlyRetrieval work
- Modifying cluster_30-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/retriever.ts` | attachFailureStage, extractFailureStage, vectorOnlyRetrieval, bm25OnlyRetrieval, hybridRetrieval (+10) |
| `src/store.ts` | clampInt, vectorSearch, bm25Search |
| `src/retrieval-trace.ts` | startStage, endStage |
| `src/embedder.ts` | embedQuery |
| `src/decay-engine.ts` | applySearchBoost |

## Entry Points

Start here when exploring this area:

- **`vectorSearch`** (Method) — `src/store.ts:608`
- **`bm25Search`** (Method) — `src/store.ts:674`
- **`vectorOnlyRetrieval`** (Method) — `src/retriever.ts:712`
- **`bm25OnlyRetrieval`** (Method) — `src/retriever.ts:798`
- **`hybridRetrieval`** (Method) — `src/retriever.ts:901`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `vectorSearch` | Method | `src/store.ts` | 608 |
| `bm25Search` | Method | `src/store.ts` | 674 |
| `vectorOnlyRetrieval` | Method | `src/retriever.ts` | 712 |
| `bm25OnlyRetrieval` | Method | `src/retriever.ts` | 798 |
| `hybridRetrieval` | Method | `src/retriever.ts` | 901 |
| `runVectorSearch` | Method | `src/retriever.ts` | 1091 |
| `runBM25Search` | Method | `src/retriever.ts` | 1116 |
| `buildBM25Query` | Method | `src/retriever.ts` | 1135 |
| `applyRecencyBoost` | Method | `src/retriever.ts` | 1380 |
| `applyImportanceWeight` | Method | `src/retriever.ts` | 1408 |
| `applyDecayBoost` | Method | `src/retriever.ts` | 1421 |
| `applyLengthNormalization` | Method | `src/retriever.ts` | 1446 |
| `applyTimeDecay` | Method | `src/retriever.ts` | 1481 |
| `applyLifecycleBoost` | Method | `src/retriever.ts` | 1526 |
| `applyMMRDiversity` | Method | `src/retriever.ts` | 1608 |
| `startStage` | Method | `src/retrieval-trace.ts` | 65 |
| `endStage` | Method | `src/retrieval-trace.ts` | 82 |
| `embedQuery` | Method | `src/embedder.ts` | 797 |
| `applySearchBoost` | Method | `src/decay-engine.ts` | 90 |
| `clampInt` | Function | `src/store.ts` | 94 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Deduplicate → LoadLockfile` | cross_community | 7 |
| `Execute → EndStage` | cross_community | 6 |
| `Evaluate → LoadLanceDB` | cross_community | 6 |
| `MigrateEntries → LoadLanceDB` | cross_community | 6 |
| `MigrateEntries → IsExplicitDenyAllScopeFilter` | cross_community | 6 |
| `Deduplicate → LoadLanceDB` | cross_community | 6 |
| `Deduplicate → IsExplicitDenyAllScopeFilter` | cross_community | 6 |
| `HybridRetrieval → Key` | cross_community | 5 |
| `HybridRetrieval → IsOllamaProvider` | cross_community | 5 |
| `HybridRetrieval → EmbedWithNativeFetch` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_22 | 7 calls |
| Test | 4 calls |
| Cluster_65 | 1 calls |
| Cluster_40 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "vectorSearch"})` — see callers and callees
2. `gitnexus_query({query: "cluster_30"})` — find related execution flows
3. Read key files listed above for implementation details
