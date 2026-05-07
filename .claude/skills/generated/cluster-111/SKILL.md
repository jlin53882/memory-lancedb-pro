---
name: cluster-111
description: "Skill for the Cluster_111 area of memory-lancedb-pro. 10 symbols across 1 files."
---

# Cluster_111

10 symbols | 1 files | Cohesion: 100%

## When to Use

- Working with code in `src/`
- Understanding how getTierBeta, getTierFloor, recency work
- Modifying cluster_111-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/decay-engine.ts` | getTierBeta, getTierFloor, recency, frequency, intrinsic (+5) |

## Entry Points

Start here when exploring this area:

- **`getTierBeta`** (Function) — `src/decay-engine.ts:124`
- **`getTierFloor`** (Function) — `src/decay-engine.ts:135`
- **`recency`** (Function) — `src/decay-engine.ts:152`
- **`frequency`** (Function) — `src/decay-engine.ts:169`
- **`intrinsic`** (Function) — `src/decay-engine.ts:187`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `getTierBeta` | Function | `src/decay-engine.ts` | 124 |
| `getTierFloor` | Function | `src/decay-engine.ts` | 135 |
| `recency` | Function | `src/decay-engine.ts` | 152 |
| `frequency` | Function | `src/decay-engine.ts` | 169 |
| `intrinsic` | Function | `src/decay-engine.ts` | 187 |
| `scoreOne` | Function | `src/decay-engine.ts` | 191 |
| `scores` | Function | `src/decay-engine.ts` | 225 |
| `score` | Method | `src/decay-engine.ts` | 207 |
| `scoreAll` | Method | `src/decay-engine.ts` | 211 |
| `applySearchBoost` | Method | `src/decay-engine.ts` | 215 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `ApplySearchBoost → GetTierBeta` | intra_community | 4 |

## How to Explore

1. `gitnexus_context({name: "getTierBeta"})` — see callers and callees
2. `gitnexus_query({query: "cluster_111"})` — find related execution flows
3. Read key files listed above for implementation details
