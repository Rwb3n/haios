---
template: work_item
id: E2-143
title: "Audit Recipe Suite"
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-24
milestone: M7a-Recipes
priority: medium
effort: medium
category: implementation
spawned_by: INV-022
spawned_by_investigation: INV-022
blocked_by: []
blocks: []
enables: []
related: [INV-022, E2-140, E2-141]
current_node: plan
node_history:
  - node: plan
    entered: 2025-12-24T18:56:00
    exited: null
  - node: plan
    entered: 2025-12-24T18:56:00
    exited: null
cycle_docs:
  plan: docs/plans/PLAN-E2-143-audit-recipe-suite.md
memory_refs: []
documents:
  investigations: [INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md]
  plans: [PLAN-E2-143-audit-recipe-suite.md]
  checkpoints: [SESSION-101]
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-24T19:14:11
---
# WORK-E2-143: Audit Recipe Suite

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md

---

## Context

**Problem:** Session 101 governance audit was manual. Should have recipes to detect drift automatically.

**Root Cause:** No automated way to find:
- Status mismatches (investigation file vs archive)
- Implementation gaps (evidence exists but item still pending)
- Stale investigations (active but older than 10 sessions)

**Pattern:** Scheduled garbage collection - detect drift before it accumulates.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization for implementation.

---

## Deliverables

- [x] `just audit-sync` - compare investigation file status vs archive
- [x] `just audit-gaps` - find backlog items with implementation evidence but still pending
- [x] `just audit-stale` - find investigations older than 10 sessions still active
- [x] `.claude/lib/audit.py` - Module with parse_frontmatter, audit_sync, audit_gaps, audit_stale
- [x] `tests/test_lib_audit.py` - 6 tests, all passing

---

## History

### 2025-12-23 - Created (Session 101)
- Spawned from INV-022 (Work-Cycle-DAG investigation)
- Added to backlog as MEDIUM priority
- Related to E2-140 (investigation sync) and E2-141 (ID uniqueness)

---

## References

- **INV-022:** Work-Cycle-DAG Unified Architecture (spawned this item)
- **justfile:** Existing recipe patterns to follow
