-- generated: 2025-10-19
-- System Auto: last updated on: 2025-10-19 17:02:41
-- memory_db_schema_v2.sql
-- Enhanced schema for the agent memory database (v2).
-- Created: 2025-10-19
-- Changes from v1:
--   - Added file_hash to artifacts for change detection
--   - Added version to artifacts for tracking re-processing
--   - Added processing_log table for batch processing and resume capability
--   - Added quality_metrics table for data quality tracking

-- Table to store information about the source artifacts (files).
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_hash TEXT NOT NULL,                    -- SHA256 hash for change detection
    last_processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1                   -- Increment on re-processing
);

-- Table to store the extracted entities.
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'User', 'Agent', 'ADR'
    value TEXT NOT NULL,
    UNIQUE(type, value)
);

-- Table to store occurrences of entities within artifacts.
CREATE TABLE entity_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY (entity_id) REFERENCES entities (id)
);

-- Table to store the extracted concepts.
CREATE TABLE concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                         -- e.g., 'Directive', 'Proposal', 'Critique'
    content TEXT NOT NULL,
    source_adr TEXT                             -- For 'Decision' concepts
);

-- Table to store occurrences of concepts within artifacts.
CREATE TABLE concept_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    line_number INTEGER,
    context_snippet TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY (concept_id) REFERENCES concepts (id)
);

-- Table to track processing status for batch processing and resume capability.
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending', 'success', 'error', 'skipped')),
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    file_hash TEXT                              -- SHA256 hash for change detection
);

-- Table to store quality metrics for each processed file.
CREATE TABLE quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER NOT NULL,
    entities_extracted INTEGER DEFAULT 0,
    concepts_extracted INTEGER DEFAULT 0,
    processing_time_seconds REAL,
    llm_tokens_used INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
);

-- Indexes for faster queries.
CREATE INDEX idx_entities_type_value ON entities (type, value);
CREATE INDEX idx_entity_occurrences_artifact_id ON entity_occurrences (artifact_id);
CREATE INDEX idx_concept_occurrences_artifact_id ON concept_occurrences (artifact_id);
CREATE INDEX idx_processing_log_status ON processing_log (status);
CREATE INDEX idx_artifacts_file_hash ON artifacts (file_hash);
