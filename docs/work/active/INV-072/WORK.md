---
template: work_item
id: INV-072
title: Spawn ID Collision - Completed Work Items Reused
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-26
spawned_by: null
chapter: null
arc: null
closed: '2026-01-26'
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 21:31:33
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 77290
- 79940
- 82467
- 82468
- 82469
- 82474
- 82475
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-26T21:32:08'
---
# INV-072: Spawn ID Collision - Completed Work Items Reused

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-294 was already COMPLETED in Session 196 (title: "Wire implementation-cycle and investigation-cycle with set-cycle"). In Session 245, when E2-236 spawned follow-up work, the spawn logic reused E2-294 instead of creating a new ID.

**Evidence:**
- `git show 921c8c3:docs/work/active/E2-294/WORK.md` shows `current_node: complete` and different title
- Current WORK.md (commit fe17c99) shows `current_node: backlog` with new title "Wire Session Event Logging into Lifecycle"
- PLAN.md was never updated - still contains Session 196 set-cycle wiring plan

**Root cause:** Spawn logic does not check if a work item ID is already complete before reusing it.

**Related prior work:**
- Memory 77290: "ID collision where two files can have the same backlog_id (e.g., two INV-011 files existed in Session 101)"
- Memory 79940: "Gap: Old INV-042 investigation file collision in docs/investigations/"

---

## Deliverables

- [ ] Identify spawn logic location (which module/function allocates IDs)
- [ ] Document ID allocation algorithm (how does it decide to reuse vs create new?)
- [ ] Find all instances of completed work items that were reused
- [ ] Propose fix: spawn MUST check status before reusing ID
- [ ] Immediate mitigation: decide how to handle E2-294 (restore vs new ID)

---

## History

### 2026-01-26 - Created (Session 246)
- Discovered during survey-cycle when E2-294 PLAN.md didn't match WORK.md
- Confirmed via git history comparison

---

## References

- @docs/work/active/E2-294/WORK.md (victim of collision)
- @docs/work/active/E2-294/plans/PLAN.md (stale from Session 196)
- @docs/work/active/E2-236/WORK.md (parent that spawned with wrong ID)
