---
template: work_item
id: WORK-098
title: Lifecycle Tooling Consumer Updates
type: investigation
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: WORK-091
chapter: null
arc: lifecycles
closed: null
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
memory_refs: []
extensions:
  epoch: E2.5
  discovered_during: WORK-091
  issue_type: tooling_gap
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T08:40:36'
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

- [ ] Document all affected just recipes
- [ ] Document all affected hooks
- [ ] Document scaffold.py changes needed
- [ ] Recommend: new chapter CH-007 or expand CH-006
- [ ] Spawn work items for each fix

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
