---
template: work_item
id: WORK-104
title: Add Validation and Triage Cycle Mappings to Activity Matrix
type: feature
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: Session-316-observation
chapter: null
arc: lifecycles
closed: null
priority: low
effort: small
traces_to:
- REQ-LIFECYCLE-001
requirement_refs: []
source_files:
- .claude/haios/config/activity_matrix.yaml
acceptance_criteria:
- activity_matrix.yaml has phase_to_state entries for validation-cycle
- activity_matrix.yaml has phase_to_state entries for triage-cycle
- Mappings match template maps_to_state values
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 21:36:18
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  note: Blocked until validation-cycle and triage-cycle skills are created
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T21:36:45'
---
# WORK-104: Add Validation and Triage Cycle Mappings to Activity Matrix

---

## Context

Session 316 created validation and triage lifecycle templates with maps_to_state values in frontmatter. However, `activity_matrix.yaml` (lines 179-241) has no `phase_to_state` entries for `validation-cycle` or `triage-cycle`. When these cycles are implemented as skills, the activity matrix needs corresponding entries for governance hooks to enforce state-based rules.

**Required mappings (from template frontmatter):**

Validation cycle:
- validation-cycle/VERIFY: CHECK
- validation-cycle/JUDGE: CHECK
- validation-cycle/REPORT: CHECK

Triage cycle:
- triage-cycle/SCAN: EXPLORE
- triage-cycle/ASSESS: EXPLORE
- triage-cycle/RANK: DESIGN
- triage-cycle/COMMIT: DONE

---

## Deliverables

- [ ] Add validation-cycle phase_to_state entries to activity_matrix.yaml
- [ ] Add triage-cycle phase_to_state entries to activity_matrix.yaml
- [ ] Verify governance hooks resolve new mappings correctly

---

## History

### 2026-02-05 - Created (Session 316)
- Spawned from WORK-091/WORK-092 observation: activity_matrix missing cycle mappings

---

## References

- @.claude/haios/config/activity_matrix.yaml (target file)
- @.claude/templates/validation/ (source of maps_to_state values)
- @.claude/templates/triage/ (source of maps_to_state values)
