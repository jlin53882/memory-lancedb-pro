---
name: cluster-39
description: "Skill for the Cluster_39 area of memory-lancedb-pro. 9 symbols across 2 files."
---

# Cluster_39

9 symbols | 2 files | Cohesion: 57%

## When to Use

- Working with code in `src/`
- Understanding how extractAndPersist, learnAsNoise, processCandidate work
- Modifying cluster_39-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/smart-extractor.ts` | extractAndPersist, learnAsNoise, processCandidate, handleProfileMerge, handleMerge (+3) |
| `src/embedder.ts` | embed |

## Entry Points

Start here when exploring this area:

- **`extractAndPersist`** (Method) — `src/smart-extractor.ts:315`
- **`learnAsNoise`** (Method) — `src/smart-extractor.ts:527`
- **`processCandidate`** (Method) — `src/smart-extractor.ts:656`
- **`handleProfileMerge`** (Method) — `src/smart-extractor.ts:974`
- **`handleMerge`** (Method) — `src/smart-extractor.ts:1042`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `extractAndPersist` | Method | `src/smart-extractor.ts` | 315 |
| `learnAsNoise` | Method | `src/smart-extractor.ts` | 527 |
| `processCandidate` | Method | `src/smart-extractor.ts` | 656 |
| `handleProfileMerge` | Method | `src/smart-extractor.ts` | 974 |
| `handleMerge` | Method | `src/smart-extractor.ts` | 1042 |
| `buildStoreEntry` | Method | `src/smart-extractor.ts` | 1406 |
| `storeCandidate` | Method | `src/smart-extractor.ts` | 1456 |
| `recordRejectedAdmission` | Method | `src/smart-extractor.ts` | 1537 |
| `embed` | Method | `src/embedder.ts` | 784 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `StoreCandidate → LoadLockfile` | cross_community | 7 |
| `ExtractAndPersist → Key` | cross_community | 7 |
| `ExtractAndPersist → IsOllamaProvider` | cross_community | 7 |
| `ExtractAndPersist → EmbedWithNativeFetch` | cross_community | 7 |
| `ExtractAndPersist → NextClient` | cross_community | 7 |
| `Register → BuildPayload` | cross_community | 7 |
| `Register → ValidateEmbedding` | cross_community | 7 |
| `HandleMerge → LoadLanceDB` | cross_community | 6 |
| `HandleMerge → IsExplicitDenyAllScopeFilter` | cross_community | 6 |
| `HandleMerge → Key` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_22 | 13 calls |
| Cluster_36 | 3 calls |
| Test | 3 calls |
| Cluster_40 | 2 calls |
| Cluster_121 | 2 calls |
| Cluster_30 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "extractAndPersist"})` — see callers and callees
2. `gitnexus_query({query: "cluster_39"})` — find related execution flows
3. Read key files listed above for implementation details
