---
template: work_item
id: WORK-125
title: "Add just queue-park recipe (reverse of queue-unpark)"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-124
chapter: null
arc: ceremonies
closed: null
priority: low
effort: small
traces_to: [REQ-QUEUE-004]
requirement_refs: []  # DEPRECATED: use traces_to instead
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-11T21:31:14
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-11
last_updated: 2026-02-11T21:31:14
---
# WORK-125: Add just queue-park recipe (reverse of queue-unpark)

---

## Context

WORK-124 added queue-prioritize, queue-commit, and queue-unpark justfile recipes but omitted queue-park (backlog -> parked). During WORK-124 testing, had to use inline Python to re-park WORK-102 after testing queue-unpark. The queue-unpark skill SKILL.md documents both directions but only unpark got a recipe. Pattern is identical to existing recipes — single line calling execute_queue_transition().

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

- [ ] Add `just queue-park {work_id} {rationale}` recipe (backlog -> parked)
- [ ] Test with a real parked/backlog item round-trip

---

## History

### 2026-02-11 - Created (Session 346)
- Spawned from WORK-124 observations: missing queue-park recipe discovered during testing

---

## References

- @justfile (queue-unpark recipe as pattern)
- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @docs/work/active/WORK-124/observations.md (source observation)
