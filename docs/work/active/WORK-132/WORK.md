---
template: work_item
id: WORK-132
title: close() does not close node_history last exited timestamp
type: bug
status: complete
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-126
chapter: null
arc: queue
closed: '2026-02-11'
priority: low
effort: small
traces_to:
- REQ-QUEUE-001
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-11 22:33:27
  exited: '2026-02-11T22:45:43.045137'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-11
last_updated: '2026-02-11T22:45:43.047646'
queue_history:
- position: done
  entered: '2026-02-11T22:45:43.045137'
  exited: null
---
# WORK-132: close() does not close node_history last exited timestamp

---

## Context

`WorkEngine.close()` sets `status: complete` and `queue_position: done` but does NOT close the last `node_history` entry's `exited` timestamp. The last entry stays `exited: null` after closure. This creates an asymmetry with the new `queue_history` (WORK-126) which properly closes the last entry on close. Also causes `scan_incomplete_work()` to report false positives based on `exited: null` pattern. Fix: add `node_history[-1]["exited"] = now` in `close()` before `_write_work_file()`, mirroring the queue_history pattern.

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

- [ ] Add `node_history[-1]["exited"] = now` in close() before _write_work_file()
- [ ] Add test: close() sets node_history last entry exited timestamp
- [ ] Verify scan_incomplete_work no longer flags closed items

---

## History

### 2026-02-11 - Created (Session 349)
- Initial creation

---

## References

- @.claude/haios/modules/work_engine.py (close method, line ~586)
- @.claude/haios/lib/governance_events.py (scan_incomplete_work)
- WORK-126 critique A7: pre-existing gap, now visible alongside queue_history
