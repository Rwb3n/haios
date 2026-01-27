# generated: 2026-01-24
# System Auto: last updated on: 2026-01-27T23:16:25
# L4: Functional Requirements

Level: L4
Status: DYNAMIC (evolves with implementation)
Derived from: L3 principles + agent_user_requirements.md

---

## Requirement ID Registry (Master)

*All L4 requirements with bidirectional traceability to L3*

| ID | Domain | Description | Derives From | Implemented By |
|----|--------|-------------|--------------|----------------|
| REQ-TRACE-001 | Traceability | Work items include `traces_to:` field | L3.7, L3.11 | WORK.md template |
| REQ-TRACE-002 | Traceability | Work creation validates `traces_to:` | L3.7, L3.15, L3.18 | work-creation-cycle |
| REQ-TRACE-003 | Traceability | Close validates requirement addressed | L3.7, L3.18 | close-work-cycle |
| REQ-TRACE-004 | Traceability | Work items MUST trace to existing chapter file | L3.7, L3.11 | WorkEngine.get_ready() |
| REQ-TRACE-005 | Traceability | Full chain: L4 → Epoch → Arc → Chapter → Work | L3.7 | work-creation-cycle |
| REQ-CONTEXT-001 | Context | Coldstart MUST inject prior session context | L3.3, L3.16 | ColdstartOrchestrator |
| REQ-CONTEXT-002 | Context | Files are context windows for next node | L3.3 | Gate output files |
| REQ-CONTEXT-003 | Context | Memory refs MUST be queried on document load | L3.3, L3.14 | Memory refs rule |
| REQ-GOVERN-001 | Governance | Gates MUST block invalid transitions | L3.1, L3.15 | GovernanceLayer |
| REQ-GOVERN-002 | Governance | Irreversible actions require explicit permission | L3.5, L3.8 | PreToolUse hooks |
| REQ-GOVERN-003 | Governance | SQL queries MUST use schema-verifier | L3.2, L3.13 | PreToolUse hook |
| REQ-MEMORY-001 | Memory | Store learnings with provenance | L3.3, L3.7 | MemoryBridge |
| REQ-MEMORY-002 | Memory | Query before deciding (retrieval over generation) | L3.2, L3.14 | memory-agent skill |
| REQ-WORK-001 | Work | Work items track lifecycle via node_history | L3.1, L3.7 | WorkEngine |
| REQ-WORK-002 | Work | Status over location (ADR-041) | L3.1 | Work item structure |
| REQ-VALID-001 | Validation | Work creation MUST validate ID availability against terminal statuses | L3.1, L3.5 | WorkEngine, scaffold.py |
| REQ-VALID-002 | Validation | Scaffold templates MUST produce files with all required fields populated | L3.2 | scaffold.py |
| REQ-VALID-003 | Validation | Plan validation MUST check for unresolved decisions before DO phase | L3.1, L3.15 | plan-validation-cycle Gate 4 |

*Registry grows as requirements are enumerated from L3 principles.*

---

## Traceability Requirements

*Derived from L3.7 (Traceability) + L3 LLM Nature (enforcement principle)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-TRACE-001** | Work items MUST include `traces_to:` field in frontmatter | L3.7, L3.11 | WORK.md template includes field |
| **REQ-TRACE-002** | Work creation MUST validate `traces_to:` references a valid requirement ID | L3.7, L3.15, L3.18 | `work-creation-cycle` blocks on empty/invalid `traces_to:` |
| **REQ-TRACE-003** | Close-work-cycle MUST verify the traced requirement was addressed | L3.7, L3.18 | DoD validation includes requirement satisfaction check |
| **REQ-TRACE-004** | Work items MUST trace to an existing chapter file. No chapter → BLOCKED. | L3.7, L3.11 | `WorkEngine.get_ready()` filters items without chapter file |
| **REQ-TRACE-005** | Full traceability chain MUST exist: L4 Requirement → Epoch → Arc → Chapter → Work Item | L3.7 | `work-creation-cycle` validates chain before READY |

**Invariants:**
- Traceability is governance, not documentation (enforcement over enablement)
- Invalid requirement IDs MUST block, not warn
- Requirement IDs follow pattern: `REQ-{DOMAIN}-{NNN}` (e.g., `REQ-TRACE-001`)
- **No chapter file → work item BLOCKED** (REQ-TRACE-004)
- **Orphan work items are invalid** - every work item must trace up to L4 (REQ-TRACE-005)

---

## Validation Requirements

*Derived from L3.1 (Certainty Ratchet) + L3.5 (Reversibility) + L3.2 (Evidence Over Assumption)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-VALID-001** | Work creation MUST validate ID availability against terminal statuses (complete/archived) | L3.1, L3.5 | `create_work()` raises on ID with terminal status |
| **REQ-VALID-002** | Scaffold templates MUST produce files with all required fields populated (no `{{PLACEHOLDER}}` in output) | L3.2 | Scaffolded files pass template validation |
| **REQ-VALID-003** | Plan validation MUST check Open Decisions for `[BLOCKED]` entries before DO phase | L3.1, L3.15 | plan-validation-cycle Gate 4 blocks on unresolved decisions |

**Invariants:**
- Validation is enforcement, not documentation (L3.15: enforcement over enablement)
- Terminal status collision MUST block, not warn (data loss is irreversible)
- REQ-VALID-002 supersedes scaffold recipes — `/new-*` commands are the governed path

---

## Module Function Specifications

### GovernanceLayer

**Purpose:** Policy enforcement, gate checks, transition validation.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `check_gate(gate_id, context)` | Gate ID + work context | `GateResult(allowed, reason)` | Returns deny for incomplete DoD |
| `validate_transition(from_node, to_node)` | DAG nodes | `bool` | Blocks invalid transitions (e.g., backlog→complete) |
| `load_handlers(config_path)` | Path to components.yaml | Handler registry | Loads all registered handlers |
| `on_event(event_type, payload)` | Event + data | Side effects | Routes to correct handlers |

**Invariants:**
- MUST NOT modify work files directly (that's WorkEngine's job)
- MUST log all gate decisions for audit
- MUST be stateless (no internal state between calls)

---

### MemoryBridge

**Purpose:** Wrap haios-memory MCP, provide query modes, auto-link.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `query(query, mode)` | Search string + mode | List of concepts | Returns relevant concepts for "session recovery" |
| `store(content, source_path)` | Content + provenance | Concept IDs | Creates concepts with correct classification |
| `auto_link(work_id, concept_ids)` | Work ID + refs | Updated WORK.md | Adds memory_refs to frontmatter |

**Query Modes:**
- `semantic`: Pure similarity search
- `session_recovery`: Excludes synthesis, for coldstart
- `knowledge_lookup`: Filters to episteme/techne

**Invariants:**
- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)

---

### WorkEngine

**Purpose:** Own WORK.md, manage lifecycle, single source of truth.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_work(id)` | Work ID | WorkState object | Returns parsed WORK.md |
| `create_work(id, title, ...)` | Work item data | Created file path | Creates directory + WORK.md |
| `transition(id, to_node)` | Work ID + target node | Updated WorkState | Updates current_node, appends node_history |
| `get_ready()` | None | List of unblocked items | Returns items where blocked_by is empty |
| `archive(id)` | Work ID | Archived path | Moves to docs/work/archive/ |

**Invariants:**
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

---

### ConfigLoader

**Purpose:** Unified config loading with domain organization.

| File | Required Sections | Acceptance Test |
|------|-------------------|-----------------|
| `haios.yaml` | manifest, toggles, thresholds | Loads without error, toggles accessible |
| `cycles.yaml` | node_bindings | Node bindings parseable |
| `components.yaml` | skills, agents, hooks | Registries accessible |

**Invariants:**
- MUST be valid YAML (schema validation on load)
- MUST return empty dict on missing files (graceful degradation)

---

### ContextLoader

**Purpose:** Role-based context loading for coldstart and agent bootstrap.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `load_context(role)` | Role name | ContextResult | Returns loaded content for role |
| `register_loader(name, loader_class)` | Loader registration | None | Loader callable for role |

**Invariants:**
- MUST use config-driven loader selection (haios.yaml roles section)
- MUST support custom loaders via registration

---

### CycleRunner

**Purpose:** Phase execution and cycle chaining.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_cycle_phases(cycle_id)` | Cycle ID | Phase list | Returns phases for known cycles |
| `set_cycle(cycle, phase, work_id)` | Cycle state | Session state updated | State persists |

**Invariants:**
- MUST be stateless (state stored in session_state, not runner)

---

## Testing Requirements

### Unit Tests (per module)

| Module | Test File | Key Tests |
|--------|-----------|-----------|
| GovernanceLayer | `tests/test_governance_layer.py` | Gate blocking, transition validation |
| MemoryBridge | `tests/test_memory_bridge.py` | Query modes, auto-link parsing |
| WorkEngine | `tests/test_work_engine.py` | CRUD, transitions, node_history |
| Config | `tests/test_config.py` | YAML loading, schema validation |
| ContextLoader | `tests/test_context_loader.py` | Role loading, loader registration |

### Integration Tests

| Test | Modules | Scenario |
|------|---------|----------|
| `test_work_lifecycle.py` | All | Create -> transition -> archive |
| `test_memory_integration.py` | MemoryBridge + WorkEngine | Store -> auto-link -> verify refs |
| `test_governance_gates.py` | GovernanceLayer + WorkEngine | Transition blocked by gate |

### Acceptance Criteria (DoD per module)

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] **Runtime consumer exists** (something outside tests imports/calls the code)
- [ ] Typed interfaces (Protocol classes)
- [ ] Docstrings on public methods

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used.

---

## References

- @agent_user_requirements.md (source)
- @technical_requirements.md (implementation mapping)
