---
template: implementation_plan
status: approved
date: 2025-12-06
backlog_id: E2-001
title: "PLAN-EPOCH2-001: Debug Hooks Python Scripts"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-08 22:52:45
# Implementation Plan: Debug Hooks Python Scripts

@docs/README.md
@.claude/hooks/README.md

> **ID:** PLAN-EPOCH2-001-HOOKS-WIRING
> **Status:** Draft (CORRECTED by Hephaestus - 2025-12-06)
> **Author:** Genesis (Architect), Hephaestus (Corrections)
> **Target:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement (Turn-by-Turn Execution)

## 1. Goal
Debug and verify the Python scripts called by governance hooks to ensure memory retrieval and reasoning extraction are actually functioning.

## 2. Problem Statement (CORRECTED)

~~The hook scripts exist in `.claude/hooks/` but are currently "dead code" because there is no `.claude/settings.json`~~

**CORRECTION:** Hooks ARE configured in `.claude/settings.local.json` and ARE firing:
- `UserPromptSubmit.ps1` - Part 1 (date/time) WORKS, Part 2 (memory_retrieval.py) UNKNOWN
- `Stop.ps1` - Calls reasoning_extraction.py - UNKNOWN if working
- `PostToolUse.ps1` + `ValidateTemplateHook.ps1` - WORKING (timestamps added)

**The Real Problem:** The Python scripts fail silently by design:
- `memory_retrieval.py` - 5s timeout, catches all exceptions, no logging
- `reasoning_extraction.py` - 10s timeout, catches all exceptions, no logging

We have ZERO visibility into whether these scripts:
1. Execute successfully
2. Time out
3. Return useful data
4. Store anything to the database

## 3. Proposed Changes

### 3.1. Add Diagnostic Logging to memory_retrieval.py
Add a log file to track execution:
- Log when script starts
- Log query received
- Log search results (count, latency)
- Log errors with stack traces

**Log Location:** `.claude/logs/memory_retrieval.log`

### 3.2. Add Diagnostic Logging to reasoning_extraction.py
Add a log file to track execution:
- Log when script starts
- Log transcript path received
- Log extraction results (strategy found, stored)
- Log errors with stack traces

**Log Location:** `.claude/logs/reasoning_extraction.log`

### 3.3. Manual Script Verification
Before adding logging, test scripts directly:
```bash
# Test memory retrieval
python .claude/hooks/memory_retrieval.py "test query about authentication"

# Test reasoning extraction (needs valid transcript path)
python .claude/hooks/reasoning_extraction.py "<transcript_path>"
```

## 4. Verification Plan

### 4.1 Direct Script Test: memory_retrieval.py
1. Run directly: `python .claude/hooks/memory_retrieval.py "how does authentication work"`
2. Expected: Returns TOON-encoded memory context OR error message
3. If silent/empty: Script is failing - check imports, DB path, API keys

### 4.2 Direct Script Test: reasoning_extraction.py
1. Find a recent transcript: `ls ~/.claude/projects/*/`
2. Run directly: `python .claude/hooks/reasoning_extraction.py "<transcript_path>"`
3. Expected: Returns extraction summary OR error message
4. If silent/empty: Script is failing - check imports, DB path, API keys

### 4.3 End-to-End Verification
After adding logging:
1. Submit a prompt
2. Check `.claude/logs/memory_retrieval.log` for execution trace
3. End session
4. Check `.claude/logs/reasoning_extraction.log` for extraction trace

## 5. Risks
*   **Infinite Loops:** The `Stop` hook invokes python which might fail. The script has a `stop_hook_active` check, which is critical.
*   **Performance:** `UserPromptSubmit` runs on *every* prompt. The `memory_retrieval.py` it calls must timeout quickly (currently set to 5s in script) to avoid lag.
*   **Silent Failures:** Current design hides errors. Logging addition may reveal issues that were always there.


<!-- VALIDATION ERRORS (2025-12-06 14:56:35):
  - ERROR: Missing YAML header in template
  - ERROR: Only 0 @ reference(s) found (minimum 2 required)
-->


<!-- VALIDATION ERRORS (2025-12-06 14:56:55):
  - ERROR: Missing YAML header in template
  - ERROR: Only 0 @ reference(s) found (minimum 2 required)
-->
