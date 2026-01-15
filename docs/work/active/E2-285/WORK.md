---
template: work_item
id: E2-285
title: Skill Template Single-Phase Default
status: complete
owner: Hephaestus
created: 2026-01-10
closed: 2026-01-15
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-10 11:54:42
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-10
last_updated: '2026-01-10T11:56:32'
---
# WORK-E2-285: Skill Template Single-Phase Default

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Skill template has "The Cycle" section with phases as default structure. This nudges toward multi-phase design, violating S20 "each skill does ONE thing."

**Evidence:** survey-cycle (5 phases), observation-capture-cycle (3 phases), implementation-cycle (5 phases) all built as multi-phase because the template encouraged it.

**Solution:** Change skill template to:
- Default to single-phase
- Require explicit justification for multi-phase
- Remove "Exit Criteria" checklists (self-validated ceremony)

---

## Deliverables

- [ ] Skill template defaults to single-phase
- [ ] Multi-phase requires explicit rationale section
- [ ] Remove exit criteria checklists from template
- [ ] Add "Principle Alignment" verification

---

## History

### 2026-01-10 - Created (Session 186)
- Template encouraged what S20 prohibited
- Change template to enforce S20

---

## References

- Memory 81248-81266 (E2.2 drift diagnosis)
- S20-pressure-dynamics.md ("each skill does ONE thing")
- Current: .claude/templates/skill.md (if exists)
