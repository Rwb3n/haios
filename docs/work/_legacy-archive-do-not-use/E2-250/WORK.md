---
template: work_item
id: E2-250
title: Chariot Module Integration - Wire WorkEngine to Runtime
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-03'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- E2-240
- E2-241
- E2-242
current_node: implement
node_history:
- node: backlog
  entered: 2026-01-03 19:27:28
  exited: '2026-01-03T19:28:23.544856'
- node: implement
  entered: '2026-01-03T19:28:23.544856'
  exited: '2026-01-03T19:32:40.059805'
- node: close
  entered: '2026-01-03T19:32:40.059805'
  exited: '2026-01-03T19:49:44.375791'
- node: implement
  entered: '2026-01-03T19:49:44.375791'
  exited: null
cycle_docs:
  implement: docs/checkpoints/test.md
memory_refs:
- 80601
- 80602
- 80603
- 80604
- 80605
documents:
  investigations: []
  plans:
  - docs/work/active/E2-250/WORK.md
  checkpoints:
  - docs/checkpoints/test.md
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T22:04:15'
---
# WORK-E2-250: Chariot Module Integration - Wire WorkEngine to Runtime

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The 3 Chariot modules (GovernanceLayer, MemoryBridge, WorkEngine) are built and tested but have ZERO runtime consumers. All hooks, just recipes, and skills still use the old `.claude/lib/` code paths.

**Root Cause:** "Complete" was defined as "code exists and tests pass" not "integrated and being used." The strangler fig pattern was designed but never planted.

**Evidence (Session 162 discovery):**
- `grep "from.*\.claude\.haios\.modules"` returns empty - nothing imports the modules
- justfile uses `work_item.py` directly via inline python
- Hooks use `haios_etl.database` and `haios_etl.retrieval`

**Impact:** The 2.2 architecture exists on paper but doesn't run the system. Future sessions inherit documentation that describes intent, not reality.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [x] Update `just node` to use `WorkEngine.transition()`
- [x] Update `just link` to use `WorkEngine.add_document_link()`
- [x] Update `just link-spawn` to use `WorkEngine.link_spawned_items()`
- [x] Update `just close-work` to use `WorkEngine.close()`
- [x] Verify all existing tests still pass (19 passed for WorkEngine + CLI)
- [x] Add integration test that proves WorkEngine is called at runtime
- [x] DoD framework updated with "Runtime consumer exists" criterion

---

## History

### 2026-01-03 - Full Integration Complete (Session 162 continued)
- Added `add_document_link()` and `link_spawned_items()` to WorkEngine
- Added `link` and `link-spawn` CLI commands
- Updated justfile: now 4 recipes use WorkEngine via CLI
- All tests pass (19 for WorkEngine + CLI)
- **Runtime consumers verified:** just node, just link, just link-spawn, just close-work

### 2026-01-03 - DoD Framework Update (Session 162)
- Added "Runtime consumer exists" to L4 DoD (L4-implementation.md)
- Added to implementation_plan template DoD section
- Added to CLAUDE.md quick reference table
- Stored learning to memory (concepts 80601-80605)
- **Principle:** "Tests pass" ≠ "Code is used". Modules without consumers are prototypes.

### 2026-01-03 - Module Wiring (Session 162)
- Created CLI entry point `.claude/haios/modules/cli.py`
- Updated `just node` to use WorkEngine.transition()
- Updated `just close-work` to use WorkEngine.close()
- Added WorkEngine.close() method for atomic close operation
- Added `close -> implement` transition for rework cases
- Created integration tests `tests/test_modules_cli.py`
- **Key insight:** The modules were built but not wired - this session planted the strangler fig

### 2026-01-03 - Created (Session 162)
- Initial creation from coldstart discovery

---

## References

- `.claude/haios/modules/work_engine.py` - The module to wire in
- `.claude/lib/work_item.py` - The old code to replace/facade
- `justfile:39-53` - The 4 recipes that need updating
- Session 162 discovery grep results
