---
template: implementation_plan
status: complete
date: 2025-12-07
backlog_id: PLAN-PM-SELF-AWARENESS
title: "PM Self-Awareness Wiring"
author: Hephaestus
version: "1.0"
lifecycle_phase: complete
completed_session: 56
completion_note: "SUPERSEDED. Completed work absorbed into ADR-031 (workspace awareness). Remaining work (memory sync, backlog refs) covered by E2-021."
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-10 22:08:17
# Implementation Plan: PM Self-Awareness Wiring

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Wire the `docs/pm/` directory into HAIOS self-awareness mechanisms so that:
1. Agents are aware of outstanding backlog items at session start
2. Backlog changes are synced to memory for cross-session persistence
3. System status commands reflect PM state

---

## Problem Statement

Backlog items exist in files but aren't visible to agents unless explicitly loaded. Without wiring:
- Agents don't know what's outstanding
- Items get lost across sessions
- No single source of truth for project status

---

## Proposed Changes

### 1. /coldstart Enhancement
- [ ] Add `docs/pm/backlog.md` to files loaded on cold start
- [ ] Query memory for `pm:backlog` items
- [ ] Include active item count in summary

### 2. /haios Enhancement
- [ ] Add PM section to status output
- [ ] Show active item count from backlog.md
- [ ] Show last sync timestamp

### 3. haios-status.json Update
- [ ] Add `pm` section with backlog path and item count
- [ ] Keep in sync with actual backlog state

### 4. Memory Sync Hook
- [ ] On backlog.md edit, sync items to memory
- [ ] Store with `source_path: "pm:backlog"`
- [ ] Enable cross-session queries

### 5. Governance Integration
- [ ] Add `docs/pm/` to governed paths (optional - may want flexibility here)
- [ ] Or keep ungoverned for easy editing

---

## Verification

- [ ] /coldstart shows backlog summary
- [ ] /haios shows PM section with item count
- [ ] memory_search("active backlog") returns items
- [ ] Cross-session: items persist after compact

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sync complexity | Medium | Start simple - manual sync, automate later |
| Token bloat | Low | Only load summary, not full backlog |
| Stale data | Medium | Include "last synced" timestamp |

---

## References

- @docs/pm/README.md
- @docs/pm/backlog.md
- @docs/plans/PLAN-EPOCH2-008-MEMORY-LEVERAGE.md

---
