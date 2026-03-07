# Exhuastive HAIOS Deep System Inventory

This document contains a totally comprehensive mapping of every database schema definition, Python module, class, and method within the HAIOS core.

## 1. Database Schema (`haios_memory.db`)

### Index: `idx_agent_capabilities`
```sql
CREATE INDEX idx_agent_capabilities ON agent_registry(capabilities)
```

### Index: `idx_artifacts_file_hash`
```sql
CREATE INDEX idx_artifacts_file_hash ON artifacts (file_hash)
```

### Index: `idx_artifacts_space_id`
```sql
CREATE INDEX idx_artifacts_space_id ON artifacts(space_id)
```

### Index: `idx_cluster_members_cluster`
```sql
CREATE INDEX idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id)
```

### Index: `idx_cluster_members_type`
```sql
CREATE INDEX idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id)
```

### Index: `idx_concept_occurrences_artifact_id`
```sql
CREATE INDEX idx_concept_occurrences_artifact_id ON concept_occurrences (artifact_id)
```

### Index: `idx_concepts_cluster`
```sql
CREATE INDEX idx_concepts_cluster ON concepts(synthesis_cluster_id) WHERE synthesis_cluster_id IS NOT NULL
```

### Index: `idx_concepts_synthesized`
```sql
CREATE INDEX idx_concepts_synthesized ON concepts(synthesized_at) WHERE synthesized_at IS NOT NULL
```

### Index: `idx_embeddings_artifact`
```sql
CREATE INDEX idx_embeddings_artifact ON embeddings(artifact_id)
```

### Index: `idx_embeddings_concept`
```sql
CREATE INDEX idx_embeddings_concept ON embeddings(concept_id)
```

### Index: `idx_entities_type_value`
```sql
CREATE INDEX idx_entities_type_value ON entities (type, value)
```

### Index: `idx_entity_occurrences_artifact_id`
```sql
CREATE INDEX idx_entity_occurrences_artifact_id ON entity_occurrences (artifact_id)
```

### Index: `idx_metadata_key`
```sql
CREATE INDEX idx_metadata_key ON memory_metadata(key)
```

### Index: `idx_metadata_memory_id`
```sql
CREATE INDEX idx_metadata_memory_id ON memory_metadata(memory_id)
```

### Index: `idx_processing_log_status`
```sql
CREATE INDEX idx_processing_log_status ON processing_log (status)
```

### Index: `idx_provenance_source`
```sql
CREATE INDEX idx_provenance_source ON synthesis_provenance(source_type, source_id)
```

### Index: `idx_provenance_synthesized`
```sql
CREATE INDEX idx_provenance_synthesized ON synthesis_provenance(synthesized_concept_id)
```

### Index: `idx_reasoning_approach`
```sql
CREATE INDEX idx_reasoning_approach ON reasoning_traces(approach_taken)
```

### Index: `idx_reasoning_has_strategy`
```sql
CREATE INDEX idx_reasoning_has_strategy ON reasoning_traces(strategy_title) WHERE strategy_title IS NOT NULL
```

### Index: `idx_reasoning_model`
```sql
CREATE INDEX idx_reasoning_model ON reasoning_traces(model_used)
```

### Index: `idx_reasoning_outcome`
```sql
CREATE INDEX idx_reasoning_outcome ON reasoning_traces(outcome, timestamp DESC)
```

### Index: `idx_reasoning_space`
```sql
CREATE INDEX idx_reasoning_space ON reasoning_traces(space_id, timestamp DESC)
```

### Index: `idx_relationships_source`
```sql
CREATE INDEX idx_relationships_source ON memory_relationships(source_id)
```

### Index: `idx_relationships_target`
```sql
CREATE INDEX idx_relationships_target ON memory_relationships(target_id)
```

### Index: `idx_synthesis_clusters_status`
```sql
CREATE INDEX idx_synthesis_clusters_status ON synthesis_clusters(status)
```

### Index: `idx_synthesis_clusters_type`
```sql
CREATE INDEX idx_synthesis_clusters_type ON synthesis_clusters(cluster_type)
```

### Table: `agent_registry`
```sql
CREATE TABLE agent_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL, -- 'subagent', 'worker', 'orchestrator'
    capabilities JSON, -- List of capability strings
    tools JSON, -- List of tool names
    input_schema JSON,
    output_schema JSON,
    status TEXT DEFAULT 'active', -- 'active', 'deprecated', 'development'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Table: `artifacts`
```sql
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_hash TEXT NOT NULL,                    -- SHA256 hash for change detection
    last_processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1                   -- Increment on re-processing
, space_id TEXT)
```

### Table: `concept_occurrences`
```sql
CREATE TABLE concept_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY (concept_id) REFERENCES concepts (id)
)
```

### Table: `concepts`
```sql
CREATE TABLE concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'Directive', 'Proposal', 'Critique'
    content TEXT NOT NULL,
    source_adr TEXT                             -- For 'Decision' concepts
, synthesis_confidence REAL, synthesized_at TIMESTAMP, synthesis_cluster_id INTEGER, synthesis_source_count INTEGER DEFAULT 0)
```

### Table: `concepts_backup_20260130`
```sql
CREATE TABLE concepts_backup_20260130(
  id INT,
  type TEXT,
  content TEXT,
  source_adr TEXT,
  synthesis_confidence REAL,
  synthesized_at NUM,
  synthesis_cluster_id INT,
  synthesis_source_count INT
)
```

### Table: `embeddings`
```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER,
    concept_id INTEGER,
    entity_id INTEGER,
    vector BLOB NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
)
```

### Table: `entities`
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'User', 'Agent', 'ADR'
    value TEXT NOT NULL,
    UNIQUE(type, value)
)
```

### Table: `entity_occurrences`
```sql
CREATE TABLE entity_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY (entity_id) REFERENCES entities (id)
)
```

### Table: `memory_metadata`
```sql
CREATE TABLE memory_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(memory_id) REFERENCES artifacts(id) ON DELETE CASCADE
)
```

### Table: `memory_relationships`
```sql
CREATE TABLE memory_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('implements', 'justifies', 'derived_from', 'supports', 'contradicts', 'related')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES artifacts(id) ON DELETE CASCADE
)
```

### Table: `processing_log`
```sql
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending', 'success', 'error', 'skipped')),
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    file_hash TEXT                              -- SHA256 hash for change detection
)
```

### Table: `quality_metrics`
```sql
CREATE TABLE quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entities_extracted INTEGER DEFAULT 0,
    concepts_extracted INTEGER DEFAULT 0,
    processing_time_seconds REAL,
    llm_tokens_used INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
)
```

### Table: `reasoning_traces`
```sql
CREATE TABLE reasoning_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    query_embedding BLOB,  -- For similarity search
    approach_taken TEXT NOT NULL,
    strategy_details JSON,  -- Detailed strategy parameters
    outcome TEXT CHECK(outcome IN ('success', 'partial_success', 'failure')),
    failure_reason TEXT,
    success_factors JSON,
    memories_used JSON,  -- Which memories were retrieved
    memories_helpful JSON,  -- Which were actually useful
    context_snapshot JSON,
    execution_time_ms INTEGER,
    model_used TEXT,
    space_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    similar_to_trace_id INTEGER, strategy_description TEXT, strategy_content TEXT, strategy_title TEXT, extraction_model TEXT,  -- Link to similar past reasoning
    FOREIGN KEY (similar_to_trace_id) REFERENCES reasoning_traces(id)
)
```

### Table: `skill_registry`
```sql
CREATE TABLE skill_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    provider_agent_id TEXT,
    parameters JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(provider_agent_id) REFERENCES agent_registry(id)
)
```

### Table: `sqlite_sequence`
```sql
CREATE TABLE sqlite_sequence(name,seq)
```

### Table: `synthesis_cluster_members`
```sql
CREATE TABLE "synthesis_cluster_members" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace', 'cross')), -- Added 'cross'
    member_id INTEGER NOT NULL,
    similarity_to_centroid REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
)
```

### Table: `synthesis_clusters`
```sql
CREATE TABLE synthesis_clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_type TEXT NOT NULL CHECK(cluster_type IN ('concept', 'trace', 'cross')),
    centroid_embedding BLOB,
    member_count INTEGER DEFAULT 0,
    synthesized_concept_id INTEGER,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'synthesized', 'skipped')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synthesized_at TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE SET NULL
)
```

### Table: `synthesis_provenance`
```sql
CREATE TABLE synthesis_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthesized_concept_id INTEGER NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
    source_id INTEGER NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
)
```

## 2. Python Core Definitions

### Directory: `.claude/haios/modules`

#### Module: `__init__.py`
*HAIOS Modules Package.*

*No classes or functions defined.*

#### Module: `assets.py`
*Assets Module (WORK-093, REQ-ASSET-001)*

- **Class** `Asset`
  - *Base class for all lifecycle assets - flat provenance structure.*
  - `def to_dict(...)`
  - `def to_markdown(...)`
- **Class** `FindingsAsset`
  - *Investigation lifecycle output: Question -> Findings.*
- **Class** `SpecificationAsset`
  - *Design lifecycle output: Requirements -> Specification.*
- **Class** `ArtifactAsset`
  - *Implementation lifecycle output: Specification -> Artifact.*
- **Class** `VerdictAsset`
  - *Validation lifecycle output: Artifact x Spec -> Verdict.*
- **Class** `PriorityListAsset`
  - *Triage lifecycle output: [Items] -> [PrioritizedItems].*

#### Module: `backfill_engine.py`
*BackfillEngine Module (E2-279)*

- **Class** `BackfillEngine`
  - *Backlog content backfill for work items.*
  - `def __init__(...)`
  - `def active_dir(...)`
  - `def backfill(...)`
  - `def backfill_all(...)`
  - `def _parse_backlog_entry(...)`
  - `def _update_work_file_content(...)`

#### Module: `cascade_engine.py`
*CascadeEngine Module (E2-279)*

- **Class** `CascadeResult`
  - *Result of cascade operation (E2-251).*
- **Class** `CascadeEngine`
  - *Stateless cascade manager for work item completion effects.*
  - `def __init__(...)`
  - `def active_dir(...)`
  - `def archive_dir(...)`
  - `def cascade(...)`
  - `def _get_unblocked_items(...)`
  - `def _is_item_complete(...)`
  - `def _get_related_items(...)`
  - `def _get_milestone_delta(...)`
  - `def _get_substantive_refs(...)`
  - `def _format_cascade_message(...)`
  - `def _write_cascade_event(...)`
  - `def _parse_work_file(...)`

#### Module: `ceremony_runner.py`
*CeremonyRunner Module (WORK-118, CH-013)*

- **Class** `CeremonyResult`
  - *Result of a ceremony invocation.*
- **Class** `CeremonyRunner`
  - *Ceremony phase validator and invoker.*
  - `def __init__(...)`
  - `def get_ceremony_phases(...)`
  - `def invoke(...)`

#### Module: `cli.py`
*HAIOS Modules CLI Entry Point*

- **Function** `def get_engine(...)`
- **Function** `def cmd_transition(...)`
- **Function** `def cmd_close(...)`
- **Function** `def cmd_archive(...)`
- **Function** `def cmd_get_ready(...)`
- **Function** `def cmd_get_work(...)`
- **Function** `def cmd_link(...)`
- **Function** `def cmd_link_spawn(...)`
- **Function** `def cmd_cascade(...)`
- **Function** `def cmd_clear_blocked_by(...)`
- **Function** `def cmd_spawn_tree(...)`
- **Function** `def cmd_backfill(...)`
- **Function** `def cmd_backfill_all(...)`
- **Function** `def cmd_memory_query(...)`
- **Function** `def cmd_context_load(...)`
- **Function** `def cmd_coldstart(...)`
- **Function** `def cmd_cycle_phases(...)`
- **Function** `def cmd_corpus_list(...)`
- **Function** `def cmd_plan(...)`
- **Function** `def cmd_extract_requirements(...)`
- **Function** `def cmd_validate(...)`
- **Function** `def cmd_scaffold(...)`
- **Function** `def cmd_pipeline_run(...)`
- **Function** `def main(...)`

#### Module: `context_loader.py`
*ContextLoader Module (E2-254, WORK-008)*

- **Class** `GroundedContext`
  - *Result of context loading - role-based composition.*
- **Class** `ContextLoader`
  - *Bootstrap the agent with config-driven, role-based context grounding.*
  - `def __init__(...)`
  - `def _register_default_loaders(...)`
  - `def _load_config(...)`
  - `def _get_loaders_for_role(...)`
  - `def compute_session_number(...)`
  - `def load_context(...)`
  - `def _read_manifesto_file(...)`
  - `def _get_latest_checkpoint(...)`
  - `def _get_strategies(...)`
  - `def _get_ready_work(...)`
  - `def generate_status(...)`

#### Module: `corpus_loader.py`
*CorpusLoader Module (WORK-031, CH-001)*

- **Class** `CorpusSource`
  - *Single source definition within a corpus.*
- **Class** `CorpusConfig`
  - *Parsed corpus configuration.*
- **Class** `CorpusLoader`
  - *Load and discover files from a configured corpus.*
  - `def __init__(...)`
  - `def _load_config(...)`
  - `def _parse_config(...)`
  - `def discover(...)`
  - `def _apply_exclusions(...)`
  - `def filter_by_type(...)`

#### Module: `cycle_runner.py`
*CycleRunner Module (E2-255)*

- **Class** `CycleResult`
  - *Result of a cycle validation or execution.*
- **Class** `CycleRunner`
  - *Stateless phase gate validator for cycle skills.*
  - `def __init__(...)`
  - `def _load_cycle_definitions(...)`
  - `def get_cycle_phases(...)`
  - `def check_phase_entry(...)`
  - `def check_phase_exit(...)`
  - `def _get_node_for_cycle(...)`
  - `def _emit_phase_entered(...)`
  - `def build_scaffold_command(...)`
  - `def run(...)`
  - `def run_batch(...)`
  - `def _load_phase_template(...)`
  - `def validate_phase_input(...)`
  - `def validate_phase_output(...)`
  - `def _check_work_has_field(...)`

#### Module: `governance_layer.py`
*GovernanceLayer Module (E2-240)*

- **Class** `GateResult`
  - *Result of a gate check.*
- **Class** `GovernanceLayer`
  - *Stateless policy enforcement module.*
  - `def __init__(...)`
  - `def check_gate(...)`
  - `def _check_dod_gate(...)`
  - `def _check_preflight_gate(...)`
  - `def _check_observation_gate(...)`
  - `def validate_transition(...)`
  - `def validate_queue_transition(...)`
  - `def load_handlers(...)`
  - `def _parse_handlers(...)`
  - `def on_event(...)`
  - `def validate_template(...)`
  - `def scaffold_template(...)`
  - `def get_toggle(...)`
  - `def get_activity_state(...)`
  - `def map_tool_to_primitive(...)`
  - `def check_activity(...)`
  - `def _check_skill_restriction(...)`
  - `def _load_activity_matrix(...)`
- **Class** `CeremonyRequiredError`
  - *Raised when state change attempted outside ceremony context in block mode.*
- **Class** `CeremonyNestingError`
  - *Raised when ceremony_context opened within existing context.*
- **Class** `CeremonyContext`
  - *Active ceremony context with side-effect tracking.*
  - `def log_side_effect(...)`
  - `def execute_step(...)`
- **Function** `def ceremony_context(...)`
- **Function** `def in_ceremony_context(...)`
- **Function** `def _get_current_ceremony(...)`
- **Function** `def _set_ceremony_context(...)`
- **Function** `def _clear_ceremony_context(...)`
- **Function** `def check_ceremony_required(...)`
- **Function** `def _get_ceremony_enforcement(...)`
- **Function** `def _log_ceremony_event(...)`

#### Module: `memory_bridge.py`
*MemoryBridge Module (E2-241)*

- **Class** `QueryResult`
  - *Result of a memory query.*
- **Class** `StoreResult`
  - *Result of a memory store operation.*
- **Class** `LearningExtractionResult`
  - *Result of learning extraction operation (E2-262).*
- **Class** `MemoryBridge`
  - *Stateless memory abstraction module.*
  - `def __init__(...)`
  - `def query(...)`
  - `def store(...)`
  - `def auto_link(...)`
  - `def _parse_work_id(...)`
  - `def _call_mcp_with_retry(...)`
  - `def _call_mcp(...)`
  - `def _search_with_experience(...)`
  - `def _ingest(...)`
  - `def _rewrite_query(...)`
  - `def is_actual_error(...)`
  - `def capture_error(...)`
  - `def extract_learnings(...)`

#### Module: `pipeline_orchestrator.py`
*PipelineOrchestrator Module (WORK-033, CH-006)*

- **Class** `PipelineState`
  - *Pipeline execution states per S26.*
- **Class** `InvalidStateError`
  - *Raised when operation called in invalid state.*
- **Class** `PipelineResult`
  - *Result of pipeline execution.*
- **Class** `PipelineOrchestrator`
  - *Pipeline state machine per S26.*
  - `def __init__(...)`
  - `def state(...)`
  - `def state_history(...)`
  - `def requirement_set(...)`
  - `def work_plan(...)`
  - `def _transition(...)`
  - `def ingest(...)`
  - `def plan(...)`
  - `def run(...)`

#### Module: `planner_agent.py`
*PlannerAgent Module (WORK-032, CH-003)*

- **Class** `PlannedWorkItem`
  - *A work item suggested by the planner.*
- **Class** `RequirementGroup`
  - *A group of requirements to become a single work item.*
  - `def __post_init__(...)`
- **Class** `DependencyGraph`
  - *Graph of dependencies between requirements/work items.*
  - `def add_edge(...)`
  - `def topological_sort(...)`
- **Class** `WorkPlan`
  - *Output of the PLAN stage per S26.*
- **Class** `PlannerAgent`
  - *PLAN stage component per S26.*
  - `def __init__(...)`
  - `def suggest_groupings(...)`
  - `def estimate_dependencies(...)`
  - `def plan(...)`
  - `def _extract_domain(...)`
  - `def _strength_priority(...)`
  - `def _next_work_id(...)`

#### Module: `portal_manager.py`
*PortalManager Module (E2-279)*

- **Class** `PortalManager`
  - *Portal (REFS.md) management for work items.*
  - `def __init__(...)`
  - `def active_dir(...)`
  - `def archive_dir(...)`
  - `def create_portal(...)`
  - `def update_portal(...)`
  - `def link_spawned_items(...)`
  - `def _find_work_file(...)`

#### Module: `requirement_extractor.py`
*RequirementExtractor Module (WORK-015, CH-002)*

- **Class** `RequirementStrength`
  - *RFC 2119 requirement strength levels.*
- **Class** `RequirementType`
  - *Requirement type classification.*
- **Class** `DocumentType`
  - *Source document type.*
- **Class** `RequirementStatus`
  - *Requirement lifecycle status.*
- **Class** `RequirementSource`
  - *Provenance information for a requirement.*
- **Class** `Requirement`
  - *A single extracted requirement.*
- **Class** `TraceabilityLink`
  - *Traceability from requirement to artifacts (CH-002 R4).*
- **Class** `RequirementSet`
  - *Collection of extracted requirements with metadata.*
- **Class** `Parser`
  - *Protocol for requirement parsers.*
  - `def can_parse(...)`
  - `def parse(...)`
- **Class** `TRDParser`
  - *Extracts requirements from TRD R0-R8 tables.*
  - `def can_parse(...)`
  - `def parse(...)`
- **Class** `ManifestoParser`
  - *Extracts requirements from L4 manifesto REQ-{DOMAIN}-{NNN} patterns.*
  - `def can_parse(...)`
  - `def parse(...)`
- **Class** `NaturalLanguageParser`
  - *Extracts requirements from prose with RFC 2119 keywords.*
  - `def can_parse(...)`
  - `def parse(...)`
- **Class** `RequirementExtractor`
  - *Main extractor that orchestrates parsing across a corpus.*
  - `def __init__(...)`
  - `def extract(...)`
  - `def extract_from_file(...)`
  - `def _select_parser(...)`
  - `def _discover_files(...)`

#### Module: `spawn_tree.py`
*SpawnTree Module (E2-279)*

- **Class** `SpawnTree`
  - *Spawn tree traversal and formatting.*
  - `def __init__(...)`
  - `def active_dir(...)`
  - `def archive_dir(...)`
  - `def spawn_tree(...)`
  - `def _find_children(...)`
  - `def format_tree(...)`

#### Module: `work_engine.py`
*WorkEngine Module (E2-242, E2-279 refactored)*

- **Class** `InvalidTransitionError`
  - *Raised when a DAG transition is invalid.*
- **Class** `WorkNotFoundError`
  - *Raised when work item doesn't exist.*
- **Class** `WorkIDUnavailableError`
  - *Raised when work item ID exists with terminal status (E2-304, REQ-VALID-001).*
- **Class** `WorkState`
  - *Typed work item state from parsed WORK.md.*
- **Class** `QueueConfig`
  - *Queue configuration from work_queues.yaml (E2-290).*
- **Class** `WorkEngine`
  - *Stateless work item management module.*
  - `def __init__(...)`
  - `def active_dir(...)`
  - `def archive_dir(...)`
  - `def get_work(...)`
  - `def _validate_id_available(...)`
  - `def create_work(...)`
  - `def transition(...)`
  - `def get_ready(...)`
  - `def is_at_pause_point(...)`
  - `def _get_queue_config_path(...)`
  - `def load_queues(...)`
  - `def get_queue(...)`
  - `def get_next(...)`
  - `def is_cycle_allowed(...)`
  - `def _work_exists(...)`
  - `def close(...)`
  - `def _set_closed_date(...)`
  - `def archive(...)`
  - `def add_memory_refs(...)`
  - `def set_queue_position(...)`
  - `def get_working(...)`
  - `def get_in_progress(...)`
  - `def get_parked(...)`
  - `def get_by_queue_position(...)`
  - `def get_in_lifecycle(...)`
  - `def count_active_in_lifecycle(...)`
  - `def add_document_link(...)`
  - `def _validate_state_combination(...)`
  - `def _is_actually_blocked(...)`
  - `def _find_work_file(...)`
  - `def _parse_work_file(...)`
  - `def _write_work_file(...)`
  - `def _get_portal_manager(...)`
  - `def _create_portal(...)`
  - `def _update_portal(...)`
  - `def link_spawned_items(...)`
  - `def cascade(...)`
  - `def spawn_tree(...)`
  - `def format_tree(...)`
  - `def get_work_lineage(...)`
  - `def backfill(...)`
  - `def backfill_all(...)`
- **Function** `def is_valid_queue_transition(...)`

### Directory: `.claude/haios/lib`

#### Module: `__init__.py`
*HAIOS Library - Portable plugin utilities.*

*No classes or functions defined.*

#### Module: `audit.py`
*Governance audit functions for detecting drift.*

- **Function** `def _iter_work_files_glob(...)`
- **Function** `def _work_file_exists(...)`
- **Function** `def parse_frontmatter(...)`
- **Function** `def audit_sync(...)`
- **Function** `def audit_gaps(...)`
- **Function** `def audit_stale(...)`
- **Function** `def audit_status_divergence(...)`

#### Module: `audit_decision_coverage.py`
*Decision traceability validation for HAIOS.*

- **Class** `ValidationResult`
  - *Result of validation with warnings and errors.*
- **Function** `def parse_epoch_decisions(...)`
- **Function** `def _parse_assigned_to_block(...)`
- **Function** `def parse_chapter_refs(...)`
- **Function** `def validate_decision_coverage(...)`
- **Function** `def validate_chapter_traceability(...)`
- **Function** `def validate_bidirectional(...)`
- **Function** `def validate_full_coverage(...)`
- **Function** `def get_exit_code(...)`
- **Function** `def get_default_paths(...)`

#### Module: `blocked_by_cascade.py`
*Blocked-by cascade on work closure (WORK-173).*

- **Function** `def _format_blocked_by(...)`
- **Function** `def _replace_blocked_by_block(...)`
- **Function** `def clear_blocked_by(...)`
- **Function** `def _log_warning(...)`

#### Module: `ceremony_contracts.py`
*Ceremony contract schema, registry, and validation (CH-011, WORK-111, WORK-113).*

- **Class** `ContractField`
  - *Input contract field definition.*
  - `def __post_init__(...)`
- **Class** `OutputField`
  - *Output contract field definition.*
  - `def __post_init__(...)`
- **Class** `CeremonyContract`
  - *Full ceremony contract parsed from skill frontmatter.*
  - `def __post_init__(...)`
  - `def from_frontmatter(...)`
- **Class** `RegistryEntry`
  - *Single ceremony entry in the registry.*
- **Class** `CeremonyRegistry`
  - *Collection of all ceremonies loaded from registry YAML.*
- **Class** `ValidationResult`
  - *Result of validating inputs/outputs against a contract.*
- **Function** `def _validate_category(...)`
- **Function** `def validate_ceremony_input(...)`
- **Function** `def validate_ceremony_output(...)`
- **Function** `def enforce_ceremony_contract(...)`
- **Function** `def _read_enforcement_toggle(...)`
- **Function** `def _find_registry_path(...)`
- **Function** `def load_ceremony_registry(...)`

#### Module: `cli.py`
- **Function** `def get_db_path(...)`
- **Function** `def cmd_status(...)`
- **Function** `def cmd_reset(...)`
- **Function** `def cmd_process(...)`
- **Function** `def cmd_synthesis(...)`
- **Function** `def cmd_refinement(...)`
- **Function** `def cmd_ingest(...)`
- **Function** `def main(...)`

#### Module: `coldstart_orchestrator.py`
*Coldstart Orchestrator for Configuration Arc.*

- **Class** `ColdstartOrchestrator`
  - *Orchestrate coldstart phases with breathing room.*
  - `def __init__(...)`
  - `def _load_config(...)`
  - `def _check_for_orphans(...)`
  - `def _make_work_status_fn(...)`
  - `def run(...)`
  - `def _run_epoch_validation(...)`

#### Module: `config.py`
*Unified configuration loader for HAIOS modules.*

- **Class** `ConfigLoader`
  - *Unified config access for HAIOS modules.*
  - `def get(...)`
  - `def reset(...)`
  - `def __init__(...)`
  - `def _load_schemas(...)`
  - `def _load(...)`
  - `def haios(...)`
  - `def cycles(...)`
  - `def components(...)`
  - `def toggles(...)`
  - `def thresholds(...)`
  - `def node_bindings(...)`
  - `def paths(...)`
  - `def get_path(...)`
  - `def schemas(...)`
  - `def get_schema(...)`

#### Module: `critique_injector.py`
*Critique injection for PreToolUse hook (WORK-169).*

- **Function** `def _default_project_root(...)`
- **Function** `def _get_current_phase(...)`
- **Function** `def _get_current_work_id_for_critique(...)`
- **Function** `def _is_inhale_to_exhale(...)`
- **Function** `def compute_critique_injection(...)`
- **Function** `def _log_critique_injection(...)`
- **Function** `def _log_critique_warning(...)`

#### Module: `cycle_state.py`
*Cycle phase auto-advancement for PostToolUse hook (WORK-168).*

- **Function** `def _default_project_root(...)`
- **Function** `def advance_cycle_phase(...)`
- **Function** `def sync_work_md_phase(...)`

#### Module: `database.py`
- **Class** `DatabaseManager`
  - `def __init__(...)`
  - `def get_connection(...)`
  - `def setup(...)`
  - `def insert_artifact(...)`
  - `def insert_entity(...)`
  - `def insert_concept(...)`
  - `def record_entity_occurrence(...)`
  - `def record_concept_occurrence(...)`
  - `def get_processing_status(...)`
  - `def get_artifact_hash(...)`
  - `def insert_quality_metrics(...)`
  - `def update_processing_status(...)`
  - `def insert_embedding(...)`
  - `def insert_concept_embedding(...)`
  - `def search_memories(...)`
  - `def get_stats(...)`
  - `def register_agent(...)`
  - `def get_agent(...)`
  - `def list_agents(...)`
  - `def get_schema_info(...)`
  - `def _list_tables(...)`
  - `def query_read_only(...)`

#### Module: `dependencies.py`
*Dependency Integrity Validator (E2-024).*

- **Function** `def extract_skill_refs(...)`
- **Function** `def extract_agent_refs(...)`
- **Function** `def get_available_skills(...)`
- **Function** `def get_available_agents(...)`
- **Function** `def validate_dependencies(...)`

#### Module: `dod_validation.py`
*DoD validation functions for closure ceremonies (CH-015, WORK-122).*

- **Class** `DoDCheck`
  - *Single DoD check result.*
- **Class** `DoDResult`
  - *Result of DoD validation at any level.*
- **Function** `def _parse_frontmatter(...)`
- **Function** `def _parse_markdown_field(...)`
- **Function** `def _count_exit_criteria(...)`
- **Function** `def _find_work_items_for_chapter(...)`
- **Function** `def validate_work_dod(...)`
- **Function** `def validate_chapter_dod(...)`
- **Function** `def validate_arc_dod(...)`
- **Function** `def validate_epoch_dod(...)`

#### Module: `epoch_validator.py`
*Epoch Transition Validator (WORK-154).*

- **Class** `EpochValidator`
  - *Epoch transition consistency validator.*
  - `def __init__(...)`
  - `def _load_haios_config(...)`
  - `def _load_queue_config(...)`
  - `def _load_epoch_content(...)`
  - `def _load_work_status(...)`
  - `def validate_queue_config(...)`
  - `def validate_epoch_status(...)`
  - `def validate(...)`

#### Module: `error_capture.py`
*Error Capture Module (E2-130).*

- **Function** `def _get_db(...)`
- **Function** `def is_actual_error(...)`
- **Function** `def store_error(...)`
- **Function** `def get_error_summary(...)`

#### Module: `errors.py`
*Error Handling and Logging*

*No classes or functions defined.*

#### Module: `governance_events.py`
*Governance event logging and threshold monitoring.*

- **Function** `def log_phase_transition(...)`
- **Function** `def log_validation_outcome(...)`
- **Function** `def log_gate_violation(...)`
- **Function** `def get_gate_violations(...)`
- **Function** `def log_session_start(...)`
- **Function** `def log_session_end(...)`
- **Function** `def log_tier_detected(...)`
- **Function** `def log_critique_injected(...)`
- **Function** `def detect_orphan_session(...)`
- **Function** `def scan_incomplete_work(...)`
- **Function** `def get_threshold_warnings(...)`
- **Function** `def check_work_item_events(...)`
- **Function** `def get_governance_metrics(...)`
- **Function** `def read_events(...)`
- **Function** `def _append_event(...)`
- **Function** `def _check_repeated_failure(...)`
- **Function** `def _top_failure_reasons(...)`

#### Module: `hierarchy_engine.py`
*Stateless hierarchy query engine for epoch/arc/chapter/work navigation.*

- **Class** `ArcInfo`
  - *Arc metadata parsed from haios.yaml active_arcs + ARC.md.*
- **Class** `ChapterInfo`
  - *Chapter metadata parsed from ARC.md chapter table row.*
- **Class** `WorkInfo`
  - *Lightweight work item metadata for hierarchy queries.*
- **Class** `HierarchyChain`
  - *Full hierarchy chain from work item up to epoch.*
- **Class** `HierarchyQueryEngine`
  - *Stateless hierarchy query engine for epoch/arc/chapter/work navigation.*
  - `def __init__(...)`
  - `def get_arcs(...)`
  - `def get_chapters(...)`
  - `def get_work(...)`
  - `def get_hierarchy(...)`
  - `def _load_haios_config(...)`
  - `def _parse_arc_metadata(...)`
  - `def _parse_arc_chapters(...)`
  - `def _parse_work_info(...)`
  - `def _parse_frontmatter(...)`

#### Module: `identity_loader.py`
*Identity Loader for Configuration Arc.*

- **Class** `IdentityLoader`
  - *Extract identity context from manifesto files.*
  - `def __init__(...)`
  - `def config(...)`
  - `def extract(...)`
  - `def format(...)`
  - `def load(...)`

#### Module: `loader.py`
*Config-driven content extractor for structured markdown files.*

- **Class** `Loader`
  - *Config-driven content extractor for structured markdown files.*
  - `def __init__(...)`
  - `def extract(...)`
  - `def _extract_one(...)`
  - `def format(...)`
  - `def load(...)`
- **Function** `def _find_section(...)`
- **Function** `def extract_blockquote(...)`
- **Function** `def extract_first_paragraph(...)`
- **Function** `def extract_all_h3(...)`
- **Function** `def extract_numbered_list(...)`
- **Function** `def extract_bulleted_list(...)`
- **Function** `def extract_bold_items(...)`
- **Function** `def extract_frontmatter(...)`
- **Function** `def extract_code_block(...)`
- **Function** `def extract_full_section(...)`

#### Module: `node_cycle.py`
*Node-Cycle binding operations (E2-154 scaffold-on-entry, E2-155 exit gates).*

- **Function** `def load_node_cycle_bindings(...)`
- **Function** `def get_node_binding(...)`
- **Function** `def detect_node_change(...)`
- **Function** `def check_doc_exists(...)`
- **Function** `def build_scaffold_command(...)`
- **Function** `def extract_work_id(...)`
- **Function** `def extract_title(...)`
- **Function** `def update_cycle_docs(...)`
- **Function** `def get_exit_criteria(...)`
- **Function** `def detect_node_exit_attempt(...)`
- **Function** `def check_exit_criteria(...)`
- **Function** `def _check_single_criterion(...)`
- **Function** `def build_exit_gate_warning(...)`

#### Module: `observations.py`
*Observation capture, triage, and retro-triage module for HAIOS.*

- **Function** `def validate_observations(...)`
- **Function** `def scaffold_observations(...)`
- **Function** `def scan_uncaptured_observations(...)`
- **Function** `def _find_observations_file(...)`
- **Function** `def parse_observations(...)`
- **Function** `def triage_observation(...)`
- **Function** `def scan_archived_observations(...)`
- **Function** `def promote_observation(...)`
- **Function** `def mark_triaged(...)`
- **Function** `def load_threshold_config(...)`
- **Function** `def get_observation_threshold(...)`
- **Function** `def get_pending_observation_count(...)`
- **Function** `def should_trigger_triage(...)`
- **Function** `def _ensure_parsed(...)`
- **Function** `def _rows_to_dicts(...)`
- **Function** `def query_retro_kss(...)`
- **Function** `def query_retro_bugs(...)`
- **Function** `def query_retro_features(...)`
- **Function** `def _normalize_directive(...)`
- **Function** `def _parse_kss_content(...)`
- **Function** `def aggregate_kss_frequency(...)`
- **Function** `def _parse_bug_feature_content(...)`
- **Function** `def surface_bug_candidates(...)`
- **Function** `def surface_feature_candidates(...)`

#### Module: `queue_ceremonies.py`
*Queue ceremony execution and event logging (CH-010, WORK-110).*

- **Function** `def _ceremony_context_safe(...)`
- **Function** `def log_queue_ceremony(...)`
- **Function** `def execute_queue_transition(...)`
- **Function** `def _append_event(...)`

#### Module: `retro_scale.py`
*Retro-cycle scale assessment (WORK-171).*

- **Function** `def _default_project_root(...)`
- **Function** `def _get_changed_files(...)`
- **Function** `def assess_scale(...)`

#### Module: `routing.py`
*Routing-gate module for HAIOS (E2-221).*

- **Function** `def determine_route(...)`

#### Module: `scaffold.py`
*DEPRECATED: Use GovernanceLayer.scaffold_template() instead.*

- **Function** `def _create_slug(...)`
- **Function** `def _work_file_exists(...)`
- **Function** `def _get_work_status(...)`
- **Function** `def _get_work_type(...)`
- **Function** `def _create_work_subdirs(...)`
- **Function** `def get_next_work_id(...)`
- **Function** `def generate_output_path(...)`
- **Function** `def load_template(...)`
- **Function** `def get_plan_type(...)`
- **Function** `def load_plan_template(...)`
- **Function** `def substitute_variables(...)`
- **Function** `def get_next_sequence_number(...)`
- **Function** `def get_current_session(...)`
- **Function** `def get_prev_session(...)`
- **Function** `def scaffold_template(...)`
- **Function** `def update_chapter_manifest(...)`
- **Function** `def _try_update_chapter_manifest(...)`

#### Module: `session_end_actions.py`
*Session-end actions for Stop hook (WORK-161: Session Boundary Fix).*

- **Function** `def _default_project_root(...)`
- **Function** `def read_session_number(...)`
- **Function** `def log_session_ended(...)`
- **Function** `def clear_cycle_state(...)`
- **Function** `def detect_uncommitted_changes(...)`

#### Module: `session_loader.py`
*Session Loader for Configuration Arc.*

- **Class** `SessionLoader`
  - *Extract session context from latest checkpoint + memory.*
  - `def __init__(...)`
  - `def _load_config(...)`
  - `def checkpoint_dir(...)`
  - `def _find_latest_checkpoint(...)`
  - `def _parse_frontmatter(...)`
  - `def _query_memory_ids(...)`
  - `def validate_pending_items(...)`
  - `def extract(...)`
  - `def format(...)`
  - `def load(...)`

#### Module: `spawn_ceremonies.py`
*Spawn ceremony execution and event logging (CH-017, WORK-137).*

- **Function** `def log_spawn_ceremony(...)`
- **Function** `def execute_spawn(...)`
- **Function** `def _update_parent_children(...)`
- **Function** `def _ceremony_context_safe(...)`
- **Function** `def _append_event(...)`

#### Module: `status.py`
*Core status module for HAIOS plugin.*

- **Function** `def _iter_work_files(...)`
- **Function** `def get_agents(...)`
- **Function** `def get_commands(...)`
- **Function** `def get_skills(...)`
- **Function** `def get_memory_stats(...)`
- **Function** `def get_backlog_stats(...)`
- **Function** `def _parse_checkpoint_yaml(...)`
- **Function** `def get_session_delta(...)`
- **Function** `def _find_completed_items(...)`
- **Function** `def get_milestone_progress(...)`
- **Function** `def get_blocked_items(...)`
- **Function** `def get_valid_templates(...)`
- **Function** `def get_live_files(...)`
- **Function** `def _parse_yaml_frontmatter(...)`
- **Function** `def get_outstanding_items(...)`
- **Function** `def get_stale_items(...)`
- **Function** `def get_workspace_summary(...)`
- **Function** `def check_alignment(...)`
- **Function** `def get_spawn_map(...)`
- **Function** `def get_work_items(...)`
- **Function** `def get_active_work_cycle(...)`
- **Function** `def generate_full_status(...)`
- **Function** `def generate_slim_status(...)`
- **Function** `def _get_active_work(...)`
- **Function** `def _load_existing_milestones(...)`
- **Function** `def _format_milestone_name(...)`
- **Function** `def _discover_milestones_from_backlog(...)`
- **Function** `def _discover_milestones_from_work_files(...)`
- **Function** `def _select_current_milestone(...)`
- **Function** `def write_slim_status(...)`
- **Function** `def write_full_status(...)`

#### Module: `status_propagator.py`
*Upstream Status Propagation (WORK-034).*

- **Class** `StatusPropagator`
  - *Upstream status propagation from work item closure to ARC.md chapter rows.*
  - `def __init__(...)`
  - `def propagate(...)`
  - `def get_hierarchy_context(...)`
  - `def is_chapter_complete(...)`
  - `def update_arc_chapter_status(...)`
  - `def is_arc_complete(...)`
  - `def _log_event(...)`

#### Module: `tier_detector.py`
*Governance Tier Detection (WORK-167).*

- **Function** `def _default_project_root(...)`
- **Function** `def _parse_frontmatter(...)`
- **Function** `def _has_adr_reference(...)`
- **Function** `def _plan_exists(...)`
- **Function** `def _log_tier_event(...)`
- **Function** `def detect_tier(...)`

#### Module: `validate.py`
*DEPRECATED: Use GovernanceLayer.validate_template() instead.*

- **Function** `def get_template_registry(...)`
- **Function** `def extract_yaml_header(...)`
- **Function** `def parse_yaml_full(...)`
- **Function** `def parse_yaml(...)`
- **Function** `def count_references(...)`
- **Function** `def get_expected_sections(...)`
- **Function** `def extract_sections(...)`
- **Function** `def is_placeholder_content(...)`
- **Function** `def check_section_coverage(...)`
- **Function** `def validate_cycle_docs_consistency(...)`
- **Function** `def validate_node_history_integrity(...)`
- **Function** `def validate_template(...)`
- **Function** `def classify_verification_type(...)`
- **Function** `def parse_ground_truth_table(...)`

#### Module: `work_item.py`
*DEPRECATED: This module is deprecated as of E2-298 (Session 201).*

- **Function** `def find_work_file(...)`
- **Function** `def update_work_file_status(...)`
- **Function** `def update_work_file_closed_date(...)`
- **Function** `def move_work_file_to_archive(...)`
- **Function** `def update_node(...)`
- **Function** `def add_document_link(...)`
- **Function** `def batch_update_fields(...)`
- **Function** `def link_spawned_items(...)`

#### Module: `work_loader.py`
*Work Loader for Configuration Arc.*

- **Class** `WorkLoader`
  - *Extract work context for coldstart Phase 3.*
  - `def __init__(...)`
  - `def _load_config(...)`
  - `def checkpoint_dir(...)`
  - `def _default_queue_fn(...)`
  - `def _parse_queue_output(...)`
  - `def _find_latest_checkpoint(...)`
  - `def _get_pending_from_checkpoint(...)`
  - `def _check_epoch_alignment(...)`
  - `def extract(...)`
  - `def format(...)`
  - `def load(...)`

### Directory: `haios_etl`

#### Module: `__init__.py`
*HAIOS ETL Pipeline - Agent Memory System*

*No classes or functions defined.*

#### Module: `cli.py`
- **Function** `def get_db_path(...)`
- **Function** `def cmd_status(...)`
- **Function** `def cmd_reset(...)`
- **Function** `def cmd_process(...)`
- **Function** `def cmd_synthesis(...)`
- **Function** `def cmd_refinement(...)`
- **Function** `def cmd_ingest(...)`
- **Function** `def main(...)`

#### Module: `database.py`
- **Class** `DatabaseManager`
  - `def __init__(...)`
  - `def get_connection(...)`
  - `def setup(...)`
  - `def insert_artifact(...)`
  - `def insert_entity(...)`
  - `def insert_concept(...)`
  - `def record_entity_occurrence(...)`
  - `def record_concept_occurrence(...)`
  - `def get_processing_status(...)`
  - `def get_artifact_hash(...)`
  - `def insert_quality_metrics(...)`
  - `def update_processing_status(...)`
  - `def insert_embedding(...)`
  - `def insert_concept_embedding(...)`
  - `def search_memories(...)`
  - `def get_stats(...)`
  - `def register_agent(...)`
  - `def get_agent(...)`
  - `def list_agents(...)`
  - `def get_schema_info(...)`
  - `def _list_tables(...)`
  - `def query_read_only(...)`

#### Module: `errors.py`
*Error Handling and Logging*

*No classes or functions defined.*

#### Module: `extraction.py`
- **Class** `Entity`
- **Class** `Concept`
- **Class** `ExtractionResult`
- **Class** `ExtractionError`
  - *Custom exception for extraction failures.*
- **Class** `ErrorType`
  - *Classification of extraction errors.*
- **Class** `ExtractionConfig`
  - *Configuration for extraction with error handling.*
- **Class** `ExtractionManager`
  - `def __init__(...)`
  - `def _build_prompt(...)`
  - `def _build_examples(...)`
  - `def _classify_error(...)`
  - `def _apply_preprocessors(...)`
  - `def extract_from_file(...)`
  - `def embed_content(...)`
  - `def extract_strategy(...)`

#### Module: `health_checks.py`
*System Health Checks for HAIOS Process Observability (E2-011 Phase 3).*

- **Class** `DBHealth`
  - *Database health status.*
  - `def to_dict(...)`
- **Class** `MemoryHealth`
  - *Memory health status.*
  - `def to_dict(...)`
- **Class** `MCPHealth`
  - *MCP server health status.*
  - `def to_dict(...)`
- **Class** `HealthStatus`
  - *Overall health status combining all checks.*
  - `def to_dict(...)`
- **Class** `HealthChecker`
  - *Health checker for HAIOS system components.*
  - `def __init__(...)`
  - `def check_db_health(...)`
  - `def check_memory_health(...)`
  - `def check_mcp_health(...)`
  - `def _ping_mcp(...)`
  - `def full_health_check(...)`

#### Module: `job_registry.py`
*Background Job Registry for HAIOS Process Observability (E2-011 Phase 2).*

- **Class** `JobInfo`
  - *Information about a background job.*
  - `def to_dict(...)`
  - `def from_dict(...)`
- **Class** `JobRegistry`
  - *Registry for tracking background jobs.*
  - `def __init__(...)`
  - `def _load(...)`
  - `def _save(...)`
  - `def register(...)`
  - `def deregister(...)`
  - `def list_jobs(...)`
  - `def get_job(...)`
  - `def update_status(...)`
  - `def clear_completed(...)`

#### Module: `mcp_server.py`
- **Function** `def memory_search_with_experience(...)`
- **Function** `def memory_stats(...)`
- **Function** `def marketplace_list_agents(...)`
- **Function** `def marketplace_get_agent(...)`
- **Function** `def memory_store(...)`
- **Function** `def extract_content(...)`
- **Function** `def interpreter_translate(...)`
- **Function** `def ingester_ingest(...)`
- **Function** `def schema_info(...)`
- **Function** `def db_query(...)`

#### Module: `processing.py`
- **Class** `BatchProcessor`
  - `def __init__(...)`
  - `def process_file(...)`
- **Function** `def read_file_safely(...)`
- **Function** `def compute_file_hash(...)`

#### Module: `quality.py`
*Quality and Metrics Layer*

*No classes or functions defined.*

#### Module: `refinement.py`
- **Class** `RefinementResult`
- **Class** `RefinementManager`
  - `def __init__(...)`
  - `def scan_raw_memories(...)`
  - `def _classify_with_llm(...)`
  - `def refine_memory(...)`
  - `def save_refinement(...)`
  - `def _set_metadata(...)`
  - `def _get_or_create_episteme(...)`
  - `def _link_memories(...)`

#### Module: `retrieval.py`
- **Class** `RetrievalService`
  - *Core retrieval service implementing Hybrid Search (Vector + Metadata).*
  - `def __init__(...)`
  - `def search(...)`
  - `def _generate_embedding(...)`
- **Class** `ReasoningAwareRetrieval`
  - *Retrieval service with ReasoningBank-style experience learning.*
  - `def search_with_experience(...)`
  - `def find_similar_reasoning_traces(...)`
  - `def _determine_strategy(...)`
  - `def record_reasoning_trace(...)`

#### Module: `synthesis.py`
*Memory Synthesis Pipeline - Phase 9 Enhancement*

- **Class** `SynthesisResult`
  - *Result of synthesizing a cluster of memories.*
- **Class** `ClusterInfo`
  - *Information about a memory cluster.*
- **Class** `SynthesisStats`
  - *Statistics about synthesis pipeline state.*
- **Class** `SynthesisManager`
  - *Manages memory consolidation and synthesis.*
  - `def __init__(...)`
  - `def find_similar_concepts(...)`
  - `def find_similar_traces(...)`
  - `def _build_clusters(...)`
  - `def _parse_embedding(...)`
  - `def _cosine_similarity(...)`
  - `def synthesize_cluster(...)`
  - `def _get_concept_contents(...)`
  - `def _get_trace_contents(...)`
  - `def _build_concept_synthesis_prompt(...)`
  - `def _build_trace_synthesis_prompt(...)`
  - `def _call_synthesis_llm(...)`
  - `def store_synthesis(...)`
  - `def _save_cluster(...)`
  - `def _bridge_exists(...)`
  - `def find_cross_type_overlaps(...)`
  - `def create_bridge_insight(...)`
  - `def mark_as_synthesized(...)`
  - `def run_synthesis_pipeline(...)`
  - `def get_synthesis_stats(...)`

## 3. CLI Commands and Tools

### `commands/`
- `README.md`
- `close.md`
- `coldstart.md`
- `critique.md`
- `haios.md`
- `implement.md`
- `new-adr.md`
- `new-checkpoint.md`
- `new-handoff.md`
- `new-investigation.md`
- `new-plan.md`
- `new-report.md`
- `new-work.md`
- `ready.md`
- `reason.md`
- `schema.md`
- `status.md`
- `tree.md`
- `validate.md`
- `workspace.md`

### `tools/`
- `Get-ValidationSummary.ps1`
