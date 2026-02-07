---
template: work_item
id: INV-047
title: Close Cycle Observation Phase Ordering
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7b-WorkInfra
priority: high
effort: small
category: investigation
spawned_by: E2-215
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- E2-217
- E2-215
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 14:43:46
  exited: null
cycle_docs: {}
memory_refs:
- 79873
- 79874
- 79875
- 79876
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T14:49:49'
---
# WORK-INV-047: Close Cycle Observation Phase Ordering

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Observation capture gate (E2-217) runs in CAPTURE phase, but `just close-work` recipe moves work item to archive/ during ARCHIVE phase. By the time CAPTURE runs, `scaffold-observations` and `validate-observations` fail because `find_work_file()` only checks active/.

**Root cause:** Phase ordering in close-work-cycle is VALIDATE -> ARCHIVE -> CAPTURE, but observations should be captured BEFORE archiving.

**Discovered:** Session 134 during E2-215 closure - scaffold-observations looked in active/ but item was already in archive/.

---

## Current State

```
Current: VALIDATE -> ARCHIVE -> CAPTURE (observation gate fails)
Target:  VALIDATE -> OBSERVE -> ARCHIVE -> MEMORY
```

Work item in BACKLOG. Design agreed with operator.

---

## Deliverables

- [ ] Add OBSERVE phase to close-work-cycle between VALIDATE and ARCHIVE
- [ ] Move observation gate logic from CAPTURE to OBSERVE
- [ ] Rename CAPTURE to MEMORY (clarity - only memory storage remains)
- [ ] Update `just close-work` to NOT include observation scaffolding (keep it pure archive mechanics)
- [ ] Test full closure flow with new ordering

---

## History

### 2025-12-28 - Created (Session 134)
- Discovered during E2-215 closure
- Design discussion with operator: Option B selected (OBSERVE as separate phase before ARCHIVE)

---

## References

- E2-215: Created just close-work recipe (where bug discovered)
- E2-217: Observation Capture Gate (original implementation)
- close-work-cycle skill: `.claude/skills/close-work-cycle/SKILL.md`
