-- generated: 2025-11-29
-- System Auto: last updated on: 2025-11-30 17:26:49
-- Migration: 007_add_synthesis_tables
-- Description: Adds tables and columns for Memory Synthesis Pipeline (Phase 9)
-- Date: 2025-11-29
-- Plan: PLAN-SYNTHESIS-001

-- Add synthesis-specific columns to concepts table
-- These track synthesized concepts and their provenance
ALTER TABLE concepts ADD COLUMN synthesis_source_count INTEGER DEFAULT 0;
ALTER TABLE concepts ADD COLUMN synthesis_confidence REAL;
ALTER TABLE concepts ADD COLUMN synthesized_at TIMESTAMP;
ALTER TABLE concepts ADD COLUMN synthesis_cluster_id INTEGER;

-- Create synthesis_clusters table for batch tracking
-- Clusters group similar memories before synthesis
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

-- Create synthesis_cluster_members for tracking cluster membership
CREATE TABLE IF NOT EXISTS synthesis_cluster_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace')),
    member_id INTEGER NOT NULL,
    similarity_to_centroid REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
);

-- Create synthesis_provenance for tracking what was synthesized into what
-- This is separate from memory_relationships to avoid schema conflicts
CREATE TABLE IF NOT EXISTS synthesis_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthesized_concept_id INTEGER NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
    source_id INTEGER NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_concepts_synthesized ON concepts(synthesized_at) WHERE synthesized_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_concepts_cluster ON concepts(synthesis_cluster_id) WHERE synthesis_cluster_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_type ON synthesis_clusters(cluster_type);
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_status ON synthesis_clusters(status);
CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id);
CREATE INDEX IF NOT EXISTS idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id);
CREATE INDEX IF NOT EXISTS idx_provenance_synthesized ON synthesis_provenance(synthesized_concept_id);
CREATE INDEX IF NOT EXISTS idx_provenance_source ON synthesis_provenance(source_type, source_id);
