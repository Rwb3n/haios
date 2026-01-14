---
template: checkpoint
status: complete
date: 2025-12-21
title: "Session 95: E2-130 Error Capture Rebuild and Taxonomy Discussion"
author: Hephaestus
session: 95
prior_session: 94
backlog_ids: [E2-130, INV-020, INV-021]
memory_refs: [77029, 77030, 77031, 77032, 77033]
project_phase: Epoch 2 - Governance Suite
lifecycle_phase: done
version: "1.3"
generated: 2025-12-21
last_updated: 2025-12-21T23:04:37
---
# Session 95 Checkpoint: E2-130 Error Capture Rebuild and Taxonomy Discussion

@docs/plans/PLAN-E2-130-error-capture-rebuild.md
@docs/checkpoints/2025-12-21-05-SESSION-94-m5-complete-e2-125-e2-129-migration.md

> **Date:** 2025-12-21
> **Focus:** Fix broken error capture hook, taxonomy discussion
> **Context:** Session started with M4-Research review but pivoted to fix a blocking issue (stale PowerShell hook causing errors).

---

## Session Summary

Fixed broken error capture system (E2-130): removed stale PowerShell hook, rebuilt detection logic in Python with 93% false positive elimination, added dedicated `type: tool_error` for queryability. Created two future investigations: INV-020 (LLM Energy Channeling Patterns) and INV-021 (Work Item Taxonomy). Key insight: use industry-standard terminology so LLMs leverage training data.

---

## Completed Work

### 1. E2-130: Error Capture Rebuild (Tech Debt)
- [x] Removed stale ErrorCapture.ps1 hook from settings.local.json
- [x] Created `.claude/lib/error_capture.py` with `is_actual_error()` and `store_error()`
- [x] Tool-specific detection logic (Bash: exit_code, Read/Edit/Write: error structure)
- [x] Added `type: tool_error` for queryability
- [x] Wired `_capture_errors()` into post_tool_use.py
- [x] Extended PostToolUse matcher to all tools
- [x] Cleaned up 188 false positive concepts from memory
- [x] 7 tests added (345 total pass)

### 2. INV-020: LLM Energy Channeling Patterns
- [x] Created investigation for auditing M3 infrastructure effectiveness
- [x] Documented pattern: Blocker → Agent, Tool → Tracker, Governance → Command

### 3. INV-021: Work Item Taxonomy and Schema Semantics
- [x] Created investigation for formalizing backlog field taxonomy
- [x] Key principle: Use industry-standard Agile/PMBOK terms

### 4. Taxonomy Clarification
- [x] M4-Research = Building investigation-cycle infrastructure (not doing investigations)
- [x] E2-130 categorized as `tech-debt` (not milestone work)

---

## Files Modified This Session

```
.claude/settings.local.json           - Removed stale hook, expanded PostToolUse matcher
.claude/lib/error_capture.py          - NEW: Detection + storage (6 functions)
.claude/hooks/hooks/post_tool_use.py  - Added _capture_errors()
.claude/lib/README.md                 - Added error_capture.py
.claude/hooks/README.md               - Updated PostToolUse docs
.claude/hooks/archive/error_capture_old.py - Archived old file
tests/test_error_capture.py           - NEW: 7 tests
scripts/cleanup_false_positives.py    - One-time cleanup script
docs/plans/PLAN-E2-130-*.md           - Marked complete
docs/pm/backlog.md                    - E2-130 complete, INV-020, INV-021 added
docs/investigations/INVESTIGATION-INV-020-*.md - NEW
```

---

## Key Findings

1. **False positive rate was 93%** - Old error capture stored 189 concepts, 188 were garbage
2. **PostToolUse may not fire for failed tools** - Claude Code limitation, known constraint
3. **M4-Research is infrastructure, not investigations** - Parallel to M3-Cycles for implementation
4. **Use industry-standard vocabulary** - LLMs leverage training data without fine-tuning
5. **TodoWrite channeling observed** - Visible progress tracking kept implementation on track

---

## WHY Captured (ADR-033)

| Decision/Learning | Memory ID | Source |
|-------------------|-----------|--------|
| Use standard Agile terms for LLM compatibility | 77029 | INV-021 |
| Blocker→Agent pattern effective (LLM channeling) | 77030, 77031 | INV-020 |
| M4-Research = infrastructure, not investigations | 77032, 77033 | Session 95 |

> Memory refs updated in frontmatter.

---

## Session Verification (Yes/No)

| Question | Answer | Notes |
|----------|--------|-------|
| Was all planned work completed? | Yes | E2-130 complete, investigations created |
| Were tests run and passing? | Yes | 345 tests |
| Any unplanned deviations? | Yes | Pivoted from M4 review to fix E2-130 (interrupt) |
| WHY captured to memory? | Partial | Documented in investigations |

---

## Pending Work (For Next Session)

1. **M4-Research** - E2-111 (Investigation Cycle Skill) is the critical path item
2. **INV-020** - LLM Energy Channeling audit (future, uses M4 once built)
3. **INV-021** - Taxonomy formalization (low priority)

---

## Continuation Instructions

1. Run `/coldstart` to load context
2. Focus on M4-Research: E2-111 is the starting point (builds investigation-cycle skill)
3. E2-130 is closed - error capture working, 345 tests pass

---

**Session:** 95
**Date:** 2025-12-21
**Status:** COMPLETE
