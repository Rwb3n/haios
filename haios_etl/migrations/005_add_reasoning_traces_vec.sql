-- generated: 2025-11-27
-- System Auto: last updated on: 2025-11-27 23:04:59
-- Migration: 005_add_reasoning_traces_vec
-- Description: Adds vec0 virtual table for vector search on reasoning traces.
-- Date: 2025-11-27
-- Design Decision: DD-002 - Infrastructure for future scale, direct search for MVP

-- Create vec0 virtual table for optimized vector search on reasoning traces
-- Note: This is infrastructure for when traces exceed 10k rows
-- Current implementation uses direct vec_distance_cosine() on the column
CREATE VIRTUAL TABLE IF NOT EXISTS reasoning_traces_vec USING vec0(
    trace_id INTEGER PRIMARY KEY,
    query_embedding FLOAT[768]
);

-- Populate from existing traces that have embeddings
-- This is idempotent - vec0 handles duplicates gracefully
INSERT OR IGNORE INTO reasoning_traces_vec (trace_id, query_embedding)
SELECT id, query_embedding
FROM reasoning_traces
WHERE query_embedding IS NOT NULL;

-- Create trigger to keep vec0 table in sync with reasoning_traces
-- When a new trace is inserted with an embedding, add to vec0
CREATE TRIGGER IF NOT EXISTS sync_reasoning_traces_vec_insert
AFTER INSERT ON reasoning_traces
WHEN NEW.query_embedding IS NOT NULL
BEGIN
    INSERT OR REPLACE INTO reasoning_traces_vec (trace_id, query_embedding)
    VALUES (NEW.id, NEW.query_embedding);
END;

-- When a trace embedding is updated, update vec0
CREATE TRIGGER IF NOT EXISTS sync_reasoning_traces_vec_update
AFTER UPDATE OF query_embedding ON reasoning_traces
WHEN NEW.query_embedding IS NOT NULL
BEGIN
    INSERT OR REPLACE INTO reasoning_traces_vec (trace_id, query_embedding)
    VALUES (NEW.id, NEW.query_embedding);
END;
