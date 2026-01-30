---
template: observations
work_id: WORK-038
captured_session: '264'
generated: '2026-01-30'
last_updated: '2026-01-30T20:25:58'
---
# Observations: WORK-038

## What surprised you?

**The critique agent value was higher than expected.** Initially I thought a 1-line bug fix wouldn't need critique, but the agent surfaced 6 assumptions. Two of them (A1, A2) directly improved the migration SQL:

- **A1**: Not all concepts with LENGTH=100 are truncated. Some may legitimately be 100 chars. The SUBSTR match filter (`content = SUBSTR(source_adr, 1, 100)`) prevented corrupting legitimate data.

- **A2**: The `source_adr` column has different semantics for Decision-type concepts (holds ADR paths, not content). Excluding `type NOT IN ('Decision')` prevented overwriting path references.

**Original estimate was 1,298 concepts. Actual recovery was 614.** The refined SQL filtered out 684 false positives that would have been silently corrupted by the naive migration.

## What's missing?

**No write-capable migration path through governance.** The PreToolUse hook blocks all SQL. The schema-verifier subagent is read-only by design. For data migrations, I had to create a standalone script (`scripts/migrations/work_038_fix_truncation.py`) that the operator runs manually.

**Consider:** A migration subagent with write capability but requiring explicit operator approval for each UPDATE statement? Or a governed migration pattern in justfile?

## What should we remember?

**Pattern: Critique before migration, not just before implementation.**

For any data migration:
1. Define the WHERE clause
2. Run critique agent to surface assumptions about data
3. Refine WHERE clause with safeguards (SUBSTR match, type exclusions)
4. Create backup BEFORE migration
5. Run count query to set expectations
6. Execute migration
7. Verify with post-count

**The `[:100]` slice was defensive coding gone wrong.** Someone added it to create a "name" from content, not realizing the database.py mapped `name` -> `content` column. Variable naming matters - calling it `name` when it's actually the full content led to confusion.

## What drift did you notice?

**The deprecated `memory_store` MCP tool still has the same bug at mcp_server.py:174.** It uses `content[:100]` for the name parameter. However, since it's deprecated (notice on line 184) and `ingester_ingest` is the recommended path, I did not fix it. The deprecation should be tracked to eventual removal.
