---
name: cluster-89
description: "Skill for the Cluster_89 area of memory-lancedb-pro. 9 symbols across 1 files."
---

# Cluster_89

9 symbols | 1 files | Cohesion: 87%

## When to Use

- Working with code in `src/`
- Understanding how migrateFromLegacy, checkForLegacyData, migrate work
- Modifying cluster_89-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/migrate.ts` | normalizeLegacyVector, getDefaultLegacyPaths, migrate, findSourceDatabase, loadLegacyData (+4) |

## Entry Points

Start here when exploring this area:

- **`migrateFromLegacy`** (Function) — `src/migrate.ts:325`
- **`checkForLegacyData`** (Function) — `src/migrate.ts:333`
- **`migrate`** (Method) — `src/migrate.ts:76`
- **`findSourceDatabase`** (Method) — `src/migrate.ts:130`
- **`loadLegacyData`** (Method) — `src/migrate.ts:157`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `migrateFromLegacy` | Function | `src/migrate.ts` | 325 |
| `checkForLegacyData` | Function | `src/migrate.ts` | 333 |
| `migrate` | Method | `src/migrate.ts` | 76 |
| `findSourceDatabase` | Method | `src/migrate.ts` | 130 |
| `loadLegacyData` | Method | `src/migrate.ts` | 157 |
| `checkMigrationNeeded` | Method | `src/migrate.ts` | 242 |
| `verifyMigration` | Method | `src/migrate.ts` | 274 |
| `normalizeLegacyVector` | Function | `src/migrate.ts` | 40 |
| `getDefaultLegacyPaths` | Function | `src/migrate.ts` | 60 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `MigrateFromLegacy → LoadLanceDB` | cross_community | 8 |
| `VerifyMigration → LoadLockfile` | cross_community | 7 |
| `Migrate → IsExplicitDenyAllScopeFilter` | cross_community | 7 |
| `VerifyMigration → LoadLanceDB` | cross_community | 6 |
| `VerifyMigration → IsExplicitDenyAllScopeFilter` | cross_community | 6 |
| `MigrateFromLegacy → LoadLockfile` | cross_community | 6 |
| `MigrateFromLegacy → EscapeSqlLiteral` | cross_community | 5 |
| `MigrateFromLegacy → IsExplicitDenyAllScopeFilter` | cross_community | 5 |
| `MigrateFromLegacy → ClampInt` | cross_community | 5 |
| `MigrateFromLegacy → GetDefaultLegacyPaths` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 2 calls |
| Cluster_22 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "migrateFromLegacy"})` — see callers and callees
2. `gitnexus_query({query: "cluster_89"})` — find related execution flows
3. Read key files listed above for implementation details
