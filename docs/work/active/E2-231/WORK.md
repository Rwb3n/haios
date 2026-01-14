---
template: work_item
id: E2-231
title: Add just validate-refs Recipe
status: active
owner: Hephaestus
created: 2025-12-29
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-040
spawned_by_investigation: INV-040
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-29 10:55:17
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-29
last_updated: '2025-12-29T10:55:49'
---
# WORK-E2-231: Add just validate-refs Recipe

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Consumer Verification Gap Pattern - migrations change path patterns but consumer files (skills, agents, commands) retain stale references. E2-212 was closed with "Verify zero stale references" incomplete, leaving 10+ files with outdated `docs/plans/PLAN-{id}-*.md` paths.

**Root Cause:** Close workflow has no automated gate; consumer verification is manual and easily skipped (Ceremonial Completion anti-pattern).

**Solution:** INV-040 investigation found: dod-validation-cycle already has grep-check mechanism; a standalone `just validate-refs` recipe provides flexibility while integration with dod provides enforcement.

---

## Current State

Work item in BACKLOG node. Spawned from INV-040 investigation.

---

## Deliverables

- [ ] Add `validate_stale_refs()` function to `.claude/lib/dependencies.py`
- [ ] Define common stale patterns (legacy `docs/plans/PLAN-*`, old work file patterns like `WORK-{id}-*.md`)
- [ ] Add `just validate-refs` recipe to justfile
- [ ] Document in CLAUDE.md governance section
- [ ] Integration: warn (not block) behavior initially

---

## History

### 2025-12-29 - Created (Session 143)
- Spawned from INV-040 investigation (Automated Stale Reference Detection)
- INV-040 findings: layered approach recommended (standalone + dod integration)

---

## References

- Spawned by: INV-040 (Automated Stale Reference Detection)
- Related: E2-228 (Add just validate-deps Recipe) - different scope (skill/agent refs)
- Related: E2-212 (Work Directory Structure Migration) - original trigger
- Memory: 77088 (Ceremonial Completion anti-pattern), 77093 (consumer grep MUST)
