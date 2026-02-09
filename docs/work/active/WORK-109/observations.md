---
template: observations
work_id: WORK-109
captured_session: '327'
generated: '2026-02-09'
last_updated: '2026-02-09T19:21:21'
---
# Observations: WORK-109

## What surprised you?

The existing WORK-105 tests accidentally formed a valid transition chain in `test_set_queue_position_five_values` - iterating `parked, backlog, ready, working, done` from a default `backlog` start happened to produce all valid transitions (backlog->parked->backlog->ready->working->done). This was pure coincidence. However, 8 other tests across WORK-066 (2 tests) and WORK-105 (6 tests) used direct `backlog->working` jumps, confirming the CH-006 consumer update pattern: adding validation to an existing field always breaks callers that took shortcuts. The scaffold_template keyword-only fix was also discovered as a latent bug during this session - all 22 callers already used keyword args, so the `*` separator was purely preventive.

## What's missing?

No automated way to detect tests that use invalid transition paths before the state machine is enforced. A test helper like `advance_queue_to(engine, work_id, target_position)` that automatically chains valid transitions would reduce test maintenance burden. Currently each test must manually chain `set_queue_position` calls through intermediate positions (e.g., backlog->ready->working requires two explicit calls). This helper would be especially valuable for CH-010 (QueueCeremonies) which will add more queue interactions.

## What should we remember?

**Test Helper Pattern:** When adding state machine validation to existing fields, consider adding a test helper that chains valid transitions. Something like `advance_to_working(engine, id)` that calls `set_queue_position(id, "ready")` then `set_queue_position(id, "working")`. This would make future tests cleaner and immune to transition path changes. **Keyword-Only Prevention:** The scaffold_template `*` fix is a good pattern for any function where parameter ordering creates latent misroute risk - apply proactively to other functions with Optional params that could be confused positionally (e.g., `generate_output_path`, `create_work`).

## What drift did you notice?

CH-009 spec section R3 lists `get_backlog()`, `get_ready()`, `get_working()` as methods that should delegate to `get_by_queue_position()`, but the existing `get_ready()` has richer semantics (excludes blocked, terminal, parked) and was intentionally not refactored. This is acceptable divergence - `get_by_queue_position()` provides the pure queue filter, while `get_ready()` remains a domain-specific query with business logic. The spec's R3 interface was aspirational; the implementation correctly preserves backward compatibility over spec purity.
