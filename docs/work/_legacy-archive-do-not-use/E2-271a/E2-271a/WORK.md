---
template: work_item
id: E2-271a
title: Routing Import Cleanup
status: complete
owner: Hephaestus
created: 2026-01-07
closed: '2026-01-07'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: E2-271
spawned_by_investigation: INV-057
blocked_by: []
blocks: []
enables: []
related:
- E2-271
- E2-271b
- E2-271c
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-07 19:49:30
  exited: null
cycle_docs: {}
memory_refs:
- 81075
- 81076
- 81077
- 81078
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-07
last_updated: '2026-01-07T20:51:28'
---
# WORK-E2-271a: Routing Import Cleanup

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Skills contain `from routing import` examples that cannot be executed because the routing module isn't in Python path.

**Root cause:** Skills contain aspirational documentation (code examples showing desired interfaces) that was never implemented as importable modules.

**Source:** E2-271 split (Session 181), originally from INV-057

---

## Current State

Work item in BACKLOG node. Ready for implementation (inherits approved plan from E2-271).

---

## Deliverables

- [ ] Remove `from routing import` from routing-gate/SKILL.md
- [ ] Remove `from routing import` from implementation-cycle/SKILL.md CHAIN phase
- [ ] Remove `from routing import` from investigation-cycle/SKILL.md CHAIN phase
- [ ] Replace with prose decision tables

---

## Affected Files (3)

| File | Change |
|------|--------|
| `.claude/skills/routing-gate/SKILL.md` | Remove Python import section, replace with prose usage |
| `.claude/skills/implementation-cycle/SKILL.md` | Replace CHAIN phase Python import with decision table |
| `.claude/skills/investigation-cycle/SKILL.md` | Replace CHAIN phase Python import with decision table |

---

## History

### 2026-01-07 - Created (Session 181)
- Split from E2-271 to respect 3-file threshold
- Inherits design from E2-271 plan

---

## References

- E2-271: Parent work item (Skill Module Reference Cleanup)
- E2-271 PLAN.md: Detailed design for changes
- INV-057: Source investigation
