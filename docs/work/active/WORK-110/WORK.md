---
template: work_item
id: WORK-110
title: Implement Queue Ceremonies (CH-010)
type: implementation
status: active
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: CH-010
arc: queue
closed: null
priority: high
effort: medium
traces_to:
- REQ-QUEUE-004
- REQ-CEREMONY-001
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_5/arcs/queue/CH-010-QueueCeremonies.md
- .claude/haios/modules/work_engine.py
- .claude/haios/modules/governance_layer.py
acceptance_criteria:
- 'AC1: 4 new queue ceremony skills created (Unpark, Intake, Prioritize, Commit)'
- 'AC2: Each ceremony has input/output contract per REQ-CEREMONY-002'
- 'AC3: Ceremonies log QueueCeremony events to governance-events.jsonl'
- 'AC4: Unpark moves parked->backlog (and Park moves backlog->parked)'
- 'AC5: Intake creates work item at queue_position=backlog'
- 'AC6: Prioritize moves items backlog->ready with rationale'
- 'AC7: Commit moves item ready->working'
- 'AC8: Unit tests for each ceremony'
- 'AC9: Integration test: full queue lifecycle via ceremonies'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-09 19:36:31
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84155
- 84156
- 84157
- 84158
extensions: {}
version: '2.0'
generated: 2026-02-09
last_updated: '2026-02-09T20:03:32.616210'
---
# WORK-110: Implement Queue Ceremonies (CH-010)

---

## Context

CH-010 requires implementing queue ceremonies as formal skill files that govern queue state transitions. WORK-109 (CH-009) built the state machine with `QUEUE_TRANSITIONS`, `is_valid_queue_transition()`, and `validate_queue_transition()` in the governance layer. However, no ceremony skills exist to invoke these transitions in a governed way.

**Root Cause:** Queue transitions currently happen via direct `set_queue_position()` calls without ceremony boundaries. There are no skills for Unpark, Intake, Prioritize, or Commit. The Release ceremony is already handled by `close-work-cycle` (CH-008 decision).

**What exists (WORK-109 deliverables):**
- `QUEUE_TRANSITIONS` state machine (6 valid paths)
- `is_valid_queue_transition()` + `validate_queue_transition()` enforcement
- `get_parked()`, `get_by_queue_position()` query methods
- `governance-events.jsonl` logging infrastructure

**What doesn't exist:**
- `queue-unpark.md` skill (parked <-> backlog)
- `queue-intake.md` skill (create at backlog)
- `queue-prioritize.md` skill (backlog -> ready)
- `queue-commit.md` skill (ready -> working)
- QueueCeremony event type in governance-events
- Unit tests for ceremony execution

**Note:** Release ceremony (working -> done) IS `close-work-cycle` per CH-008 decision. 4 new skills needed, not 5.

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

- [ ] `queue-unpark.md` skill with input/output contract (parked <-> backlog transitions)
- [ ] `queue-intake.md` skill with input/output contract (create work at backlog)
- [ ] `queue-prioritize.md` skill with input/output contract (backlog -> ready with rationale)
- [ ] `queue-commit.md` skill with input/output contract (ready -> working)
- [ ] QueueCeremony event logging in governance-events.jsonl for all ceremony invocations
- [ ] Python ceremony module with functions: `log_queue_ceremony()`, `execute_queue_transition()`
- [ ] Unit tests for each ceremony function
- [ ] Integration test: full queue lifecycle (parked -> backlog -> ready -> working -> done) via ceremonies

---

## History

### 2026-02-09 - Created (Session 328)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-010-QueueCeremonies.md (chapter spec)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-009-QueueLifecycle.md (predecessor - state machine)
- @docs/work/active/WORK-109/WORK.md (WORK-109: Queue Lifecycle State Machine)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-004, REQ-CEREMONY-001, REQ-CEREMONY-002)
