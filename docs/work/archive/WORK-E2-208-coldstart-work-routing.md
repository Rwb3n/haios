---
template: work_item
id: E2-208
title: Coldstart Work Routing
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: high
effort: small
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
  entered: 2025-12-27 14:35:24
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T16:07:34'
---
# WORK-E2-208: Coldstart Work Routing

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Coldstart gathers comprehensive context (checkpoint, status, memory) but stops at summary output. Agent waits for human to say "work on X" instead of auto-routing to work.

**Root Cause:** coldstart.md ends with "provide a brief summary" and lists "Key pending items" as informational only. No MUST instruction to pick and begin work.

**Evidence:** coldstart.md:45-51

---

## Current State

Work item in BACKLOG node. Ready for implementation.

---

## Deliverables

- [ ] Add MUST instruction to coldstart.md: "Pick highest-priority unblocked item from `just ready` and invoke appropriate cycle"
- [ ] Add routing logic based on work item type (investigation vs implementation)

---

## History

### 2025-12-27 - Created (Session 127)
- Initial creation

---

## References

- [Related documents]
