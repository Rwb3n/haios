---
template: work_item
id: E2-278
title: Create observation-capture-cycle Skill
status: complete
owner: Hephaestus
created: 2026-01-08
closed: '2026-01-08'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-059
spawned_by_investigation: INV-059
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-08 18:44:35
  exited: null
cycle_docs: {}
memory_refs:
- 81159
- 81160
- 81161
- 81162
- 81163
- 81164
- 81165
- 81166
- 81167
- 81168
- 81169
- 81170
- 81171
- 81172
- 81173
- 81174
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-08
last_updated: '2026-01-08T18:45:05'
---
# WORK-E2-278: Create observation-capture-cycle Skill

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Observation capture is buried as OBSERVE phase inside close-work-cycle, causing agents to treat it as a checkbox step rather than genuine reflection. When an agent is in "completion mode" (rushing to close), it doesn't inhabit volumous reflection space.

**Evidence:** Session 179 - Agent checked all "None observed" boxes without reflecting. INV-059 confirmed: current OBSERVE phase has 4 mechanical actions with 0 volumous space.

**Solution:** Extract observation capture into standalone skill invoked BEFORE close-work-cycle.

---

## Current State

Work item in BACKLOG node. Spawned from INV-059 investigation.

---

## Deliverables

- [ ] Create `.claude/skills/observation-capture-cycle/SKILL.md` with 3-phase structure
- [ ] Implement RECALL phase [volumous, MAY] - freeform replay
- [ ] Implement NOTICE phase [volumous, MAY] - surface surprises
- [ ] Implement COMMIT phase [tight, MUST] - capture in observations.md
- [ ] Update close-work-cycle to remove OBSERVE phase (lines 66-129)
- [ ] Update /close command to chain observation-capture-cycle → close-work-cycle
- [ ] Add tests for new skill

---

## History

### 2026-01-08 - Created (Session 182)
- Spawned from INV-059 Observation Capture Skill Isolation investigation
- Design based on S22 observation:recall pattern and S20 pressure dynamics

---

## References

- INV-059: Source investigation with full design rationale
- `.claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md` - Phase pressure design
- `.claude/haios/epochs/E2/architecture/S22-skill-patterns.md` - observation:recall pattern
- `.claude/haios/epochs/E2/architecture/S19-skill-work-unification.md` - Section 19.1
- `.claude/skills/close-work-cycle/SKILL.md` - Current OBSERVE phase to remove
- `.claude/lib/observations.py` - Validation functions
