---
template: work_item
id: E2-236
title: Orphan Session Detection and Recovery
status: active
owner: Hephaestus
created: 2025-12-30
closed: null
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 20:19:18
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2025-12-30T20:19:56'
---
# WORK-E2-236: Orphan Session Detection and Recovery

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** When context exhausts or connection drops, there's no automatic recovery: no session-end is logged, no checkpoint is created, and work may be lost (not committed).

**Root cause:** No crash detection mechanism exists. Session state assumes clean session-end will always happen.

**Source:** INV-052 Issue 5 (No Crash Recovery)

---

## Current State

Work item created from INV-052 findings. Ready for implementation.

---

## Deliverables

- [ ] Add function to detect orphaned sessions in `.claude/lib/status.py`
- [ ] Check events for "start without end" pattern (session N started, no end logged, session N+1 started)
- [ ] Log synthetic session-end for orphaned session on coldstart
- [ ] Optionally create recovery checkpoint with what's known
- [ ] Test recovery with simulated crash scenarios

---

## History

### 2025-12-30 - Created (Session 150)
- Initial creation

---

## References

- [Related documents]
