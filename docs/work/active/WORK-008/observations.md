---
template: observations
work_id: WORK-008
captured_session: '227'
generated: '2026-01-22'
last_updated: '2026-01-22T20:38:50'
---
# Observations: WORK-008

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Graceful degradation pattern was essential for backward compatibility.** The original design would have raised ValueError when config was missing, but this broke existing tests that use tmp_path without setting up haios.yaml. The fix was to return empty loader list when no config exists, allowing legacy behavior to continue while new role-based loading works when config is present.
- [x] **Import path complexity across modules.** The IdentityLoader import required careful sys.path manipulation because the loader lives in `.claude/haios/lib/` while ContextLoader is in `.claude/haios/modules/`.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Session loader and work loader not yet implemented.** The config has placeholders for `builder` and `validator` roles but they all point to just `[identity]` loader. Future loaders needed for full role-based context composition.
- [x] **Hot-reload for config changes.** Currently config is loaded once at init. Deferred per plan.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **Config-driven extensibility pattern:** Define registry in code (`_loader_registry: Dict[str, type]`), register defaults in `_register_default_loaders()`, load config mapping in `_load_config()`, graceful degradation when config missing.
- [x] **L4 principle applied:** "Selective loading by role | haios.yaml defines role -> files mapping" - explicitly followed and works well.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] None observed - Implementation matches TRD and plan exactly. Graceful degradation for missing config is an improvement, not drift.
