---
name: cluster-22
description: "Skill for the Cluster_22 area of memory-lancedb-pro. 20 symbols across 6 files."
---

# Cluster_22

20 symbols | 6 files | Cohesion: 63%

## When to Use

- Working with code in `src/`
- Understanding how evaluate, getById, lexicalFallbackSearch work
- Modifying cluster_22-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/store.ts` | escapeSqlLiteral, normalizeSearchText, isExplicitDenyAllScopeFilter, scoreLexicalHit, getById (+4) |
| `src/smart-extractor.ts` | handleSupersede, handleSupport, handleContextualize, handleContradict, mapToStoreCategory (+2) |
| `src/tier-manager.ts` | evaluate |
| `src/retriever.ts` | recordAccessAndMaybeTransition |
| `src/decay-engine.ts` | score |
| `src/access-tracker.ts` | doFlush |

## Entry Points

Start here when exploring this area:

- **`evaluate`** (Method) — `src/tier-manager.ts:67`
- **`getById`** (Method) — `src/store.ts:576`
- **`lexicalFallbackSearch`** (Method) — `src/store.ts:759`
- **`stats`** (Method) — `src/store.ts:945`
- **`update`** (Method) — `src/store.ts:989`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `evaluate` | Method | `src/tier-manager.ts` | 67 |
| `getById` | Method | `src/store.ts` | 576 |
| `lexicalFallbackSearch` | Method | `src/store.ts` | 759 |
| `stats` | Method | `src/store.ts` | 945 |
| `update` | Method | `src/store.ts` | 989 |
| `patchMetadata` | Method | `src/store.ts` | 1140 |
| `handleSupersede` | Method | `src/smart-extractor.ts` | 1155 |
| `handleSupport` | Method | `src/smart-extractor.ts` | 1246 |
| `handleContextualize` | Method | `src/smart-extractor.ts` | 1277 |
| `handleContradict` | Method | `src/smart-extractor.ts` | 1332 |
| `mapToStoreCategory` | Method | `src/smart-extractor.ts` | 1474 |
| `getDefaultImportance` | Method | `src/smart-extractor.ts` | 1498 |
| `withAdmissionAudit` | Method | `src/smart-extractor.ts` | 1524 |
| `recordAccessAndMaybeTransition` | Method | `src/retriever.ts` | 1548 |
| `score` | Method | `src/decay-engine.ts` | 86 |
| `doFlush` | Method | `src/access-tracker.ts` | 320 |
| `escapeSqlLiteral` | Function | `src/store.ts` | 99 |
| `normalizeSearchText` | Function | `src/store.ts` | 103 |
| `isExplicitDenyAllScopeFilter` | Function | `src/store.ts` | 107 |
| `scoreLexicalHit` | Function | `src/store.ts` | 111 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `UpgradeEntry → LoadLockfile` | cross_community | 8 |
| `RecordAccessAndMaybeTransition → LoadLockfile` | cross_community | 8 |
| `HandleContextualize → LoadLockfile` | cross_community | 7 |
| `HandleSupersede → LoadLockfile` | cross_community | 7 |
| `UpgradeEntry → LoadLanceDB` | cross_community | 7 |
| `UpgradeEntry → IsExplicitDenyAllScopeFilter` | cross_community | 7 |
| `RecordAccessAndMaybeTransition → LoadLanceDB` | cross_community | 7 |
| `RecordAccessAndMaybeTransition → IsExplicitDenyAllScopeFilter` | cross_community | 7 |
| `VerifyMigration → LoadLockfile` | cross_community | 7 |
| `Run → IsExplicitDenyAllScopeFilter` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 9 calls |
| Cluster_39 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "evaluate"})` — see callers and callees
2. `gitnexus_query({query: "cluster_22"})` — find related execution flows
3. Read key files listed above for implementation details
