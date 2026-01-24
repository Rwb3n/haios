---
template: observations
work_id: WORK-011
captured_session: '233'
generated: '2026-01-24'
last_updated: '2026-01-24T20:57:33'
---
# Observations: WORK-011

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] Implementation was more straightforward than anticipated - sibling loader pattern was well-established
- [x] TDD worked smoothly - 7 tests passed on first implementation run
- [x] Backward-compat pattern emerged: added `coldstart-orchestrator` recipe rather than modifying existing `coldstart`

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] Memory query automation: SessionLoader extracts memory_refs but doesn't query them
- [x] EpochLoader: Could complete the injection pattern (currently /coldstart still requires manual epoch reads)

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] Composition over modification: orchestrator calls loader.load() methods, doesn't modify loaders
- [x] Graceful degradation: hardcoded defaults when config missing (same pattern as sibling loaders)
- [x] [BREATHE] markers implement S20 pressure dynamics - explicit processing time between phases

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] WORK.md node transitions not tracked: node_history shows only backlog, no implement/check transitions
- [x] 10 pre-existing test failures in suite (checkpoint-cycle, survey-cycle, scaffold, templates)
