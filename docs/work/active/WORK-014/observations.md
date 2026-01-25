---
template: observations
work_id: WORK-014
captured_session: '240'
generated: '2026-01-25'
last_updated: '2026-01-25T21:46:03'
---
# Observations: WORK-014

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- Scope narrower than expected: 11 files vs 12 predicted (work_item.py optional/untracked)
- Six skill files duplicate routing logic - synchronization risk

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- No runtime integration test for full work item -> cycle routing flow
- Type field not enforced at work item creation (fallback perpetuates legacy)

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- Pattern: `type == X OR id.startswith(PREFIX)` for backward-compatible migrations
- Isolated test files (test_routing_gate.py) improve debugging

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- WORK.md current_node not updated during implementation phases
- Skill prose duplicates routing code - no sync mechanism
