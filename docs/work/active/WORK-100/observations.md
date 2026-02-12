---
template: observations
work_id: 'WORK-100'
captured_session: '358'
generated: '2026-02-12'
last_updated: '2026-02-12T22:11:19'
---
# Observations: WORK-100

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

The fix was a 2-line change in `__main__` but the function `validate_full_coverage()` was already properly parameterized — it accepts `epoch_path` and `arcs_dir` as arguments. The bug was only in the CLI entry point, not the library API. This means any programmatic caller was unaffected; only `just audit-decision-coverage` (which runs `__main__`) was broken. The silent nature of the bug is what made it insidious — the audit returned "CONSISTENT" for stale E2.4 data, giving false confidence rather than erroring.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

The `__main__` block pattern (hardcoded defaults as CLI entry point) exists in other lib/ files too — WORK-094 identified 17 hardcoded paths total. Each one is a ticking time bomb for the next epoch transition. A systematic pass or a shared `get_epoch_paths()` utility would prevent this class of bug entirely.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

Pattern: when fixing hardcoded paths in `__main__` blocks, extract a named, testable function (`get_default_paths()`) rather than inlining ConfigLoader. This makes the fix testable and reusable. The test asserts the absence of the old value (`E2_4`) rather than the presence of a specific new value, so it won't break on E2.6 transition.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] None observed — fix aligns with WORK-080 (ConfigLoader as single source of truth) and haios.yaml epoch section already had correct paths.
