---
template: work_item
id: WORK-098
title: Lifecycle Tooling Consumer Updates
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-05
spawned_by: WORK-091
chapter: null
arc: lifecycles
closed: '2026-02-05'
priority: high
effort: medium
traces_to:
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/hooks/hooks/pre_tool_use.py
- justfile
acceptance_criteria:
- Scope of tooling updates documented
- Affected files identified
- Work items spawned for fixes
blocked_by: []
blocks:
- WORK-091
- WORK-092
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 08:38:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83975
- 83976
- 83977
- 83978
- 83984
- 83985
- 83986
- 83987
- 83988
extensions:
  epoch: E2.5
  discovered_during: WORK-091
  issue_type: tooling_gap
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T18:38:45.640269'
queue_position: backlog
cycle_phase: backlog
---
# WORK-098: Lifecycle Tooling Consumer Updates

---

## Context

During WORK-091 (Fracture Validation Templates), discovered that tooling doesn't support the new fractured template pattern:

1. **`just plan` recipe broken** - Scaffold module looks for monolithic `implementation_plan.md` which was archived in WORK-090
2. **PreToolUse hook regex too narrow** - Only accepted `E2-\d{3}` for backlog_id, not `WORK-\d{3}` (fixed in session 313)
3. **Governed path hook blocks valid writes** - Had to use workaround to create plan files
4. **`just prioritize` recipe missing** - No way to reorder queue programmatically
5. **`just work` blocked by hook** - Hook blocks scaffold but no alternative path provided

**Pattern:** This is a systemic situation - multiple just recipes and hooks are out of sync with the WORK-XXX ID format and fractured template structure introduced in E2.5.

CH-006 (TemplateFracturing) focused on creating fractured templates but didn't include updating consumers.

---

## Objective

Investigate the full scope of tooling updates needed to support fractured lifecycle templates, then spawn work items for systematic fixes.

---

## Deliverables

- [x] Document all affected just recipes
- [x] Document all affected hooks
- [x] Document scaffold.py changes needed
- [x] Recommend: new chapter CH-007 or expand CH-006
- [x] Spawn work items for each fix

---

## Findings (Session 314)

### Tier 1: Broken at Runtime (5 test failures, 1 recipe broken)

| File | Line(s) | Issue |
|------|---------|-------|
| `.claude/haios/lib/scaffold.py` | 266 | `load_template("implementation_plan")` → FileNotFoundError (template moved to `_legacy/`) |
| `tests/test_lib_validate.py` | 124, 131, 138 | 3 tests read deleted `implementation_plan.md` directly |
| `tests/test_template_rfc2119.py` | 29 | Reads deleted `implementation_plan.md` |
| `tests/test_lib_scaffold.py` | 147 | `test_known_templates_exist` lists `implementation_plan` |

**Impact:** `just plan` recipe broken. 5 tests fail.

### Tier 2: Wrong Data (runs but incorrect)

| File | Line(s) | Issue |
|------|---------|-------|
| `.claude/haios/lib/audit_decision_coverage.py` | 306-307 | Hardcoded `E2_4` epoch path; audits wrong epoch |

**Impact:** `just audit-decision-coverage` reports stale E2.4 decisions instead of E2.5.

### Tier 3: Stale Documentation

| File | Line(s) | Issue |
|------|---------|-------|
| `.claude/skills/plan-authoring-cycle/SKILL.md` | 333 | References deleted `.claude/templates/implementation_plan.md` |
| `.claude/skills/plan-validation-cycle/SKILL.md` | 257 | References deleted `.claude/templates/implementation_plan.md` |
| `justfile` | 390 | `commit-close` uses old `WORK-{{id}}` archive path pattern |

### Missing (Never Existed)

| Item | Description |
|------|-------------|
| `just prioritize` recipe | No way to reorder queue programmatically |
| `ConfigLoader.get_phase_template()` | No API for fractured template discovery (CH-006 success criteria) |

### Hooks (Already Fixed)

| Item | Status |
|------|--------|
| PreToolUse backlog_id regex | Fixed in Session 313 (memory 83972) |
| Path governance for work dirs | Working correctly |

### Recommendation

Expand CH-006 scope (not new chapter). The consumer updates are part of the same fracturing effort - CH-006 success criteria already includes "Skill loaders updated to use fractured templates."

### Spawned Work Items

- **WORK-099**: Fix scaffold.py template loading + broken tests + stale skill docs (Tier 1 + Tier 3)
- **WORK-100**: Fix audit_decision_coverage.py hardcoded epoch path (Tier 2, independent)

---

## History

### 2026-02-05 - Created (Session 313)
- Spawned from WORK-091 when tooling gaps discovered
- Blocks WORK-091, WORK-092 from clean completion

---

## References

- @docs/work/active/WORK-091/WORK.md (spawning work)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/haios/epochs/E2_5/observations/obs-313-ceremony-composition-gap.md (related observation)
