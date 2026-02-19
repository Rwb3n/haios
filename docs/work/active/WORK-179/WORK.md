---
template: work_item
id: WORK-179
title: "Queue Commit Cycle Phase Auto-Advance Investigation"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-177
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/lib/queue_ceremonies.py
acceptance_criteria:
- "Investigation determines whether auto-advancing cycle_phase on queue commit violates the orthogonality principle (queue vs lifecycle)"
- "Clear recommendation: auto-advance, manual-only, or conditional"
- "If auto-advance recommended, spawns implementation work item"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-19T23:15:57
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T23:15:57
---
# WORK-179: Queue Commit Cycle Phase Auto-Advance Investigation

---

## Context

During WORK-177 (S407), critique-agent caught that `cycle_phase: backlog` was inconsistent with `queue_position: working` after queue commit. The `execute_queue_transition()` function in queue_ceremonies.py advances queue_position but does NOT advance cycle_phase. This creates a consistent mismatch requiring manual correction every time a work item enters the working queue.

However, CLAUDE.md declares queue and lifecycle as orthogonal: "Queue position is separate from lifecycle phase." Auto-advancing cycle_phase on queue commit would couple them. The question is whether this specific transition (backlog->plan at commit time) is a predictable co-occurrence that should be automated, or whether it violates the design principle.

Evidence: S407 WORK-177 WCBB-1, retro-kss S1, retro-extract FEATURE-1.

---

## Deliverables

- [ ] Investigation document with analysis of orthogonality principle vs practical friction
- [ ] Survey of how many times manual cycle_phase correction was needed (grep governance events)
- [ ] Clear recommendation with rationale
- [ ] If auto-advance: spawned implementation work item

---

## History

### 2026-02-19 - Created (Session 407)
- Spawned from WORK-177 retro FEATURE-1: queue commit auto-advance cycle_phase

---

## References

- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @docs/work/active/WORK-177/WORK.md (parent)
- CLAUDE.md "Queue (Orthogonal to Lifecycle)" section
