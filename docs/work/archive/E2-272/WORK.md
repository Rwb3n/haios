---
template: work_item
id: E2-272
title: Add operator_decisions Field to Work Item Template
status: complete
owner: Hephaestus
created: 2026-01-05
closed: '2026-01-05'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-058
blocked_by: []
blocks:
- E2-271
enables:
- E2-273
- E2-274
- E2-275
related:
- INV-058
- E2-271
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-05 21:34:44
  exited: null
cycle_docs: {}
memory_refs:
- 80820
- 80821
- 80822
- 80823
- 80824
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-05
last_updated: '2026-01-05T22:25:44'
---
# WORK-E2-272: Add operator_decisions Field to Work Item Template

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work items can have operator decisions needed but there's no structured field to capture them. Agents must infer from prose, which is unreliable.

**Root cause:** INV-058 Finding 1 - work_item.md template has no `operator_decisions` field.

**Source:** INV-058 investigation (Session 175)

---

## Current State

Work item in BACKLOG node. First of 4 gates to implement.

---

## Deliverables

- [ ] Add `operator_decisions` field to work_item.md template frontmatter
- [ ] Document field schema (question, options, resolved, chosen)
- [ ] Update CLAUDE.md if behavioral change

---

## History

### 2026-01-05 - Created (Session 175)
- Spawned from INV-058 investigation

---

## References

- INV-058: Ambiguity Gating for Plan Authoring (source investigation)
- E2-271: Skill Module Reference Cleanup (blocked by this)
