---
template: work_item
id: WORK-095
title: E2.5 Legacy Assimilation Triage
type: triage
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: Session-298-operator-request
chapter: null
arc: null
closed: '2026-02-03'
priority: high
effort: large
traces_to:
- REQ-QUEUE-001
- REQ-QUEUE-004
requirement_refs: []
source_files:
- docs/work/active/
- .claude/haios/epochs/E2_3/observations/
- .claude/haios/epochs/E2_4/observations/
acceptance_criteria:
- All legacy work items (E2-*, INV-*, TD-*, WORK-001 to ~083) triaged
- Valid concepts have fresh E2.5 work items created
- Legacy items archived with "superseded by WORK-XXX" or "obsolete" rationale
- Observations from E2_3/E2_4 harvested to memory or new work items
- Queue reflects E2.5 priorities only
blocked_by: []
blocks: []
enables:
- WORK-084
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 20:22:53
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83366
- 83367
- 83373
- 83374
- 83375
- 83376
- 83377
- 83378
- 83379
extensions:
  epoch: E2.5
  lifecycle_type: triage
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T21:01:04'
---
# WORK-095: E2.5 Legacy Assimilation Triage

---

## Context

The E2.5 epoch introduces a new architecture with independent lifecycles, orthogonal queues, and typed arcs/chapters. However, the work queue still contains ~40+ legacy items from E2.3/E2.4 eras with outdated structure:

- Old frontmatter (missing `arc`, `chapter`, `extensions.epoch`)
- Stale context and references
- Some concepts superseded by E2.5 design decisions
- Observations in prior epoch directories not harvested

**The Problem:** Legacy items pollute the queue and don't fit E2.5 structure.

**The Solution:** Triage lifecycle (SCAN → ASSESS → RANK → COMMIT):
1. SCAN all legacy items
2. ASSESS: Is the underlying need still valid?
3. For valid needs: Create NEW E2.5 work item, archive legacy as superseded
4. For obsolete: Archive with rationale
5. Harvest observations from E2_3/E2_4 to memory

---

## Deliverables

- [ ] Legacy work items scanned (E2-*, INV-*, TD-*, WORK-001 to ~083)
- [ ] Each item assessed for E2.5 relevance
- [ ] Fresh E2.5 work items created for valid concepts (proper arc/chapter mapping)
- [ ] Legacy items archived with traceability (superseded_by or obsolete rationale)
- [ ] E2_3/E2_4 observations harvested (to memory or promoted to work)
- [ ] Clean E2.5 queue with only modern work items

---

## History

### 2026-02-03 - Created (Session 298)
- Operator requested legacy assimilation for next session
- First use of Triage lifecycle type in E2.5

---

## References

- @.claude/haios/epochs/E2_5/EPOCH.md (E2.5 structure)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-*, Triage lifecycle)
- @docs/checkpoints/2026-02-03-05-SESSION-298-work-094-portability-investigation-complete.md
