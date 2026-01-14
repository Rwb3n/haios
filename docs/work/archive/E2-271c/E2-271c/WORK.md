---
template: work_item
id: E2-271c
title: Extract Content Deprecation Fix
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
- E2-271b
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-07 19:49:36
  exited: null
cycle_docs: {}
memory_refs:
- 81081
- 81082
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-07
last_updated: '2026-01-07T20:52:16'
---
# WORK-E2-271c: Extract Content Deprecation Fix

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** extract-content skill references deprecated `haios_etl.extraction` module.

**Root cause:** Module was moved to `.claude/lib/extraction.py` but skill documentation wasn't updated.

**Source:** E2-271 split (Session 181), originally from INV-057

---

## Current State

Work item in BACKLOG node. Ready for implementation (inherits approved plan from E2-271).

---

## Deliverables

- [ ] Replace `from haios_etl.extraction import` with correct `.claude/lib/` path
- [ ] Note MCP tool as recommended approach

---

## Affected Files (1)

| File | Change |
|------|--------|
| `.claude/skills/extract-content/SKILL.md` | Replace deprecated haios_etl reference |

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
