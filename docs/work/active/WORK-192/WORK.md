---
template: work_item
id: WORK-192
title: "Spawn-Time Feasibility Check via Memory Query"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: medium
traces_to:
- REQ-OBSERVE-004
requirement_refs: []
source_files:
- .claude/skills/spawn-work-ceremony/SKILL.md
acceptance_criteria:
- "spawn-work-ceremony queries memory for prior work on the target component/topic"
- "Prior-art findings surfaced to operator before work item creation"
- "Graceful degradation if memory unavailable"
blocked_by: []
blocks: []
enables: []
queue_position: parked  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T15:20:16
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T15:20:16
---
# WORK-192: Spawn-Time Feasibility Check via Memory Query

---

## Context

spawn-work-ceremony does not check prior art before creating work items. This leads to infeasible specifications entering the backlog — e.g., WORK-189 was spawned with `context_window.used_percentage` in acceptance criteria despite E2-235 having documented that hooks don't receive context_window data 200+ sessions earlier.

A memory query at spawn time (e.g., "prior work on {component}") would surface relevant constraints and prior findings before a work item is created, catching infeasibility before it enters the backlog rather than at critique time.

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

- [ ] spawn-work-ceremony includes memory query step in POPULATE phase
- [ ] Prior-art findings surfaced before work item creation
- [ ] Graceful degradation if memory unavailable

---

## History

### 2026-02-22 - Created (Session 423)
- Extracted from WORK-189 retro-cycle (FEATURE-1)
- Parked: ergonomic improvement, low frequency, critique-agent catches the issue at PLAN phase

---

## References

- @docs/work/active/WORK-189/WORK.md (source retro extraction)
- @docs/work/active/E2-235/WORK.md (prior art that was missed)
- Memory: 87517-87525 (S423 retro-extract)
