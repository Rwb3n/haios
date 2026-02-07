---
template: work_item
id: INV-059
title: Observation Capture Skill Isolation
status: complete
owner: Hephaestus
created: 2026-01-06
closed: '2026-01-08'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- E2-276
- E2-217
- E2-224
- INV-047
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-06 21:31:16
  exited: null
cycle_docs: {}
memory_refs:
- 81105
- 81106
- 81107
- 81108
- 81109
- 81110
- 81111
- 81112
- 81113
- 81114
- 81115
- 81116
- 81117
- 81118
- 81119
- 81120
- 81121
- 81122
- 81426
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-06
last_updated: '2026-01-08T18:46:02'
---
# WORK-INV-059: Observation Capture Skill Isolation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Observation capture is buried as OBSERVE phase inside close-work-cycle (between VALIDATE and ARCHIVE). This causes agents to treat it as a checkbox step rather than genuine reflection.

**Root cause:** When observation is sandwiched in a "closing" cycle, the agent is in completion mode - rushing to finish. The cognitive context is wrong for reflection. The mechanical gate (check boxes or add content) passes even when the agent hasn't actually reflected.

**Evidence:** Session 179 - E2-276 closure. Agent checked all "None observed" boxes without reflecting, only catching real observations (dual GroundedContext schema gap, runtime consumer ambiguity) when operator challenged.

**Proposed solution:** Extract observation capture into standalone `observation-capture-cycle` skill that is invoked with dedicated focus before close-work-cycle begins.

**Related insight (19.2):** "All investigation is work, but not all work is investigation." The current ID prefix routing (`INV-*` vs `E2-*`) conflates identity with type. Category field should drive cycle routing, not ID prefix. This investigation should consider how observation-capture-cycle fits into a unified work taxonomy.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [x] Analysis of current observation capture flow (where it happens, what triggers it)
- [x] Design for standalone observation-capture-cycle skill
- [x] Phases that enforce actual reflection (not just checkbox compliance)
- [x] Integration pattern: how close-work-cycle calls observation-capture-cycle
- [x] Recommendations for template changes (if needed)
- [x] Consider work taxonomy unification (S19.2): how does observation-capture fit into category-driven routing?

---

## Findings (Session 182)

### Hypothesis Evaluation

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| H1: Observation capture fails when embedded | **CONFIRMED** | OBSERVE phase has 4 mechanical actions with 0 volumous space. S20: "Completion bias - LLMs want to finish." |
| H2: Standalone skill forces dedicated focus | **SUPPORTED** | S20 UNIX philosophy, precedent from observation-triage-cycle |
| H3: Follow [MAY] explore → [MUST] commit | **CONFIRMED** | S20 observe-cycle template, S22 observation:recall pattern |

### Recommended Design

**observation-capture-cycle** following S22 `observation:recall` pattern:

```
Phase 1: RECALL [volumous, MAY]
- Goal: Freeform replay of what happened
- Prompt: "What happened during this work?"
- Tools: None (pure reflection)

Phase 2: NOTICE [volumous, MAY]
- Goal: Surface surprises and anomalies
- Prompt: "What surprised you?"
- Tools: None (pure reflection)

Phase 3: COMMIT [tight, MUST]
- Goal: Capture in observations.md
- Gate: validate_observations() must pass
- Tools: Edit, just validate-observations
```

### Integration Pattern

```
/close {id}
  ├── observation-capture-cycle  <-- FIRST
  │     ├── RECALL  [volumous]
  │     ├── NOTICE  [volumous]
  │     └── COMMIT  [tight]
  │
  └── close-work-cycle (modified)
        ├── VALIDATE (DoD)
        ├── ARCHIVE   <-- OBSERVE removed
        └── MEMORY
```

### Spawned Work

- **E2-278:** Create observation-capture-cycle Skill (implementation)

---

## History

### 2026-01-08 - Investigation Complete (Session 182)
- All deliverables complete
- Design validated against S20, S22 patterns
- Spawned E2-278 for implementation

### 2026-01-06 - Created (Session 179)
- Spawned from E2-276 closure where agent skipped reflection
- Operator identified design flaw: observation buried in close-work-cycle

---

## References

- `.claude/skills/close-work-cycle/SKILL.md` - Current OBSERVE phase location
- `.claude/skills/observation-triage-cycle/SKILL.md` - Related triage cycle
- `.claude/templates/observations.md` - Observation template
- `.claude/lib/observations.py` - Observation functions
- E2-217: Observation capture gate implementation
- E2-224: Observation threshold triage
- INV-047: Observation capture design (original)
- `.claude/haios/epochs/E2/architecture/S19-skill-work-unification.md` - Accumulating decisions (19.1, 19.2)
