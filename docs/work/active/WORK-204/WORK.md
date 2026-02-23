---
template: work_item
id: WORK-204
title: Chapter Manifest Auto-Update on Work Closure
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-179
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: medium
effort: small
traces_to:
- REQ-TRACE-004
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- WorkEngine.close() auto-updates parent chapter CHAPTER.md work items table (status
  -> Complete)
- 'Fail-permissive: chapter update failure never blocks closure'
- Test verifies chapter manifest updated after work closure
- Test verifies closure succeeds without error when chapter file is missing or chapter
  field is empty
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-23 13:38:35
  exited: '2026-02-23T14:54:31.404496'
artifacts: []
cycle_docs: {}
memory_refs:
- 87789
- 87826
- 87839
- 87840
- 87841
- 87842
- 87843
- 85322
- 87844
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T14:54:31.409306'
queue_history:
- position: parked
  entered: '2026-02-23T13:40:34.647345'
  exited: '2026-02-23T13:59:58.780051'
- position: backlog
  entered: '2026-02-23T13:59:58.780051'
  exited: '2026-02-23T14:21:10.096291'
- position: ready
  entered: '2026-02-23T14:21:10.096291'
  exited: '2026-02-23T14:21:10.368223'
- position: working
  entered: '2026-02-23T14:21:10.368223'
  exited: '2026-02-23T14:54:31.404496'
- position: done
  entered: '2026-02-23T14:54:31.404496'
  exited: null
---
# WORK-204: Chapter Manifest Auto-Update on Work Closure

---

## Context

During WORK-179 investigation (S431), CH-059 CHAPTER.md had WORK-200 listed as "Active" despite completion in S430. WORK-177 (S407) solved the creation side — `scaffold_template()` auto-updates chapter manifest when a work item is created with a `chapter` field. But the closure side has no equivalent: `WorkEngine.close()` sets `status: complete` and `queue_position: done` but does not update the parent chapter's CHAPTER.md work items table.

This creates progressive drift: each closure without chapter update increases manual reconciliation burden. The fix mirrors WORK-177's creation-side pattern — add fail-permissive chapter manifest update to `close()`.

Evidence: WORK-179 retro WDN-1, retro-extract FEATURE-1 (mem:87789).

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

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] Chapter manifest update function in WorkEngine.close() (fail-permissive)
- [x] Test verifying chapter CHAPTER.md status updated on work closure
- [x] Test verifying graceful failure when chapter file missing

---

## History

### 2026-02-23 - Implemented (Session 432)
- Added update_chapter_manifest_status() and _try_update_chapter_manifest_status() to scaffold.py
- Integrated into WorkEngine.close() via lazy import (fail-permissive)
- 3 new tests, 108 total pass, zero debug cycles (TDD RED-GREEN)

### 2026-02-23 - Created (Session 431)
- Spawned from WORK-179 retro-cycle EXTRACT FEATURE-1
- Mirrors WORK-177 (creation-side auto-update) for the closure side

---

## References

- @.claude/haios/modules/work_engine.py (close method, target for change)
- @docs/work/active/WORK-177/WORK.md (creation-side equivalent, reference pattern)
- @docs/work/active/WORK-179/WORK.md (parent investigation)
- Memory: 87789 (retro-extract FEATURE-1)
