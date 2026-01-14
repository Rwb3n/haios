-- generated: 2025-11-30
-- System Auto: last updated on: 2025-11-30 17:27:11
-- Migration: 008_add_synthesis_constraints
-- Description: Adds CHECK and FOREIGN KEY constraints to synthesis tables
-- Date: 2025-11-30
-- Plan: PLAN-FIX-001 (Schema Source-of-Truth Restoration)
-- Fixes: Schema drift discovered in PLAN-INVESTIGATION-001
--
-- Background:
--   Migration 007 defined constraints, but they were not applied to live DB.
--   This migration recreates tables WITH constraints.
--
-- Design Decisions:
--   DD-011: source_type includes 'cross' for bridge insights

-- SQLite does not support ALTER TABLE ADD CONSTRAINT
-- Must recreate tables with constraints

-- =============================================================================
-- Step 1: Rename existing tables
-- =============================================================================

ALTER TABLE synthesis_clusters RENAME TO synthesis_clusters_old;
ALTER TABLE synthesis_cluster_members RENAME TO synthesis_cluster_members_old;
ALTER TABLE synthesis_provenance RENAME TO synthesis_provenance_old;

-- =============================================================================
-- Step 2: Create new tables WITH constraints
-- =============================================================================

-- Table: synthesis_clusters (with CHECK constraints)
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
);

-- Table: synthesis_cluster_members (with CHECK constraint)
CREATE TABLE synthesis_cluster_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace')),
    member_id INTEGER NOT NULL,
    similarity_to_centroid REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
);

-- Table: synthesis_provenance (with CHECK constraint including 'cross' per DD-011)
CREATE TABLE synthesis_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthesized_concept_id INTEGER NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
    source_id INTEGER NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- =============================================================================
-- Step 3: Copy data (preserves existing data if any)
-- =============================================================================

INSERT INTO synthesis_clusters SELECT * FROM synthesis_clusters_old;
INSERT INTO synthesis_cluster_members SELECT * FROM synthesis_cluster_members_old;
INSERT INTO synthesis_provenance SELECT * FROM synthesis_provenance_old;

-- =============================================================================
-- Step 4: Drop old tables
-- =============================================================================

DROP TABLE synthesis_clusters_old;
DROP TABLE synthesis_cluster_members_old;
DROP TABLE synthesis_provenance_old;

-- =============================================================================
-- Step 5: Recreate indexes
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_type ON synthesis_clusters(cluster_type);
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_status ON synthesis_clusters(status);
CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id);
CREATE INDEX IF NOT EXISTS idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id);
CREATE INDEX IF NOT EXISTS idx_provenance_synthesized ON synthesis_provenance(synthesized_concept_id);
CREATE INDEX IF NOT EXISTS idx_provenance_source ON synthesis_provenance(source_type, source_id);

-- =============================================================================
-- Step 6: Add missing column to concepts if not exists
-- =============================================================================

-- Note: ALTER TABLE ADD COLUMN IF NOT EXISTS is not supported in SQLite
-- This will fail silently if column already exists (which is fine)
-- If you get an error, the column already exists
-- ALTER TABLE concepts ADD COLUMN synthesis_source_count INTEGER DEFAULT 0;
