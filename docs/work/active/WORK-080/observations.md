---
template: observations
work_id: WORK-080
captured_session: '291'
generated: '2026-02-02'
last_updated: '2026-02-02T19:07:38'
---
# Observations: WORK-080

## What surprised you?

**Critique agent scope mismatch detection was valuable.** The critique-agent (A7 assumption) caught that WORK.md deliverable said "migrate 9 remaining files" but the plan explicitly scoped to 2 files. This forced reconciliation before implementation - updating WORK.md to add a scope note. Without critique, I would have implemented the plan and then had a deliverable mismatch at closure. The defense-in-depth gates (INV-058) are working as designed.

**Test assertions needed platform awareness.** Tests comparing `str(path) == "docs/work"` failed on Windows because Path normalizes to backslashes. The fix was simple (compare Path objects directly: `path == Path("docs/work")`), but this is a recurring pattern worth noting. All path string comparisons in tests should use Path object comparison for cross-platform compatibility.

## What's missing?

**No automated follow-up work item creation.** When scoping a work item down (as we did here with the 8 deferred files), there's no automated mechanism to create the follow-up work item. The scope note is manual prose. A pattern like `spawns: [WORK-081]` in the work item frontmatter with auto-scaffold would ensure deferred work doesn't get lost. Currently relies on memory/checkpoint to track this.

## What should we remember?

**Pattern: ConfigLoader.get_path() with ValueError for unresolved placeholders.** The critique agent recommended (A4 mitigation) adding validation for unresolved placeholders. The implementation raises `ValueError` if `{` remains in the resolved path string. This fail-fast approach prevents silent bugs where a caller forgets to pass kwargs. This pattern should be documented for future similar interpolation functions.

**Pattern: Scope reduction requires WORK.md update.** When plan scope is narrower than work item deliverables, the work item MUST be updated to reflect actual scope. Otherwise DoD verification will flag incomplete deliverables. The critique agent enforces this, but it's worth making explicit: deliverables define the acceptance criteria, plan defines the execution approach - they must align.

## What drift did you notice?

**Pyright import warnings are noise.** The `reportMissingImports` warnings for sibling module imports (e.g., `from .governance_layer import GovernanceLayer`) appear throughout the codebase but don't affect runtime. The try/except import pattern used for package vs standalone compatibility is correct but static analysis can't resolve it. These warnings should be suppressed in pyright config or ignored - they're not actionable drift.
