# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T21:14:13
# L4: Functional Requirements

Derived from agent_user_requirements.md. Specifies what each module MUST do.

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
