---
template: work_item
id: E2-241
title: Implement MemoryBridge Module
status: complete
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-03
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-053
blocked_by:
- E2-240
blocks:
- E2-242
enables:
- E2-242
related:
- INV-052
- INV-053
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 13:07:55
  exited: null
cycle_docs: {}
memory_refs:
- 80534
- 80535
- 80536
- 80537
- 80538
- 80539
- 80540
documents:
  investigations: []
  plans:
  - docs/work/active/E2-241/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T16:10:07'
---
# WORK-E2-241: Implement MemoryBridge Module

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Memory integration (MCP server calls, query modes, auto-linking) is scattered across codebase with direct MCP calls.

**Root cause:** Organic growth without module boundary. INV-052 designed MemoryBridge; INV-053 validated it.

**Goal:** Create black-box MemoryBridge module wrapping haios-memory MCP server. Swappable for different memory backends (local DB, external service, different MCP).

---

## Current State

Work item in BACKLOG node. Phase 2 of implementation sequence (depends on E2-240).

---

## Deliverables

- [ ] MemoryBridge module in `.claude/haios/modules/memory_bridge.py`
- [ ] MCP tool facade (thin wrapper over 13 tools)
- [ ] Query interface with mode support (semantic, session_recovery, knowledge_lookup)
- [ ] Store interface with classification
- [ ] Auto-linking logic (parse work_id from source_path)
- [ ] Typed callback for WorkEngine integration
- [ ] Unit tests in `tests/test_memory_bridge.py`
- [ ] Integration tests with MCP server

---

## History

### 2026-01-03 - Created (Session 158)
- Spawned from INV-053 (HAIOS Modular Architecture Review)
- Phase 2 of implementation sequence (blocked by E2-240)

---

## References

- INV-052: HAIOS Architecture Reference (design source)
- INV-053: HAIOS Modular Architecture Review (spawn source)
- docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md (module spec)
- docs/work/active/INV-052/SECTION-17.12-IMPLEMENTATION-SEQUENCE.md (Phase 2)
