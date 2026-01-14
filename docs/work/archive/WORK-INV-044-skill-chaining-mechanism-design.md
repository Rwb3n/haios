---
template: work_item
id: INV-044
title: Skill Chaining Mechanism Design
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: high
effort: small
category: investigation
spawned_by: E2-209
spawned_by_investigation: null
blocked_by: []
blocks:
- E2-209
enables:
- E2-209
related:
- INV-041
- E2-210
current_node: discovery
node_history:
- node: backlog
  entered: 2025-12-27 18:43:50
  exited: '2025-12-27T18:44:50.765701'
- node: discovery
  entered: '2025-12-27T18:44:50.765701'
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T18:56:35'
---
# WORK-INV-044: Skill Chaining Mechanism Design

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-209 proposes adding a CHAIN phase to cycle skills, but the mechanism is undefined. How does one skill invoke another? How does work routing work?

**Questions to Answer:**
1. How does a skill "auto-invoke" another skill? (Skill tool? Prompt injection? Hook?)
2. What triggers the chain? (Phase completion? Explicit instruction?)
3. How does "route to next work" work? (Query `just ready`? Work queue?)
4. Does this require skill architecture changes or just skill content changes?

**Background:** INV-041 identified the gap (skills don't chain). E2-209 proposes the solution (add CHAIN phase). This investigation designs the mechanism.

---

## Current State

Work item in BACKLOG node. Ready for investigation.

---

## Deliverables

- [ ] Document current skill invocation patterns (how does Skill tool work?)
- [ ] Design CHAIN phase mechanism (what triggers it, what it does)
- [ ] Design work routing mechanism (how to pick next work item)
- [ ] Assess impact on existing skills (implementation-cycle, investigation-cycle, close-work-cycle)
- [ ] Spawn updated E2-209 with concrete implementation spec

---

## History

### 2025-12-27 - Created (Session 129)
- Spawned to design mechanism before E2-209 implementation
- E2-209 identified WHAT to do, this investigates HOW

---

## References

- Related: INV-041 (Autonomous Session Loop Gap Analysis) - identified the gap
- Blocks: E2-209 (Cycle Skill Chain Phases) - implementation
- Related: E2-210 (Context Threshold Auto-Checkpoint) - parallel autonomous loop work
