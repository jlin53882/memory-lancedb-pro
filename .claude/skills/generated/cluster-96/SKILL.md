---
name: cluster-96
description: "Skill for the Cluster_96 area of memory-lancedb-pro. 17 symbols across 1 files."
---

# Cluster_96

17 symbols | 1 files | Cohesion: 81%

## When to Use

- Working with code in `src/`
- Understanding how listOAuthProviders, normalizeOAuthProviderId, getOAuthProvider work
- Modifying cluster_96-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/llm-oauth.ts` | createPkceChallenge, listOAuthProviders, normalizeOAuthProviderId, getOAuthProvider, getOAuthProviderLabel (+12) |

## Entry Points

Start here when exploring this area:

- **`listOAuthProviders`** (Function) — `src/llm-oauth.ts:110`
- **`normalizeOAuthProviderId`** (Function) — `src/llm-oauth.ts:118`
- **`getOAuthProvider`** (Function) — `src/llm-oauth.ts:127`
- **`getOAuthProviderLabel`** (Function) — `src/llm-oauth.ts:131`
- **`getDefaultOauthModelForProvider`** (Function) — `src/llm-oauth.ts:135`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `listOAuthProviders` | Function | `src/llm-oauth.ts` | 110 |
| `normalizeOAuthProviderId` | Function | `src/llm-oauth.ts` | 118 |
| `getOAuthProvider` | Function | `src/llm-oauth.ts` | 127 |
| `getOAuthProviderLabel` | Function | `src/llm-oauth.ts` | 131 |
| `getDefaultOauthModelForProvider` | Function | `src/llm-oauth.ts` | 135 |
| `isOauthModelSupported` | Function | `src/llm-oauth.ts` | 139 |
| `resolveOAuthCallbackListenHost` | Function | `src/llm-oauth.ts` | 549 |
| `normalizeOauthModel` | Function | `src/llm-oauth.ts` | 582 |
| `buildOauthEndpoint` | Function | `src/llm-oauth.ts` | 600 |
| `createPkceChallenge` | Function | `src/llm-oauth.ts` | 106 |
| `resolveOauthClientId` | Function | `src/llm-oauth.ts` | 154 |
| `resolveOauthAuthorizeUrl` | Function | `src/llm-oauth.ts` | 158 |
| `resolveOauthTokenUrl` | Function | `src/llm-oauth.ts` | 162 |
| `resolveOauthRedirectUri` | Function | `src/llm-oauth.ts` | 166 |
| `buildAuthorizationUrl` | Function | `src/llm-oauth.ts` | 170 |
| `exchangeAuthorizationCode` | Function | `src/llm-oauth.ts` | 406 |
| `waitForAuthorizationCode` | Function | `src/llm-oauth.ts` | 485 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `PerformOAuthLogin → ListOAuthProviders` | cross_community | 6 |
| `LoadOAuthSession → ListOAuthProviders` | cross_community | 6 |
| `RefreshOAuthSession → ListOAuthProviders` | cross_community | 5 |
| `ExchangeAuthorizationCode → ListOAuthProviders` | intra_community | 5 |
| `BuildOauthEndpoint → ListOAuthProviders` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_94 | 2 calls |

## How to Explore

1. `gitnexus_context({name: "listOAuthProviders"})` — see callers and callees
2. `gitnexus_query({query: "cluster_96"})` — find related execution flows
3. Read key files listed above for implementation details
