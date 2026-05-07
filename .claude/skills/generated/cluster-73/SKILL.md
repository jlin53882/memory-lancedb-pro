---
name: cluster-73
description: "Skill for the Cluster_73 area of memory-lancedb-pro. 16 symbols across 1 files."
---

# Cluster_73

16 symbols | 1 files | Cohesion: 98%

## When to Use

- Working with code in `src/`
- Understanding how loadAgentReflectionSlicesFromEntries, isOwnedByAgent, loadReflectionMappedRowsFromEntries work
- Modifying cluster_73-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/reflection-store.ts` | loadAgentReflectionSlicesFromEntries, buildInvariantCandidates, itemCandidates, buildDerivedCandidates, rankReflectionLines (+11) |

## Entry Points

Start here when exploring this area:

- **`loadAgentReflectionSlicesFromEntries`** (Function) — `src/reflection-store.ts:233`
- **`isOwnedByAgent`** (Function) — `src/reflection-store.ts:442`
- **`loadReflectionMappedRowsFromEntries`** (Function) — `src/reflection-store.ts:532`
- **`weighted`** (Function) — `src/reflection-store.ts:550`
- **`sortedByKind`** (Function) — `src/reflection-store.ts:607`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `loadAgentReflectionSlicesFromEntries` | Function | `src/reflection-store.ts` | 233 |
| `isOwnedByAgent` | Function | `src/reflection-store.ts` | 442 |
| `loadReflectionMappedRowsFromEntries` | Function | `src/reflection-store.ts` | 532 |
| `weighted` | Function | `src/reflection-store.ts` | 550 |
| `sortedByKind` | Function | `src/reflection-store.ts` | 607 |
| `buildInvariantCandidates` | Function | `src/reflection-store.ts` | 282 |
| `itemCandidates` | Function | `src/reflection-store.ts` | 286 |
| `buildDerivedCandidates` | Function | `src/reflection-store.ts` | 324 |
| `rankReflectionLines` | Function | `src/reflection-store.ts` | 388 |
| `isReflectionMetadataType` | Function | `src/reflection-store.ts` | 438 |
| `toStringArray` | Function | `src/reflection-store.ts` | 475 |
| `metadataTimestamp` | Function | `src/reflection-store.ts` | 482 |
| `readPositiveNumber` | Function | `src/reflection-store.ts` | 488 |
| `readClampedNumber` | Function | `src/reflection-store.ts` | 494 |
| `resolveLegacyDeriveBaseWeight` | Function | `src/reflection-store.ts` | 506 |
| `parseMappedKind` | Function | `src/reflection-store.ts` | 625 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `LoadAgentReflectionSlicesFromEntries → MetadataTimestamp` | intra_community | 3 |
| `LoadAgentReflectionSlicesFromEntries → ToStringArray` | intra_community | 3 |
| `LoadAgentReflectionSlicesFromEntries → ResolveLegacyDeriveBaseWeight` | intra_community | 3 |
| `LoadAgentReflectionSlicesFromEntries → ComputeDerivedLineQuality` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 1 calls |

## How to Explore

1. `gitnexus_context({name: "loadAgentReflectionSlicesFromEntries"})` — see callers and callees
2. `gitnexus_query({query: "cluster_73"})` — find related execution flows
3. Read key files listed above for implementation details
