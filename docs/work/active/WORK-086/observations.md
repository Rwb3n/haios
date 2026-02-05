---
template: observations
work_id: WORK-086
captured_session: '317'
generated: '2026-02-05'
last_updated: '2026-02-05T22:14:17'
---
# Observations: WORK-086

## What surprised you?

**Zero-iteration TDD execution.** All 19 tests passed on the first implementation attempt with no debugging cycles. This is unusual — typically at least 1-2 tests need adjustment for edge cases or mismatched assumptions. The cause: the plan specified exact line numbers, sample WORK.md templates, test table with numbered IDs (T1-T19), and precise method signatures. This eliminated the ambiguity gap between "what to build" and "how to verify it." The plan itself was the debugging — all edge cases were caught during planning, not implementation.

**The phase filter logic was simpler than expected.** The plan anticipated needing `cycle_phase` with `current_node` fallback logic, but `_parse_work_file` already handles this fallback at parse time (`work_engine.py:767`), so `get_in_lifecycle` just reads `cycle_phase` directly. The effective_phase conditional in the implementation is technically redundant but harmless.

## What's missing?

**No governance ceremony was invoked.** The session ran entirely outside PLAN-DO-CHECK-DONE. The Builder should have flagged the missing `/coldstart` before starting work, even when the operator jumps straight to "implement this plan." There's no hook or gate that prevents ungoverned implementation — the warning is informational only. A PreToolUse hook that blocks `Edit` on module files when no governance cycle is active would enforce this.

**`run_batch` has no progress callback.** For large batches, callers have no way to observe intermediate progress. Not needed for MVP but worth noting for CH-003 evolution.

## What should we remember?

**Plan fidelity at the line-number level enables single-pass TDD.** The pattern: exact file paths + line numbers for insertion points + numbered test table (T1-T19) + sample data specifications + execution order. This should be the standard for implementation plans going forward. When the plan is this precise, the implementation becomes mechanical — no architectural decisions remain. Memory ref: concept 84021.

**TYPE_TO_LIFECYCLE as shared constant was the right extraction.** Both `is_at_pause_point()` and `get_in_lifecycle()` need type-to-lifecycle mapping. Extracting it once at module level (`work_engine.py:131`) prevents drift between the two usages. If a new work type is added, only one place to update.

## What drift did you notice?

**WORK-086 WORK.md had `current_node: active` which is not a standard lifecycle phase.** The node_history shows only a `backlog` entry but current_node says `active`. This is inconsistent — likely set manually during work item creation outside the normal transition path. The WorkEngine.transition() method should be the only way current_node changes, but something wrote `active` directly.
