---
template: work_item
id: WORK-128
title: "execute_queue_transition accepts no-op same-state transitions"
type: bug
status: active
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-125
chapter: null
arc: queue
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
    entered: 2026-02-11T21:43:51
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-11
last_updated: 2026-02-11T21:43:51
---
# WORK-128: execute_queue_transition accepts no-op same-state transitions

---

## Context

`execute_queue_transition()` in `queue_ceremonies.py` accepts transitions where from_position == to_position (e.g., `parked -> parked`). It succeeds silently and logs a QueueCeremony event for a no-op transition. Discovered during WORK-125 round-trip testing when WORK-102 was already parked but `just queue-park WORK-102 "test"` succeeded.

**Root cause:** `execute_queue_transition()` delegates to `work_engine.set_queue_position()` which doesn't validate whether the current position matches the target. No guard for same-state transitions.

**Impact:** Low — idempotent behavior is safe but logs misleading audit events (`"from": "parked", "to": "parked"`). Could mask operator errors where they think a transition happened but state was already at target.

**Fix options:**
1. Warn on same-state (log but don't block) — preserves idempotent behavior
2. Block same-state (raise ValueError) — stricter but could break scripts

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

- [ ] Add same-state guard to `execute_queue_transition()` (warn or block — operator decision)
- [ ] Add test for same-state transition behavior
- [ ] Verify no-op events are not logged (or are logged with `"no_op": true` marker)

---

## History

### 2026-02-11 - Created (Session 347)
- Discovered during WORK-125 round-trip testing with WORK-102

---

## References

- @.claude/haios/lib/queue_ceremonies.py:96 (execute_queue_transition)
- @docs/work/active/WORK-125/observations.md (source observation)
