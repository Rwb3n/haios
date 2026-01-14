-- generated: 2025-11-28
-- System Auto: last updated on: 2025-11-28 00:16:22
-- Migration: 006_add_strategy_columns
-- Description: Adds strategy extraction columns to reasoning_traces per ReasoningBank paper.
-- The paper stores {title, description, content} for learned strategies, not execution logs.
-- Date: 2025-11-28

-- Strategy columns: stores WHAT WAS LEARNED, not what happened
ALTER TABLE reasoning_traces ADD COLUMN strategy_title TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_description TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_content TEXT;

-- Track which model extracted the strategy
ALTER TABLE reasoning_traces ADD COLUMN extraction_model TEXT;

-- Index for finding traces with strategies
CREATE INDEX IF NOT EXISTS idx_reasoning_has_strategy ON reasoning_traces(strategy_title) WHERE strategy_title IS NOT NULL;
