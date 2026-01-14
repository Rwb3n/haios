---
template: work_item
id: E2-081
title: Heartbeat Scheduler (RHYTHM)
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-25
milestone: M7d-Plumbing
priority: high
effort: small
category: implementation
spawned_by: Session 78 symphony design
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
memory_refs:
- 71863
- 72474
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-25T20:20:59'
---
# WORK-E2-081: Heartbeat Scheduler (RHYTHM)

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Claude is reactive - responds to prompts, can't initiate. Symphony needs rhythm. External scheduler provides pulse.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add `just heartbeat` recipe to justfile
- [ ] Create Windows Task Scheduler task (hourly)
- [ ] Heartbeat appends to `.claude/haios-events.jsonl`
- [ ] Document: "System has pulse even without operator"

**Architecture:**
```
Windows Task Scheduler (hourly)
    │
    ▼
just heartbeat
    │
    ├── python synthesis run --quiet
    ├── just update-status
    └── Append event to haios-events.jsonl
```

**Pattern:** External rhythm compensates for Claude's reactive nature.

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
