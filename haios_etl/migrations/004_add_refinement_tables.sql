-- Migration 004: Add Refinement Tables
-- Created: 2025-11-27
-- Description: Adds memory_metadata and memory_relationships tables for the Knowledge Refinement Layer.

-- memory_metadata
CREATE TABLE IF NOT EXISTS memory_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(memory_id) REFERENCES artifacts(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_metadata_memory_id ON memory_metadata(memory_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON memory_metadata(key);

-- memory_relationships
CREATE TABLE IF NOT EXISTS memory_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('implements', 'justifies', 'derived_from', 'supports', 'contradicts', 'related')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES artifacts(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON memory_relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON memory_relationships(target_id);
