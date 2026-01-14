---
template: architecture_decision_record
status: accepted
date: 2025-12-31
adr_id: ADR-040
title: HAIOS Modular Black Box Architecture
author: Hephaestus
session: 153
lifecycle_phase: decide
decision: accepted
spawned_by: INV-052
related:
- ADR-033
- ADR-039
milestone: M7b-WorkInfra
memory_refs: []
version: '1.1'
generated: '2025-12-31'
last_updated: '2025-12-31T17:20:07'
---
# ADR-040: HAIOS Modular Black Box Architecture

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-31
> **Decision:** Accepted (Session 153)

---

## Context

INV-052 produced comprehensive architecture documentation across 16 sections covering hooks, lifecycles, state, data flow, commands, skills, agents, memory, and bootstrap. While thorough, the design is **descriptive** (documenting what exists) rather than **prescriptive** (defining how to build cleanly).

The current architecture suffers from:
- **Coupling:** Everything connects to everything (hooks touch state, skills invoke agents, cycles depend on memory)
- **Unclear boundaries:** No explicit contracts between subsystems
- **Testing difficulty:** Hard to test one component in isolation
- **Portability risk:** LLM-specific code mixed with core logic

---

## Decision Drivers

- **Testability:** Each module should be testable in isolation
- **Portability:** Core HAIOS logic should work across LLM platforms (Claude, Gemini, etc.)
- **Clarity:** New contributors should understand boundaries without reading 16 documents
- **Maintainability:** Changes to one module shouldn't cascade unpredictably
- **Incremental adoption:** Can implement module-by-module, not big-bang

---

## Considered Options

### Option A: Black Box Modules with Explicit I/O

**Description:** Define 5 discrete modules with explicit input/output contracts. Each module owns its state and communicates through defined interfaces.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CONTEXT        │     │  WORK ENGINE    │     │  MEMORY         │
│  LOADER         │     │                 │     │  BRIDGE         │
│  ─────────────  │     │  ─────────────  │     │  ─────────────  │
│  IN: coldstart  │     │  IN: work_id    │     │  IN: content    │
│  OUT: grounded  │────►│  OUT: state     │◄───►│  OUT: concepts  │
│       context   │     │       changes   │     │       strategies│
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       ▼                       │
        │               ┌─────────────────┐             │
        │               │  CYCLE RUNNER   │             │
        │               │  ─────────────  │             │
        └──────────────►│  IN: cycle_id   │◄────────────┘
                        │  OUT: phase     │
                        │       result    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  GOVERNANCE     │
                        │  LAYER          │
                        │  ─────────────  │
                        │  IN: events     │
                        │  OUT: allow/    │
                        │       deny      │
                        └─────────────────┘
```

**Pros:**
- Clear boundaries - each box has defined I/O
- Testable - mock inputs, verify outputs
- Portable - core modules don't depend on Claude CLI specifics

**Cons:**
- May require refactoring existing code
- Event coordination between modules adds complexity

### Option B: Layered Architecture (Clean Architecture)

**Description:** Organize into concentric layers with strict dependency direction (outer depends on inner, never reverse).

```
┌─────────────────────────────────────────┐
│  PRESENTATION (Commands, Skills)        │
├─────────────────────────────────────────┤
│  APPLICATION (Cycles, Routing)          │
├─────────────────────────────────────────┤
│  DOMAIN (Work Items, Sessions, Gates)   │
├─────────────────────────────────────────┤
│  INFRASTRUCTURE (Hooks, MCP, Files)     │
└─────────────────────────────────────────┘
```

**Pros:**
- Well-known pattern
- Clear dependency direction

**Cons:**
- Doesn't fit prompt-based execution well
- HAIOS is more event-driven than request-response

### Option C: Event-Driven Bounded Contexts

**Description:** Define independent contexts that communicate via events only.

**Pros:**
- Maximum decoupling
- Each context is self-contained

**Cons:**
- Event choreography complexity
- Harder to trace execution flow

### Option D: Pipeline Architecture

**Description:** Model as linear data transformation pipeline.

**Pros:**
- Simple mental model

**Cons:**
- Doesn't capture recursive/looping nature of cycles

---

## Decision

**Adopt Option A: Black Box Modules with Explicit I/O**, incorporating event communication from Option C for loose coupling.

### The 5 Modules

| Module | Responsibility | Owns | Inputs | Outputs |
|--------|---------------|------|--------|---------|
| **ContextLoader** | Bootstrap, L0-L3 grounding | north-star.md, invariants.md, coldstart sequence | `/coldstart` trigger | Grounded context dict |
| **WorkEngine** | Work item lifecycle, DAG | WORK.md, node_history | work_id, node transition | State changes, events |
| **CycleRunner** | Cycle execution, phases, gates | Cycle state (in-memory) | cycle_id, work context | Phase results, gate outcomes |
| **MemoryBridge** | MCP wrapper, auto-linking | None (delegates to MCP) | content, queries | concepts, strategies |
| **GovernanceLayer** | Hooks, validation, enforcement | governance-toggles.yaml | tool events | allow/deny, modifications |

### Communication Pattern

Modules communicate via:
1. **Direct calls** for synchronous operations (ContextLoader → WorkEngine)
2. **Events** for loose coupling (WorkEngine emits `NodeTransitioned`, MemoryBridge consumes for auto-linking)

### Boundary Rules

1. **No module reads another module's owned state directly**
2. **All inter-module communication via defined interfaces**
3. **GovernanceLayer is passive** - reacts to events, doesn't initiate
4. **MemoryBridge is the only MCP interface** - other modules don't call MCP directly

---

## Consequences

**Positive:**
- Clear contracts enable unit testing
- Portability: swap ContextLoader for Gemini version, core unchanged
- Onboarding: "Here are 5 boxes, here's what each does"
- Incremental: Can refactor one module at a time

**Negative:**
- Refactoring effort to extract clean boundaries
- Some natural coupling becomes explicit (more code)
- Event tracing requires tooling

**Neutral:**
- Design documentation shifts from 16 sections to 5 module specs
- Implementation items from INV-052 gap analysis need re-scoping to modules

---

## Implementation

- [ ] Create SECTION-17-MODULAR-ARCHITECTURE.md in INV-052 with detailed module specs
- [ ] Define I/O contracts for each module (TypedDict or dataclass)
- [ ] Identify current code that violates boundaries
- [ ] Spawn implementation items per module (E2-xxx)
- [ ] Update CLAUDE.md quick reference with module mental model

---

## References

- INV-052: HAIOS Architecture Reference (source analysis)
- ADR-033: Work Item Lifecycle Governance
- ADR-039: Work Item as File Architecture

---
