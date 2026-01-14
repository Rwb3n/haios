---
template: work_item
id: E2-271
title: Skill Module Reference Cleanup
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-07'
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-057
blocked_by: []
blocks: []
enables: []
related:
- INV-057
- INV-058
- E2-272
- E2-273
- E2-274
- E2-275
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 22:28:59
  exited: null
cycle_docs: {}
memory_refs:
- 81075
- 81076
- 81077
- 81078
- 81079
- 81080
- 81081
- 81082
documents:
  investigations: []
  plans:
  - plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-07T23:20:07'
---
# WORK-E2-271: Skill Module Reference Cleanup

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Skills reference Python modules that don't exist (`routing`, `observations`, `governance_events`), causing confusion about available APIs.

**Root cause:** Skills contain aspirational documentation (code examples showing desired interfaces) that was never implemented.

**Source:** INV-057 investigation (Session 172)

---

## Current State

**SPLIT** (Session 181): Work split into 3 child items to respect 3-file threshold:
- E2-271a: Routing import cleanup (3 files)
- E2-271b: Observations/governance import cleanup (3 files)
- E2-271c: Extract content deprecation fix (1 file)

This parent item will close when all children complete.

---

## Deliverables

- [ ] Audit: List all non-existent module references in skills
- [ ] Decision: Implement modules OR remove references (operator input needed)
- [ ] If implement: Create `routing.py`, `observations.py`, `governance_events.py` in modules/
- [ ] If remove: Replace code examples with working alternatives
- [ ] Fix deprecated `haios_etl.extraction` reference in `extract-content`
- [ ] Fix direct `.claude/lib/validate.py` reference in `dod-validation-cycle`

---

## Affected Files

| Skill | Module Referenced | Status |
|-------|-------------------|--------|
| investigation-cycle | `routing` | Non-existent |
| routing-gate | `routing` | Non-existent |
| close-work-cycle | `routing`, `observations`, `governance_events` | Non-existent |
| implementation-cycle | `routing`, `governance_events` | Non-existent |
| observation-triage-cycle | `observations` | Non-existent |
| extract-content | `haios_etl.extraction` | Deprecated |
| dod-validation-cycle | `.claude/lib/validate.py` | Exists but tight coupling |

---

## History

### 2026-01-07 - Split (Session 181)
- Split into E2-271a, E2-271b, E2-271c per operator request
- 7-file scope exceeded 3-file threshold

### 2026-01-04 - Created (Session 172)
- Spawned from INV-057 investigation
- 6 skills with portability issues identified

---

## References

- INV-057: Commands Skills Templates Portability investigation
