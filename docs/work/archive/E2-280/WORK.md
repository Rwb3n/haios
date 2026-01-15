---
template: work_item
id: E2-280
title: SURVEY Skill-Cycle Implementation
status: complete
owner: Hephaestus
created: 2026-01-08
closed: '2026-01-08'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-061
spawned_by_investigation: INV-061
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-08 20:03:07
  exited: null
cycle_docs: {}
memory_refs:
- 81149
- 81150
- 81151
- 81152
- 81153
- 81154
- 81177
- 81178
- 81179
- 81180
- 81181
- 81182
- 81183
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-08
last_updated: '2026-01-08T23:20:31'
---
# WORK-E2-280: SURVEY Skill-Cycle Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session flow is all exhale ("chain chain chain"). No volumous phase at session level before picking work.

**Root cause:** Coldstart immediately picks READY item and chains into cycle. No pause to survey landscape.

**Solution:** SURVEY skill-cycle between coldstart and work item cycles per INV-061 findings.

---

## Design (from INV-061 H3)

```
SURVEY-cycle:
  GATHER     [volumous]  - What work is available? What chapters? What arcs?
  ASSESS     [volumous]  - What's the landscape? Priorities? Blockers?
  OPTIONS    [volumous]  - Present 2-3 options to operator
  CHOOSE     [tight]     - Commit to one path (gate: exactly one chosen)
  ROUTE      [tight]     - Invoke appropriate cycle skill
```

---

## Deliverables

- [x] Create SURVEY skill-cycle SKILL.md
- [x] Implement 5 phases per design
- [x] Add pressure annotations [volumous]/[tight]
- [x] Wire into coldstart flow
- [x] Tests pass (3/3)

---

## History

### 2026-01-08 - Completed (Session 184)
- All deliverables complete
- Tests pass (3/3)
- Memory captured (concepts 81177-81182)

### 2026-01-08 - Created (Session 183)
- Spawned from INV-061 (Svelte Governance Architecture)
- Per H3 findings: SURVEY creates volumous space

---

## References

@docs/work/active/INV-061/WORK.md (status: complete)
@.claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md
@docs/ADR/ADR-041-svelte-governance-criteria.md
