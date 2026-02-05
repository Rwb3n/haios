---
template: observations
work_id: WORK-099
captured_session: '247'
generated: '2026-02-05'
last_updated: '2026-02-05T19:24:44'
---
# Observations: WORK-099

## What surprised you?

Bootstrap problem: `just plan` (the tool to create the implementation plan) was itself broken by the bug this work item fixes. `load_template("implementation_plan")` failed because the template was moved to `_legacy/`, so plan scaffolding couldn't run until the core fix was applied first. This forced reordering implementation steps - fix the code before scaffolding the plan. This is a class of bug where governance tooling is broken by the very change it should govern. Implication: when moving/restructuring foundational files, always verify the scaffolding/governance tools that depend on them still work.

## What's missing?

Proportional governance fast-path is not yet formalized. Memory ref 83990 (Session 314) says small items should have fast-path through lifecycle/ceremony chains, but there's no actual mechanism - no `effort` field check, no ceremony skip logic. I manually skipped plan-authoring-cycle and plan-validation-cycle because WORK-098 investigation had fully scoped all 7 deliverables. This should be a documented pattern (perhaps per WORK-101, parked for E2.6), not an ad-hoc decision each time.

## What should we remember?

- `_legacy/` fallback pattern in `load_template()` (`scaffold.py:269-272`): transitional pattern that should be removed when all consumers use fractured templates directly. Currently only `implementation_plan` lives in `_legacy/`.
- Test path resolution pattern: `_get_template_path()` static method in `TestImplementationPlanTemplate` provides the fallback. Reuse this pattern for any test that hardcodes template paths.
- 16 pre-existing test failures documented in MEMORY.md. These predate WORK-099 and are not regressions.
- Session field stale: scaffold_template populates SESSION from events log, which returned 247 instead of 315. This is known drift (S314) but not in WORK-099 scope.

## What drift did you notice?

- `justfile:commit-close` was using flat file archive patterns (`WORK-{id}-*`, `PLAN-{id}*`, `INVESTIGATION-{id}*`) from pre-E2-212 era. Now fixed to directory pattern (`{id}/`). Other justfile recipes may have similar drift with legacy path patterns - worth auditing.
- `scaffold_template` SESSION variable reads from events log and returned 247 instead of current 315. The `get_current_session()` function may be reading stale data. Not fixed by WORK-099 (different scope).
