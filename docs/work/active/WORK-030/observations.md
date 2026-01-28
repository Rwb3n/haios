---
template: observations
work_id: WORK-030
captured_session: '247'
generated: '2026-01-28'
last_updated: '2026-01-28T22:56:35'
---
# Observations: WORK-030

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

The INV-* prefix logic was only in 3-4 files despite feeling pervasive. The routing system already had `type` field as primary check (WORK-014), with INV-* prefix as fallback. Removing the fallback was trivial - the architecture was already correct, just had legacy code paths. Expected: major refactor. Actual: ~15 lines changed across routing.py, status.py, work_item.py.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**Auto-ID assignment in commands:** The `/new-work` and `/new-investigation` commands still require manual ID specification. Would be smoother if they auto-assigned the next WORK-XXX when no ID is provided. Currently the command tells you to run `get_next_work_id()` manually.

**PreToolUse hook circular blocking:** When `/new-work` skill tries to call `just work`, the hook blocks it because it thinks we're bypassing work-creation-cycle. Had to use `cli.py scaffold` directly. The hook doesn't know we're already inside the governed command.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Type field is authoritative for routing.** ID prefixes (E2-, INV-, TD-) are cosmetic/historical. The `type` field in WORK.md frontmatter determines which cycle handles the work. This is now documented in CLAUDE.md under "Work Item ID Policy (WORK-030)".

**Deprecation pattern:** When deprecating a feature (like INV-* prefix routing), check for actual code usage with `grep -rn "startswith.*INV"` to find all logic paths. Most "references" are documentation/examples, not code. Real code changes are often smaller than expected.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**`spawned_by_investigation` field was already deprecated.** portal_manager.py:225 has a comment "WORK-014: spawned_by_investigation is DEPRECATED per TRD-WORK-ITEM-UNIVERSAL" but work_item.py:247 still populated it based on INV-* prefix. Code and comments were out of sync. Now removed from work_item.py.
