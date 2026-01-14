---
template: implementation_plan
status: approved
date: 2025-12-06
backlog_id: E2-003
title: "PLAN-EPOCH2-003: Memory Integration & Audit"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-08 22:53:09
# Implementation Plan: Memory Integration & Audit

@docs/README.md
@.claude/hooks/memory_retrieval.py

> **ID:** PLAN-EPOCH2-003-MEMORY-INTEGRATION
> **Status:** Draft (ENHANCED by Hephaestus - 2025-12-06)
> **Author:** Genesis (Architect)
> **Target:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement (Turn-by-Turn Execution)

## 1. Goal
Verify and stabilize the Memory System Integration to ensure "ReasoningBank" data is legitimately being used in turn-by-turn execution, avoiding the "Building Infrastructure During Business UI" (BIDBUI) anti-pattern.

## 2. Problem Statement (VERIFIED CORRECT + ENHANCED)
We have a sophisticated `memory_retrieval.py` script and `UserPromptSubmit` hook, but we lack visibility into whether they are actually effective.

**Specific unknowns:**
- Is `memory_retrieval.py` being called at all? (PowerShell silent fail)
- Is it timing out (5s limit)?
- Is it returning data? If so, how much?
- Is the agent actually *using* the injected context?
- Is `reasoning_extraction.py` storing new traces at session end?

**Evidence of gap:** We see "Today is Saturday..." (Part 1 of hook) but NEVER see memory context (Part 2). This suggests Part 2 is silently failing.

## 3. Proposed Changes

### 3.1. Create `/memory-stats` Slash Command
Create `.claude/commands/memory-stats.md` to expose the health of the vector db.

**Command Specification:**
```markdown
---
allowed-tools: Bash
description: Check the status of the HAIOS Memory System (Embeddings count, DB size)
---

# Memory Stats

Ref: @.claude/mcp/haios_memory_mcp.md

Run the following diagnostics:
1. Check DB File size: `ls -lh haios_memory.db`
2. Run Stats Script (if available) or SQL query:
   ! `sqlite3 haios_memory.db "SELECT count(*) FROM memories;"`
   ! `sqlite3 haios_memory.db "SELECT count(*) FROM vec_items;"`

Report the summary of "Total Memories" and "Vectorized Memories".
```

### 3.2. Add Diagnostic Logging (CRITICAL - see PLAN-001)
Update both Python scripts to log execution:

**memory_retrieval.py logging:**
- Timestamp, query received, results count, latency
- Log to `.claude/logs/memory_retrieval.log`

**reasoning_extraction.py logging:**
- Timestamp, transcript path, extraction result, store success
- Log to `.claude/logs/reasoning_extraction.log`

This enables post-hoc debugging without slowing down the agent loop.

### 3.3. Verify MCP Server Availability
The `memory_retrieval.py` script should use the MCP server tools (already exposed). Verify:
```bash
# Check if MCP server tools are available
python -c "from haios_etl.mcp_server import mcp; print(mcp.list_tools())"
```

## 4. Verification Plan

### 4.1 Audit via Command
1.  Run `/memory-stats`.
2.  Expectation: Returns a non-zero count of memories. If zero, we know the "Cold Start" problem is real and needs an ETL run (which is a separate task).

## 5. Risks
*   **Locked DB:** `sqlite3` command might fail if the DB is currently locked by the MCP server or another hook.


<!-- VALIDATION ERRORS (2025-12-06 14:57:41):
  - ERROR: Missing 'template' field in YAML header
  - ERROR: Only 1 @ reference(s) found (minimum 2 required)
-->


<!-- VALIDATION ERRORS (2025-12-06 14:57:56):
  - ERROR: Missing 'template' field in YAML header
  - ERROR: Only 1 @ reference(s) found (minimum 2 required)
-->
