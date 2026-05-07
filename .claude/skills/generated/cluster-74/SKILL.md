---
name: cluster-74
description: "Skill for the Cluster_74 area of memory-lancedb-pro. 9 symbols across 1 files."
---

# Cluster_74

9 symbols | 1 files | Cohesion: 91%

## When to Use

- Working with code in `src/`
- Understanding how extractSectionMarkdown, parseSectionBullets, isPlaceholderReflectionSliceLine work
- Modifying cluster_74-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/reflection-slices.ts` | extractSectionMarkdown, parseSectionBullets, isPlaceholderReflectionSliceLine, normalizeReflectionSliceLine, sanitizeReflectionSliceLines (+4) |

## Entry Points

Start here when exploring this area:

- **`extractSectionMarkdown`** (Function) — `src/reflection-slices.ts:36`
- **`parseSectionBullets`** (Function) — `src/reflection-slices.ts:55`
- **`isPlaceholderReflectionSliceLine`** (Function) — `src/reflection-slices.ts:68`
- **`normalizeReflectionSliceLine`** (Function) — `src/reflection-slices.ts:79`
- **`sanitizeReflectionSliceLines`** (Function) — `src/reflection-slices.ts:86`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `extractSectionMarkdown` | Function | `src/reflection-slices.ts` | 36 |
| `parseSectionBullets` | Function | `src/reflection-slices.ts` | 55 |
| `isPlaceholderReflectionSliceLine` | Function | `src/reflection-slices.ts` | 68 |
| `normalizeReflectionSliceLine` | Function | `src/reflection-slices.ts` | 79 |
| `sanitizeReflectionSliceLines` | Function | `src/reflection-slices.ts` | 86 |
| `isUnsafeInjectableReflectionLine` | Function | `src/reflection-slices.ts` | 99 |
| `sanitizeInjectableReflectionLines` | Function | `src/reflection-slices.ts` | 107 |
| `extractReflectionLessons` | Function | `src/reflection-slices.ts` | 127 |
| `extractReflectionLearningGovernanceCandidates` | Function | `src/reflection-slices.ts` | 131 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `ExtractReflectionSliceItems → ExtractSectionMarkdown` | cross_community | 5 |
| `ExtractInjectableReflectionSliceItems → ExtractSectionMarkdown` | cross_community | 5 |
| `SanitizeInjectableReflectionLines → IsPlaceholderReflectionSliceLine` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "extractSectionMarkdown"})` — see callers and callees
2. `gitnexus_query({query: "cluster_74"})` — find related execution flows
3. Read key files listed above for implementation details
