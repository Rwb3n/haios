---
template: observations
work_id: E2-236
captured_session: '245'
generated: '2026-01-26'
last_updated: '2026-01-26T20:19:25'
---
# Observations: E2-236

## What surprised you?

The critique-agent (E2-072) caught a significant file path mismatch between WORK.md and PLAN.md that would have caused verification failure. WORK.md deliverable 1 said "Add function in `.claude/lib/status.py`" but the plan's Detailed Design specified `.claude/haios/lib/governance_events.py`. The critique surfaced this as "A1: LOW confidence, no mitigation" and blocked with verdict REVISE. Without the critique phase, implementation would have completed successfully but DoD verification would have failed because the deliverable specified the wrong file. This validates the Gate 3/4 defense-in-depth strategy from INV-058.

Also surprising: pytest picks up modules from sys.path in order, and when `test_governance_events.py` adds `.claude/lib/` to path, it pollutes the path for subsequent tests. Running `test_orphan_detection.py` alone passes, but running it after governance tests fails because imports resolve to the deprecated path.

## What's missing?

The orphan detection mechanism is complete, but actual session event logging is not wired. No code currently calls `log_session_start()` when sessions begin. The plan explicitly deferred this to "follow-up work" in Step 5: "Wire Session Logging into Recipes". This means the feature is infrastructure-complete but won't trigger until:
1. `just session-start` is modified to call `log_session_start()`
2. Checkpoint/session-end hooks call `log_session_end()`

This is documented in plan's Open Questions but creates a "feature exists but doesn't fire" situation.

## What should we remember?

1. **Use canonical path**: Always `.claude/haios/lib/` for new modules, never deprecated `.claude/lib/`. The deprecated location still exists and causes import confusion.

2. **Test isolation matters**: Tests need explicit sys.path handling. Pattern used in test_orphan_detection.py:
   ```python
   DEPRECATED_LIB_PATH = str(Path(__file__).parent.parent / ".claude" / "lib")
   if DEPRECATED_LIB_PATH in sys.path:
       sys.path.remove(DEPRECATED_LIB_PATH)
   ```

3. **Critique agent value**: For medium+ effort work items, the critique-agent catches issues that pass plan-validation-cycle but would fail at DoD verification. The 10 assumptions it surfaces provide a pre-flight checklist.

4. **Update docstrings**: When adding event types to governance_events.py, remember to update the module docstring's "Event Types:" list (added SessionStarted, SessionEnded).

## What drift did you notice?

The `.claude/lib/` directory is marked DEPRECATED in its README (lines 5-8) but:
1. `tests/test_governance_events.py` still imports from it
2. Both directories contain identical `governance_events.py` files
3. The WORK-006 migration (Session 221) supposedly moved all modules but didn't update all consumers

This creates a dual-module problem where changes to `.claude/haios/lib/governance_events.py` don't affect code importing from `.claude/lib/governance_events.py`. The deprecation is incomplete.
