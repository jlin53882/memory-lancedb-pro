---
name: cluster-118
description: "Skill for the Cluster_118 area of memory-lancedb-pro. 10 symbols across 1 files."
---

# Cluster_118

10 symbols | 1 files | Cohesion: 100%

## When to Use

- Working with code in `src/`
- Understanding how readAdmissionRejectionAudits, normalizeReasonKey, extractAdmissionReasonLabel work
- Modifying cluster_118-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/admission-stats.ts` | readAdmissionRejectionAudits, normalizeReasonKey, extractAdmissionReasonLabel, summarizeAdmissionRejections, getAdmissionAuditDecision (+5) |

## Entry Points

Start here when exploring this area:

- **`readAdmissionRejectionAudits`** (Function) — `src/admission-stats.ts:73`
- **`normalizeReasonKey`** (Function) — `src/admission-stats.ts:98`
- **`extractAdmissionReasonLabel`** (Function) — `src/admission-stats.ts:106`
- **`summarizeAdmissionRejections`** (Function) — `src/admission-stats.ts:114`
- **`getAdmissionAuditDecision`** (Function) — `src/admission-stats.ts:150`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `readAdmissionRejectionAudits` | Function | `src/admission-stats.ts` | 73 |
| `normalizeReasonKey` | Function | `src/admission-stats.ts` | 98 |
| `extractAdmissionReasonLabel` | Function | `src/admission-stats.ts` | 106 |
| `summarizeAdmissionRejections` | Function | `src/admission-stats.ts` | 114 |
| `getAdmissionAuditDecision` | Function | `src/admission-stats.ts` | 150 |
| `getAdmittedDecisionTimestamp` | Function | `src/admission-stats.ts` | 163 |
| `getObservedAdmissionCategory` | Function | `src/admission-stats.ts` | 184 |
| `buildAdmissionCategoryBreakdown` | Function | `src/admission-stats.ts` | 190 |
| `buildAdmissionWindowSummary` | Function | `src/admission-stats.ts` | 234 |
| `buildAdmissionStats` | Function | `src/admission-stats.ts` | 262 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `BuildAdmissionStats → ExtractAdmissionReasonLabel` | intra_community | 3 |
| `BuildAdmissionStats → NormalizeReasonKey` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "readAdmissionRejectionAudits"})` — see callers and callees
2. `gitnexus_query({query: "cluster_118"})` — find related execution flows
3. Read key files listed above for implementation details
