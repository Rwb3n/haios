---
template: work_item
id: WORK-099
title: Fix Scaffold Template Loading and Broken Tests
type: bugfix
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: WORK-098
chapter: CH-006-TemplateFracturing
arc: lifecycles
closed: null
priority: high
effort: small
traces_to:
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- tests/test_lib_validate.py
- tests/test_template_rfc2119.py
- tests/test_lib_scaffold.py
- .claude/skills/plan-authoring-cycle/SKILL.md
- .claude/skills/plan-validation-cycle/SKILL.md
- justfile
acceptance_criteria:
- scaffold.py load_template resolves fractured templates
- All 5 broken tests pass
- Skill docs reference correct template paths
- just plan recipe works with fractured templates
blocked_by: []
blocks:
- WORK-091
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:34:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  discovered_during: WORK-098
  issue_type: tooling_gap
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T18:35:06'
---
# WORK-099: Fix Scaffold Template Loading and Broken Tests

---

## Context

WORK-098 investigation found that CH-006 (TemplateFracturing) moved `implementation_plan.md` to `_legacy/` but left 8+ consumer files broken. This work item fixes the Tier 1 (broken at runtime) and Tier 3 (stale docs) issues.

**Root cause:** `scaffold.py:load_template()` resolves templates as `.claude/templates/{name}.md` but fractured templates live at `.claude/templates/{lifecycle}/{PHASE}.md`. The monolithic `implementation_plan.md` was archived to `_legacy/` in WORK-090.

---

## Deliverables

- [ ] Fix `scaffold.py:load_template()` to handle fractured template path or update TEMPLATE_CONFIG
- [ ] Fix 3 tests in `test_lib_validate.py::TestImplementationPlanTemplate` to reference `_legacy/` or fractured path
- [ ] Fix 1 test in `test_template_rfc2119.py` to reference correct path
- [ ] Fix 1 test in `test_lib_scaffold.py::test_known_templates_exist` to exclude or update `implementation_plan`
- [ ] Update `plan-authoring-cycle/SKILL.md:333` template reference
- [ ] Update `plan-validation-cycle/SKILL.md:257` template reference
- [ ] Fix `justfile:390` `commit-close` recipe archive path pattern for WORK-XXX dirs

---

## History

### 2026-02-05 - Created (Session 314)
- Spawned from WORK-098 investigation findings
- Covers Tier 1 (broken) and Tier 3 (stale docs) fixes

---

## References

- @docs/work/active/WORK-098/WORK.md (investigation)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @docs/work/active/WORK-091/WORK.md (blocked by this)
