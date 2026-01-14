# generated: 2025-12-31
# System Auto: last updated on: 2025-12-31T17:22:27
# Section 17: Modular Black Box Architecture

Generated: 2025-12-31 (Session 153)
Purpose: Restructure INV-052 findings into 5 discrete modules with explicit I/O contracts
Status: DESIGN
Authority: ADR-040 (Accepted)

---

## 17.1 Module Overview

Per ADR-040, HAIOS is decomposed into 5 black-box modules:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         HAIOS MODULAR ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐                                                                │
│  │  CONTEXT        │                                                                │
│  │  LOADER         │─────────────────────────────────────┐                          │
│  │  ─────────────  │                                     │                          │
│  │  IN: coldstart  │                                     │                          │
│  │  OUT: context   │                                     ▼                          │
│  └────────┬────────┘                             ┌─────────────────┐                │
│           │                                      │  CYCLE RUNNER   │                │
│           │ grounded_context                     │  ─────────────  │                │
│           │                                      │  IN: cycle_id,  │                │
│           ▼                                      │      work_ctx   │                │
│  ┌─────────────────┐      work_id, transitions   │  OUT: phase_    │                │
│  │  WORK ENGINE    │◄───────────────────────────►│       result    │                │
│  │  ─────────────  │                             └────────┬────────┘                │
│  │  IN: work_id    │                                      │                          │
│  │  OUT: state     │                                      │ query/store              │
│  └────────┬────────┘                                      │                          │
│           │                                               ▼                          │
│           │ NodeTransitioned                     ┌─────────────────┐                │
│           │ (event)                              │  MEMORY BRIDGE  │                │
│           │                                      │  ─────────────  │                │
│           │                                      │  IN: content,   │                │
│           ▼                                      │      queries    │                │
│  ┌─────────────────┐                             │  OUT: concepts, │                │
│  │  GOVERNANCE     │◄────────────────────────────│       strategies│                │
│  │  LAYER          │      tool_events            └─────────────────┘                │
│  │  ─────────────  │                                                                │
│  │  IN: events     │                                                                │
│  │  OUT: allow/    │                                                                │
│  │       deny      │                                                                │
│  └─────────────────┘                                                                │
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  COMMUNICATION:                                                                     │
│  ───────────►  Direct call (synchronous)                                            │
│  - - - - - ►  Event (asynchronous, loose coupling)                                  │
│  ◄──────────►  Bidirectional                                                        │
│                                                                                     │
│  BOUNDARY RULES:                                                                    │
│  1. No module reads another module's owned state directly                           │
│  2. All inter-module communication via defined interfaces                           │
│  3. GovernanceLayer is passive - reacts to events, doesn't initiate                 │
│  4. MemoryBridge is the only MCP interface                                          │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 17.2 Section-to-Module Mapping

| Section | Title | Primary Module | Secondary |
|---------|-------|----------------|-----------|
| S1A | Hooks Current | GovernanceLayer | - |
| S1B | Hooks Target | GovernanceLayer | - |
| S2A | Session Lifecycle | ContextLoader | WorkEngine |
| S2B | Work Item Lifecycle | WorkEngine | - |
| S2C | Work Item Directory | WorkEngine | - |
| S2D | Cycle Extensibility | CycleRunner | - |
| S2E | Cycle Skill Analysis | CycleRunner | - |
| S2F | Cycle Definitions Schema | CycleRunner | - |
| S2G | Cycle Extension Guide | CycleRunner | - |
| S3 | State Storage | WorkEngine | - |
| S4 | Data Flow | Cross-cutting | - |
| S5 | Session Number Computation | ContextLoader | - |
| S6 | Configuration Surface | Cross-cutting | GovernanceLayer |
| S7 | Justfile Recipes | Cross-cutting | - |
| S8 | Memory Integration | MemoryBridge | - |
| S9 | Slash Commands | Cross-cutting | - |
| S10 | Skills Taxonomy | CycleRunner | - |
| S11 | Subagents | CycleRunner | GovernanceLayer |
| S12 | Invocation Paradigm | Cross-cutting | - |
| S13 | MCP Servers | MemoryBridge | - |
| S14 | Bootstrap Architecture | ContextLoader | - |
| S15 | Information Architecture | ContextLoader | - |
| S16 | Scaffold Templates | GovernanceLayer | - |

**Coverage Summary:**
| Module | Primary Sections | Count |
|--------|------------------|-------|
| ContextLoader | S2A, S5, S14, S15 | 4 |
| WorkEngine | S2B, S2C, S3 | 3 |
| CycleRunner | S2D, S2E, S2F, S2G, S10, S11 | 6 |
| MemoryBridge | S8, S13 | 2 |
| GovernanceLayer | S1A, S1B, S16 | 3 |
| Cross-cutting | S4, S6, S7, S9, S12 | 5 |

---

## 17.3 ContextLoader Module

**Responsibility:** Bootstrap the agent with L0-L3 context grounding.

### Interface

```
INPUT:
  trigger: "coldstart" | "session_recovery"

OUTPUT:
  GroundedContext:
    session_number: int
    prior_session: int | null
    l0_north_star: str           # Mission, principles
    l1_invariants: str           # Patterns, anti-patterns
    l2_operational: dict         # Status, phase, milestone
    l3_session: dict             # Checkpoint, work context
    strategies: list[Strategy]   # From memory query
    ready_work: list[WorkItem]   # From `just ready`
```

### Owned State

| File | Description |
|------|-------------|
| `.claude/config/north-star.md` | L0 context (read-only) |
| `.claude/config/invariants.md` | L1 context (read-only) |
| `.claude/config/roadmap.md` | Strategic direction |
| `docs/checkpoints/*.md` | Session history (read for session number) |

### Dependencies

| Module | Interface | Direction |
|--------|-----------|-----------|
| WorkEngine | `get_ready_items()` | calls |
| MemoryBridge | `query_strategies(mode="session_recovery")` | calls |

### Events Emitted

| Event | Payload | Consumers |
|-------|---------|-----------|
| `SessionStarted` | `{session: int, prior: int}` | GovernanceLayer |

### Source Sections

- S5: Session number computation logic
- S14: Bootstrap architecture (L0-L3 hierarchy)
- S15: Information architecture (token budgets, loading priority)
- S2A: Session lifecycle (ceremony, not state)

---

## 17.4 WorkEngine Module

**Responsibility:** Manage work item lifecycle, DAG transitions, state persistence.

### Interface

```
INPUT:
  work_id: str                   # E2-xxx or INV-xxx
  action: "create" | "transition" | "close" | "get"
  target_node?: str              # For transition: backlog|discovery|plan|implement|close

OUTPUT:
  WorkState:
    id: str
    title: str
    status: "draft" | "active" | "complete" | "blocked"
    current_node: str
    node_history: list[NodeEntry]
    memory_refs: list[int]
    documents: dict
```

### Owned State

| File | Description |
|------|-------------|
| `docs/work/active/{id}/WORK.md` | Work item state (single writer) |
| `docs/work/active/{id}/*.md` | Associated documents |
| `docs/work/archive/{id}/` | Archived work items |

### Dependencies

| Module | Interface | Direction |
|--------|-----------|-----------|
| MemoryBridge | `auto_link_refs(work_id, concept_ids)` | calls |
| GovernanceLayer | `validate_transition(from, to)` | calls |

### Events Emitted

| Event | Payload | Consumers |
|-------|---------|-----------|
| `WorkCreated` | `{id, title, node}` | GovernanceLayer |
| `NodeTransitioned` | `{id, from_node, to_node, session}` | MemoryBridge, GovernanceLayer |
| `WorkClosed` | `{id, memory_refs}` | MemoryBridge |

### Source Sections

- S2B: Work item lifecycle (DAG, node_history)
- S2C: Work item directory (self-contained universe)
- S3: State storage (WORK.md is truth)
- S4: Data flow (single writer principle)

---

## 17.5 CycleRunner Module

**Responsibility:** Execute phase-based workflows with gates.

### Interface

```
INPUT:
  cycle_id: str                  # implementation-cycle, investigation-cycle, etc.
  work_context: WorkState        # From WorkEngine
  current_phase?: str            # Resume from phase

OUTPUT:
  CycleResult:
    cycle_id: str
    final_phase: str
    outcome: "completed" | "blocked" | "chain"
    gate_results: list[GateResult]
    next_cycle?: str             # If outcome == "chain"
```

### Owned State

| File | Description |
|------|-------------|
| (in-memory) | Current phase, gate results |
| `.claude/haios/config/cycle-definitions.yaml` | Cycle schemas (read-only) |
| `.claude/skills/*/SKILL.md` | Phase prompts (read-only) |

**Note:** CycleRunner owns no persistent state. Cycle progress is derived from work item state (WorkEngine).

### Dependencies

| Module | Interface | Direction |
|--------|-----------|-----------|
| WorkEngine | `get_work_state(id)` | calls |
| WorkEngine | `transition_node(id, node)` | calls |
| MemoryBridge | `query_strategies(query)` | calls (at DO phase) |
| MemoryBridge | `store_learnings(content)` | calls (at DONE phase) |
| GovernanceLayer | `check_gate(gate_id, context)` | calls |

### Events Emitted

| Event | Payload | Consumers |
|-------|---------|-----------|
| `PhaseEntered` | `{cycle, phase, work_id}` | GovernanceLayer |
| `GatePassed` | `{gate_id, outcome}` | GovernanceLayer |
| `CycleCompleted` | `{cycle, work_id, outcome}` | WorkEngine |

### Cycle Inventory (from S10)

| Cycle | Phases | Node Binding |
|-------|--------|--------------|
| implementation-cycle | PLAN→DO→CHECK→DONE→CHAIN | implement |
| investigation-cycle | HYPOTHESIZE→EXPLORE→CONCLUDE→CHAIN | discovery |
| close-work-cycle | VALIDATE→OBSERVE→ARCHIVE→MEMORY | close |
| work-creation-cycle | VERIFY→POPULATE→READY | backlog |
| checkpoint-cycle | SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT | (none) |
| plan-authoring-cycle | GATHER→DRAFT→VALIDATE | plan |
| observation-triage-cycle | SCAN→TRIAGE→PROMOTE | (none) |

### Source Sections

- S2E: Cycle skill analysis (7 cycles normalized)
- S2F: Cycle definitions schema (YAML spec)
- S2G: Cycle extension guide
- S10: Skills taxonomy (cycles, bridges, router, utilities)
- S11: Subagents (invoked by cycles)

---

## 17.6 MemoryBridge Module

**Responsibility:** Wrap MCP tools, provide unified memory interface, handle auto-linking.

### Interface

```
INPUT (query):
  query: str
  mode: "semantic" | "session_recovery" | "knowledge_lookup"

OUTPUT (query):
  QueryResult:
    concepts: list[Concept]
    strategies: list[Strategy]
    reasoning_trace: dict

INPUT (store):
  content: str
  source_path: str
  work_id?: str                  # For auto-linking

OUTPUT (store):
  StoreResult:
    concept_ids: list[int]
    entity_ids: list[int]
    classification: str          # episteme|techne|doxa
```

### Owned State

| File | Description |
|------|-------------|
| (none) | Delegates to MCP server |

**Note:** MemoryBridge owns no state. All persistence is in `haios_memory.db` via MCP.

### Dependencies

| Module | Interface | Direction |
|--------|-----------|-----------|
| (MCP) | `memory_search_with_experience` | external |
| (MCP) | `ingester_ingest` | external |
| (MCP) | `schema_info`, `db_query` | external |
| WorkEngine | `update_memory_refs(work_id, refs)` | calls |

### Events Consumed

| Event | Source | Action |
|-------|--------|--------|
| `WorkClosed` | WorkEngine | Store final learnings |

### Auto-Linking Flow

```
ingester_ingest(content, source_path="docs/work/active/E2-150/...")
    │
    ▼
Parse work_id from source_path → "E2-150"
    │
    ▼
Store concept → concept_id
    │
    ▼
Call WorkEngine.update_memory_refs("E2-150", [concept_id])
```

### Source Sections

- S8: Memory integration (13 MCP tools)
- S13: MCP servers (haios-memory, context7)

---

## 17.7 GovernanceLayer Module

**Responsibility:** Enforce policies via hooks, validate state transitions, block forbidden operations.

### Interface

```
INPUT:
  event: ToolEvent              # PreToolUse, PostToolUse, etc.

OUTPUT:
  Decision:
    action: "allow" | "deny" | "modify"
    reason?: str
    modifications?: dict
```

### Owned State

| File | Description |
|------|-------------|
| `.claude/config/governance-toggles.yaml` | Feature flags |
| `.claude/haios/config/hook-handlers.yaml` | Handler registry |
| `.claude/haios/config/gates.yaml` | Gate definitions |
| `.claude/haios/config/node-bindings.yaml` | DAG rules |

### Dependencies

| Module | Interface | Direction |
|--------|-----------|-----------|
| (none) | - | GovernanceLayer is passive |

### Events Consumed

| Event | Source | Action |
|-------|--------|--------|
| `SessionStarted` | ContextLoader | Log session start |
| `NodeTransitioned` | WorkEngine | Validate transition, log |
| `PhaseEntered` | CycleRunner | Log governance event |
| `GatePassed` | CycleRunner | Log gate outcome |
| `WorkClosed` | WorkEngine | Trigger observation capture |

### Hook Handlers (Target: 19)

| Event | Handlers |
|-------|----------|
| PreToolUse | sql_blocking, powershell_blocking, path_governance, exit_gate_check, backlog_id_unique |
| PostToolUse | timestamp_injection, node_history_update, error_capture, template_validation, artifact_refresh, cascade_trigger, memory_refs_auto_link |
| UserPromptSubmit | date_time_inject, context_percentage, slim_status_refresh, vitals_inject |
| Stop | reasoning_bank_extract, session_summary, checkpoint_reminder |

### Source Sections

- S1A: Hooks current (22 handlers)
- S1B: Hooks target (19 handlers)
- S16: Scaffold templates (validation)

---

## 17.8 Cross-Cutting Concerns

These sections don't map cleanly to a single module:

| Section | Concern | Resolution |
|---------|---------|------------|
| S4 | Data Flow | Principle applied to all modules (single writer) |
| S6 | Configuration Surface | Each module owns its config subset |
| S7 | Justfile Recipes | Execution layer below modules (shell) |
| S9 | Slash Commands | Entry points that invoke modules |
| S12 | Invocation Paradigm | Describes how modules compose |

### Configuration Ownership

| Config File | Owning Module |
|-------------|---------------|
| north-star.md | ContextLoader |
| invariants.md | ContextLoader |
| roadmap.md | ContextLoader |
| governance-toggles.yaml | GovernanceLayer |
| hook-handlers.yaml | GovernanceLayer |
| gates.yaml | GovernanceLayer |
| node-bindings.yaml | GovernanceLayer |
| cycle-definitions.yaml | CycleRunner |
| thresholds.yaml | GovernanceLayer |

---

## 17.9 Inter-Module Event Catalog

| Event | Producer | Consumers | Payload |
|-------|----------|-----------|---------|
| SessionStarted | ContextLoader | GovernanceLayer | `{session, prior}` |
| WorkCreated | WorkEngine | GovernanceLayer | `{id, title, node}` |
| NodeTransitioned | WorkEngine | MemoryBridge, GovernanceLayer | `{id, from, to, session}` |
| WorkClosed | WorkEngine | MemoryBridge | `{id, memory_refs}` |
| PhaseEntered | CycleRunner | GovernanceLayer | `{cycle, phase, work_id}` |
| GatePassed | CycleRunner | GovernanceLayer | `{gate_id, outcome}` |
| CycleCompleted | CycleRunner | WorkEngine | `{cycle, work_id, outcome}` |

---

## 17.10 Boundary Violations (Current State)

Analysis of existing code that violates module boundaries:

| Violation | Current | Module A | Module B | Fix |
|-----------|---------|----------|----------|-----|
| Hook reads WORK.md | post_tool_use.py edits node_history | GovernanceLayer | WorkEngine | GovernanceLayer emits event, WorkEngine updates |
| Skill calls MCP directly | memory-agent calls ingester_ingest | CycleRunner | MemoryBridge | CycleRunner calls MemoryBridge interface |
| Coldstart reads work files | coldstart.md reads WORK.md | ContextLoader | WorkEngine | ContextLoader calls WorkEngine.get_ready_items() |
| Status.py reads everything | status.py scans work/, checkpoints/ | Cross-cutting | All | Status is a read-only aggregator (acceptable) |

---

## Related

- **ADR-040:** Modular Black Box Architecture (decision authority)
- **TARGET-ARCHITECTURE-DIAGRAM.md:** Visual synthesis (pre-modularization)
- **SECTIONS-INDEX.md:** Section navigation

---

*Created Session 153*
