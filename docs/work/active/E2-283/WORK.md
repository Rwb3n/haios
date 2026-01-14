---
template: work_item
id: E2-283
title: Survey-Cycle Prune to Minimal Routing
status: complete
owner: Hephaestus
created: 2026-01-10
closed: '2026-01-11'
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
  entered: 2026-01-10 11:54:25
  exited: null
cycle_docs: {}
memory_refs:
- 81299
- 81300
- 81301
- 81302
- 81303
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-10
last_updated: '2026-01-10T11:56:04'
---
# WORK-E2-283: Survey-Cycle Prune to Minimal Routing

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** survey-cycle is 241 lines with 5 phases (GATHER→ASSESS→OPTIONS→CHOOSE→ROUTE) to accomplish "pick a work item." S20 says "each skill does ONE thing."

**Evidence:** Session 186 demonstrated pattern-matching through phases without thinking differently. The cycle added overhead without changing the decision.

**Solution:** Minimal routing:
- If in-progress work exists from prior session: continue it
- Otherwise: present top 3 unblocked items
- Operator steers or agent picks highest priority

---

## Deliverables

- [ ] Replace 241-line survey-cycle with minimal version
- [ ] Remove 5-phase structure
- [ ] Simple logic: continue previous OR present options
- [ ] No exit criteria checklists

---

## History

### 2026-01-10 - Created (Session 186)
- Spawned from Session 186 meta-observation: skills as procedural theater
- S20 says single-phase, we built 5-phase

---

## References

- Memory 81211-81221 (skills as procedural theater)
- S20-pressure-dynamics.md lines 92-107 ("smaller containers, harder boundaries")
- Current: .claude/skills/survey-cycle/SKILL.md
