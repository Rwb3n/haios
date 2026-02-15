---
template: work_item
id: WORK-150
title: Plan Decomposition Traceability ADR
type: design
status: complete
owner: Hephaestus
created: 2026-02-14
spawned_by: WORK-097
spawned_children: []
chapter: CH-038
arc: traceability
closed: '2026-02-15'
priority: medium
effort: small
traces_to:
- REQ-ASSET-003
- REQ-ASSET-004
- REQ-ASSET-005
requirement_refs: []
source_files: []
acceptance_criteria:
- ADR documents spawn_type field design
- ADR documents plan decomposition_map section
- ADR documents computable trigger thresholds
- ADR records case study evidence from E2-292
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-14 14:49:15
  exited: '2026-02-15T23:28:52.605517'
artifacts:
- docs/ADR/ADR-046-plan-decomposition-traceability.md
cycle_docs: {}
memory_refs:
- 85545
- 85546
- 85547
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-14
last_updated: '2026-02-15T23:28:52.608523'
queue_history:
- position: ready
  entered: '2026-02-15T23:14:04.799362'
  exited: '2026-02-15T23:14:04.828039'
- position: working
  entered: '2026-02-15T23:14:04.828039'
  exited: '2026-02-15T23:28:52.605517'
- position: done
  entered: '2026-02-15T23:28:52.605517'
  exited: null
---
# WORK-150: Plan Decomposition Traceability ADR

---

## Context

WORK-097 investigated plan decomposition traceability and designed a pattern. This ADR formalizes three decisions:

1. **spawn_type field:** Decomposition is spawning with a type tag, not a separate concept
2. **decomposition_map:** Plans that get split include a step-to-child mapping section
3. **computable triggers:** Thresholds checked at plan-validation time, not DO phase

---

## Deliverables

- [ ] ADR document created (docs/ADR/ADR-XXX-plan-decomposition-traceability.md)
- [ ] spawn_type enum values documented with usage criteria
- [ ] decomposition_map section format specified
- [ ] Trigger thresholds with SHOULD/MAY levels
- [ ] CLAUDE.md updated if needed

---

## History

### 2026-02-14 - Created (Session 368)
- Spawned from WORK-097 Plan Decomposition Traceability investigation

---

## References

- @docs/work/active/WORK-097/WORK.md (spawn source)
- @docs/work/active/E2-292/WORK.md (case study)
- Memory: 85325, 85331 (WORK-097 findings)
