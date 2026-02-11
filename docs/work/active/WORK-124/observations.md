---
template: observations
work_id: 'WORK-124'
captured_session: '346'
generated: '2026-02-11'
last_updated: '2026-02-11T21:25:15'
---
# Observations: WORK-124

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

The recipes worked on first try with no issues. The dual `sys.path.insert` pattern (modules/ for WorkEngine + lib/ for queue_ceremonies) was the only non-obvious part. The ceremony_context integration inside execute_queue_transition() handled governance logging transparently — the recipes didn't need to do anything special for ceremony boundaries.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

No `just queue-park` recipe (backlog -> parked, reverse of unpark). Had to use inline Python to re-park WORK-102 after testing. The WORK-124 deliverables didn't specify it, but the queue-unpark skill documents both directions. Also no `just queue-release` (working -> done), but that path is covered by `just close-work` which handles the Release ceremony.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

Justfile recipes for queue ceremonies need dual sys.path.insert: `.claude/haios/modules` for WorkEngine/GovernanceLayer and `.claude/haios/lib` for queue_ceremonies. The error dict from execute_queue_transition uses key `"error"` (string value), so print formatting needs `r["error"]` not `r.error`.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

The queue-commit skill SKILL.md references `just queue-commit` which didn't exist before this work — that reference is now actionable. No other drift observed.
