---
template: observations
work_id: WORK-105
captured_session: '322'
generated: '2026-02-08'
last_updated: '2026-02-08T22:10:46'
---
# Observations: WORK-105

## What surprised you?

The catch-all validation in `_write_work_file()` (A6 mitigation from critique) immediately surfaced a test design issue in T8. The test tried to write `status=archived + queue_position=backlog` to set up the precondition, but the catch-all fired during setup rather than during the assertion. This is exactly the defense-in-depth behavior the critique predicted (memory 84038) - it prevents forbidden states through ANY code path, including test setup. The fix was simple: establish valid state first (set `queue_position=done`, then set `status=archived`), then attempt the forbidden transition. This validates the critique agent's A6 finding about defense-in-depth at the writer level.

## What's missing?

No `get_parked()` query method exists yet. CH-009 (QueueLifecycle) will need it for the Unpark ceremony to list parked items. Also, no transition validation exists for `queue_position` changes - currently any valid value can be set from any other value. CH-009 will need to enforce the transition graph (e.g., `parked -> backlog` only via Unpark ceremony, `backlog -> ready` only via Prioritize ceremony). The current implementation is intentionally permissive per CH-007 scope; transition rules belong to CH-009/CH-010.

## What should we remember?

When adding catch-all validation to write paths (defense-in-depth pattern), test setup code that writes intermediate states will trigger that validation. Always establish valid state combinations before writing. Pattern: if testing "archived + backlog is forbidden", first create a valid archived state (`archived + done`), then try the forbidden transition (`set_queue_position("backlog")`). This applies broadly to any dual-validation pattern where both setter and writer validate constraints. The plan's T8 test code was correct in intent but needed the setup order adjusted - a common issue when catch-all validation is added retroactively to existing write paths.

## What drift did you notice?

The `get_ready()` docstring (work_engine.py:360) still referenced `status in ('active', 'in_progress')` which was stale - the actual implementation filters by terminal_statuses set exclusion. Fixed during implementation. Also, WORK-105's `blocked_by: [WORK-106]` in frontmatter was not cleared even though WORK-106 is `status: complete`. This is a manual bookkeeping gap - the cascade system doesn't currently auto-clear `blocked_by` when a blocker completes. CH-010 (QueueCeremonies) or a PostToolUse hook could address this.
