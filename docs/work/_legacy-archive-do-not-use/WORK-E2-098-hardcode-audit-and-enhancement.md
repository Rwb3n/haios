---
template: work_item
id: E2-098
title: Hardcode Audit and Enhancement
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
last_updated: '2025-12-27T10:04:42'
---
# WORK-E2-098: Hardcode Audit and Enhancement

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Multiple scripts/hooks have hardcoded values that should be dynamic. Discovered when M3-Cycles milestone caused vitals to show 0% instead of M2's 82%.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Audit all hooks/scripts for hardcoded milestone/backlog references
- [ ] Fix any hardcoded milestone references (like M2-Governance in plan_tree.py - fixed Session 83)
- [ ] Enhance vitals to dynamically select milestone (not hardcoded)
- [ ] Document dynamic selection logic in CLAUDE.md or relevant README

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
