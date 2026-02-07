# generated: 2026-01-02
# System Auto: last updated on: 2026-01-02T20:06:15
# Section 17.12: Implementation Sequence

Generated: 2026-01-02 (Session 156)
Purpose: Define module build order with dependency rationale
Status: DESIGN
Resolves: G1 (Implementation Sequence)

---

## Overview

This section defines the implementation order for the 5 HAIOS modules. The order is determined by analyzing inter-module dependencies from Section 17.3-17.7.

---

## Module Dependency Graph

```
                    ┌─────────────────────┐
                    │  GovernanceLayer    │
                    │  (passive, no deps) │
                    └──────────┬──────────┘
                               │ consumed by
                               ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  MemoryBridge   │◄───│   WorkEngine    │◄───│   CycleRunner   │
│  (MCP wrapper)  │    │  (state owner)  │    │ (orchestrator)  │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         │                      ▼                      │
         │             ┌─────────────────┐             │
         └────────────►│  ContextLoader  │◄────────────┘
                       │   (bootstrap)   │
                       └─────────────────┘

Arrow direction: A ◄─── B means "B calls A"
```

---

## Dependency Analysis

### GovernanceLayer
| Depends On | Why |
|------------|-----|
| (none) | Passive module - reacts to events, doesn't initiate |

**Dependencies from others:**
- WorkEngine calls `validate_transition(from, to)`
- CycleRunner calls `check_gate(gate_id, context)`
- All modules emit events consumed by GovernanceLayer

### MemoryBridge
| Depends On | Why |
|------------|-----|
| (MCP only) | External dependency on haios-memory MCP server |
| WorkEngine | Auto-linking: `update_memory_refs(work_id, refs)` |

**Dependencies from others:**
- ContextLoader calls `query_strategies(mode="session_recovery")`
- WorkEngine calls `auto_link_refs(work_id, concept_ids)`
- CycleRunner calls `query_strategies(query)` and `store_learnings(content)`

### WorkEngine
| Depends On | Why |
|------------|-----|
| MemoryBridge | Auto-link memory refs after ingestion |
| GovernanceLayer | Validate node transitions |

**Dependencies from others:**
- ContextLoader calls `get_ready_items()`
- CycleRunner calls `get_work_state(id)` and `transition_node(id, node)`
- MemoryBridge calls `update_memory_refs(work_id, refs)` (circular)

### ContextLoader
| Depends On | Why |
|------------|-----|
| WorkEngine | Get ready work items for routing |
| MemoryBridge | Query strategies for session recovery |

**Dependencies from others:**
- (none - entry point)

### CycleRunner
| Depends On | Why |
|------------|-----|
| WorkEngine | Get work state, trigger transitions |
| MemoryBridge | Query strategies, store learnings |
| GovernanceLayer | Gate checks during phases |

**Dependencies from others:**
- (none - orchestrates others)

---

## Implementation Sequence

Based on dependency analysis, the build order is:

### Phase 1: Foundation (No Dependencies)

**Module:** GovernanceLayer

**Rationale:**
- Passive module with no outgoing dependencies
- Other modules emit events to it, but it doesn't call others
- Can be built with stub event handlers
- Provides immediate governance value

**Deliverables:**
1. Handler registry loader (from hook-handlers.yaml)
2. Event dispatcher (route events to handlers)
3. Gate check interface (return allow/deny)
4. Stub handlers for each event type

**Test Strategy:**
- Unit tests for handler dispatch
- Gate check response validation
- Event consumption verification

---

### Phase 2: External Interface

**Module:** MemoryBridge

**Rationale:**
- Wraps external MCP server (already exists)
- Only internal dependency is WorkEngine for auto-linking (can be stubbed)
- Critical path for all memory operations

**Deliverables:**
1. MCP tool wrapper (thin facade over 13 tools)
2. Query interface with mode support (semantic, session_recovery, knowledge_lookup)
3. Store interface with classification
4. Auto-linking logic (parse work_id from source_path)

**Test Strategy:**
- Integration tests with MCP server
- Query mode behavior verification
- Auto-link parsing tests

**Dependency Handling:**
- WorkEngine.update_memory_refs() → stub initially, wire later

---

### Phase 3: State Management

**Module:** WorkEngine

**Rationale:**
- Core state owner (WORK.md is truth)
- Depends on MemoryBridge (Phase 2) and GovernanceLayer (Phase 1)
- Must be complete before orchestration layer

**Deliverables:**
1. WORK.md parser/serializer
2. Node transition logic with validation
3. node_history management
4. Work item CRUD operations
5. Ready items query (for ContextLoader)

**Test Strategy:**
- YAML frontmatter parsing tests
- Transition validation tests
- node_history append/read tests
- File system integration tests

**Dependency Wiring:**
- GovernanceLayer.validate_transition() → wire to Phase 1
- MemoryBridge.auto_link_refs() → wire to Phase 2

---

### Phase 4: Bootstrap

**Module:** ContextLoader

**Rationale:**
- Entry point for all sessions
- Depends on WorkEngine (Phase 3) and MemoryBridge (Phase 2)
- Simple composition of existing capabilities

**Deliverables:**
1. L0-L3 file loader (read manifesto corpus)
2. Session number computation (checkpoint parsing)
3. Ready work aggregation (call WorkEngine)
4. Strategy query (call MemoryBridge)
5. SessionStarted event emission

**Test Strategy:**
- File loading tests (L0-L3 presence)
- Session number calculation tests
- GroundedContext structure validation

**Dependency Wiring:**
- WorkEngine.get_ready_items() → wire to Phase 3
- MemoryBridge.query_strategies() → wire to Phase 2
- GovernanceLayer (emit SessionStarted) → wire to Phase 1

---

### Phase 5: Orchestration

**Module:** CycleRunner

**Rationale:**
- Highest-level orchestrator
- Depends on all other modules
- Must be built last

**Deliverables:**
1. Cycle definition loader (from cycle-definitions.yaml)
2. Phase executor (run phases in order)
3. Gate orchestration (invoke skills/subagents/gates)
4. Memory integration (query/store at correct phases)
5. Chaining logic (routing_gate invocation)

**Test Strategy:**
- Cycle definition parsing tests
- Phase transition tests
- Gate blocking behavior tests
- Full cycle integration tests

**Dependency Wiring:**
- WorkEngine.get_work_state() → wire to Phase 3
- WorkEngine.transition_node() → wire to Phase 3
- MemoryBridge.query_strategies() → wire to Phase 2
- MemoryBridge.store_learnings() → wire to Phase 2
- GovernanceLayer.check_gate() → wire to Phase 1

---

## Circular Dependency Resolution

**Issue:** MemoryBridge calls WorkEngine.update_memory_refs(), but WorkEngine calls MemoryBridge.auto_link_refs().

**Resolution:**
1. Build MemoryBridge (Phase 2) with stub for WorkEngine call
2. Build WorkEngine (Phase 3) with real MemoryBridge
3. Wire MemoryBridge's WorkEngine stub to real implementation

**Code Pattern:**
```python
# MemoryBridge initially:
class MemoryBridge:
    def __init__(self, work_engine=None):
        self.work_engine = work_engine  # None during Phase 2

    def auto_link_refs(self, work_id, concept_ids):
        if self.work_engine:
            self.work_engine.update_memory_refs(work_id, concept_ids)

# After Phase 3:
memory_bridge.work_engine = work_engine  # Wire the dependency
```

---

## Implementation Timeline

| Phase | Module | Est. Complexity | Key Risk |
|-------|--------|-----------------|----------|
| 1 | GovernanceLayer | Medium | Handler dispatch correctness |
| 2 | MemoryBridge | Low | MCP server stability |
| 3 | WorkEngine | High | YAML parsing edge cases |
| 4 | ContextLoader | Low | L0-L3 file format stability |
| 5 | CycleRunner | High | Gate orchestration complexity |

---

## Validation Checkpoints

After each phase, validate:

1. **Phase 1 Complete:** GovernanceLayer handles all event types, gates return decisions
2. **Phase 2 Complete:** MemoryBridge queries return results, ingestion works
3. **Phase 3 Complete:** WorkEngine creates/reads/transitions work items
4. **Phase 4 Complete:** ContextLoader produces GroundedContext with all fields
5. **Phase 5 Complete:** CycleRunner executes full implementation-cycle end-to-end

---

## Gap Resolution

**G1 Status:** DESIGNED

Implementation sequence defined:
1. GovernanceLayer (no deps, passive)
2. MemoryBridge (MCP wrapper, stub WorkEngine)
3. WorkEngine (state owner, wire deps)
4. ContextLoader (bootstrap, composition)
5. CycleRunner (orchestration, all deps)

Circular dependency between MemoryBridge and WorkEngine resolved via late binding.

---

*Created Session 156*
