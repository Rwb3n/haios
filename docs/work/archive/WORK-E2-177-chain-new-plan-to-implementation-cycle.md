---
template: work_item
id: E2-177
title: Chain new-plan to implementation-cycle
status: complete
owner: Hephaestus
created: 2025-12-25
closed: 2025-12-25
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-033
spawned_by_investigation: INV-033
blocked_by: []
blocks: []
enables: []
related: []
current_node: plan
node_history:
- node: backlog
  entered: 2025-12-25 08:51:28
  exited: '2025-12-25T14:29:05.279686'
- node: plan
  entered: '2025-12-25T14:29:05.279686'
  exited: null
cycle_docs:
  backlog: docs/plans/PLAN-E2-177-chain-new-plan-to-implementation-cycle.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/plans/PLAN-E2-177-chain-new-plan-to-implementation-cycle.md
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T14:30:49'
---
# WORK-E2-177: Chain new-plan to implementation-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-033 found that command-to-skill chaining is the gate entry mechanism, but only 2/10 commands currently chain:
- `/new-investigation` → `investigation-cycle` (added Session 116)
- `/implement` → `implementation-cycle`

The `/new-plan` command scaffolds a plan file but does NOT chain to the implementation-cycle skill. This creates an inconsistency where:
- Creating an investigation automatically enters the investigation cycle
- Creating a plan does NOT automatically enter the implementation cycle

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add "Chain to Implementation Cycle" section to `/new-plan` command
- [ ] Add `Skill(skill="implementation-cycle")` invocation after scaffolding
- [ ] Mirror the pattern used in `/new-investigation` command
- [ ] Test that plan creation chains correctly to PLAN phase

---

## History

### 2025-12-25 - Created (Session 116)
- Spawned from INV-033 to address command-skill chaining gap

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- `.claude/commands/new-investigation.md:47-62` (reference implementation)
- `.claude/commands/new-plan.md` (target file)
- `.claude/skills/implementation-cycle/SKILL.md`
