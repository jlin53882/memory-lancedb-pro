---
name: cluster-20
description: "Skill for the Cluster_20 area of memory-lancedb-pro. 13 symbols across 1 files."
---

# Cluster_20

13 symbols | 1 files | Cohesion: 94%

## When to Use

- Working with code in `src/`
- Understanding how lines, execute work
- Modifying cluster_20-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/tools.ts` | clampInt, clamp01, normalizeInlineText, truncateText, deriveManualMemoryLayer (+8) |

## Entry Points

Start here when exploring this area:

- **`lines`** (Function) — `src/tools.ts:2191`
- **`execute`** (Method) — `src/tools.ts:273`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `lines` | Function | `src/tools.ts` | 2191 |
| `execute` | Method | `src/tools.ts` | 273 |
| `clampInt` | Function | `src/tools.ts` | 79 |
| `clamp01` | Function | `src/tools.ts` | 84 |
| `normalizeInlineText` | Function | `src/tools.ts` | 89 |
| `truncateText` | Function | `src/tools.ts` | 93 |
| `deriveManualMemoryLayer` | Function | `src/tools.ts` | 99 |
| `sanitizeMemoryForSerialization` | Function | `src/tools.ts` | 106 |
| `sleep` | Function | `src/tools.ts` | 165 |
| `retrieveWithRetry` | Function | `src/tools.ts` | 169 |
| `resolveMemoryId` | Function | `src/tools.ts` | 192 |
| `resolveWorkspaceDir` | Function | `src/tools.ts` | 246 |
| `escapeRegExp` | Function | `src/tools.ts` | 254 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Execute → EndStage` | cross_community | 6 |
| `Execute → ApplyRecencyBoost` | cross_community | 5 |
| `Execute → ApplyImportanceWeight` | cross_community | 5 |
| `Execute → BuildBM25Query` | cross_community | 5 |
| `Execute → ExtractTagTokens` | cross_community | 4 |
| `Execute → Sleep` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_62 | 2 calls |
| Cluster_21 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "lines"})` — see callers and callees
2. `gitnexus_query({query: "cluster_20"})` — find related execution flows
3. Read key files listed above for implementation details
