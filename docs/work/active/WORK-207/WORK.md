---
template: work_item
id: WORK-207
title: "Auto-Reset Stale Status on Unpark Queue Transition"
type: refactor
status: open
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-102
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
  - REQ-QUEUE-001
requirement_refs: []
source_files:
  - .claude/haios/lib/queue_ceremonies.py
acceptance_criteria:
  - "execute_queue_transition() auto-resets status to 'open' when transitioning parked->backlog if blocked_by is empty"
  - "Test verifies stale status=blocked with empty blocked_by is corrected on unpark"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-23T18:04:37
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-23
last_updated: 2026-02-23T18:04:37
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

- [ ] queue_ceremonies.py: unpark transition auto-resets stale status
- [ ] Test coverage for stale status correction

---

## History

### 2026-02-23 - Created (Session 435)
- Initial creation

---

## References

- @docs/work/active/WORK-102/WORK.md (parent retro extract)
- @.claude/haios/lib/queue_ceremonies.py (target file)
- Memory: 87988 (retro-extract REFACTOR-1)
