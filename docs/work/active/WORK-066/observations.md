---
template: observations
work_id: WORK-066
captured_session: '307'
generated: '2026-02-04'
last_updated: '2026-02-04T21:16:59'
---
# Observations: WORK-066

## What surprised you?

**TDD worked smoothly with existing test infrastructure.** I expected to create a new test file (`test_queue_position.py`) but discovered it was better to add tests to the existing `test_work_engine.py` file. This maintained test organization consistency and allowed reuse of existing fixtures (`governance`, `engine`, `setup_work_item`). The 6 new tests integrated seamlessly and all 41 tests passed without modification to the test infrastructure.

**Backward compatibility was cleaner than anticipated.** The fallback pattern `cycle_phase = fm.get("cycle_phase", current_node_val)` elegantly handles legacy items. Demo showed WORK-020 (a legacy item without queue_position field) correctly defaulted to `queue_position: backlog` and `cycle_phase: backlog`. No migration script needed.

## What's missing?

**Runtime consumers for the new methods.** The `set_queue_position()` and `get_in_progress()` methods are implemented and tested, but no skill currently calls them. Survey-cycle and close-work-cycle wiring are explicitly out of scope (tracked in WORK-066 deliverables). This is intentional scope discipline, not a gap.

**No automated consumer for queue_position transitions.** The field exists but transitions are manual. Future work should wire:
- survey-cycle: `set_queue_position(id, "in_progress")` on selection
- close-work-cycle: `set_queue_position(id, "done")` on closure

## What should we remember?

**Critique A1 mitigation pattern:** When adding new fields that need persistence, use the unified write path (`_write_work_file()`) rather than creating dual write paths. This was explicitly called out in the plan from Session 305 critique and successfully implemented. See `work_engine.py:653` where `set_queue_position()` calls `_write_work_file()`.

**Deprecation alias pattern:** When renaming fields, keep old field as deprecated alias with fallback logic. Document in README and TRD. This allows incremental migration without breaking consumers. Pattern: `cycle_phase = fm.get("cycle_phase", current_node_val)` at `work_engine.py:767`.

**Plan scope discipline worked:** Explicitly marking survey/close-cycle wiring as "OUT OF SCOPE" in the plan (PLAN.md lines 637-642) prevented scope creep and kept the implementation focused on schema changes.

## What drift did you notice?

**Pre-existing test failures unrelated to WORK-066:** Two tests failed during broader test runs:
- `test_checkpoint_cycle_verify.py::test_verify_phase_section_exists` - Missing VERIFY phase section in checkpoint-cycle skill documentation
- `test_survey_cycle.py::test_survey_cycle_has_pressure_annotations` - Missing `[volumous]` annotation in survey-cycle SKILL.md

These are documentation drift in skills, not code drift. The skill implementations work but their documentation doesn't match the test expectations. Should be tracked as separate work items for skill documentation alignment.
