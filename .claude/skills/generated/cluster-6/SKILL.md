---
name: cluster-6
description: "Skill for the Cluster_6 area of memory-lancedb-pro. 15 symbols across 1 files."
---

# Cluster_6

15 symbols | 1 files | Cohesion: 83%

## When to Use

- Understanding how readSessionConversationWithResetFallback work
- Modifying cluster_6-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `index.ts` | isAgentDeclaredInConfig, readSessionConversationForReflection, readSessionConversationWithResetFallback, ensureDailyLogFile, sortFileNamesByMtimeDesc (+10) |

## Entry Points

Start here when exploring this area:

- **`readSessionConversationWithResetFallback`** (Function) — `index.ts:984`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `readSessionConversationWithResetFallback` | Function | `index.ts` | 984 |
| `isAgentDeclaredInConfig` | Function | `index.ts` | 728 |
| `readSessionConversationForReflection` | Function | `index.ts` | 963 |
| `ensureDailyLogFile` | Function | `index.ts` | 1007 |
| `sortFileNamesByMtimeDesc` | Function | `index.ts` | 1458 |
| `sanitizeFileToken` | Function | `index.ts` | 1476 |
| `findPreviousSessionFile` | Function | `index.ts` | 1486 |
| `_dedupHookEvent` | Function | `index.ts` | 1698 |
| `appendSelfImprovementNote` | Function | `index.ts` | 3152 |
| `resolveReflectionRunAgentId` | Function | `index.ts` | 3246 |
| `getGlobalReflectionLock` | Function | `index.ts` | 3392 |
| `getSerialGuardMap` | Function | `index.ts` | 3401 |
| `runMemoryReflection` | Function | `index.ts` | 3408 |
| `embedPassage` | Function | `index.ts` | 3698 |
| `vectorSearch` | Function | `index.ts` | 3699 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `RunMemoryReflection → PruneOldestByUpdatedAt` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 3 calls |
| Cluster_7 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "readSessionConversationWithResetFallback"})` — see callers and callees
2. `gitnexus_query({query: "cluster_6"})` — find related execution flows
3. Read key files listed above for implementation details
