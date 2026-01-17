---
template: work_item
id: E2-253
title: MemoryBridge Implementation - MCP Integration
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: high
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by:
- E2-251
blocks: []
enables:
- E2-254
- E2-255
related:
- E2-241
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 23:21:49
  exited: null
cycle_docs:
  backlog: docs/work/active/E2-253/plans/PLAN.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-253/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-17T15:32:02'
---
# WORK-E2-253: MemoryBridge Implementation - MCP Integration

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md

---

## Context

**Problem:** MemoryBridge (E2-241) is a **STUB ONLY** - `_call_mcp()` raises NotImplementedError. Hooks bypass modules entirely, using `haios_etl.*` directly.

**Scope (from INV-052 S17.5):**
- S8: Memory Integration - **Not implemented**
- S13: MCP Servers - **Not implemented**

**Current hook code to migrate:**
- `.claude/hooks/memory_retrieval.py` → uses haios_etl.retrieval
- `.claude/hooks/reasoning_extraction.py` → uses haios_etl.database

**Key decision:** MemoryBridge wraps MCP tools, OR wraps haios_etl directly?

---

## IMPORTANT: Recursive Adjustment Note

This work item requires **recursive scope tightening** during implementation:
1. Query memory for prior decisions on MCP vs direct DB access
2. Determine if hooks should use MemoryBridge or call MCP directly
3. Query rewriting (E2-063) may need to move into MemoryBridge
4. Adjust deliverables based on actual hook requirements
5. This is highest-effort item - may need splitting

---

## Deliverables

- [ ] Implement `_call_mcp()` to actually call MCP tools
- [ ] Add query rewriting to MemoryBridge (from memory_retrieval.py)
- [ ] Migrate `memory_retrieval.py` to use MemoryBridge
- [ ] Migrate `reasoning_extraction.py` to use MemoryBridge
- [ ] Tests for MCP integration
- [ ] Verify runtime consumers exist (E2-250 DoD criterion)

---

## History

### 2026-01-03 - Created (Session 162)
- Part of Epoch 2.2 full migration plan
- Spawned from INV-052 Section 17 analysis
- S162 discovery: MemoryBridge._call_mcp() is NotImplementedError

---

## References

- `docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` - Module design
- `.claude/haios/modules/memory_bridge.py` - Current stub
- `.claude/hooks/memory_retrieval.py` - To migrate
- `.claude/hooks/reasoning_extraction.py` - To migrate
- `haios_etl/retrieval.py` - Current implementation
