---
template: observations
work_id: WORK-098
captured_session: '314'
generated: '2026-02-05'
last_updated: '2026-02-05T18:37:38'
---
# Observations: WORK-098

## What surprised you?

The monolithic `implementation_plan.md` was already moved to `_legacy/` (by WORK-090, git status shows `D .claude/templates/implementation_plan.md`), but no test caught the breakage before this investigation. This means the test suite wasn't running as part of the WORK-090 closure DoD, or the move happened after tests passed. The `test_lib_validate.py::TestImplementationPlanTemplate` tests directly read the template file path rather than using `load_template()`, so the breakage manifests in 5 independent locations rather than a single function. If `load_template()` had been the only consumer, a single fix would suffice.

Also surprising: `audit_decision_coverage.py` with hardcoded `E2_4` path doesn't crash - it silently audits the wrong epoch. This is worse than a crash because it gives false confidence. The audit reports "INCONSISTENT" but for stale E2.4 data, not current E2.5.

## What's missing?

A **template consumer registry** or at least a test that validates all `load_template()` calls resolve to existing files. Currently each consumer hardcodes the template name string independently (`scaffold.py:266`, `test_lib_validate.py:124`, `test_template_rfc2119.py:29`, etc.). When a template is moved/renamed, you must grep for every reference - which is exactly what this investigation did manually.

Also missing: a **pre-close smoke test** that runs `pytest` as a hard gate in the close-work-cycle. If WORK-090's close had run the test suite, the 5 failures would have been caught before the template was archived.

## What should we remember?

**Pattern: "Restructure + Consumer Update" must be atomic.** When any file is moved, renamed, or restructured, the work item MUST include updating all consumers OR spawn a companion work item before closing. This was captured as memory 83974 but bears repeating: CH-006 is the canonical example of this anti-pattern. Consider adding this as an L3 principle or close-work-cycle gate: "Are all consumers of modified files updated?"

**Investigation timing:** This investigation took ~15 minutes of effective work because the EXPLORE phase was directed - reading the 3 source_files plus grepping for `implementation_plan` across the codebase was sufficient. Short, focused investigations that test concrete hypotheses are efficient. The 4-hypothesis structure (H1-H4) with explicit test methods made VALIDATE a mechanical exercise.

## What drift did you notice?

- `justfile:390` `commit-close` recipe uses `docs/work/archive/WORK-{{id}}-*` glob pattern, which doesn't match the WORK-XXX directory structure (`docs/work/active/WORK-099/`). This means `just commit-close` hasn't worked for any WORK-XXX format items - only legacy E2-XXX flat files. Added to WORK-099 deliverables.
- The `SESSION` variable in `scaffold_template()` produces "247" instead of "314" for the current session. The `get_current_session()` function reads from events log or status file, but the status file's `session_delta.current_session` may be stale if `just update-status` hasn't run recently. The scaffolded observations file had `captured_session: '247'` - significantly wrong.
- Skills `plan-authoring-cycle` and `plan-validation-cycle` both reference `.claude/templates/implementation_plan.md` which no longer exists. Agents following these skills would get confused looking for the file.
