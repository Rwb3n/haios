---
template: work_item
id: WORK-179
title: Queue Commit Cycle Phase Auto-Advance Investigation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-177
spawned_children:
  - WORK-204
  - WORK-205
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/lib/queue_ceremonies.py
acceptance_criteria:
- Investigation determines whether auto-advancing cycle_phase on queue commit violates
  the orthogonality principle (queue vs lifecycle)
- 'Clear recommendation: auto-advance, manual-only, or conditional'
- If auto-advance recommended, spawns implementation work item
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-19 23:15:57
  exited: '2026-02-23T13:26:28.713254'
artifacts: []
cycle_docs: {}
memory_refs:
- 87765
- 87766
- 87767
- 87768
- 87769
- 87770
- 87771
- 87772
- 87773
- 87797
- 87798
- 87799
- 87800
extensions: {}
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-23T13:26:28.717016'
queue_history:
- position: ready
  entered: '2026-02-23T13:15:44.589812'
  exited: '2026-02-23T13:15:54.182916'
- position: working
  entered: '2026-02-23T13:15:54.182916'
  exited: '2026-02-23T13:26:28.713254'
- position: done
  entered: '2026-02-23T13:26:28.713254'
  exited: null
---
# WORK-179: Queue Commit Cycle Phase Auto-Advance Investigation

---

## Context

During WORK-177 (S407), critique-agent caught that `cycle_phase: backlog` was inconsistent with `queue_position: working` after queue commit. The `execute_queue_transition()` function in queue_ceremonies.py advances queue_position but does NOT advance cycle_phase. This creates a consistent mismatch requiring manual correction every time a work item enters the working queue.

However, CLAUDE.md declares queue and lifecycle as orthogonal: "Queue position is separate from lifecycle phase." Auto-advancing cycle_phase on queue commit would couple them. The question is whether this specific transition (backlog->plan at commit time) is a predictable co-occurrence that should be automated, or whether it violates the design principle.

Evidence: S407 WORK-177 WCBB-1, retro-kss S1, retro-extract FEATURE-1.

---

## Deliverables

- [x] Investigation document with analysis of orthogonality principle vs practical friction
- [x] Survey of how many times manual cycle_phase correction was needed (grep governance events)
- [x] Clear recommendation with rationale
- [ ] ~~If auto-advance: spawned implementation work item~~ (N/A — recommendation is do-not-implement)

---

## History

### 2026-02-23 - Investigation Complete (Session 431)
- **Recommendation: Do NOT auto-advance cycle_phase on queue commit**
- Orthogonality principle (queue separate from lifecycle) confirmed correct
- Evidence gathered: 47 Commit ceremonies, 15 active items, zero real-world mismatches
- Auto-advance not universally possible: CYCLE_PHASES covers 3/5 lifecycles (design, validation, triage have no entries)
- Auto-advance would create lib/→modules/ coupling (queue_ceremonies.py → cycle_runner.py)
- Duplicate event risk: Memory 86779 documents prior bug with multiple auto-advance triggers
- Current design works: lifecycle skills own phase transitions via just set-cycle, gap is sub-second
- No spawned work items (recommendation is do-not-implement)
- Memory: 87765-87773

### 2026-02-19 - Created (Session 407)
- Spawned from WORK-177 retro FEATURE-1: queue commit auto-advance cycle_phase

---

## References

- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @docs/work/active/WORK-177/WORK.md (parent)
- CLAUDE.md "Queue (Orthogonal to Lifecycle)" section
