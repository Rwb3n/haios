---
template: work_item
id: E2-249
title: Agent UX Test in DoD
status: archived
owner: Hephaestus
created: 2026-01-03
closed: 2026-02-03
archive_reason: Superseded by WORK-096 during E2.5 Legacy Assimilation Triage (WORK-095)
superseded_by: WORK-096
milestone: M7b-WorkInfra
priority: low
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: INV-055
arc: pipeline
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 18:32:04
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-02-03T20:40:39'
---
# WORK-E2-249: Agent UX Test in DoD

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Current DoD (ADR-033) doesn't include Agent UX Test, so new components can ship without meeting agent usability requirements.

**Root cause:** L3 Agent Usability Requirements section was just added; DoD predates it.

**Goal:** Add optional Agent UX Test criterion to dod-validation-cycle for new components (commands, skills, agents, modules).

---

## Current State

Work item in BACKLOG node. Low priority - existing components pass most tests.

---

## Deliverables

- [ ] Add optional "Agent UX Test" criterion to dod-validation-cycle skill
- [ ] Define trigger conditions (when to apply: new components only)
- [ ] Add 4-question checklist to validation output
- [ ] Update ADR-033 with optional criteria section

---

## History

### 2026-01-03 - Created (Session 161)
- Spawned from INV-055: Agent Usability Requirements Detailing
- H3 confirmed: DoD lacks agent usability check

---

## References

- INV-055: Agent Usability Requirements Detailing (spawn source)
- L3-requirements.md: Agent UX Test (lines 104-113)
- ADR-033: Work Item Lifecycle Governance
