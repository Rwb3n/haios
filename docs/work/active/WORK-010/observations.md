---
template: observations
work_id: WORK-010
captured_session: '231'
generated: '2026-01-24'
last_updated: '2026-01-24T19:56:31'
---
# Observations: WORK-010

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] Loader pattern is well-established. SessionLoader (CH-005) was a clean template. Implementation took ~60 minutes as estimated.
- [x] Epoch alignment is straightforward - E2- prefix check against current epoch works without complex logic.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] No automatic wiring to coldstart Phase 3 yet. WorkLoader registered but coldstart skill not updated to call `just work-options`. This is CH-007 work.
- [x] Queue output format is fragile. Regex parsing depends on exact format. Consider structured (JSON) output from queue recipe.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] Dependency injection pattern (queue_fn) enables testability. All tests pass without subprocess mocking. Pattern 82323 should be used for loaders calling external commands.
- [x] Loader triad complete: IdentityLoader (Phase 1), SessionLoader (Phase 2), WorkLoader (Phase 3). Future coldstart can compose these.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] L4 lookup in plan-validation-cycle looks for wrong path (`L4-implementation.md` vs `.claude/haios/manifesto/L4/` directory).
- [x] WORK.md node transitions still not tracked. Inherited from Session 230. current_node stayed at backlog throughout implementation cycle.
