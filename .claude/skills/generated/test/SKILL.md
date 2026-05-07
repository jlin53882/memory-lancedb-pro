---
name: test
description: "Skill for the Test area of memory-lancedb-pro. 299 symbols across 67 files."
---

# Test

299 symbols | 67 files | Cohesion: 80%

## When to Use

- Working with code in `test/`
- Understanding how classifyTemporal, inferExpiry, deriveFactKey work
- Modifying test-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `index.ts` | getDefaultWorkspaceDir, getDefaultMdMirrorDir, resolveWorkspaceDirFromContext, clampInt, resolveHookAgentId (+27) |
| `src/store.ts` | MemoryStore, store, list, loadLockfile, runWithFileLock (+14) |
| `test/smart-extractor-branches.mjs` | seedPreference, createDeterministicEmbedding, createEmbeddingServer, createMockApi, runAgentEndHook (+12) |
| `test/cjk-recursion-regression.test.mjs` | generateCJKText, createJsonServer, withServer, testSingleChunkFallbackTerminates, testDepthLimitTermination (+7) |
| `src/tools.ts` | stringEnum, registerSelfImprovementLogTool, registerSelfImprovementExtractSkillTool, registerMemoryRecallTool, registerMemoryStoreTool (+7) |
| `src/access-tracker.ts` | AccessTracker, recordAccess, getPendingUpdates, flush, destroy (+6) |
| `test/recall-text-cleanup.test.mjs` | makeResults, makeExpandedResults, makeUserMdExclusiveResults, makeLegacyAddressingResults, makeRecallContext (+5) |
| `test/openclaw-host-functional.mjs` | startMockEmbeddingServer, close, stripPluginLogs, parseJsonOutput, runOpenClaw (+5) |
| `test/memory-reflection-issue680-tdd.test.mjs` | store, bulkStore, makeMockEmbedder, embedPassage, embedPassages (+4) |
| `test/is-latest-auto-supersede.test.mjs` | makeOldEntry, makeApiCapture, getCreator, createTool, makeMockStore (+4) |

## Entry Points

Start here when exploring this area:

- **`classifyTemporal`** (Function) — `src/temporal-classifier.ts:40`
- **`inferExpiry`** (Function) — `src/temporal-classifier.ts:107`
- **`deriveFactKey`** (Function) — `src/smart-metadata.ts:204`
- **`isMemoryActiveAt`** (Function) — `src/smart-metadata.ts:231`
- **`isMemoryExpired`** (Function) — `src/smart-metadata.ts:244`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `MemoryStore` | Class | `src/store.ts` | 202 |
| `Embedder` | Class | `src/embedder.ts` | 455 |
| `AccessTracker` | Class | `src/access-tracker.ts` | 213 |
| `MemoryScopeManager` | Class | `src/scopes.ts` | 126 |
| `MemoryMigrator` | Class | `src/migrate.ts` | 73 |
| `MemoryRetriever` | Class | `src/retriever.ts` | 533 |
| `SmartExtractor` | Class | `src/smart-extractor.ts` | 277 |
| `MemoryUpgrader` | Class | `src/memory-upgrader.ts` | 159 |
| `classifyTemporal` | Function | `src/temporal-classifier.ts` | 40 |
| `inferExpiry` | Function | `src/temporal-classifier.ts` | 107 |
| `deriveFactKey` | Function | `src/smart-metadata.ts` | 204 |
| `isMemoryActiveAt` | Function | `src/smart-metadata.ts` | 231 |
| `isMemoryExpired` | Function | `src/smart-metadata.ts` | 244 |
| `buildSmartMetadata` | Function | `src/smart-metadata.ts` | 338 |
| `appendRelation` | Function | `src/smart-metadata.ts` | 436 |
| `stringifySmartMetadata` | Function | `src/smart-metadata.ts` | 457 |
| `parseSupportInfo` | Function | `src/smart-metadata.ts` | 600 |
| `createLlmClient` | Function | `src/llm-client.ts` | 414 |
| `createEmbedder` | Function | `src/embedder.ts` | 1149 |
| `legacyMemories` | Function | `src/memory-upgrader.ts` | 234 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `UpgradeEntry → LoadLockfile` | cross_community | 8 |
| `RecordAccessAndMaybeTransition → LoadLockfile` | cross_community | 8 |
| `Run → LoadLockfile` | cross_community | 8 |
| `MigrateFromLegacy → LoadLanceDB` | cross_community | 8 |
| `Upgrade → LoadLockfile` | cross_community | 7 |
| `HandleContextualize → LoadLockfile` | cross_community | 7 |
| `HandleSupersede → LoadLockfile` | cross_community | 7 |
| `UpgradeEntry → LoadLanceDB` | cross_community | 7 |
| `UpgradeEntry → IsExplicitDenyAllScopeFilter` | cross_community | 7 |
| `StoreCandidate → LoadLockfile` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_34 | 18 calls |
| Cluster_22 | 10 calls |
| Cluster_21 | 10 calls |
| Cluster_0 | 8 calls |
| Cluster_62 | 4 calls |
| Cluster_30 | 3 calls |
| Cluster_39 | 2 calls |
| Worker | 2 calls |

## How to Explore

1. `gitnexus_context({name: "classifyTemporal"})` — see callers and callees
2. `gitnexus_query({query: "test"})` — find related execution flows
3. Read key files listed above for implementation details
