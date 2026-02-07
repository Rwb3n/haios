---
template: work_item
id: E2-271b
title: Observations and Governance Import Cleanup
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
- E2-271a
- E2-271c
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-07 19:49:33
  exited: null
cycle_docs: {}
memory_refs:
- 81079
- 81080
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-07
last_updated: '2026-01-07T20:52:12'
---
# WORK-E2-271b: Observations and Governance Import Cleanup

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Skills contain `from observations import` and `from governance_events import` examples that cannot be executed.

**Root cause:** Skills contain aspirational documentation that was never implemented as importable modules.

**Source:** E2-271 split (Session 181), originally from INV-057

---

## Current State

Work item in BACKLOG node. Ready for implementation (inherits approved plan from E2-271).

---

## Deliverables

- [ ] Remove `from observations import` from close-work-cycle/SKILL.md OBSERVE phase
- [ ] Remove `from governance_events import` from close-work-cycle/SKILL.md MEMORY phase
- [ ] Remove `from governance_events import` from implementation-cycle/SKILL.md
- [ ] Remove `from observations import` from observation-triage-cycle/SKILL.md
- [ ] Replace with just recipes or prose instructions

---

## Affected Files (3)

| File | Change |
|------|--------|
| `.claude/skills/close-work-cycle/SKILL.md` | Replace OBSERVE and MEMORY phase Python imports |
| `.claude/skills/implementation-cycle/SKILL.md` | Replace governance event logging section |
| `.claude/skills/observation-triage-cycle/SKILL.md` | Replace SCAN phase Python import |

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
