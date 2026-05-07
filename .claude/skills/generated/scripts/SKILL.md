---
name: scripts
description: "Skill for the Scripts area of memory-lancedb-pro. 35 symbols across 7 files."
---

# Scripts

35 symbols | 7 files | Cohesion: 82%

## When to Use

- Working with code in `scripts/`
- Understanding how run_extract, init_from_now, commit_batch work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/jsonl_distill.py` | _get_allowed_agent_ids, _read_jsonl_lines, _extract_text_blocks, _clean_text, _is_noise (+8) |
| `scripts/verify-ci-test-manifest.mjs` | fail, normalizeArgs, formatCommand, verifyGroups, verifyFilesExist (+3) |
| `scripts/run-ci-tests.mjs` | parseArgs, buildCommand, runEntry, main |
| `scripts/sync-plugin-version.mjs` | parseJsonStringToken, skipWhitespace, replaceTopLevelVersion, syncManifestVersion |
| `scripts/governance-maintenance.mjs` | parseArgs, loadAllEntries, normalizeKey, run |
| `test/embedder-error-hints.test.mjs` | expectReject |
| `scripts/ci-test-manifest.mjs` | getEntriesForGroup |

## Entry Points

Start here when exploring this area:

- **`run_extract`** (Function) — `scripts/jsonl_distill.py:252`
- **`init_from_now`** (Function) — `scripts/jsonl_distill.py:225`
- **`commit_batch`** (Function) — `scripts/jsonl_distill.py:413`
- **`main`** (Function) — `scripts/jsonl_distill.py:447`
- **`getEntriesForGroup`** (Function) — `scripts/ci-test-manifest.mjs:64`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `run_extract` | Function | `scripts/jsonl_distill.py` | 252 |
| `init_from_now` | Function | `scripts/jsonl_distill.py` | 225 |
| `commit_batch` | Function | `scripts/jsonl_distill.py` | 413 |
| `main` | Function | `scripts/jsonl_distill.py` | 447 |
| `getEntriesForGroup` | Function | `scripts/ci-test-manifest.mjs` | 64 |
| `replaceTopLevelVersion` | Function | `scripts/sync-plugin-version.mjs` | 33 |
| `syncManifestVersion` | Function | `scripts/sync-plugin-version.mjs` | 75 |
| `expectReject` | Function | `test/embedder-error-hints.test.mjs` | 91 |
| `fail` | Function | `scripts/verify-ci-test-manifest.mjs` | 65 |
| `normalizeArgs` | Function | `scripts/verify-ci-test-manifest.mjs` | 69 |
| `formatCommand` | Function | `scripts/verify-ci-test-manifest.mjs` | 73 |
| `verifyGroups` | Function | `scripts/verify-ci-test-manifest.mjs` | 77 |
| `verifyFilesExist` | Function | `scripts/verify-ci-test-manifest.mjs` | 85 |
| `verifyExactOnceCoverage` | Function | `scripts/verify-ci-test-manifest.mjs` | 94 |
| `verifyExactBaseline` | Function | `scripts/verify-ci-test-manifest.mjs` | 121 |
| `main` | Function | `scripts/verify-ci-test-manifest.mjs` | 150 |
| `_get_allowed_agent_ids` | Function | `scripts/jsonl_distill.py` | 46 |
| `_read_jsonl_lines` | Function | `scripts/jsonl_distill.py` | 69 |
| `_extract_text_blocks` | Function | `scripts/jsonl_distill.py` | 97 |
| `_clean_text` | Function | `scripts/jsonl_distill.py` | 113 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run → LoadLockfile` | cross_community | 8 |
| `Run → LoadLanceDB` | cross_community | 7 |
| `Run → IsExplicitDenyAllScopeFilter` | cross_community | 7 |
| `Run → EscapeSqlLiteral` | cross_community | 4 |
| `Main → _now_ms` | intra_community | 4 |
| `Main → _get_allowed_agent_ids` | cross_community | 4 |
| `Main → NormalizeArgs` | intra_community | 4 |
| `Run → ReverseMapLegacyCategory` | cross_community | 3 |
| `Run → NormalizeText` | cross_community | 3 |
| `Run → NormalizeTimestamp` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 3 calls |
| Cluster_22 | 2 calls |
| Worker | 1 calls |
| Cluster_34 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "run_extract"})` — see callers and callees
2. `gitnexus_query({query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
