## PR Update

This PR was split from [#367](https://github.com/CortexReach/memory-lancedb-pro/pull/367) — `import-markdown` CLI is now standalone.

### What this PR does

Adds `memory-pro import-markdown` command to migrate existing Markdown memories (`MEMORY.md`, `memory/YYYY-MM-DD.md`) into the plugin LanceDB store for semantic recall.

### Review checklist

The following items were flagged during the original PR #367 review and should be verified here:

- [ ] **File path resolution** — does the command correctly resolve `MEMORY.md` and `memory/YYYY-MM-DD.md` paths across different workspace layouts?
- [ ] **Error handling** — graceful handling when files are missing, permissions denied, or content is malformed
- [ ] **Duplicate detection** — if a memory already exists in LanceDB, is it skipped or overwritten?
- [ ] **Scope handling** — imported memories should have appropriate scope assignment
- [ ] **Batch processing** — large imports (many daily notes) should process without OOM
- [ ] **Progress/logging** — user-visible progress for long imports
- [ ] **Dry-run mode** — is there a `--dry-run` flag to preview what would be imported?
- [ ] **Test coverage** — are there tests for the import logic?

### Related

- [#344](https://github.com/CortexReach/memory-lancedb-pro/issues/344) — original dual-memory confusion issue
- [#367](https://github.com/CortexReach/memory-lancedb-pro/pull/367) — documentation + startup warning (merged separately)
