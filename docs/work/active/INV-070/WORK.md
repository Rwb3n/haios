---
template: work_item
id: INV-070
title: Queue Ready Filter Bug - Complete Items Returned
status: dismissed
owner: Hephaestus
created: 2026-01-18
closed: '2026-01-18'
milestone: null
priority: critical
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-18 12:08:30
  exited: null
cycle_docs: {}
memory_refs:
- 81521
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-18
last_updated: '2026-01-18T21:56:50'
---
# WORK-INV-070: Queue Ready Filter Bug - Complete Items Returned

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `WorkEngine.get_ready()` returns work items with `status: complete`, polluting the queue with 10 already-closed items. This causes the survey-cycle to present completed work as options.

**Trigger:** Session 203 - `just queue default` showed E2-234 (closed 2026-01-17) as first item.

**Root Cause:** `get_ready()` only checks `blocked_by` is empty, but does not filter out `status: complete` items.

**Location:** `.claude/haios/modules/work_engine.py:278-296`

**Current buggy logic:**
```python
if work and not work.blocked_by:
    ready.append(work)  # Missing: and work.status != 'complete'
```

**Impact:** 10 of 50 "ready" items are actually complete. Queue is 20% polluted.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.
-->

- [x] Identify root cause of status filtering gap
- [x] Fix `get_ready()` to exclude `status: complete` items
- [x] Verify queue shows only active items after fix
- [x] Add test coverage for status filtering

---

## History

### 2026-01-18 - Fixed (Session 203)
- Identified bug: `get_ready()` missing status check at work_engine.py:294
- Fix: Added `and work.status != "complete"` to filter condition
- Added test: `test_get_ready_excludes_complete_items`
- Queue: 50→41 items (10 complete items removed)

---

## References

- @.claude/haios/modules/work_engine.py - Location of `get_ready()` bug
- Memory concept 78866: "Track complete items by status field" - confirms expected behavior
