## Conflict Analysis

This PR has a base that's 7 commits behind `master`. During that gap, the `index.ts` auto-recall block was heavily refactored:

- `recallMode` ("full"/"summary"/"adaptive") was added
- `autoRecallExcludeAgents` exclusion logic was added
- The entire `before_prompt_build` hook structure changed significantly

The `MAX_RECALL_QUERY_LENGTH` truncation logic in this PR targets the old architecture. After a rebase onto current master, it would need to be re-applied at the correct location in the new structure.

**Proposed fix approach:**

1. Rebase this PR onto current `master` (`7fe2ae0`)
2. Re-apply the truncation logic in the new `before_prompt_build` hook — likely after `accessibleScopes` is set and before `retrieveWithRetry` is called
3. Add `autoRecallMaxQueryLength` to `PluginConfig` interface and `parsePluginConfig` (similar to how `autoRecallMaxChars` is handled)
4. Add `autoRecallMaxQueryLength` to `openclaw.plugin.json` schema

This would be a straightforward rebase + re-apply.

@xiaoyuervae would you like help with the rebase? I can handle it on this PR if you'd like.
