---
template: work_item
id: E2-082
title: Dynamic Thresholds (DYNAMICS)
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
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
last_updated: '2025-12-28T11:56:20'
---
# WORK-E2-082: Dynamic Thresholds (DYNAMICS)

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Milestones are flat checkboxes (75%... 76%...). Symphony needs crescendo - building intensity as completion approaches.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [x] Add threshold logic to user_prompt_submit.py (after vitals injection) - `_get_thresholds()` at line 182
- [x] Define thresholds: milestone > 90%, stale items > 5, blocked items > 3 - lines 200-220
- [x] Create dynamic messages with prefixes: APPROACHING, ATTENTION, BOTTLENECK - all implemented
- [x] Integrate with session_delta data from E2-078 (MOMENTUM already implemented) - line 222
- [x] Test: M7d at 92% triggers "APPROACHING: M7d-Plumbing at 92%" - verified S132
- [x] Document threshold configuration in hooks README - added table

**Verified:** Session 132 saw "APPROACHING: M7d-Plumbing at 92% - 2 items to completion"

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
