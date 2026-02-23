---
template: work_item
id: WORK-207
title: Auto-Reset Stale Status on Unpark Queue Transition
type: refactor
status: complete
owner: Hephaestus
created: 2026-02-23
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: medium
effort: small
traces_to:
- REQ-QUEUE-001
- REQ-QUEUE-004
requirement_refs: []
source_files:
- .claude/haios/lib/queue_ceremonies.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- set_queue_position() auto-resets status to 'active' when transitioning parked->backlog
  if _is_actually_blocked() returns False
- Test verifies stale status=blocked with empty blocked_by is corrected on unpark
- Test verifies stale status=blocked with all-terminal blocked_by is corrected on
  unpark
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: DONE
node_history:
- node: backlog
  entered: 2026-02-23 18:04:37
  exited: '2026-02-23T20:51:18.934881'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T20:51:18.938945'
queue_history:
- position: done
  entered: '2026-02-23T20:51:18.934881'
  exited: null
---
# WORK-207: Auto-Reset Stale Status on Unpark Queue Transition

---

## Context

Retro extract from WORK-102 (S435). WORK-102 had `status: blocked` with `blocked_by: []` — stale from E2.5 parking era. queue-commit rejected the backlog->working transition with "Forbidden state combination: status=blocked + queue_position=working". Required manual Edit to fix status before queue could proceed. Cross-epoch items accumulate stale status fields when parked with blockers that are later resolved independently.

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

- [x] work_engine.py: set_queue_position() auto-resets stale blocked status on parked->backlog
- [x] Test coverage for stale status correction (empty blocked_by + all-terminal blocked_by)

---

## History

### 2026-02-23 - Implemented (Session 438)
- Added 7-line auto-reset guard in set_queue_position() before _validate_state_combination()
- Uses _is_actually_blocked() to detect stale blocked status (empty blocked_by or all-terminal blockers)
- 3 tests: empty blocked_by reset, all-terminal reset, genuinely blocked regression guard
- Discovery: _write_work_file does not persist blocked_by — tests use direct YAML frontmatter writes

### 2026-02-23 - Created (Session 435)
- Initial creation

---

## References

- Session 435 retro extract (REFACTOR-1)
- @.claude/haios/lib/queue_ceremonies.py (target file)
- Memory: 87988 (retro-extract REFACTOR-1)
