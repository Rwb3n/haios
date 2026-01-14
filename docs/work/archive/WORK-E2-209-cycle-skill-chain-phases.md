---
template: work_item
id: E2-209
title: Cycle Skill Chain Phases
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: INV-041
spawned_by_investigation: INV-041
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 14:35:30
  exited: null
cycle_docs: {}
memory_refs:
- 79802
- 79803
- 79804
- 79805
- 79806
- 79807
- 79808
- 79809
- 79810
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T19:46:51'
---
# WORK-E2-209: Cycle Skill Chain Phases

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Cycle skills list `/close` as an action but don't auto-invoke it. Agent must remember to close work items. Close-work-cycle ends at CAPTURE without routing to next work item.

**Root Cause:** investigation-cycle and implementation-cycle CONCLUDE/DONE phases list `/close {backlog_id}` as a step, not as a MUST auto-invoked action. No CHAIN phase exists (unlike work-creation-cycle which does have one).

**Evidence:** investigation-cycle/SKILL.md:96, implementation-cycle/SKILL.md:192

**Design (from INV-044):** Add CHAIN phase following work-creation-cycle pattern. Instruction-based chaining - skills contain routing instructions, agent follows them. Use `just ready` for work selection.

---

## Current State

Work item in BACKLOG node. Design complete from INV-044. Ready for implementation.

---

## Deliverables

### investigation-cycle CHAIN Phase
- [ ] Add "### 4. CHAIN Phase (Post-CONCLUDE)" section
- [ ] Actions: (1) `/close {backlog_id}`, (2) `just ready`, (3) route per decision table

### implementation-cycle CHAIN Phase
- [ ] Add "### 5. CHAIN Phase (Post-DONE)" section
- [ ] Actions: (1) `/close {backlog_id}`, (2) `just ready`, (3) route per decision table

### close-work-cycle CHAIN Phase
- [ ] Add "### 4. CHAIN Phase (Post-CAPTURE)" section
- [ ] Actions: (1) skip close (already done), (2) `just ready`, (3) route per decision table

### Routing Decision Table (shared)
```
| Signal | Action |
|--------|--------|
| No items returned | Report "No unblocked work. Awaiting operator." |
| ID starts with `INV-` | Invoke `Skill(skill="investigation-cycle")` |
| Work file has plan in `documents.plans` | Invoke `Skill(skill="implementation-cycle")` |
| Otherwise | Invoke `Skill(skill="work-creation-cycle")` to populate |
```

---

## History

### 2025-12-27 - Created (Session 127)
- Initial creation from INV-041

### 2025-12-27 - Design Complete (Session 129)
- INV-044 completed, provides concrete CHAIN phase design
- Deliverables updated with specific implementation spec

---

## References

- Spawned by: INV-041 (Autonomous Session Loop Gap Analysis)
- Design from: INV-044 (Skill Chaining Mechanism Design)
- Pattern: work-creation-cycle/SKILL.md:100-125
