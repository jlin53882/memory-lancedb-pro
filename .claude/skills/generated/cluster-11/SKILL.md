---
name: cluster-11
description: "Skill for the Cluster_11 area of memory-lancedb-pro. 19 symbols across 1 files."
---

# Cluster_11

19 symbols | 1 files | Cohesion: 81%

## When to Use

- Understanding how runImportMarkdown, scanAgentMd, registerMemoryCLI work
- Modifying cluster_11-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `cli.ts` | getPluginVersion, clampInt, resolveOpenClawConfigPath, resolveOpenClawHome, resolveDefaultOauthPath (+14) |

## Entry Points

Start here when exploring this area:

- **`runImportMarkdown`** (Function) — `cli.ts:489`
- **`scanAgentMd`** (Function) — `cli.ts:581`
- **`registerMemoryCLI`** (Function) — `cli.ts:745`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `runImportMarkdown` | Function | `cli.ts` | 489 |
| `scanAgentMd` | Function | `cli.ts` | 581 |
| `registerMemoryCLI` | Function | `cli.ts` | 745 |
| `getPluginVersion` | Function | `cli.ts` | 59 |
| `clampInt` | Function | `cli.ts` | 69 |
| `resolveOpenClawConfigPath` | Function | `cli.ts` | 74 |
| `resolveOpenClawHome` | Function | `cli.ts` | 88 |
| `resolveDefaultOauthPath` | Function | `cli.ts` | 94 |
| `resolveLoginOauthPath` | Function | `cli.ts` | 98 |
| `resolveConfiguredOauthPath` | Function | `cli.ts` | 104 |
| `hasRestorableApiKeyLlmConfig` | Function | `cli.ts` | 176 |
| `pickOauthModel` | Function | `cli.ts` | 358 |
| `loadOpenClawConfig` | Function | `cli.ts` | 379 |
| `ensurePluginConfigRoot` | Function | `cli.ts` | 388 |
| `saveOpenClawConfig` | Function | `cli.ts` | 398 |
| `formatMemory` | Function | `cli.ts` | 403 |
| `formatJson` | Function | `cli.ts` | 412 |
| `formatRetrievalDiagnosticsLines` | Function | `cli.ts` | 416 |
| `buildSearchErrorPayload` | Function | `cli.ts` | 466 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `RunCliSmoke → Render` | cross_community | 6 |
| `RunCliSmoke → PickOauthProvider` | cross_community | 5 |
| `RunCliSmoke → ResolveOpenClawHome` | cross_community | 5 |
| `RunCliSmoke → GetPluginVersion` | cross_community | 4 |
| `RunCliSmoke → PickOauthModel` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_12 | 4 calls |
| Cluster_13 | 3 calls |
| Cluster_14 | 1 calls |
| Cluster_15 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "runImportMarkdown"})` — see callers and callees
2. `gitnexus_query({query: "cluster_11"})` — find related execution flows
3. Read key files listed above for implementation details
