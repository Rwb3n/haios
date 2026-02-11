---
template: work_item
id: WORK-131
title: "cycle_phase stays backlog when items skip plan-authoring"
type: bug
status: active
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-126
chapter: null
arc: queue
closed: null
priority: medium
effort: medium
traces_to: [REQ-QUEUE-001]
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
    entered: 2026-02-11T22:33:27
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-11
last_updated: 2026-02-11T22:33:27
---
# WORK-131: cycle_phase stays backlog when items skip plan-authoring

---

## Context

When work items skip plan-authoring (e.g., small bug fixes that go directly to implementation), the `cycle_phase` field stays at `backlog` throughout the entire lifecycle and is never updated. WORK-127 and WORK-128 both closed with `cycle_phase: backlog`. Root cause: `just set-cycle` updates a transient governance state but does NOT update the WORK.md `cycle_phase` field. The `cycle_phase` field is only written by `_write_work_file()` which copies from `work.cycle_phase` — but nothing sets `work.cycle_phase` during informal bug-fix flows. Either `set-cycle` should update WORK.md, or `close()` should set `cycle_phase: done`.

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

- [ ] Investigate: should set-cycle update WORK.md or should close() set cycle_phase: done?
- [ ] Implement chosen approach
- [ ] Verify closed items show cycle_phase: done (not backlog)

---

## History

### 2026-02-11 - Created (Session 349)
- Initial creation

---

## References

- @.claude/haios/modules/work_engine.py (close, _write_work_file)
- @justfile (set-cycle recipe)
- S348 checkpoint drift note: cycle_phase not updated during informal bug-fix flow
