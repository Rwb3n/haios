---
template: work_item
id: WORK-124
title: "Add justfile recipes for queue ceremonies"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-122
chapter: null
arc: ceremonies
closed: null
priority: medium
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
    entered: 2026-02-11T21:10:44
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-11
last_updated: 2026-02-11T21:10:44
---
# WORK-124: Add justfile recipes for queue ceremonies

---

## Context

Queue ceremony module (queue_ceremonies.py) has execute_queue_transition() but no justfile recipes to invoke it. WorkEngine requires full governance init, making direct Python calls impractical. In S345, queue-commit for WORK-122 had to bypass the ceremony module entirely (direct frontmatter edit) because there's no `just queue-commit`, `just queue-prioritize`, or `just queue-unpark` recipe. This defeats the purpose of the queue ceremony infrastructure built in CH-010.

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

- [ ] Add `just queue-prioritize {work_id} {rationale}` recipe (backlog -> ready)
- [ ] Add `just queue-commit {work_id}` recipe (ready -> working)
- [ ] Add `just queue-unpark {work_id} {rationale}` recipe (parked -> backlog)
- [ ] Verify recipes invoke queue_ceremonies.execute_queue_transition() correctly

---

## History

### 2026-02-11 - Created (Session 345)
- Spawned from WORK-122 observations: queue ceremony bypass discovered during queue-commit attempt

---

## References

- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @.claude/skills/queue-commit/SKILL.md
- @docs/work/active/WORK-122/observations.md (source observation)
