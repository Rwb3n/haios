# generated: 2026-01-03
# System Auto: last updated on: 2026-02-04T21:12:23
# HAIOS Modules

Core modules for HAIOS Chariot Architecture (L4-implementation.md).

## Overview

This directory contains the black-box modules that form the HAIOS runtime:

| Module | Status | Lines | Purpose |
|--------|--------|-------|---------|
| `governance_layer.py` | Implemented (E2-240) | ~350 | Policy enforcement, gate checks, transition validation |
| `memory_bridge.py` | Implemented (E2-241, E2-253) | ~450 | MCP wrapper, query modes, auto-link |
| `work_engine.py` | Refactored (E2-242, E2-279) | ~585 | Work file ownership, lifecycle management (core CRUD) |
| `cascade_engine.py` | Extracted (E2-279) | ~387 | Completion cascade, unblock, milestone tracking |
| `portal_manager.py` | Extracted (E2-279) | ~230 | Portal REFS.md management |
| `spawn_tree.py` | Extracted (E2-279) | ~170 | Spawn tree traversal and formatting |
| `backfill_engine.py` | Extracted (E2-279) | ~220 | Backlog content backfill |
| `context_loader.py` | Implemented (E2-254) | ~300 | L0-L4 context loading, session tracking |
| `cycle_runner.py` | Implemented (E2-255) | ~350 | Phase gate validation, cycle phase lookup |
| `requirement_extractor.py` | Implemented (WORK-015) | ~390 | Extract requirements from TRDs, manifesto, prose |
| `corpus_loader.py` | Implemented (WORK-031) | ~180 | YAML-configurable file discovery for RequirementExtractor |
| `planner_agent.py` | Implemented (WORK-032) | ~300 | PLAN stage: RequirementSet → WorkPlan with groupings and dependencies |

## GovernanceLayer (E2-240)

Stateless policy enforcement module.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `check_gate(gate_id, context)` | Gate ID + work context | `GateResult(allowed, reason, degraded)` |
| `validate_transition(from_node, to_node)` | DAG nodes | `bool` |
| `load_handlers(config_path)` | Path to components.yaml | Handler registry dict |
| `on_event(event_type, payload)` | Event + data | Side effects (handler calls) |
| `validate_template(file_path)` | Path to template file | Validation result dict (E2-252) |
| `scaffold_template(template, ...)` | Template type + options | Path to created file (E2-252) |
| `get_toggle(name, default)` | Toggle name + optional default | Toggle value from haios.yaml (E2-260) |

### Gates

| Gate ID | Context Keys | Purpose |
|---------|--------------|---------|
| `dod` | tests_pass, why_captured, docs_current | Definition of Done validation |
| `preflight` | plan_approved, file_count | Plan readiness before DO phase |
| `observation` | pending_observations, max_observations | Observation threshold check |

### DAG Transitions

Valid transitions are defined in `VALID_TRANSITIONS`:
- backlog -> discovery, plan
- discovery -> backlog, plan
- plan -> backlog, implement
- implement -> plan, close
- close -> complete
- complete -> (terminal)

### GateResult Dataclass

```python
@dataclass
class GateResult:
    allowed: bool     # Whether the gate permits the operation
    reason: str       # Human-readable explanation
    degraded: bool = False  # E2-248: Indicates governance system degradation
```

### Error Visibility (E2-248)

Exception handlers log warnings instead of silent failure:
- `load_handlers`: Logs YAML parse errors with config path
- `on_event`: Logs handler exceptions with event type

This enables agents to detect governance degradation via logs.

### Invariants

- MUST NOT modify work files directly (that's WorkEngine's job)
- MUST log all gate decisions for audit (via governance_events)
- MUST be stateless (no internal state between calls)
- MUST log exceptions for visibility (E2-248) instead of silent failure

### Usage

```python
from governance_layer import GovernanceLayer, GateResult

layer = GovernanceLayer()

# Check a gate
result = layer.check_gate("dod", {
    "work_id": "E2-240",
    "tests_pass": True,
    "why_captured": True,
    "docs_current": True
})
if result.allowed:
    print("Gate passed")
else:
    print(f"Blocked: {result.reason}")

# Validate a transition
if layer.validate_transition("backlog", "discovery"):
    print("Transition allowed")

# Validate a template file (E2-252)
result = layer.validate_template("docs/checkpoints/checkpoint.md")
if result["is_valid"]:
    print(f"Valid: {result['template_type']}")
else:
    print(f"Errors: {result['errors']}")

# Scaffold a new document (E2-252)
path = layer.scaffold_template(
    template="checkpoint",
    backlog_id="164",
    title="Session Checkpoint"
)
print(f"Created: {path}")

# Get toggle value (E2-260)
if layer.get_toggle("block_powershell"):
    print("PowerShell commands are blocked")
```

## MemoryBridge (E2-241, E2-253)

Stateless memory abstraction module. Wraps haios_etl for memory operations.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `query(query, mode, space_id)` | Search string + mode + optional space | `QueryResult(concepts, reasoning)` |
| `store(content, source_path, content_type_hint)` | Content + path + optional hint | `StoreResult(concept_ids, classification, error)` |
| `auto_link(work_id, concept_ids)` | Work ID + concept list | None (calls callback) |
| `_rewrite_query(query)` | Raw query | Rewritten technical query (E2-253) |
| `is_actual_error(tool_name, tool_response)` | Tool name + response dict | bool (E2-261) |
| `capture_error(tool_name, error_message, tool_input)` | Tool + error + input | Result dict (E2-261) |
| `extract_learnings(transcript_path)` | Path to transcript JSONL | `LearningExtractionResult` (E2-262) |

### Constructor Parameters (E2-253)

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `work_engine_callback` | Callable | None | Callback for auto-linking |
| `db_path` | Path | haios_memory.db | Path to memory database |
| `api_key` | str | GOOGLE_API_KEY env | API key for embeddings/rewriting |
| `enable_rewriting` | bool | True | Enable query rewriting for better retrieval |

### Query Modes

| Mode | Purpose |
|------|---------|
| `semantic` | Pure semantic similarity (default) |
| `session_recovery` | Excludes synthesis, for coldstart |
| `knowledge_lookup` | Filters to episteme/techne types |

### Query Rewriting (E2-253)

When `enable_rewriting=True`, conversational queries are transformed into technical, retrieval-optimized queries using Gemini. Queries shorter than 10 chars pass through unchanged.

Example: "that schema thing" -> "database schema ADR architecture decision"

### Invariants

- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)

### Usage

```python
from memory_bridge import MemoryBridge, QueryResult, StoreResult, LearningExtractionResult

# Create bridge with optional callback
bridge = MemoryBridge(work_engine_callback=my_callback)

# Query memory (with automatic query rewriting)
result = bridge.query("implementation patterns", mode="session_recovery")
if result.concepts:
    for concept in result.concepts:
        print(f"Found: {concept['content']}")

# Query without rewriting
bridge_raw = MemoryBridge(enable_rewriting=False)
result = bridge_raw.query("exact search terms")

# Store content
store_result = bridge.store(
    content="MemoryBridge implementation pattern",
    source_path="docs/work/active/E2-241/plans/PLAN.md"
)
# Auto-links to E2-241 if callback is set

# Extract learnings from session transcript (E2-262)
result = bridge.extract_learnings("/path/to/transcript.jsonl")
if result.success:
    print(f"Extracted: {result.outcome}, query: {result.initial_query}")
else:
    print(f"Skipped: {result.reason}")  # e.g., too_short, no_tool_usage
```

### CLI Integration (E2-253)

```bash
# Query via justfile recipe
just memory-query "implementation patterns"
just memory-query "coldstart" "session_recovery"
```

## WorkEngine (E2-242, E2-279 refactored)

Stateless work item management module. Core CRUD operations, with delegated functionality to extracted modules.

### Functions (Core)

| Function | Input | Output |
|----------|-------|--------|
| `get_work(id)` | Work item ID | `WorkState` or None |
| `create_work(id, title, ...)` | Work item data | Path to WORK.md |
| `transition(id, to_node)` | Work ID + target node | `WorkState` (updated) |
| `get_ready()` | None | List of unblocked `WorkState` |
| `close(id)` | Work item ID | Path to WORK.md |
| `archive(id)` | Work item ID | Path to archived WORK.md |
| `add_memory_refs(id, concept_ids)` | Work ID + concept list | None |
| `set_queue_position(id, position)` | Work ID + position | `WorkState` or None (WORK-066) |
| `get_in_progress()` | None | `List[WorkState]` with queue_position=in_progress (WORK-066) |

### Functions (Delegated to E2-279 modules)

| Function | Delegated To | Output |
|----------|--------------|--------|
| `cascade(id, new_status)` | CascadeEngine | `CascadeResult` |
| `spawn_tree(root_id)` | SpawnTree | Nested dict tree |
| `format_tree(tree)` | SpawnTree | ASCII string |
| `backfill(id, force)` | BackfillEngine | bool |
| `backfill_all(force)` | BackfillEngine | dict with results |
| `link_spawned_items(...)` | PortalManager | dict with updated/failed |
| `_create_portal(...)` | PortalManager | None (creates REFS.md) |
| `_update_portal(...)` | PortalManager | None (updates REFS.md) |

### WorkState Dataclass

```python
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    current_node: str          # DEPRECATED: use cycle_phase
    type: str = "feature"
    queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done
    cycle_phase: str = "backlog"     # WORK-066: backlog|plan|implement|check|done
    blocked_by: List[str]
    node_history: List[Dict]
    memory_refs: List[int]
    requirement_refs: List[str]
    source_files: List[str]
    acceptance_criteria: List[str]
    artifacts: List[str]
    extensions: Dict[str, Any]
    path: Optional[Path]
    priority: str = "medium"
```

### Exception Classes

| Exception | Purpose | Raised By |
|-----------|---------|-----------|
| `InvalidTransitionError` | Invalid DAG node transition | `transition()` |
| `WorkNotFoundError` | Work item doesn't exist | `transition()`, `close()`, `archive()` |
| `WorkIDUnavailableError` | Work ID exists with terminal status (E2-304) | `create_work()` |

The `WorkIDUnavailableError` (E2-304, REQ-VALID-001) prevents accidental overwrite of completed work items. Raised when attempting to create a work item with an ID that already exists with status `complete` or `archived`.

### Invariants

- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

### Usage

```python
from work_engine import WorkEngine, WorkState, InvalidTransitionError
from governance_layer import GovernanceLayer

governance = GovernanceLayer()
engine = WorkEngine(governance=governance)

# Get work item
work = engine.get_work("E2-242")
print(f"Status: {work.status}, Node: {work.current_node}")

# Transition to new node (validates via GovernanceLayer)
work = engine.transition("E2-242", "plan")

# Get all unblocked items
ready = engine.get_ready()
for item in ready:
    print(f"Ready: {item.id}")

# Archive completed work
engine.archive("E2-242")
```

## CascadeEngine (E2-279)

Stateless cascade manager for work item completion effects.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `cascade(id, status, dry_run)` | Work ID + status + dry_run flag | `CascadeResult` |

### CascadeResult Dataclass

```python
@dataclass
class CascadeResult:
    unblocked: List[str]       # IDs now READY
    still_blocked: List[str]   # IDs with remaining blockers
    related: List[str]         # IDs to review
    milestone_delta: Optional[int]  # Progress change
    substantive_refs: List[str]     # Files referencing ID
    message: str               # Formatted cascade report
```

### Usage

```python
from cascade_engine import CascadeEngine, CascadeResult
from work_engine import WorkEngine

engine = CascadeEngine(work_engine=work_engine, base_path=Path("."))
result = engine.cascade("E2-001", "complete")
print(result.message)
```

## PortalManager (E2-279)

Portal (REFS.md) management for work items.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `create_portal(id, refs_path)` | Work ID + path | None (creates file) |
| `update_portal(id, updates)` | Work ID + updates dict | None |
| `link_spawned_items(spawned_by, ids, milestone)` | Parent + child IDs | dict with updated/failed |

### Usage

```python
from portal_manager import PortalManager

manager = PortalManager(base_path=Path("."))
manager.create_portal("E2-001", refs_path)
manager.update_portal("E2-001", {"spawned_from": "INV-001"})
```

## SpawnTree (E2-279)

Spawn tree traversal and formatting.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `spawn_tree(root_id, max_depth)` | Root ID + depth limit | Nested dict |
| `format_tree(tree, use_ascii)` | Tree dict + ASCII flag | String |

### Usage

```python
from spawn_tree import SpawnTree

tree = SpawnTree(base_path=Path("."))
result = tree.spawn_tree("INV-001")
print(SpawnTree.format_tree(result, use_ascii=True))
```

## BackfillEngine (E2-279)

Backlog content backfill for work items.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `backfill(id, force)` | Work ID + force flag | bool |
| `backfill_all(force)` | Force flag | dict with success/not_found/no_changes |

### Usage

```python
from backfill_engine import BackfillEngine
from work_engine import WorkEngine

engine = BackfillEngine(work_engine=work_engine, base_path=Path("."))
success = engine.backfill("E2-001")
```

## ContextLoader (E2-254, WORK-008, WORK-009)

Programmatic bootstrap module for config-driven, role-based context loading.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `compute_session_number()` | None | `Tuple[int, Optional[int]]` (current, prior) |
| `load_context(role, trigger)` | role name + trigger type | `GroundedContext` dataclass |
| `generate_status(slim)` | bool (default True) | Dict with status data (E2-259) |

### GroundedContext Dataclass

```python
@dataclass
class GroundedContext:
    """Result of context loading - role-based composition (WORK-008)."""
    session_number: int
    prior_session: Optional[int] = None
    role: str = "main"                           # WORK-008: Role that was loaded
    loaded_context: Dict[str, str] = {}          # WORK-008: loader_name -> content
    # DEPRECATED fields (kept for backward compat when no loaders configured)
    l0_telos: str = ""           # WHY - Mission, Prime Directive
    l1_principal: str = ""       # WHO - Operator constraints
    l2_intent: str = ""          # WHAT - Goals, trade-offs
    l3_requirements: str = ""    # HOW - Principles, boundaries
    l4_implementation: str = ""  # WHAT to build - Architecture
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = []
    ready_work: List[str] = []
```

### Constructor Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `work_engine` | WorkEngine | None | For getting ready work items |
| `memory_bridge` | MemoryBridge | None | For strategy retrieval |
| `project_root` | Path | Auto-detect | Project root path |

### Role-Based Loading (WORK-008)

Loaders are configured in `haios.yaml`:

```yaml
context:
  roles:
    main:
      loaders: [identity]        # List of loaders to run
      description: "Main agent"
    builder:
      loaders: [identity]
  loader_registry:
    identity:
      module: identity_loader
      class: IdentityLoader
```

When `load_context(role="main")` is called:
1. Look up `context.roles.main.loaders` → `[identity]`
2. For each loader name, get class from `loader_registry`
3. Instantiate and call `loader.load()`
4. Store result in `loaded_context[loader_name]`

### Invariants

- MUST gracefully handle missing dependencies (WorkEngine, MemoryBridge)
- MUST gracefully degrade if no config or no roles (backward compat)
- MUST truncate checkpoint to 2000 chars for token efficiency
- MUST use session_delta format from haios-status.json
- MUST raise ValueError for unknown role if roles are configured

### Usage

```python
from context_loader import ContextLoader, GroundedContext

# Role-based loading (WORK-008)
loader = ContextLoader()
ctx = loader.load_context(role="main")
print(f"Role: {ctx.role}")
print(f"Identity content: {ctx.loaded_context.get('identity', '')[:100]}...")

# With dependencies
from work_engine import WorkEngine
from memory_bridge import MemoryBridge

engine = WorkEngine(governance=GovernanceLayer())
bridge = MemoryBridge()
loader = ContextLoader(work_engine=engine, memory_bridge=bridge)
ctx = loader.load_context(role="main")
print(f"Ready: {ctx.ready_work}")
print(f"Strategies: {len(ctx.strategies)}")

# Generate status (E2-259)
status = loader.generate_status()  # slim=True by default
print(f"Milestone: {status['milestone']['name']}")

# Full status (includes live_files, templates)
full_status = loader.generate_status(slim=False)
print(f"Live files: {len(full_status['live_files'])}")
```

### CLI Integration (E2-254, WORK-009)

```bash
# Load context and output identity content (WORK-009)
just coldstart

# Output includes:
# === IDENTITY ===
# Mission: ...
# Constraints: ...
# Principles: ...
# [SESSION]
# Number: 228
# Prior: 227
```

The `just coldstart` recipe calls `cli.py context-load` which:
1. Calls `ContextLoader.load_context(role="main")`
2. Prints `loaded_context` content (identity essence ~50 lines)
3. Prints session info and ready work

This eliminates Read tool calls for L0-L4 manifesto files during coldstart.

## CycleRunner (E2-255, WORK-084)

Stateless phase gate validator for cycle skills. Now includes lifecycle output types (WORK-084).

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `get_cycle_phases(cycle_id)` | Cycle identifier | `List[str]` of phase names |
| `check_phase_entry(cycle_id, phase, work_id)` | Cycle + phase + work ID | `GateResult` |
| `check_phase_exit(cycle_id, phase, work_id)` | Cycle + phase + work ID | `GateResult` |
| `build_scaffold_command(template, work_id, title)` | Command template + IDs | `str` formatted command (E2-263) |
| `run(work_id, lifecycle)` | Work ID + lifecycle name | `LifecycleOutput` subclass (WORK-084) |

### Lifecycle Output Types (WORK-084, REQ-LIFECYCLE-001)

Lifecycles are pure functions with explicit Input → Output signatures. The `run()` method returns typed outputs:

| Lifecycle | Output Type | Input → Output |
|-----------|-------------|----------------|
| `investigation` | `Findings` | Question → Findings |
| `design` | `Specification` | Requirements → Specification |
| `implementation` | `Artifact` | Specification → Artifact |
| `validation` | `Verdict` | Artifact × Spec → Verdict |
| `triage` | `PriorityList` | [Items] → [PrioritizedItems] |

```python
@dataclass
class LifecycleOutput:
    """Base class for all lifecycle outputs."""
    lifecycle: str
    work_id: str
    timestamp: datetime
    status: Literal["success", "failure", "partial"]

@dataclass
class Findings(LifecycleOutput):
    question: str
    conclusions: List[str]
    evidence: List[str]
    open_questions: List[str]

@dataclass
class Specification(LifecycleOutput):
    requirements: List[str]
    design_decisions: List[str]
    interfaces: Dict[str, Any]
```

### Supported Cycles

| Cycle ID | Phases |
|----------|--------|
| `implementation-cycle` | PLAN, DO, CHECK, DONE, CHAIN |
| `investigation-cycle` | HYPOTHESIZE, EXPLORE, CONCLUDE, CHAIN |
| `close-work-cycle` | VALIDATE, OBSERVE, ARCHIVE, MEMORY |
| `work-creation-cycle` | VERIFY, POPULATE, READY |
| `checkpoint-cycle` | SCAFFOLD, FILL, VERIFY, CAPTURE, COMMIT |
| `plan-authoring-cycle` | ANALYZE, AUTHOR, VALIDATE, CHAIN |
| `observation-triage-cycle` | SCAN, TRIAGE, PROMOTE |

### Invariants

- MUST NOT execute skill content (Claude interprets markdown)
- MUST delegate gate checks to GovernanceLayer
- MUST emit events for observability (PhaseEntered via log_phase_transition)
- MUST NOT own persistent state

### Usage

```python
from cycle_runner import CycleRunner, CycleResult, LifecycleOutput, Specification
from governance_layer import GovernanceLayer

runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)

# Get phases for a cycle
phases = runner.get_cycle_phases("implementation-cycle")
# ['PLAN', 'DO', 'CHECK', 'DONE', 'CHAIN']

# Check phase entry (emits PhaseEntered event)
result = runner.check_phase_entry("implementation-cycle", "DO", "E2-255")
if result.allowed:
    print("Entered DO phase")

# Check phase exit (validates exit criteria)
result = runner.check_phase_exit("investigation-cycle", "CONCLUDE", "INV-055")
if not result.allowed:
    print(f"Cannot exit: {result.reason}")

# Build scaffold command (E2-263)
command = runner.build_scaffold_command(
    template="/new-plan {id} {title}",
    work_id="E2-263",
    title="Scaffold Commands"
)
# Returns: "/new-plan E2-263 Scaffold Commands"

# Execute lifecycle and get typed output (WORK-084)
output = runner.run(work_id="WORK-084", lifecycle="design")
# Returns: Specification(...) with work_id, timestamp, status, requirements, etc.
# Caller decides whether to chain to next lifecycle (pure function behavior)
```

### CLI Integration (E2-255)

```bash
# Get phases via justfile recipe
just cycle-phases implementation-cycle
# ['PLAN', 'DO', 'CHECK', 'DONE', 'CHAIN']
```

## PlannerAgent (WORK-032)

PLAN stage component for the doc-to-product pipeline. Transforms RequirementSet into WorkPlan.

### Functions

| Function | Input | Output |
|----------|-------|--------|
| `suggest_groupings()` | None | `List[RequirementGroup]` (for operator review) |
| `estimate_dependencies()` | None | `DependencyGraph` with topological sort |
| `plan(approved_groupings)` | Optional groupings | `WorkPlan` with work items and execution order |

### Data Classes

| Class | Fields | Purpose |
|-------|--------|---------|
| `PlannedWorkItem` | id, title, requirement_refs, dependencies, priority | Suggested work item (WORK-PXXX prefix) |
| `RequirementGroup` | domain, requirements, suggested_title | Group of requirements for one work item |
| `DependencyGraph` | edges, nodes, topological_sort() | Dependency graph with cycle detection |
| `WorkPlan` | source_requirements, work_items, execution_order | Output of PLAN stage per S26 |

### Invariants

- MUST group by domain (REQ-TRACE-*, REQ-CONTEXT-*, etc.)
- MUST sort MUST requirements before SHOULD within groups
- MUST use Kahn's algorithm for topological sort
- MUST NOT create work items (that's WorkEngine's job)

### Usage

```python
from planner_agent import PlannerAgent, WorkPlan
from requirement_extractor import RequirementExtractor

# Extract requirements
extractor = RequirementExtractor(corpus_path)
requirements = extractor.extract()

# Generate work plan
planner = PlannerAgent(requirements)
groupings = planner.suggest_groupings()  # For operator review
plan = planner.plan()  # Or planner.plan(approved_groupings)

print(f"Work items: {len(plan.work_items)}")
print(f"Execution order: {plan.execution_order}")
```

### CLI Integration

```bash
# Plan from requirements file
python .claude/haios/modules/cli.py plan <requirements_path>

# Plan from corpus config
python .claude/haios/modules/cli.py plan --from-corpus <corpus_config>
```

---

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization, exports |
| `governance_layer.py` | GovernanceLayer module (E2-240) |
| `memory_bridge.py` | MemoryBridge module (E2-241, E2-253) |
| `work_engine.py` | WorkEngine module - core CRUD (E2-242, E2-279) |
| `cascade_engine.py` | CascadeEngine module - completion cascade (E2-279) |
| `portal_manager.py` | PortalManager module - REFS.md management (E2-279) |
| `spawn_tree.py` | SpawnTree module - tree traversal (E2-279) |
| `backfill_engine.py` | BackfillEngine module - backlog backfill (E2-279) |
| `context_loader.py` | ContextLoader module (E2-254) |
| `cycle_runner.py` | CycleRunner module (E2-255) |
| `requirement_extractor.py` | RequirementExtractor module (WORK-015) |
| `corpus_loader.py` | CorpusLoader module (WORK-031) |
| `planner_agent.py` | PlannerAgent module (WORK-032) |
| `cli.py` | CLI entry point for justfile recipes |
| `README.md` | This documentation |

## Consumers (E2-264)

These modules are imported by the following hooks:

| Hook | Module | Function |
|------|--------|----------|
| `user_prompt_submit.py` | ContextLoader | `generate_status(slim=True)` |
| `pre_tool_use.py` | GovernanceLayer | `get_toggle()` |
| `post_tool_use.py` | MemoryBridge | `is_actual_error()`, `capture_error()` |
| `post_tool_use.py` | CycleRunner | `build_scaffold_command()` |
| `stop.py` | MemoryBridge | `extract_learnings()` |

## Related

- `L4-implementation.md`: Functional requirements
- `.claude/lib/governance_events.py`: Event logging (consumed by GovernanceLayer, CycleRunner)
- `.claude/lib/node_cycle.py`: Exit criteria (consumed by CycleRunner)
- `.claude/hooks/hooks/`: Runtime consumers of these modules (E2-264)
