---
template: observations
work_id: 'WORK-125'
captured_session: '347'
generated: '2026-02-11'
last_updated: '2026-02-11T21:38:52'
---
# Observations: WORK-125

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- The round-trip test revealed WORK-102 was already in `parked` state (from S346 testing), so the Park transition was `parked -> parked` (idempotent). `execute_queue_transition()` does not validate the from-state — it accepts any transition to any target. This is permissive by design but could mask incorrect transitions. Not a bug for WORK-125, but worth noting for WORK-126 (node_history gap) since history would record a no-op transition.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [ ] None observed — the existing queue-unpark recipe was a complete pattern to follow.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- Effort=small pattern-based work items (mirroring an existing recipe) can complete in a single pass without formal plan gates. The proportional governance pattern (WORK-101) should codify this: if the deliverable is "add X mirroring existing Y", skip PLAN 3-gate ceremony and go direct to DO.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- Two governance-events.jsonl files exist: `.claude/governance-events.jsonl` (used by hooks, last written Jan 27) and `.claude/haios/governance-events.jsonl` (used by `queue_ceremonies.py`). The split means `just events` or `just governance-metrics` may not see queue ceremony events depending on which file they read. This is a known drift from the portability arc's "single source of truth" principle. WORK-126 (node_history) may need to address which file is canonical.
