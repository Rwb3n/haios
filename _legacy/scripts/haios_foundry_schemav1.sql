-- =============================================================================
-- HAiOS Foundry Database Schema v1.1
-- Target Engine: SQLite
-- Description: This script creates all necessary tables for the
--              Minimum Viable Foundry.
--              V1.1: Removed explicit BEGIN/COMMIT transaction statements to
--              comply with the implicit transaction handling of the sqlite3 CLI.
-- =============================================================================

-- PRAGMA to enforce foreign key constraints, best practice for SQLite.
PRAGMA foreign_keys = ON;

-- =============================================================================
-- 1. Core Governance & Tracking Tables
-- =============================================================================

-- Tracks high-level projects like "Canon Hardening"
CREATE TABLE initiatives (
    initiative_id     TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    description       TEXT,
    status            TEXT NOT NULL, -- 'ACTIVE', 'BLUEPRINT', 'ARCHIVED'
    g_created         INTEGER NOT NULL,
    g_last_modified   INTEGER NOT NULL
);

-- Corresponds to our exec_plan artifacts
CREATE TABLE execution_plans (
    plan_id           TEXT PRIMARY KEY,
    initiative_id     TEXT REFERENCES initiatives(initiative_id),
    title             TEXT NOT NULL,
    status            TEXT NOT NULL, -- 'PENDING', 'ACTIVE', 'COMPLETED', 'FAILED'
    plan_body         TEXT, -- Can store Markdown or JSON of the plan steps
    g_created         INTEGER NOT NULL
);

-- A direct implementation of human_attention_queue.txt
CREATE TABLE human_attention_queue (
    queue_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    priority          TEXT NOT NULL, -- 'P0', 'P1', 'P2'
    task_description  TEXT NOT NULL,
    related_initiative_id TEXT REFERENCES initiatives(initiative_id),
    related_plan_id   TEXT REFERENCES execution_plans(plan_id),
    status            TEXT NOT NULL, -- 'OPEN', 'IN_PROGRESS', 'DONE'
    g_created         INTEGER NOT NULL
);


-- =============================================================================
-- 2. The Research Library Tables (The "Oyster Method")
-- =============================================================================

-- The "Sand": Stores raw, immutable data fetched from arXiv
CREATE TABLE research_library_source (
    arxiv_id          TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    authors           TEXT,
    abstract          TEXT,
    category          TEXT, -- e.g., 'cs.DC'
    pdf_url           TEXT,
    g_ingested        INTEGER NOT NULL
);

-- The "Pearls": Stores our value-add analysis artifacts
CREATE TABLE research_analysis_reports (
    analysis_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id          TEXT UNIQUE REFERENCES research_library_source(arxiv_id),
    status            TEXT NOT NULL, -- 'PENDING_ANALYSIS', 'ANALYSIS_COMPLETE', 'ACTIONABLE'
    priority          TEXT NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
    analyst_id        TEXT,
    synthesis         TEXT, -- Analyst's TL;DR
    strategic_implications TEXT,
    g_created         INTEGER NOT NULL,
    g_last_modified   INTEGER NOT NULL
);

-- Captures the key takeaways and new questions from our analysis
CREATE TABLE actionable_intelligence (
    intelligence_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id       INTEGER NOT NULL REFERENCES research_analysis_reports(analysis_id),
    intelligence_type TEXT NOT NULL, -- 'INSIGHT_INTEGRATE', 'QUESTION_REVEALED'
    content           TEXT NOT NULL,
    related_adr_id    TEXT,
    status            TEXT NOT NULL -- 'OPEN', 'IN_PROGRESS', 'RESOLVED'
);


-- =============================================================================
-- 3. ADR Clarification Tracking Tables ("Canon Hardening")
-- =============================================================================

-- Tracks the overall state of each clarification document
CREATE TABLE adr_clarification_records (
    record_id         TEXT PRIMARY KEY, -- e.g., 'ADR-OS-001'
    subject           TEXT,
    status            TEXT NOT NULL, -- 'DRAFT', 'PENDING_REVIEW', 'ACCEPTED'
    g_last_modified   INTEGER NOT NULL
);

-- Tracks the state of each individual question within a record
CREATE TABLE clarification_questions (
    question_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id         TEXT NOT NULL REFERENCES adr_clarification_records(record_id),
    question_number   INTEGER NOT NULL,
    question_text     TEXT NOT NULL,
    status            TEXT NOT NULL, -- 'OPEN', 'ANSWERING', 'AWAITING_REVIEW', 'DONE'
    g_created         INTEGER NOT NULL,
    UNIQUE(record_id, question_number)
);