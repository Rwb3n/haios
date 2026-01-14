-- Migration: 001_add_reasoning_traces
-- Description: Adds the reasoning_traces table for ReasoningBank integration.
-- Date: 2025-11-24

CREATE TABLE IF NOT EXISTS reasoning_traces (
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
    similar_to_trace_id INTEGER,  -- Link to similar past reasoning
    FOREIGN KEY (similar_to_trace_id) REFERENCES reasoning_traces(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reasoning_approach ON reasoning_traces(approach_taken);
CREATE INDEX IF NOT EXISTS idx_reasoning_outcome ON reasoning_traces(outcome, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reasoning_space ON reasoning_traces(space_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reasoning_model ON reasoning_traces(model_used);
