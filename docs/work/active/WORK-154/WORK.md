---
template: work_item
id: WORK-154
title: "Epoch Transition Validation and Queue Config Sync"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-16
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-OBSERVE-005
requirement_refs: []
source_files:
  - .claude/haios/config/work_queues.yaml
  - .claude/haios/config/haios.yaml
  - .claude/haios/lib/work_engine.py
acceptance_criteria:
  - "Epoch transition validates work_queues.yaml against active_arcs"
  - "EPOCH.md status table auto-syncs with work item closures (or validation warns on drift)"
  - "Queue config migration path documented for epoch transitions"
  - "Coldstart or session-start warns if queue config references stale epoch structures"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-16T18:45:11
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-16
last_updated: 2026-02-16T18:45:11
---
# WORK-154: Epoch Transition Validation and Queue Config Sync

---

## Context

WORK-034 (Upstream Status Propagation) addresses cascade on work closure, but a separate gap exists: epoch transition validation and queue config sync. Evidence from E2.6 triage (S383):

1. **EPOCH.md drift:** E2.6 EPOCH.md showed 5+ work items as incomplete (WORK-075, 104, 144, 146, 147, 151) that were all status:complete in their WORK.md files (85573, 85566-85568). No automated mechanism keeps EPOCH.md in sync.

2. **Queue config drift:** work_queues.yaml still pointed at E2.5 structures 3 sessions after E2.6 activation (85351, 85360). No governance gate prevents queue config staleness during epoch transitions.

3. **Epoch transition validation:** When epoch transitions happen, there's no validation that queue config, active_arcs, and work item assignments are consistent (85356).

WORK-034 solves status cascade (child→parent). This item solves epoch-level structural consistency.

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

- [ ] Epoch transition validation function (checks queue config vs active_arcs)
- [ ] EPOCH.md status sync mechanism (or drift warning in coldstart)
- [ ] Queue config migration guide for epoch transitions
- [ ] Integration with coldstart or session-start for staleness warning

---

## History

### 2026-02-16 - Created (Session 383)
- Spawned from S383 observation triage cycle (Theme 3: Epoch/Status Sync Drift)
- Complements WORK-034 (status cascade) with epoch-level structural validation
- Memory evidence: 85573, 85566-85568, 85572, 85351, 85356, 85360

---

## References

- WORK-034 (companion: upstream status propagation on work closure)
- Memory: 85573, 85566-85568, 85572, 85351, 85356, 85360 (drift evidence)
- Memory: 85609-85612 (S383 triage synthesis: session boundary gap)
