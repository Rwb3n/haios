---
template: observations
work_id: WORK-025
captured_session: '249'
generated: '2026-01-27'
last_updated: '2026-01-27T00:23:13'
---
# Observations: WORK-025

## What surprised you?

**The deletion immediately broke justfile recipes.** I expected the deletion to be a clean prerequisite step, with consumer updates (WORK-026, WORK-027) handled afterward. Instead, the first justfile command after deletion (`just scaffold-observations WORK-025`) failed with `ModuleNotFoundError: No module named 'observations'`. This confirms WORK-024's finding: consumers using `sys.path.insert(0, '.claude/lib'); from X import Y` cannot work after deletion - there's no graceful degradation. Had to immediately fix the `scaffold-observations` recipe to continue (pulled forward from WORK-026 scope).

**The failure is immediate and clear, which is actually good.** Rather than silent misbehavior (which we had before with stale files masking new functions), we now get explicit `ModuleNotFoundError`. This forces the migration instead of allowing drift to accumulate.

## What's missing?

**No migration order enforcement in the work system.** WORK-025 has `blocks: [WORK-026, WORK-027]` but nothing prevents an agent from trying to use justfile recipes before WORK-026 updates them. The blocking relationship is documentation, not enforcement. A real pipeline would have pre-commit hooks or CI gates that fail when dependencies aren't met.

**The remaining 12 justfile recipes are still broken.** Only `scaffold-observations` was fixed inline. The others (`obs-validate`, `obs-uncaptured`, `obs-archived`, `obs-triage`, `gov-metrics`, `status-full`, `status-debug`, `status-slim`, `milestone`, `audit-sync`, `audit-gaps`, `audit-stale`) still use deprecated path.

## What should we remember?

**Deletion forces migration faster than deprecation warnings.** The shim with deprecation warning existed since Session 221 (WORK-006), but no one migrated because the old path still worked. After deletion, the first command failed. "Works but warns" doesn't motivate change; "fails loudly" does.

**Test baseline before destructive changes.** I ran pytest before deletion to establish baseline (22 failures). This let me distinguish pre-existing failures from deletion-caused failures. Without the baseline, I couldn't have confidently said "test failures are expected, not regressions."

**When blocking work creates immediate dependencies, may need to pull forward fixes.** The `scaffold-observations` recipe had to be fixed immediately to continue work, even though it's scoped to WORK-026. Strict sequencing isn't always practical.

## What drift did you notice?

**Acceptance criteria said "Tests still pass after deletion" but that's not fully achievable until WORK-027.** The criterion was optimistic. Tests using deprecated path MUST fail after deletion. The correct criterion should have been "Tests using canonical path still pass." This is a gap in how we specify acceptance criteria for migration work.
