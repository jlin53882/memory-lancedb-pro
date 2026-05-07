---
name: cluster-99
description: "Skill for the Cluster_99 area of memory-lancedb-pro. 9 symbols across 1 files."
---

# Cluster_99

9 symbols | 1 files | Cohesion: 100%

## When to Use

- Working with code in `src/`
- Understanding how extractJsonFromResponse, previewText, nextNonWhitespaceChar work
- Modifying cluster_99-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/llm-client.ts` | extractJsonFromResponse, previewText, nextNonWhitespaceChar, repairCommonJson, looksLikeSseResponse (+4) |

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `extractJsonFromResponse` | Function | `src/llm-client.ts` | 40 |
| `previewText` | Function | `src/llm-client.ts` | 66 |
| `nextNonWhitespaceChar` | Function | `src/llm-client.ts` | 72 |
| `repairCommonJson` | Function | `src/llm-client.ts` | 86 |
| `looksLikeSseResponse` | Function | `src/llm-client.ts` | 160 |
| `createTimeoutSignal` | Function | `src/llm-client.ts` | 165 |
| `dispose` | Function | `src/llm-client.ts` | 172 |
| `getSession` | Function | `src/llm-client.ts` | 271 |
| `completeJson` | Method | `src/llm-client.ts` | 189 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `CompleteJson → NextNonWhitespaceChar` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "extractJsonFromResponse"})` — see callers and callees
2. `gitnexus_query({query: "cluster_99"})` — find related execution flows
3. Read key files listed above for implementation details
