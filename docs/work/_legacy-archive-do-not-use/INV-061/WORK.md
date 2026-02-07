---
template: work_item
id: INV-061
title: Svelte Governance Architecture for E2.2
status: complete
owner: Hephaestus
created: 2026-01-08
closed: 2026-01-08
milestone: null
priority: medium
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-08 19:35:07
  exited: null
cycle_docs: {}
memory_refs:
- 81123
- 81124
- 81125
- 81126
- 81127
- 81128
- 81129
- 81130
- 81131
- 81132
- 81133
- 81134
- 81135
- 81136
- 81137
- 81138
- 81139
- 81140
- 81141
- 81142
- 81143
- 81144
- 81145
- 81146
- 81147
- 81148
- 81149
- 81150
- 81151
- 81152
- 81153
- 81154
- 81155
- 81156
- 81157
- 81158
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-08
last_updated: '2026-01-08T20:05:57'
---
# WORK-INV-061: Svelte Governance Architecture for E2.2

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 182 survey revealed structural issues with Epoch 2.2 governance architecture:

1. **Portability broken:** Modules import from `.claude/lib/`, defeating standalone portability
2. **WorkEngine bloated:** 1195 lines owning too many responsibilities (CRUD, cascade, portal, spawn)
3. **ContextLoader insufficient:** Loads but doesn't survey, pause, or present options
4. **No SURVEY phase:** Session flow is all exhale - "chain chain chain" with no inhale
5. **No meta-choice:** Routing is hardcoded pattern matching, not "choose how to choose"

**Scope:** Define what "tight and svelte" governance looks like for E2.2 completion, scoping memory to Epoch 3.

---

## Hypotheses

| ID | Hypothesis | Status |
|----|------------|--------|
| H1 | Modules can be made portable by moving lib dependencies into haios/ | REFUTED - Facades acceptable for E2.2 |
| H2 | WorkEngine can be decomposed without breaking existing hooks | CONFIRMED |
| H3 | A SURVEY skill-cycle can create volumous space at session level | CONFIRMED |
| H4 | CycleRunner pattern (thin validator, Claude interprets markdown) is correct model | CONFIRMED |
| H5 | Meta-choice layer enables "choose how to choose" without adding complexity | DEFERRED - Not needed for E2.2 |

---

## Exploration Plan

- [x] Map lib/ dependencies for each module
- [x] Identify which can move, which must remain
- [x] Design WorkEngine decomposition (CascadeEngine, PortalManager, SpawnTree)
- [x] Design ContextLoader decomposition (Loader, Surveyor, Router) - DEFER (not needed for E2.2)
- [x] Sketch SURVEY skill-cycle phases
- [x] Evaluate meta-choice layer against S20 pressure dynamics - DEFER
- [x] Define "svelte" criteria (max lines per module, max responsibilities)

---

## Deliverables

- [x] Portability analysis: which lib/ imports block standalone modules
- [x] WorkEngine decomposition design
- [x] ContextLoader decomposition design - DEFER (not blocker)
- [x] SURVEY skill-cycle specification
- [x] Meta-choice layer design or rationale for deferral
- [x] "Svelte governance" criteria for E2.2 completion

---

## Findings

### H1: Portability Analysis

| Module | Lines | lib/ Imports | Portable? |
|--------|-------|--------------|-----------|
| work_engine.py | 1195 | None | YES |
| governance_layer.py | 302 | governance_events, validate, scaffold, config | NO |
| context_loader.py | 195 | status | NO |
| cycle_runner.py | 220 | governance_events, node_cycle | NO |
| memory_bridge.py | 484 | error_capture, haios_etl/* | NO |

**Verdict:** Only WorkEngine is portable. Facades are acceptable for E2.2.

### H2: WorkEngine Decomposition

WorkEngine (1195 lines) decomposes into 5 atomic modules:

1. **WorkEngine (Core)** ~300 lines - CRUD, transition, get_ready
2. **CascadeEngine** ~290 lines - cascade, unblock, related
3. **PortalManager** ~200 lines - portal CRUD, memory refs, spawned links
4. **SpawnTree** ~100 lines - tree traversal, format
5. **BackfillEngine** ~160 lines - backlog parsing, content update

### H3: SURVEY Skill-Cycle

```
SURVEY-cycle:
  GATHER     [volumous]  - What work is available? What chapters? What arcs?
  ASSESS     [volumous]  - What's the landscape? Priorities? Blockers?
  OPTIONS    [volumous]  - Present 2-3 options to operator
  CHOOSE     [tight]     - Commit to one path (gate: exactly one chosen)
  ROUTE      [tight]     - Invoke appropriate cycle skill
```

### H4: CycleRunner Pattern

CycleRunner (220 lines) is the exemplar:
- Validates gates, does NOT execute
- Claude interprets markdown prompts
- Stateless - no persistent state

### H5: Svelte Governance Criteria

| Criterion | Target |
|-----------|--------|
| Max lines per module | 300 |
| Max responsibilities | 1 |
| Max lib/ imports | 3 |
| Gates are binary | pass/fail only |
| Every cycle has [volumous] | At least one explore phase |

---

## Spawned Work

| ID | Title | Type |
|----|-------|------|
| E2-279 | WorkEngine Decomposition | Implementation |
| E2-280 | SURVEY Skill-Cycle | Implementation |
| ADR-041 | Svelte Governance Criteria | Decision |

---

## History

### 2026-01-08 - Completed (Session 183)
- All hypotheses verified
- 3/5 confirmed, 1 refuted (portability), 1 deferred (meta-choice)
- Spawned E2-279, E2-280, ADR-041

### 2026-01-08 - Created (Session 182)
- Spawned from Session 182 survey
- All 13 architecture docs reviewed
- Operator insight: "sorting algorithms... greedy... no survey step"
- Memory refs 81123-81148 capture full survey findings

---

## References

@.claude/haios/epochs/E2/EPOCH.md
@.claude/haios/epochs/E2/architecture/S17-modular-architecture.md
@.claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md
@.claude/haios/epochs/E2/architecture/S12-invocation-paradigm.md
@.claude/haios/modules/work_engine.py
@.claude/haios/modules/context_loader.py
@.claude/haios/modules/cycle_runner.py
