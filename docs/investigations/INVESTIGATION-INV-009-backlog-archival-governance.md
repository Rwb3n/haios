---
template: investigation
status: complete
date: 2025-12-13
backlog_id: INV-009
title: "Investigation: Backlog Archival Governance"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
generated: 2025-12-22
last_updated: 2025-12-22T22:37:32
---
# Investigation: Backlog Archival Governance

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 70 PM governance audit revealed backlog.md has grown to 961 lines with 51 work items. Analysis showed 70% of items (36/51) are non-active (complete/subsumed/closed/cancelled) but still occupy space in the active backlog file.

**Key Question:** Should completed work items remain in the active backlog indefinitely?

**Historical Context:**
- ADR-033 (Session 57) defined work item lifecycle: BACKLOG -> DISCOVERY -> DESIGN -> PLAN -> IMPLEMENT -> VERIFY -> CLOSE
- `/close` command stores WHY to memory and updates status to `complete`
- But no archival mechanism exists - items accumulate forever

---

## Objective

Determine optimal governance for backlog.md:
1. Should completed items be archived?
2. What is the archival mechanism?
3. What information must remain accessible?

---

## Scope

### In Scope
- backlog.md structure and content
- Completed item archival strategy
- `/close` command behavior
- Reference accessibility after archival

### Out of Scope
- haios-status.json structure (separate investigation INV-008)
- Memory system for WHY storage
- Active item format changes

---

## Critical Reasoning Analysis

### 1) Logical Dependencies and Constraints

**1.1) Policy-based rules:**
- ADR-033: Completed items must have WHY stored in memory
- Backlog is source of truth for work item definitions
- Human-readable history has value

**1.2) Order of operations:**
- Archive must preserve information accessibility
- `/close` should trigger archival (or archival should be periodic)

**1.3) Prerequisites:**
- Completed items have closure summaries in memory
- Associated documents (plans, checkpoints) remain in filesystem

### 2) Risk Assessment

| Option | Risk | Mitigation |
|--------|------|------------|
| Archive completed items | Can't find historical items | Archive file + memory queries |
| Delete completed items | Lose markdown reference | Memory has WHY, docs have context |
| Keep all items | Continued bloat | None - status quo |

### 3) Abductive Reasoning

**Root Cause:** No archival governance defined.

**Evidence:**
- 36 non-active items consuming ~650 lines
- Each item: 15-20 lines average
- Oldest completed items from early Epoch 2 still present
- Status inconsistency: 8 items have `completed` instead of `complete` (ADR-033 normalized to `complete`)

**Why This Matters:**
- Cognitive load when scanning backlog
- Longer file = more context tokens
- Active work obscured by historical data

### 4) Outcome Evaluation

Option A (Archive) provides best balance:
- Reduces active backlog to ~350 lines
- Preserves human-readable history
- Memory provides queryable WHY

---

## Findings

### Current State (961 lines)

| Category | Count | Lines | % |
|----------|-------|-------|---|
| Header/metadata | - | ~50 | 5% |
| Active items | 15 | ~260 | 27% |
| Non-active items | 36 | ~650 | **68%** |

### Non-Active Items Breakdown

| Status | Count | Notes |
|--------|-------|-------|
| `complete` | 28 | Properly normalized |
| `completed` | 8 | **Needs normalization** (ADR-033 uses `complete`) |
| `subsumed` | ~3 | Absorbed by other items |

### Data Quality Issue

8 items still use `completed` instead of `complete`:
- ADR-033 (Session 57) normalized status to `complete`
- These items predate the normalization or were manually edited
- **Fix:** Normalize during archival process

### Information Accessibility After Archival

| Source | What It Provides |
|--------|------------------|
| `docs/pm/archive/backlog-complete.md` | Full historical markdown |
| Memory (closure:{ID}) | WHY and closure summary |
| Associated docs (plans, checkpoints) | Implementation details |
| Active backlog | Reference to archived items |

---

## Recommendations

### ADR-036: PM Data Architecture (shared with INV-008)

**Decision:** Implement backlog archival governance with auto-archive on /close.

**Mechanism:**
1. Create `docs/pm/archive/backlog-complete.md`
2. Update `/close` to move item to archive automatically
3. **Normalize status** during archival (`completed` -> `complete`)
4. Keep reference stub in active backlog (or remove entirely - archive has full history)
5. One-time migration of existing 36 non-active items

**Why Auto-Archive on /close:**
- /close already edits backlog.md (updates status)
- Adding "move to archive" is incremental complexity
- Immediate archival = always-clean active backlog
- No arbitrary schedule (quarterly, monthly) needed
- Single source of truth at all times

**Archive Format:**
```markdown
# Completed Backlog Items

> Query memory for WHY: `closure:{ID}`

## Epoch 2 (Sessions 36-70)

### E2-001: MCP Tool Consolidation
- **Status:** complete
- **Completed:** 2025-12-08 (Session 49)
- **Memory:** closure:E2-001
```

**Active Backlog Format (after archival):**
```markdown
# HAIOS Backlog

> **Archived:** 36 items (E2-001 to E2-030, INV-001 to INV-007)
> See `docs/pm/archive/backlog-complete.md` or query memory `closure:{ID}`

## Active Work Items (15)
...
```

**Target:** Active backlog ~260 lines (73% reduction)

### Query Strategy for Archived Items

| Need | Method |
|------|--------|
| Full item details | Read `docs/pm/archive/backlog-complete.md` |
| WHY/reasoning | Query memory: `closure:{ID}` |
| Associated docs | Grep: `backlog_id: {ID}` in docs/ |
| Quick lookup | Grep archive file |

---

## Spawned Work Items

- [ ] ADR-036: PM Data Architecture (shared with INV-008)
- [ ] E2-043: One-time migration of 36 non-active items to archive
- [ ] E2-044: Update /close to auto-archive on completion

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Recommendations (ADR-036 proposal)
- [ ] Memory storage (concepts)

---

## References

- ADR-033: Work Item Lifecycle Governance
- E2-023: /close Command Implementation
- INV-008: haios-status.json Architecture Optimization (companion investigation)

---
