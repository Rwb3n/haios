---
template: investigation
status: complete
date: 2025-12-13
backlog_id: INV-008
title: "Investigation: haios-status.json Architecture Optimization"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
generated: 2025-12-22
last_updated: 2025-12-22T22:37:14
---
# Investigation: haios-status.json Architecture Optimization

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 70 PM governance audit revealed haios-status.json has grown to 1,365 lines. Analysis showed 66% of the file (895 lines) is the `work_items` section - a cached index of document associations per backlog ID.

**Key Question:** Why do we have work items displayed in BOTH backlog.md AND haios-status.json?

**Historical Context:**
- E2-023/ADR-033 (Session 58) introduced `/close` command
- `work_items` was added to pre-compute document associations for `/close`
- This was premature optimization - the data is derivable from file frontmatter

---

## Objective

Determine optimal architecture for haios-status.json:
1. What data MUST be in haios-status.json?
2. What data can be queried at runtime instead of cached?
3. What is the target line count?

---

## Scope

### In Scope
- haios-status.json structure and content
- UpdateHaiosStatus.ps1 script
- `/close` command document lookup
- `/coldstart` context loading

### Out of Scope
- backlog.md format (separate investigation INV-009)
- Memory system architecture
- Hook configuration

---

## Critical Reasoning Analysis

### 1) Logical Dependencies and Constraints

**1.1) Policy-based rules:**
- haios-status.json is loaded by `/coldstart` - bloat impacts every session
- `/close` needs to find documents associated with a backlog ID

**1.2) Order of operations:**
- Must maintain `/close` functionality
- Must reduce coldstart context load

**1.3) Prerequisites:**
- Understand what `/close` actually needs from work_items
- Verify documents can be queried at runtime

### 2) Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Remove work_items | `/close` breaks | Update `/close` to query directly |
| Remove lifecycle.live_files | Less visibility | Data queryable from filesystem |
| Keep only summaries | None | Summaries are useful |

### 3) Abductive Reasoning

**Root Cause:** work_items is a cached index that:
1. Duplicates information stored in file frontmatter
2. Gets stale between UpdateHaiosStatus.ps1 runs
3. Consumes 66% of file for rarely-used data

**Evidence:**
- `/close` only runs once per work item closure
- `/coldstart` runs every session
- Ratio: coldstart runs >> close runs

### 4) Outcome Evaluation

Current state is suboptimal. Caching data for rare operations while bloating common operations.

---

## Findings

### Current Structure (1,365 lines)

| Section | Lines | % | Usage Frequency |
|---------|-------|---|-----------------|
| work_items | ~895 | 66% | Rare (only /close) |
| lifecycle.live_files | ~345 | 25% | Rare (debugging) |
| hooks | ~40 | 3% | Every session |
| pm | ~10 | 1% | Every session |
| memory | ~8 | 1% | Every session |
| skills/agents/templates | ~30 | 2% | Every session |
| workspace | ~30 | 2% | Every session |

### Problem Analysis

**work_items section:**
- Pre-computed tree of 27 backlog IDs
- Each ID has: handoffs[], adrs[], checkpoints[], reports[], plans[]
- Most arrays are empty (lots of `[]` taking space)
- Same checkpoint appears in multiple work items (duplication)

**lifecycle.live_files section:**
- List of 43 files with full metadata
- Each file: path, template, lifecycle_phase, backlog_id, date, status
- Rarely consulted - just run `grep` on docs/ instead

### Proposed Architecture

**Keep (Essential):**
```json
{
  "last_updated": "...",
  "pm": { "active_count": N, "by_priority": {...}, "last_session": N },
  "memory": { "concepts_count": N, "entities_count": N, ... },
  "hooks": { ... },
  "skills": [...],
  "agents": [...],
  "valid_templates": [...],
  "workspace": { "summary": {...} }
}
```

**Remove:**
- `work_items` - query at runtime via `grep "backlog_id: ID" docs/`
- `lifecycle.live_files` - query at runtime if needed
- `lifecycle.counts_by_status` - derivable from live query
- `lifecycle.counts_by_phase` - derivable from live query

**Target:** ~120 lines (91% reduction)

---

## Recommendations

### ADR-036: PM Data Architecture

**Decision:** Remove cached indexes from haios-status.json. Query at runtime.

**Implementation:**
1. Update `/close` command to grep for associated documents
2. Remove `work_items` section from UpdateHaiosStatus.ps1
3. Remove `lifecycle.live_files` section
4. Keep only summary data

**Trade-offs:**
- `/close` slightly slower (grep vs JSON lookup)
- Always fresh data (no stale cache)
- Massive coldstart improvement (1,365 ? 120 lines)

---

## Spawned Work Items

- [ ] ADR-036: PM Data Architecture (haios-status.json lean redesign)
- [ ] E2-041: Implement haios-status.json cleanup
- [ ] E2-042: Update /close to query documents at runtime

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Recommendations (ADR-036 proposal)
- [ ] Memory storage (concepts)

---

## References

- E2-023: /close Command Implementation (Session 58)
- ADR-033: Work Item Lifecycle Governance
- INV-009: Backlog Archival Governance (companion investigation)

---
