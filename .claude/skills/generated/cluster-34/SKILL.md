---
name: cluster-34
description: "Skill for the Cluster_34 area of memory-lancedb-pro. 16 symbols across 1 files."
---

# Cluster_34

16 symbols | 1 files | Cohesion: 60%

## When to Use

- Working with code in `src/`
- Understanding how reverseMapLegacyCategory, parseSmartMetadata, toLifecycleMemory work
- Modifying cluster_34-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/smart-metadata.ts` | clamp01, clampCount, normalizeTier, normalizeState, normalizeSource (+11) |

## Entry Points

Start here when exploring this area:

- **`reverseMapLegacyCategory`** (Function) — `src/smart-metadata.ts:154`
- **`parseSmartMetadata`** (Function) — `src/smart-metadata.ts:251`
- **`toLifecycleMemory`** (Function) — `src/smart-metadata.ts:476`
- **`getDecayableFromEntry`** (Function) — `src/smart-metadata.ts:507`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `reverseMapLegacyCategory` | Function | `src/smart-metadata.ts` | 154 |
| `parseSmartMetadata` | Function | `src/smart-metadata.ts` | 251 |
| `toLifecycleMemory` | Function | `src/smart-metadata.ts` | 476 |
| `getDecayableFromEntry` | Function | `src/smart-metadata.ts` | 507 |
| `clamp01` | Function | `src/smart-metadata.ts` | 78 |
| `clampCount` | Function | `src/smart-metadata.ts` | 84 |
| `normalizeTier` | Function | `src/smart-metadata.ts` | 90 |
| `normalizeState` | Function | `src/smart-metadata.ts` | 101 |
| `normalizeSource` | Function | `src/smart-metadata.ts` | 112 |
| `normalizeLayer` | Function | `src/smart-metadata.ts` | 125 |
| `deriveDefaultLayer` | Function | `src/smart-metadata.ts` | 137 |
| `defaultOverview` | Function | `src/smart-metadata.ts` | 180 |
| `normalizeText` | Function | `src/smart-metadata.ts` | 184 |
| `normalizeOptionalString` | Function | `src/smart-metadata.ts` | 188 |
| `normalizeTimestamp` | Function | `src/smart-metadata.ts` | 192 |
| `normalizeOptionalTimestamp` | Function | `src/smart-metadata.ts` | 198 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run → ReverseMapLegacyCategory` | cross_community | 3 |
| `Run → NormalizeText` | cross_community | 3 |
| `Run → NormalizeTimestamp` | cross_community | 3 |
| `Run → NormalizeOptionalTimestamp` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 1 calls |

## How to Explore

1. `gitnexus_context({name: "reverseMapLegacyCategory"})` — see callers and callees
2. `gitnexus_query({query: "cluster_34"})` — find related execution flows
3. Read key files listed above for implementation details
