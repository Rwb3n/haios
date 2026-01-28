---
template: observations
work_id: WORK-012
captured_session: '256'
generated: '2026-01-28'
last_updated: '2026-01-28T23:47:42'
---
# Observations: WORK-012

## What surprised you?

The investigation resolved faster than expected. The original problem statement ("agents not available to Task tool") was actually a timing issue, not an architectural gap. All 8 HAIOS agents ARE properly registered and available - the E2-072 observation was from testing in the same session where the agent file was created. Claude Code's session-static registry is expected behavior documented in 4+ memory concepts (72427, 72431, 77181, 80290). The "problem" was already solved by the time this investigation started - we just needed to verify it.

## What's missing?

The `.claude/agents/README.md` doesn't explicitly document the hot-reload limitation. When creating new agents, operators should know to restart the session before testing. This is implicit knowledge that should be explicit. However, this is minor - the memory system already captures this pattern across multiple concepts.

## What should we remember?

**Pattern: Session-static registries in Claude Code.** The Task tool's subagent_type registry, like agent discovery, happens at session startup. Changes to `.claude/agents/*.md` files (new files, name changes) require session restart. However, changes to agent prompt content (the markdown body) apply immediately since the file is re-read on each invocation.

**Pattern: Memory-first investigation.** Querying memory BEFORE deep exploration saved significant time. The answer was already documented across 4 concepts from prior sessions. This validates the investigation-cycle's HYPOTHESIZE phase requirement to query memory first.

## What drift did you notice?

**Queue filter drift:** The `get_queue()` function filters by `status` field, but work items use `current_node` to track lifecycle. E2-293 and E2-294 had `current_node=complete` but `status=active`, causing them to appear in the queue as actionable. Fixed during this session by updating status to match node. This suggests the WorkEngine should either filter by `current_node` instead of `status`, OR ensure `status` is updated when `current_node` changes to `complete`. Related: close-work-cycle should update both fields.
