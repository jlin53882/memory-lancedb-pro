---
name: cluster-40
description: "Skill for the Cluster_40 area of memory-lancedb-pro. 12 symbols across 2 files."
---

# Cluster_40

12 symbols | 2 files | Cohesion: 75%

## When to Use

- Working with code in `src/`
- Understanding how filterNoiseByEmbedding, embedBatch, embedBatchQuery work
- Modifying cluster_40-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/embedder.ts` | _evictExpired, key, get, set, embedBatch (+6) |
| `src/smart-extractor.ts` | filterNoiseByEmbedding |

## Entry Points

Start here when exploring this area:

- **`filterNoiseByEmbedding`** (Method) — `src/smart-extractor.ts:460`
- **`embedBatch`** (Method) — `src/embedder.ts:789`
- **`embedBatchQuery`** (Method) — `src/embedder.ts:809`
- **`embedBatchPassage`** (Method) — `src/embedder.ts:813`
- **`validateEmbedding`** (Method) — `src/embedder.ts:821`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `filterNoiseByEmbedding` | Method | `src/smart-extractor.ts` | 460 |
| `embedBatch` | Method | `src/embedder.ts` | 789 |
| `embedBatchQuery` | Method | `src/embedder.ts` | 809 |
| `embedBatchPassage` | Method | `src/embedder.ts` | 813 |
| `validateEmbedding` | Method | `src/embedder.ts` | 821 |
| `buildPayload` | Method | `src/embedder.ts` | 832 |
| `embedSingle` | Method | `src/embedder.ts` | 868 |
| `embedMany` | Method | `src/embedder.ts` | 987 |
| `_evictExpired` | Method | `src/embedder.ts` | 36 |
| `key` | Method | `src/embedder.ts` | 45 |
| `get` | Method | `src/embedder.ts` | 50 |
| `set` | Method | `src/embedder.ts` | 69 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `ExtractAndPersist → Key` | cross_community | 7 |
| `ExtractAndPersist → IsOllamaProvider` | cross_community | 7 |
| `ExtractAndPersist → EmbedWithNativeFetch` | cross_community | 7 |
| `ExtractAndPersist → NextClient` | cross_community | 7 |
| `Register → BuildPayload` | cross_community | 7 |
| `Register → ValidateEmbedding` | cross_community | 7 |
| `HandleMerge → Key` | cross_community | 6 |
| `HandleMerge → IsOllamaProvider` | cross_community | 6 |
| `Init → Key` | cross_community | 6 |
| `Init → IsOllamaProvider` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_108 | 4 calls |
| Cluster_106 | 2 calls |

## How to Explore

1. `gitnexus_context({name: "filterNoiseByEmbedding"})` — see callers and callees
2. `gitnexus_query({query: "cluster_40"})` — find related execution flows
3. Read key files listed above for implementation details
