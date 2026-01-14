---
template: architecture_decision_record
status: proposed
date: 2025-12-13
adr_id: ADR-036
title: "PM Data Architecture"
author: Hephaestus
session: 70
lifecycle_phase: decide
decision: pending
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:24:37
# ADR-036: PM Data Architecture

@docs/README.md
@docs/epistemic_state.md

> **Status:** Proposed
> **Date:** 2025-12-13
> **Decision:** Pending

---

## Context

Session 70 PM governance audit (INV-008, INV-009) revealed critical bloat in operational files:

| File | Lines | Problem |
|------|-------|---------|
| haios-status.json | 1,365 | 66% is `work_items` - cached index for /close |
| backlog.md | 961 | 70% is non-active items (complete/subsumed) |
| **Total** | **2,326** | Both loaded on /coldstart |

**Root Causes:**
1. **haios-status.json:** `work_items` was premature optimization - pre-computing document associations for /close when data is queryable from frontmatter
2. **backlog.md:** No archival governance - completed items accumulate forever

**Impact:**
- Every session loads 2,326 lines of mostly stale/redundant data
- /coldstart context bloat
- Active work obscured by historical data

---

## Decision Drivers

- **Context economy:** Minimize tokens loaded per session
- **Data freshness:** Query at runtime > stale cache
- **Simplicity:** Remove redundant data structures
- **Accessibility:** Historical data must remain queryable
- **Automation:** /close should handle cleanup automatically

---

## Considered Options

### Option A: Status Quo
**Description:** Keep current structure, accept bloat.

**Pros:**
- No migration effort

**Cons:**
- Continued context bloat
- /coldstart loads 2,326 lines every session
- Problem worsens over time

### Option B: Lean Architecture (Recommended)
**Description:** Remove cached indexes from haios-status.json, auto-archive completed backlog items.

**Pros:**
- 84% reduction (2,326 ? ~380 lines)
- Always-fresh data (no stale cache)
- Clean active backlog
- Queryable history via archive + memory

**Cons:**
- /close slightly slower (grep vs JSON lookup)
- One-time migration effort

### Option C: Separate Files Only
**Description:** Keep haios-status.json structure, only archive backlog items.

**Pros:**
- Simpler implementation
- /close unchanged

**Cons:**
- Still loads 1,365 lines of haios-status.json
- Only partial improvement

---

## Decision

**Option B: Lean Architecture**

### Part 1: haios-status.json Cleanup (INV-008)

**Remove:**
- `work_items` section (895 lines) - query at runtime via grep
- `lifecycle.live_files` section (345 lines) - derivable from filesystem
- `lifecycle.counts_by_*` - derivable

**Keep:**
```json
{
  "last_updated": "...",
  "pm": { "active_count": N, "by_priority": {...}, "last_session": N },
  "memory": { "concepts_count": N, ... },
  "hooks": { ... },
  "skills": [...],
  "agents": [...],
  "valid_templates": [...],
  "workspace": { "summary": {...} }
}
```

**Target:** ~120 lines (91% reduction)

### Part 2: Backlog Archival (INV-009)

**Mechanism:**
1. Create `docs/pm/archive/backlog-complete.md`
2. Update `/close` to auto-archive completed items
3. Normalize status during archival (`completed` ? `complete`)
4. One-time migration of 36 existing non-active items

**Query Strategy:**
| Need | Method |
|------|--------|
| Full item details | `docs/pm/archive/backlog-complete.md` |
| WHY/reasoning | Memory query: `closure:{ID}` |
| Associated docs | `grep "backlog_id: {ID}" docs/` |

**Target:** ~260 lines (73% reduction)

---

## Consequences

**Positive:**
- 84% reduction in PM data (2,326 ? ~380 lines)
- /coldstart loads minimal context
- Active backlog shows only active work
- Always-fresh data on queries
- /close becomes single point of lifecycle management

**Negative:**
- /close slightly slower (grep vs pre-computed lookup)
- One-time migration effort for existing items
- /close command needs update

**Neutral:**
- Historical data moves location but remains accessible
- Query patterns change (grep vs JSON access)

---

## Implementation

### Phase 1: haios-status.json (E2-041, E2-042)
- [ ] E2-041: Remove work_items and lifecycle.live_files from UpdateHaiosStatus.ps1
- [ ] E2-042: Update /close to query documents at runtime (grep for backlog_id)

### Phase 2: Backlog Archival (E2-043, E2-044)
- [ ] E2-043: One-time migration of 36 non-active items to archive
- [ ] E2-044: Update /close to auto-archive on completion

### Verification
- [ ] haios-status.json < 150 lines
- [ ] backlog.md < 300 lines (active only)
- [ ] /close still works (test with E2-041 closure)
- [ ] Historical items queryable via archive + memory

---

## References

- INV-008: haios-status.json Architecture Optimization
- INV-009: Backlog Archival Governance
- ADR-033: Work Item Lifecycle Governance
- E2-023: /close Command Implementation

---
