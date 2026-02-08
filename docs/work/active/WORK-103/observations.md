---
template: observations
work_id: WORK-103
captured_session: '323'
generated: '2026-02-08'
last_updated: '2026-02-08T22:38:49'
---
# Observations: WORK-103

## What surprised you?

- The behavioral change exposed a hidden assumption in existing test `test_get_ready_returns_unblocked_only` (tests/test_work_engine.py:289). That test created `E2-BLOCKED` with `blocked_by: [E2-240, E2-241]` but never created those blocker items in the test fixture. Under the old static check (`not work.blocked_by`), this passed because it only checked list emptiness. Under dynamic resolution, missing blockers are treated as resolved (correct behavior), so the "blocked" item appeared as unblocked. This is a concrete instance of the general pattern: when changing filter semantics from static to dynamic, every test relying on the old static behavior needs review. The fix was simple (create active blocker items in the fixture), but would have been a confusing regression if caught later.

## What's missing?

- No mechanism to auto-clear `blocked_by` fields when blockers complete. Dynamic resolution in `get_ready()` now works around this at query time, but the static `blocked_by` list in WORK.md frontmatter still contains stale references. Any code that reads `blocked_by` directly (instead of going through `get_ready()`) will still see stale IDs. A companion fix in `cascade()` (cascade_engine.py) could remove completed blocker IDs from the `blocked_by` field at write time, eliminating the stale data at its source.

## What should we remember?

- **Static-to-dynamic filter pattern:** When changing filter semantics from static field checks (`not field`) to dynamic resolution (`not resolve(field)`), the behavior changes for any case where referenced entities don't exist in the environment. Every test relying on old static behavior must be audited. Pattern: search test files for the field name being dynamically resolved, verify each test creates the referenced entities.
- **Performance at current scale is fine:** `_is_actually_blocked()` does N additional `get_work()` calls per blocked item in `get_ready()`. At ~15 active items with ~2 blockers max, this is negligible (0.24s for 5 tests). If workspace scales to 100+ items, consider caching resolved statuses within a single `get_ready()` call.

## What drift did you notice?

- Queue showed 13 items after fix vs 10 before. Three items (WORK-093, WORK-071, WORK-075) were phantom-blocked by completed work items. This means the queue has been under-reporting available work since those blockers completed. No documentation drift - the queue arc ARC.md already describes the need for dynamic resolution. The S322 drift warning about `blocked_by` not auto-clearing is now mitigated at query time, though the static field still contains stale data (see "What's missing" above).
