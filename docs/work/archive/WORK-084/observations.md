---
template: observations
work_id: WORK-084
captured_session: '301'
generated: '2026-02-03'
last_updated: '2026-02-03T21:53:26'
---
# Observations: WORK-084

## What surprised you?

The implementation was more straightforward than anticipated. The plan estimated 75 minutes, and execution was efficient because:
- The existing cycle_runner.py structure (E2-255 pattern) was clean - dataclasses at top, methods in class, clear separation
- Python dataclass inheritance "just works" - no special handling needed for LifecycleOutput subclasses
- The critique-agent REVISE verdict (A8: lifecycle naming convention) highlighted a real design question but the operator's decision to deprecate `-cycle` suffix clarified direction immediately

The test coverage was already solid. 10 existing tests meant I could add 6 new tests and have high confidence I wasn't breaking anything. The TDD flow (RED -> GREEN) worked smoothly.

## What's missing?

**Runtime consumer for run().** Per ADR-033 DoD, "Runtime consumer exists" is required, but this is foundation work - the consumer will be CH-005 (PhaseTemplateContracts) where skills integrate with run(). This is documented as intentional scope limitation.

**Content population.** The MVP returns empty typed outputs. A future work item (likely in CH-005) needs to wire skill execution results into these typed containers.

## What should we remember?

**Pattern: Add new without modifying existing.** The implementation added LifecycleOutput types and run() method without changing any existing method signatures. This preserved backward compatibility (10 existing tests pass) while extending functionality. This pattern should be the default for module evolution.

**Critique-agent value.** The REVISE verdict surfaced the lifecycle naming convention issue (A8) which led to an important operator decision: the `-cycle` suffix is legacy, short names (`design`, `investigation`) are the forward direction. This decision was captured through the critique workflow, not discovered during implementation.

## What drift did you notice?

None significant. The CH-001 spec, the plan, and the implementation aligned well. The only "drift" was pre-existing test failures in unrelated test files (16 failed in full suite), but these are known issues not caused by WORK-084.
