## PR Split Update

This PR has been split into two separate pull requests:

| PR | Title | Contents |
|----|-------|----------|
| **#367 (this PR)** | clarify dual-memory architecture | README + startup warning (docs only) |
| **[#426](https://github.com/CortexReach/memory-lancedb-pro/pull/426)** | feat: add import-markdown CLI command | `import-markdown` CLI command |

### Changes in this update

- **Removed `cli.ts`** — moved to PR #426 as a standalone feature PR
- **Rebased onto latest master** — no longer deletes any existing functionality (`runCompaction`, `normalizeAutoCaptureText`, etc. are all preserved)
- **Only adds:**
  - `README.md`: Dual-Memory Architecture explanation section
  - `index.ts`: startup log warning about the two-layer memory model

### Related PRs

| PR | Status | Description |
|----|--------|-------------|
| [#307](https://github.com/CortexReach/memory-lancedb-pro/pull/307) | Awaiting close | `autoRecallExcludeAgents` — covered by #365 |
| [#356](https://github.com/CortexReach/memory-lancedb-pro/pull/356) | Pending | `rerankTimeoutMs` base commit done; reviewer feedback pending |
| [#365](https://github.com/CortexReach/memory-lancedb-pro/pull/365) | Ready | idempotent guard + governance logging + `autoRecallExcludeAgents` (ported from #307) |
| [#367](https://github.com/CortexReach/memory-lancedb-pro/pull/367) | Ready (this PR) | README + startup warning |
| [#426](https://github.com/CortexReach/memory-lancedb-pro/pull/426) | Ready | `import-markdown` CLI |

@AliceLJY please review #367 when ready — it should be clean to merge now.
