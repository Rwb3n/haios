---
template: work_item
id: E2-118
title: Vitals Work Cycle State Injection
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-27
milestone: M7d-Plumbing
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-27T12:28:28'
---
# WORK-E2-118: Vitals Work Cycle State Injection

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Vitals show infrastructure (commands, skills, agents) but not operational state. Missing: current session, active work item, cycle type (implementation vs investigation), cycle phase (PLAN/DO/CHECK/DONE).
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add work cycle state to vitals injection (UserPromptSubmit hook)
- [ ] Show: active work item ID, cycle type (implementation/investigation), cycle phase (PLAN/DO/CHECK/DONE)
- [ ] Read from work file `current_node` and `lifecycle_phase` fields
- [ ] Update haios-status-slim.json to include active work context

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
