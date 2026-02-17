# Plan Templates by Work Type

WORK-152: Fractured from monolithic `_legacy/implementation_plan.md`.

## Templates

| File | Work Types | Sections | Notes |
|------|-----------|----------|-------|
| `implementation.md` | feature, spike | ~15 | Full template (TDD, code diffs, call chains) |
| `design.md` | design | ~9 | ADRs, specs, documentation (no code sections) |
| `cleanup.md` | bug, chore | ~6 | Minimal (change list, verify, done) |

## Type Mapping

Work item `type` field maps to plan template type via `PLAN_TYPE_MAP` in `scaffold.py`:

| Work Item Type | Plan Template | Rationale |
|---------------|---------------|-----------|
| feature | implementation | Code-heavy, needs TDD and design sections |
| spike | implementation | Exploratory but produces code artifacts |
| design | design | ADRs, specs — no code sections needed |
| bug | cleanup | Fix and verify, minimal ceremony |
| chore | cleanup | Maintenance tasks, minimal ceremony |
| investigation | implementation (fallback) | Investigations use investigation-cycle, not plan templates |

## How Routing Works

1. `scaffold_template("implementation_plan", backlog_id="WORK-XXX")` is called
2. `_get_work_type("WORK-XXX")` reads `type` from WORK.md frontmatter
3. `get_plan_type(type)` maps to plan template type via `PLAN_TYPE_MAP`
4. `load_plan_template(type)` loads `.claude/templates/plans/{plan_type}.md`
5. Falls back to `_legacy/implementation_plan.md` if template file not found

## Validation

Type-specific templates include `subtype: design` (or `cleanup`) in frontmatter.
`validate_template()` detects `subtype` and routes to `implementation_plan_{subtype}`
registry entry for type-specific section coverage validation.

## Maintenance

Shared sections (Goal, Effort Estimation, Verification, Ground Truth Verification,
Progress Tracker) appear in all templates. When modifying shared sections, update
ALL template variants.

`implementation.md` is the canonical full template. `_legacy/implementation_plan.md`
is preserved as fallback only.
