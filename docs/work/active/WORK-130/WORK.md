---
template: work_item
id: WORK-130
title: "Coldstart prior_session shows stale value"
type: bug
status: active
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-126
chapter: null
arc: ceremonies
closed: null
priority: low
effort: small
traces_to: [REQ-CEREMONY-001]
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
# WORK-130: Coldstart prior_session shows stale value

---

## Context

Coldstart orchestrator's SESSION CONTEXT phase shows `Prior Session: 345` instead of the actual prior session 348. The SessionLoader reads from the latest checkpoint file to determine prior session, but the S348 checkpoint (`2026-02-11-07-SESSION-348-work-127-work-128-bug-fixes.md`) wasn't picked up — possibly a filename sorting issue or the checkpoint wasn't committed before coldstart ran. Root cause likely in `session_loader.py` checkpoint discovery logic.

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

- [ ] Investigate checkpoint discovery logic in session_loader.py
- [ ] Fix prior_session to reflect actual latest session
- [ ] Verify coldstart shows correct prior session after fix

---

## History

### 2026-02-11 - Created (Session 349)
- Initial creation

---

## References

- @.claude/haios/lib/session_loader.py
- @docs/checkpoints/ (checkpoint discovery)
