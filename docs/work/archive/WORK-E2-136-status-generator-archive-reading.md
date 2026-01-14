---
template: work_item
id: E2-136
title: Status Generator Archive Reading
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
last_updated: '2025-12-27T09:56:02'
---
# WORK-E2-136: Status Generator Archive Reading

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Milestone tracking shows phantom items (E2-129, E2-131, E2-116) because status generator doesn't read backlog_archive.md or backlog-complete.md.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Update status.py to read from `docs/work/archive/` in addition to `docs/work/active/`
- [ ] Fix phantom items (E2-129, E2-131, E2-116) by recognizing archived/completed work
- [ ] Milestone tracking should correctly show completed items from archive
- [ ] Verify milestone progress % is accurate after fix

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
