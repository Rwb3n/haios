---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-043
title: "Backlog Archival Migration"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:40:56
# Implementation Plan: Backlog Archival Migration

@docs/README.md
@docs/epistemic_state.md

---

## Goal

One-time migration: Move 33 non-active items from backlog.md to docs/pm/archive/backlog-complete.md, reducing active backlog from ~1,021 to ~300 lines (71% reduction).

---

## Problem Statement

backlog.md contains 33 non-active items that:
1. Clutter the active backlog view
2. Slow down parsing and scanning
3. Mix historical context with actionable work

Per INV-009 and ADR-036, these should be archived while preserving history.

**Status Distribution (actual count):**
- `complete`: 20 items
- `completed`: 8 items (non-standard per ADR-033)
- `subsumed`: 2 items
- `done`: 2 items (non-standard)
- `closed`: 1 item

**Data Quality Issues:**
1. 8 items use `completed` instead of `complete` (ADR-033 standard)
2. 2 items use `done` instead of `complete`
3. 8 items have header/status mismatch (header says `[HIGH]`, status says `complete`)

---

## Proposed Changes

### 1. Create Archive Structure
- [ ] Create docs/pm/archive/ directory if not exists
- [ ] Create backlog-complete.md with header explaining archive purpose
- [ ] Include metadata: migration date, source count

### 2. Identify Items to Archive
Items with Status field matching: `complete`, `completed`, `subsumed`, `closed`, `done`

**Source of Truth:** Use `- **Status:**` field, NOT header brackets.

Regex pattern for status field:
```
- \*\*Status:\*\* (complete|completed|subsumed|closed|done)
```

**Why Status field over header:** 8 items have stale headers (e.g., `[HIGH]` but `Status: complete`). The Status field is authoritative.

### 3. Execute Migration
- [ ] Extract each non-active item (header through next header or EOF)
- [ ] Normalize status: `completed` -> `complete`, `done` -> `complete`
- [ ] Append to archive file with original content preserved
- [ ] Remove from backlog.md

### 4. Update Backlog References
- [ ] Update "Archive Reference" section at bottom of backlog.md
- [ ] Point to docs/pm/archive/backlog-complete.md

---

## Verification

- [ ] backlog.md line count ~300 (down from ~1,021)
- [ ] Archive contains all 33 items
- [ ] No duplicate items (in both files)
- [ ] Status normalized (no `completed` or `done`, only `complete`)
- [ ] Headers normalized (all archived items show `[COMPLETE]`)
- [ ] Archive file validates (readable, well-formed markdown)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Item section boundary errors | High | Test regex on sample items first |
| Lost items during migration | High | Count items before/after |
| References to archived items break | Low | Items keep original IDs |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

---

## References

- ADR-036: PM Data Architecture
- INV-009: Backlog Archival Governance
- E2-044: Close Auto-Archive (depends on this)

---
