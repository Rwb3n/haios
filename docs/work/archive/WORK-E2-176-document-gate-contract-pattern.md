---
template: work_item
id: E2-176
title: Document Gate Contract Pattern
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
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-25 08:51:27
  exited: null
cycle_docs:
  backlog: docs/plans/PLAN-E2-176-document-gate-contract-pattern.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/plans/PLAN-E2-176-document-gate-contract-pattern.md
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T14:39:01'
---
# WORK-E2-176: Document Gate Contract Pattern

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-033 discovered that skills function as node entry gates in the work cycle DAG. Two skill categories emerged:

1. **Cycle Skills** (implementation-cycle, investigation-cycle): Have gate structures with entry conditions, guardrails, and exit criteria
2. **Utility Skills** (memory-agent, audit, schema-ref): Lightweight recipe cards without phase structure

The Gate Contract pattern is implicit in existing cycle skills but not formally documented. This makes it hard to author new cycle skills consistently.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add "Gate Contract Specification" section to plugin-dev skill-development skill
- [ ] Document the three-part structure: Entry Conditions → Guardrails → Exit Criteria
- [ ] Document the two skill categories with examples
- [ ] Add guidance on when to use Cycle Skills vs Utility Skills
- [ ] Reference INV-033 findings and memory concepts 78898-78902

---

## History

### 2025-12-25 - Created (Session 116)
- Spawned from INV-033 to formalize implicit gate contract pattern

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- Memory concepts: 78898-78902
- `.claude/skills/implementation-cycle/SKILL.md` (example cycle skill)
- `.claude/skills/memory-agent/SKILL.md` (example utility skill)
