---
template: observations
work_id: WORK-006
captured_session: '221'
generated: '2026-01-21'
last_updated: '2026-01-21T20:41:52'
---
# Observations: WORK-006

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- Path resolution: modules need `.parent.parent / "lib"` not `.parent / "lib"` since lib is sibling to modules, not child
- 11 pre-existing test failures unrelated to migration (good baseline awareness)
- haios_etl cross-dependency: some lib modules import from separate Epoch 1 codebase

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- haios_etl migration to portable plugin directory (Epoch 1 memory code still external)
- Import dependency graph tool to catch path issues before runtime

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- Strangler fig pattern works well for migrations (copy, update consumers, add shims)
- Subprocess execution doesn't inherit parent sys.path - each entry point needs own setup
- Compatibility shims with deprecation warnings enable gradual consumer migration

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- None significant. Plan matched implementation closely.
