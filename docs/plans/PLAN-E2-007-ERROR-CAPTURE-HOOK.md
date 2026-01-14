---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-007
title: "Error Capture Hook"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:31:17
# Implementation Plan: Error Capture Hook

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Capture tool errors to memory for pattern detection across sessions. When an agent encounters errors, automatically store error context to memory so future agents can learn from past failures.

---

## Problem Statement

Currently, errors happen and are handled in-session but lost across sessions. No mechanism exists to:
1. Detect when tool calls fail
2. Extract meaningful error context
3. Store errors to memory for pattern detection
4. Enable future agents to query "what errors occurred with X?"

Session 39 identified this as part of "leveraging Claude's tendencies" - using memory to break error cycles.

---

## Background (Session 58 Refocus)

Original E2-007 scope (Session 39):
1. Schema injection - **SUPERSEDED** by E2-020 (PreToolUse + schema-verifier)
2. Error-to-memory - **THIS PLAN**
3. Retry breaker - Deferred (can build on error capture)

---

## Design

### Error Detection Strategy

PostToolUse hooks receive JSON with `tool_response`. Error indicators:
1. `tool_response` contains "error", "Error", "ERROR"
2. `tool_response` contains "failed", "Failed", "FAILED"
3. `tool_response` contains "Exception", "Traceback"
4. Bash tool with non-zero exit code

### Implementation Approach

**Option B: Separate ErrorCapture.ps1 hook**
- Cleaner separation of concerns
- Doesn't bloat PostToolUse.ps1
- Can be enabled/disabled independently

### Error Context to Capture

```json
{
  "tool_name": "...",
  "tool_input_summary": "...",
  "error_message": "...",
  "timestamp": "...",
  "session": "..."
}
```

---

## Proposed Changes

### 1. Create ErrorCapture.ps1 Hook
- [x] Create `.claude/hooks/ErrorCapture.ps1`
- [x] Parse PostToolUse JSON for error indicators
- [x] Extract error context (tool, input summary, error message)
- [x] Call `ingester_ingest` via Python subprocess (`.claude/hooks/error_capture.py`)

### 2. Configure Hook
- [x] Add ErrorCapture.ps1 to settings.local.json PostToolUse array
- [x] Ensure it runs AFTER PostToolUse.ps1 (timestamps first)
- [x] Matcher: `Bash|Read|Write|Edit|Grep|Glob`

### 3. Test Coverage
- [x] Create Test-ErrorCapture.ps1 (8 tests)
- [x] Test: Bash error detection (non-zero exit)
- [x] Test: Tool response error string detection (Traceback, Permission denied)
- [x] Test: Normal responses pass through silently
- [x] Test: Error message extraction
- [x] Test: Input summary for various tools
- [x] Test: Long command truncation

---

## Verification

- [x] Tests pass (8 tests - all passing)
- [x] Documentation updated (hooks README section 8)
- [x] Hook configured in settings.local.json
- [ ] Live error capture verification (deferred - requires real error)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive error detection | Low | Conservative regex, specific patterns only |
| Performance overhead | Low | Quick regex check, async memory call |
| Memory spam from repeated errors | Medium | Rate limiting or deduplication |
| Sensitive data in error context | Medium | Truncate tool_input, sanitize paths |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 69 | 2025-12-13 | - | complete | Plan created, implemented, tested, documented |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (8/8)
- [x] WHY captured (see Memory References below)
- [x] Documentation current (hooks README updated)
- [x] All traced files complete

---

## References

- Memory Concepts 62530, 62531 (Session 39 HAIOS as Behavioral Compiler)
- Session 58 audit (E2-007 refocused)
- PostToolUse.ps1 (existing hook pattern)
- E2-020 (schema injection - superseded that scope)

---
