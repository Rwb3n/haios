---
template: work_item
id: WORK-096
title: Agent UX Test in DoD Validation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: WORK-095
chapter: CH-041
arc: observability
closed: '2026-02-15'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-003
requirement_refs: []
source_files:
- .claude/skills/dod-validation-cycle/SKILL.md
- .claude/skills/dod-validation-cycle/README.md
- docs/ADR/ADR-033-work-item-lifecycle.md
acceptance_criteria:
- Optional Agent UX Test criterion added to dod-validation-cycle
- Trigger conditions defined for new components
- 4-question checklist in validation output
- ADR-033 updated with optional criteria section
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 20:39:11
  exited: '2026-02-15T23:58:49.384209'
artifacts: []
cycle_docs: {}
memory_refs:
- 85559
- 85560
- 85561
- 85562
- 85563
- 85564
- 85575
extensions:
  epoch: E2.6
  lifecycle_type: implementation
  supersedes: E2-249
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-15T23:58:49.386209'
queue_history:
- position: done
  entered: '2026-02-15T23:58:49.384209'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-096: Agent UX Test in DoD Validation

---

## Context

**Problem:** Current DoD (ADR-033) doesn't include Agent UX Test, so new components can ship without meeting agent usability requirements.

**Root cause:** L3 Agent Usability Requirements section was added after DoD was created.

**Goal:** Add optional Agent UX Test criterion to dod-validation-cycle for new components (commands, skills, agents, modules).

**Supersedes:** E2-249 (archived - same concept, fresh E2.5 structure)

---

## Deliverables

- [ ] Add optional "Agent UX Test" criterion to dod-validation-cycle skill
- [ ] Define trigger conditions (when to apply: new components only)
- [ ] Add 4-question checklist to validation output
- [ ] Update ADR-033 with optional criteria section

---

## History

### 2026-02-03 - Created (Session 299)
- Supersedes E2-249 from E2.5 Legacy Assimilation Triage (WORK-095)
- Mapped to ceremonies arc (REQ-CEREMONY-003: ceremony contracts)

---

## References

- @docs/work/active/E2-249/WORK.md (superseded - to be archived)
- @docs/ADR/ADR-033-work-item-lifecycle-governance.md
- @.claude/haios/manifesto/L3-requirements.md (Agent UX Test)
