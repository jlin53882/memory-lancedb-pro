---
name: worker
description: "Skill for the Worker area of memory-lancedb-pro. 21 symbols across 3 files."
---

# Worker

21 symbols | 3 files | Cohesion: 89%

## When to Use

- Working with code in `examples/`
- Understanding how test work
- Modifying worker-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `examples/new-session-distill/worker/lesson-extract-worker.mjs` | ensureDirs, nowIso, run, safeJsonParse, detectLang (+14) |
| `src/retriever.ts` | test |
| `test/recall-text-cleanup.test.mjs` | extractRenderedMemoryRecallLines |

## Entry Points

Start here when exploring this area:

- **`test`** (Method) — `src/retriever.ts:1667`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test` | Method | `src/retriever.ts` | 1667 |
| `ensureDirs` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 38 |
| `nowIso` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 44 |
| `run` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 48 |
| `safeJsonParse` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 59 |
| `detectLang` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 76 |
| `buildChunksFromJsonl` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 119 |
| `buildMapPrompt` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 151 |
| `geminiGenerateJson` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 157 |
| `coerceLessons` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 185 |
| `importToLanceDb` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 239 |
| `notifyTelegram` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 256 |
| `processTaskFile` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 261 |
| `drainInboxOnce` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 374 |
| `main` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 382 |
| `watcher` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 387 |
| `extractRenderedMemoryRecallLines` | Function | `test/recall-text-cleanup.test.mjs` | 318 |
| `normalizeText` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 67 |
| `scoreLesson` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 198 |
| `reduceLessons` | Function | `examples/new-session-distill/worker/lesson-extract-worker.mjs` | 212 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `ProcessTaskFile → DetectLang` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_62 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test"})` — see callers and callees
2. `gitnexus_query({query: "worker"})` — find related execution flows
3. Read key files listed above for implementation details
