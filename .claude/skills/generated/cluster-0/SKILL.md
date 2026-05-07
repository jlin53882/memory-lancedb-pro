---
name: cluster-0
description: "Skill for the Cluster_0 area of memory-lancedb-pro. 12 symbols across 2 files."
---

# Cluster_0

12 symbols | 2 files | Cohesion: 73%

## When to Use

- Working with code in `src/`
- Understanding how parsePluginConfig, NoisePrototypeBank work
- Modifying cluster_0-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `index.ts` | isCliMode, getDefaultDbPath, resolveEnvVars, resolveFirstApiKey, resolveOptionalPathWithEnv (+6) |
| `src/noise-prototypes.ts` | NoisePrototypeBank |

## Entry Points

Start here when exploring this area:

- **`parsePluginConfig`** (Function) — `index.ts:4019`
- **`NoisePrototypeBank`** (Class) — `src/noise-prototypes.ts:48`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `NoisePrototypeBank` | Class | `src/noise-prototypes.ts` | 48 |
| `parsePluginConfig` | Function | `index.ts` | 4019 |
| `isCliMode` | Function | `index.ts` | 19 |
| `getDefaultDbPath` | Function | `index.ts` | 263 |
| `resolveEnvVars` | Function | `index.ts` | 283 |
| `resolveFirstApiKey` | Function | `index.ts` | 293 |
| `resolveOptionalPathWithEnv` | Function | `index.ts` | 301 |
| `parsePositiveInt` | Function | `index.ts` | 310 |
| `resolveLlmTimeoutMs` | Function | `index.ts` | 329 |
| `asNonEmptyString` | Function | `index.ts` | 757 |
| `createAdmissionRejectionAuditWriter` | Function | `index.ts` | 1624 |
| `_initPluginState` | Function | `index.ts` | 1745 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Register → BuildPayload` | cross_community | 7 |
| `Register → ValidateEmbedding` | cross_community | 7 |
| `Register → WithTimeout` | cross_community | 6 |
| `RunMultiRoundScenario → DebugLog` | cross_community | 6 |
| `RunMultiRoundScenario → Cosine` | cross_community | 6 |
| `RunMultiRoundScenario → ResolveEnvVars` | cross_community | 6 |
| `RunMultiRoundScenario → ClampInt` | cross_community | 6 |
| `RunMultiRoundScenario → AsNonEmptyString` | cross_community | 6 |
| `RunUserMdExclusiveProfileScenario → DebugLog` | cross_community | 6 |
| `RunUserMdExclusiveProfileScenario → Cosine` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Test | 3 calls |
| Cluster_87 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "parsePluginConfig"})` — see callers and callees
2. `gitnexus_query({query: "cluster_0"})` — find related execution flows
3. Read key files listed above for implementation details
