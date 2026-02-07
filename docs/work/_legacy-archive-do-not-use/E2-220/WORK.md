---
template: work_item
id: E2-220
title: Integrate Ground Truth Verification into dod-validation-cycle
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: INV-042
spawned_by_investigation: INV-042
blocked_by: []
blocks: []
enables: []
related: []
current_node: plan-active
node_history:
- node: backlog
  entered: 2025-12-28 16:40:56
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-220/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T21:02:45'
---
# WORK-E2-220: Integrate Ground Truth Verification into dod-validation-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Plan-specific DoD criteria (Ground Truth Verification tables) are documented but not enforced. Agent can mark work complete without executing verification commands or checking verification items.

**Root cause:** dod-validation-cycle validates ADR-033 DoD (tests/WHY/docs) but doesn't read or execute plan-specific Ground Truth Verification tables.

**Solution:** Enhance dod-validation-cycle VALIDATE phase to:
1. Find associated plans for work item
2. Parse Ground Truth Verification table (via E2-219 parser)
3. Execute machine-checkable verification items
4. Report pass/fail/warning status

---

## Current State

Work item in BACKLOG node. Blocked by E2-219 (needs parser first).

---

## Deliverables

- [ ] Enhance dod-validation-cycle VALIDATE phase to include Ground Truth Verification
- [ ] Find associated plans from work item's documents.plans field
- [ ] Call E2-219 parser for each plan's Ground Truth Verification table
- [ ] Execute machine-checkable items: file-check (Read), grep-check (Grep), test-run (Bash)
- [ ] Report: X of Y checks passed, Z require manual confirmation
- [ ] BLOCK if machine-check fails, WARN if unchecked items remain
- [ ] Update dod-validation-cycle skill documentation

---

## History

### 2025-12-28 - Created (Session 136)
- Spawned from INV-042: Machine-Checked DoD Gates investigation
- Investigation confirmed integration point is dod-validation-cycle VALIDATE phase
- Blocked by E2-219 (parser) which must be implemented first

---

## References

- Spawned by: INV-042 (Machine-Checked DoD Gates)
- Design: `docs/work/active/INV-042/investigations/001-machine-checked-dod-gates.md`
- Skill to enhance: `.claude/skills/dod-validation-cycle/SKILL.md`
- Blocked by: E2-219 (Ground Truth Verification Parser)
