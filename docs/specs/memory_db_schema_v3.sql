-- generated: 2025-11-30
-- System Auto: last updated on: 2025-11-30 17:25:14
-- memory_db_schema_v3.sql
-- Unified schema for the HAIOS agent memory database (v3).
-- Created: 2025-11-30
-- Author: Hephaestus (Session 16)
-- Plan: PLAN-FIX-001 (Schema Source-of-Truth Restoration)
--
-- This is the AUTHORITATIVE source of truth for all database tables.
-- All test fixtures and database initialization MUST derive from this file.
--
-- Changes from v2:
--   - Added space_id to artifacts (Phase 6)
--   - Added embeddings table (Phase 4)
--   - Added reasoning_traces table with strategy columns (Phase 4, 15)
--   - Added memory_metadata table (Phase 8)
--   - Added memory_relationships table with CHECK constraint (Phase 8)
--   - Added synthesis_source_count to concepts (Phase 9)
--   - Added synthesis tables with CHECK and FK constraints (Phase 9)
--   - Fixed synthesis_provenance.source_type to include 'cross' (DD-011)
--
-- Design Decisions:
--   - DD-010: This file is the single source of truth
--   - DD-011: source_type includes 'cross' for bridge insights

-- =============================================================================
-- CORE TABLES (Phase 3 ETL)
-- =============================================================================

-- Table: artifacts
-- Stores information about source files processed by the ETL pipeline.
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_hash TEXT NOT NULL,                    -- SHA256 hash for change detection
    last_processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,                  -- Increment on re-processing
    space_id TEXT                               -- Optional space scoping (Phase 6)
);

-- Table: entities
-- Stores extracted entities (User, Agent, ADR, etc.).
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'User', 'Agent', 'ADR'
    value TEXT NOT NULL,
    UNIQUE(type, value)
);

-- Table: entity_occurrences
-- Links entities to their source artifacts.
CREATE TABLE IF NOT EXISTS entity_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

-- Table: concepts
-- Stores extracted concepts (Directive, Proposal, Critique, etc.).
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'Directive', 'Proposal', 'Critique', 'SynthesizedInsight'
    content TEXT NOT NULL,
    source_adr TEXT,                            -- For 'Decision' concepts
    -- Synthesis columns (Phase 9)
    synthesis_source_count INTEGER DEFAULT 0,   -- Number of sources synthesized
    synthesis_confidence REAL,                  -- Confidence score 0.0-1.0
    synthesized_at TIMESTAMP,                   -- When synthesis occurred
    synthesis_cluster_id INTEGER                -- Link to synthesis cluster
);

-- Table: concept_occurrences
-- Links concepts to their source artifacts.
CREATE TABLE IF NOT EXISTS concept_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Table: processing_log
-- Tracks processing status for batch processing and resume capability.
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending', 'success', 'error', 'skipped')),
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    file_hash TEXT                              -- SHA256 hash for change detection
);

-- Table: quality_metrics
-- Stores quality metrics for each processed file.
CREATE TABLE IF NOT EXISTS quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entities_extracted INTEGER DEFAULT 0,
    concepts_extracted INTEGER DEFAULT 0,
    processing_time_seconds REAL,
    llm_tokens_used INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
);

-- =============================================================================
-- RETRIEVAL TABLES (Phase 4 ReasoningBank)
-- =============================================================================

-- Table: embeddings
-- Stores vector embeddings for semantic search.
CREATE TABLE IF NOT EXISTS embeddings (
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
);

-- Table: reasoning_traces
-- Stores reasoning traces for experience learning (ReasoningBank pattern).
CREATE TABLE IF NOT EXISTS reasoning_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    query_embedding BLOB,                       -- For similarity search
    approach_taken TEXT NOT NULL,
    strategy_details JSON,                      -- Detailed strategy parameters
    outcome TEXT CHECK(outcome IN ('success', 'partial_success', 'failure')),
    failure_reason TEXT,
    success_factors JSON,
    memories_used JSON,                         -- Which memories were retrieved
    memories_helpful JSON,                      -- Which were actually useful
    context_snapshot JSON,
    execution_time_ms INTEGER,
    model_used TEXT,
    space_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    similar_to_trace_id INTEGER,                -- Link to similar past reasoning
    -- Strategy extraction columns (Phase 15)
    strategy_title TEXT,
    strategy_description TEXT,
    strategy_content TEXT,
    extraction_model TEXT,
    FOREIGN KEY (similar_to_trace_id) REFERENCES reasoning_traces(id) ON DELETE SET NULL
);

-- =============================================================================
-- KNOWLEDGE LAYER TABLES (Phase 8 Refinement)
-- =============================================================================

-- Table: memory_metadata
-- Stores key-value metadata for memories (Greek Triad taxonomy, etc.).
CREATE TABLE IF NOT EXISTS memory_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES artifacts(id) ON DELETE CASCADE
);

-- Table: memory_relationships
-- Stores relationships between memories.
CREATE TABLE IF NOT EXISTS memory_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('implements', 'justifies', 'derived_from', 'supports', 'contradicts', 'related')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES artifacts(id) ON DELETE CASCADE
);

-- =============================================================================
-- SYNTHESIS TABLES (Phase 9 Memory Synthesis)
-- =============================================================================

-- Table: synthesis_clusters
-- Tracks clusters of similar memories for synthesis.
CREATE TABLE IF NOT EXISTS synthesis_clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_type TEXT NOT NULL CHECK(cluster_type IN ('concept', 'trace', 'cross')),
    centroid_embedding BLOB,
    member_count INTEGER DEFAULT 0,
    synthesized_concept_id INTEGER,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'synthesized', 'skipped')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synthesized_at TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE SET NULL
);

-- Table: synthesis_cluster_members
-- Tracks which memories belong to which clusters.
CREATE TABLE IF NOT EXISTS synthesis_cluster_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace', 'cross')),
    member_id INTEGER NOT NULL,
    similarity_to_centroid REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
);

-- Table: synthesis_provenance
-- Tracks what was synthesized into what (provenance chain).
-- NOTE: source_type includes 'cross' for bridge insights (DD-011)
CREATE TABLE IF NOT EXISTS synthesis_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthesized_concept_id INTEGER NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
    source_id INTEGER NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Core table indexes
CREATE INDEX IF NOT EXISTS idx_artifacts_file_hash ON artifacts(file_hash);
CREATE INDEX IF NOT EXISTS idx_artifacts_space_id ON artifacts(space_id);
CREATE INDEX IF NOT EXISTS idx_entities_type_value ON entities(type, value);
CREATE INDEX IF NOT EXISTS idx_entity_occurrences_artifact_id ON entity_occurrences(artifact_id);
CREATE INDEX IF NOT EXISTS idx_concept_occurrences_artifact_id ON concept_occurrences(artifact_id);
CREATE INDEX IF NOT EXISTS idx_processing_log_status ON processing_log(status);

-- Embedding indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_artifact ON embeddings(artifact_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_concept ON embeddings(concept_id);

-- Reasoning trace indexes
CREATE INDEX IF NOT EXISTS idx_reasoning_approach ON reasoning_traces(approach_taken);
CREATE INDEX IF NOT EXISTS idx_reasoning_outcome ON reasoning_traces(outcome, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reasoning_space ON reasoning_traces(space_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reasoning_model ON reasoning_traces(model_used);
CREATE INDEX IF NOT EXISTS idx_reasoning_has_strategy ON reasoning_traces(strategy_title) WHERE strategy_title IS NOT NULL;

-- Metadata indexes
CREATE INDEX IF NOT EXISTS idx_metadata_memory_id ON memory_metadata(memory_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON memory_metadata(key);

-- Relationship indexes
CREATE INDEX IF NOT EXISTS idx_relationships_source ON memory_relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON memory_relationships(target_id);

-- Synthesis indexes
CREATE INDEX IF NOT EXISTS idx_concepts_cluster ON concepts(synthesis_cluster_id) WHERE synthesis_cluster_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_concepts_synthesized ON concepts(synthesized_at) WHERE synthesized_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_type ON synthesis_clusters(cluster_type);
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_status ON synthesis_clusters(status);
CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id);
CREATE INDEX IF NOT EXISTS idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id);
CREATE INDEX IF NOT EXISTS idx_provenance_synthesized ON synthesis_provenance(synthesized_concept_id);
CREATE INDEX IF NOT EXISTS idx_provenance_source ON synthesis_provenance(source_type, source_id);

-- ==================================================================================
-- 7. AGENT ECOSYSTEM (Session 17)
-- ==================================================================================

-- Registry for Agents (Subagents, Workers, etc.)
CREATE TABLE IF NOT EXISTS agent_registry (
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
);

-- Registry for Skills (Capabilities provided by Agents)
CREATE TABLE IF NOT EXISTS skill_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    provider_agent_id TEXT,
    parameters JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(provider_agent_id) REFERENCES agent_registry(id)
);

-- Index for capability search
CREATE INDEX IF NOT EXISTS idx_agent_capabilities ON agent_registry(capabilities);
