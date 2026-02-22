---
template: work_item
id: WORK-193
title: "Queue State Machine Invariants Design"
type: design
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: null
priority: medium
effort: medium
traces_to:
- REQ-QUEUE-001
requirement_refs: []
source_files:
- .claude/haios/lib/queue_ceremonies.py
- .claude/haios/config/work_queues.yaml
acceptance_criteria:
- "Formal state machine defined for queue positions (parked/backlog/ready/working/done)"
- "Invariants documented: parked=out-of-epoch, ready requires plan or trivial, max 1 working per agent, ready->backlog demotion allowed"
- "Enforcement mechanism designed (PreToolUse gate or WorkEngine validation)"
- "Epoch transition carry-forward rules defined"
blocked_by: []
blocks: []
enables: []
queue_position: parked  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T15:35:26
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 87528
- 87529
- 87530
- 87531
- 87532
- 87533
- 87534
- 87535
- 87536
extensions:
  epoch: E2.9
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T15:35:26
---
# WORK-193: Queue State Machine Invariants Design

---

## Context

The queue system (parked/backlog/ready/working/done) has no formal state machine or transition validation. Queue position is a frontmatter field that can be set to any value without enforcement. This leads to inconsistent states — items outside the current epoch sitting in `ready`, items without plans being worked on, multiple items in `working` simultaneously.

Operator-Hephaestus design discussion (S423) identified 5 proposed invariants:
1. Parked = out-of-epoch (epochs define scope boundaries)
2. Ready requires plan OR effort=trivial
3. Max 1 working per agent (formalize single-threaded reality)
4. Ready->backlog demotion is a valid transition (re-prioritization)
5. Enforcement via PreToolUse gate or WorkEngine method

This is E2.9 (Governance) scope — queue invariants are scope management.

---

## Deliverables

- [ ] ADR documenting queue state machine invariants and valid transitions
- [ ] Transition diagram (states + edges + guard conditions)
- [ ] Enforcement mechanism design (gate vs engine vs both)
- [ ] Epoch transition carry-forward rules

---

## History

### 2026-02-22 - Created (Session 423)
- Design discussion between operator and Hephaestus during WORK-189 closure
- Parked for E2.9 (Governance epoch)

---

## References

- @docs/work/active/WORK-179/WORK.md (related: queue-commit auto-advance)
- Memory: 87528-87536 (S423 design discussion)
- WORK-105 (original queue position implementation)
