## Relationship with PR #365

This PR (#307) adds `autoRecallExcludeAgents` — the same feature also present in [PR #365](https://github.com/CortexReach/memory-lancedb-pro/pull/365).

What #365 covers vs #307:

| Feature | PR #307 | PR #365 |
|---------|---------|---------|
| `autoRecallExcludeAgents` | ✅ | ✅ |
| `recallMode` | ❌ | ✅ |
| Idempotent guard (`_initialized`) | ❌ | ✅ |
| Governance detail logging | ❌ | ✅ |
| `openclaw.plugin.json` schema | ❌ | ✅ |
| E2E tests | ❌ | ✅ |

**Recommendation:** #365 is a superset of #307. Please close this PR in favor of #365.
