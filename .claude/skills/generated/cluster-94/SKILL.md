---
name: cluster-94
description: "Skill for the Cluster_94 area of memory-lancedb-pro. 11 symbols across 1 files."
---

# Cluster_94

11 symbols | 1 files | Cohesion: 81%

## When to Use

- Working with code in `src/`
- Understanding how loadOAuthSession, refreshOAuthSession work
- Modifying cluster_94-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/llm-oauth.ts` | parseNumericTimestamp, decodeJwtPayload, getJwtExpiry, getJwtAccountId, pickString (+6) |

## Entry Points

Start here when exploring this area:

- **`loadOAuthSession`** (Function) — `src/llm-oauth.ts:301`
- **`refreshOAuthSession`** (Function) — `src/llm-oauth.ts:349`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `loadOAuthSession` | Function | `src/llm-oauth.ts` | 301 |
| `refreshOAuthSession` | Function | `src/llm-oauth.ts` | 349 |
| `parseNumericTimestamp` | Function | `src/llm-oauth.ts` | 77 |
| `decodeJwtPayload` | Function | `src/llm-oauth.ts` | 206 |
| `getJwtExpiry` | Function | `src/llm-oauth.ts` | 216 |
| `getJwtAccountId` | Function | `src/llm-oauth.ts` | 221 |
| `pickString` | Function | `src/llm-oauth.ts` | 231 |
| `pickTimestamp` | Function | `src/llm-oauth.ts` | 241 |
| `extractSessionFromObject` | Function | `src/llm-oauth.ts` | 249 |
| `createTimeoutSignal` | Function | `src/llm-oauth.ts` | 338 |
| `dispose` | Function | `src/llm-oauth.ts` | 345 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `LoadOAuthSession → ListOAuthProviders` | cross_community | 6 |
| `RefreshOAuthSession → ListOAuthProviders` | cross_community | 5 |
| `LoadOAuthSession → ParseNumericTimestamp` | intra_community | 4 |
| `LoadOAuthSession → DecodeJwtPayload` | intra_community | 4 |
| `RefreshOAuthSession → DecodeJwtPayload` | intra_community | 3 |
| `RefreshOAuthSession → ParseNumericTimestamp` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_96 | 4 calls |

## How to Explore

1. `gitnexus_context({name: "loadOAuthSession"})` — see callers and callees
2. `gitnexus_query({query: "cluster_94"})` — find related execution flows
3. Read key files listed above for implementation details
