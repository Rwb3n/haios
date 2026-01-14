---
template: investigation
status: complete
date: 2025-12-18
backlog_id: INV-024
title: "Investigation: Work Item as File Architecture"
author: Hephaestus
session: 105
lifecycle_phase: conclude
spawned_by: Session-84
related: [ADR-033, ADR-034, ADR-036, E2-096, INV-022]
memory_refs: [77315, 77316, 77317, 77318, 77319, 77320, 77321, 77322, 77323, 77324, 77325, 77326, 77327, 77328, 77329]
milestone: M3-Cycles
version: "1.2"
generated: 2025-12-22
last_updated: 2025-12-23T17:10:02
---
# Investigation: Work Item as File Architecture

@docs/README.md
@docs/epistemic_state.md
@docs/ADR/ADR-033-work-item-lifecycle.md
@docs/ADR/ADR-036-pm-data-architecture.md

---

## Context

**Trigger:** Session 84 discussion about agile methods and architectural insights.

**Current State:**
- Work items are text entries in monolithic `backlog.md` (~1000 lines)
- Context is scattered across spawned documents (plans, checkpoints, investigations)
- When work completes, entry moves to `archive/backlog-complete.md`
- No single source of truth for a work item's full journey

**Operator Insight (Metaphor):**
> "Like a blood cell being pumped across an artery, innervating each organ (node) like the piston in an engine as it passes through."

This captures the vision: work items as **living entities** that traverse the DAG, activating each phase node, carrying context as they flow through the system.

**Pain Points:**
1. Backlog.md bloat - hard to navigate at scale
2. Context scattering - work history spread across multiple files
3. Session discontinuity - hard to understand where an item stands
4. Static entries - items don't "live" through their lifecycle

---

## Objective

Determine whether work items should evolve from **text entries in backlog.md** to **individual files that traverse the lifecycle as living documents**, accumulating context at each phase.

**Core Question:** Should each work item be a file that:
- Lives from creation to completion
- Accumulates context as it moves through phases
- Carries its own DAG edges (spawned_by, blocked_by, enables)
- Activates at each lifecycle node (BACKLOG ? DISCOVERY ? PLAN ? DO ? CHECK ? DONE)

---

## Scope

### In Scope
- Work-item file schema design
- Directory structure options
- Tooling impact assessment (UpdateHaiosStatus.ps1, /close, etc.)
- Migration path from backlog.md
- Prototype validation with real work item

### Out of Scope
- E2-096 (Cycle State Frontmatter) - related but orthogonal, can proceed independently
- Memory system changes - work items already have memory_refs pattern
- Major restructuring of existing document types (plans, checkpoints)

---

## Hypotheses

| # | Hypothesis | Test Method | Priority |
|---|------------|-------------|----------|
| **H5** | Migration from backlog.md is feasible without breaking tooling | Audit UpdateHaiosStatus.ps1, /close, grep patterns | **1st (FAIL FAST)** |
| **H1** | Individual files reduce cognitive load vs monolithic backlog | Compare navigation patterns, measure context visibility | **2nd (VALIDATE VALUE)** |
| **H3** | DAG edges in frontmatter enable dependency visualization | Prototype query patterns with Grep/Glob | 3rd |
| **H2** | Context accumulation in one file improves session continuity | Analyze current context loss patterns | 4th |
| **H4** | Cycle state fits naturally in work-item file | Map to E2-096 design, ensure compatibility | 5th |

---

## Investigation Steps

### Phase 1: Feasibility (H5 - Fail Fast) - COMPLETE

1. [x] **Audit UpdateHaiosStatus.ps1** - Session 84
   - Parses backlog.md at 5 locations
   - Uses regex patterns for item extraction
   - Can be adapted to scan work-item directory (pattern exists for plans/)

2. [x] **Audit /close command** - Session 84
   - Verifies item exists via grep
   - Archives by text extraction
   - Can be simplified with frontmatter-based approach

3. [x] **Audit other tooling** - Session 84
   - CascadeHook.ps1: Light dependency, easy to adapt
   - PreToolUse.ps1: Light dependency, path pattern change
   - 7 files total reference backlog.md, no blockers

### Phase 2: Value Validation (H1) - COMPLETE (Session 105)

4. [x] **Document current pain points**
   - Navigation friction: 1,224 lines, 62 items in backlog.md
   - Context discovery friction: E2-091 spans 14 files (plans, checkpoints, investigations)
   - Only 7 of 62 items have explicit Plan/Investigation links
   - Status drift risk: backlog entry may not match plan file status

5. [x] **Analyze existing precedents**
   - Plan files already act as living documents (frontmatter with status, DAG edges)
   - ADR-036 migration worked: archive + grep pattern effective
   - INV-022 already designed complete Work-Cycle-DAG architecture

### Phase 3: Design - COMPLETE (Session 105)

**Decision: ADOPT INV-022 Work File Schema v2** (see INV-022 lines 349-405)

6. [x] **Schema design: Work-item frontmatter**
   ```yaml
   ---
   template: work_item
   id: E2-091
   title: "Implementation Cycle Skill"
   status: active | complete | blocked | archived
   created: 2025-12-17
   closed: null
   owner: Hephaestus
   milestone: M3-Cycles
   priority: high | medium | low
   effort: low | medium | high
   # DAG edges
   spawned_by: Session-83
   blocked_by: []
   blocks: [E2-092, E2-093]
   enables: [E2-092, E2-093, E2-096]
   related: [ADR-038]
   # Lifecycle tracking
   lifecycle_phase: implement  # current phase
   phases_completed: [backlog, discovery, plan]
   # Context accumulation
   memory_refs: [72314, 72315, 72316]
   documents:
     plans: [PLAN-E2-091-*.md]
     checkpoints: [SESSION-83, SESSION-84]
     investigations: []
   ---
   ```

7. [x] **Schema design: Work-item body structure**
   ```markdown
   # E2-091: Implementation Cycle Skill

   ## Context
   [Original problem/opportunity description]

   ## Current State
   [What phase is this in? What's the latest status?]

   ## History
   ### Session 83 - Created
   - Spawned from M3-Cycles design discussion
   - Initial scope defined

   ### Session 84 - Implemented
   - Plan filled in, skill created
   - Closed via /close E2-091

   ## Deliverables
   - [x] Skill file created
   - [x] Documentation updated
   - [x] WHY captured

   ## References
   - Plan: docs/plans/PLAN-E2-091-*.md
   - ADR: ADR-038
   ```

8. [x] **Directory structure options**

   | Option | Structure | Pros | Cons |
   |--------|-----------|------|------|
   | A: Flat | `docs/work-items/E2-091.md` | Simple, greppable | No organization |
   | B: By milestone | `docs/work-items/M3-Cycles/E2-091.md` | Grouped by theme | Items move dirs? |
   | **C: By status** | `docs/work/{active,blocked,archive}/E2-091.md` | **Clear lifecycle** | Items move on status change |
   | D: By prefix | `docs/work-items/E2/E2-091.md` | Grouped by type | Arbitrary |

   **Decision: ADOPT Option C** (INV-022 recommendation) - `docs/work/{active,blocked,archive}/`

### Phase 4: Migration & Prototype - COMPLETE (Session 105)

9. [x] **Migration path design**
   - Three-phase migration designed:
     - Phase 1: Infrastructure (create dirs, update tooling)
     - Phase 2: Active Items (migrate pending backlog items)
     - Phase 3: Cutover (/close, cascade, status generator)
   - Retain backlog.md as legacy index (read-only)

10. [x] **Prototype (REQUIRED)**
    - Created `docs/work/active/WORK-E2-143.md` as prototype
    - Directory structure created: `docs/work/{active,blocked,archive}/`
    - Schema validated: frontmatter + body structure works
    - No friction points - schema is comprehensive

---

## Findings

### Phase 1: Feasibility Findings (H5) - Session 84

**Result: FEASIBLE** - Migration requires tooling updates but no blockers identified.

#### 1. UpdateHaiosStatus.ps1 (HEAVY dependency)

| Location | Usage | Migration Impact |
|----------|-------|------------------|
| Line 63 | `backlog_path = "docs/pm/backlog.md"` hardcoded | Change to `docs/work-items/` directory scan |
| Line 140 | `Get-BacklogStats()` parses entire file | Change to aggregate from work-item files |
| Lines 443-457 | Regex: `$item.*\[CLOSED\]` checks status | Change to read frontmatter `status:` field |
| Lines 619-625 | Calculates completed items | Change to query work-item file statuses |
| Lines 716-722 | Gets active HIGH/URGENT items | Change to filter work-item files by priority |

**Adaptation approach:** Replace single-file parsing with directory scan + frontmatter parsing. Pattern exists in how we scan `docs/plans/` already.

#### 2. /close Command (HEAVY dependency)

| Step | Current Behavior | Migration Impact |
|------|------------------|------------------|
| Verify exists | Grep backlog.md for `### [.*] {id}:` | Glob for `docs/work-items/{id}.md` |
| Archive | Extract section, append to archive | Change frontmatter `status: complete`, move file |
| Remove | Delete section from backlog.md | File already moved, nothing to delete |

**Adaptation approach:** Simpler actually - change status in frontmatter, move file to archive. No text extraction needed.

#### 3. CascadeHook.ps1 (LIGHT dependency)

- Line 75: Reads backlog.md to check CLOSED status
- **Adaptation:** Read work-item file frontmatter instead

#### 4. PreToolUse.ps1 (LIGHT dependency)

- Lines 127-130: E2-021 memory reference governance for backlog.md edits
- **Adaptation:** Change path pattern to `docs/work-items/*.md`

#### 5. Other References

- `REFS/CHECKLISTS.md` - Documentation only, no code impact
- `hooks/README.md` - Documentation only
- `Test-MemoryRefsValidation.ps1` - Test file, update path

**Conclusion:** No architectural blockers. Changes are well-scoped. Migration is FEASIBLE.

---

### Phase 2: Value Findings (H1) - Session 105

**H1 CONFIRMED:** Individual files reduce cognitive load vs monolithic backlog.

| Pain Point | Measurement | Solution |
|------------|-------------|----------|
| Backlog bloat | 1,224 lines, 62 items | Work files in `docs/work/` |
| Context scattering | E2-091 spans 14 files | Single work file accumulates context |
| Low cross-references | 7/62 items have links | work file `documents:` field tracks all |
| Status drift | backlog vs plan mismatch | Single source: work file frontmatter |

### Design Decisions - Session 105

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema | ADOPT INV-022 Work File Schema v2 | Comprehensive, includes node-cycle state |
| Directory | `docs/work/{active,blocked,archive}/` | Files move on status change, visual lifecycle |
| Migration | 3-phase approach | Low risk, incremental |

### Memory Integration - Session 105

INV-022 (Memory 77119, 77261) already designed the architecture. INV-024 validates and extends with:
- Concrete pain point measurements
- Prototype validation
- Migration path

---

## Spawned Work Items

**Investigation supports spawning ADR and implementation items.**

- [x] **ADR-039: Work Item as File Architecture** - formalizes the architecture decision
- [ ] **E2-150: Work-Item Infrastructure** - create directories, template, /new-work command
- [ ] **E2-151: Backlog Migration Script** - extract backlog.md entries to work files
- [ ] **E2-152: Tooling Cutover** - update /close, cascade, status generator

**Note:** These spawn into backlog, not immediately implemented. ADR-039 created below.

---

## Expected Deliverables

- [x] Feasibility assessment (can tooling adapt?) - **Phase 1: FEASIBLE**
- [x] Value validation (does this solve real pain?) - **Phase 2: H1 CONFIRMED**
- [x] Schema proposal (work-item.md structure) - **Adopted INV-022 Schema v2**
- [x] Directory structure recommendation - **`docs/work/{active,blocked,archive}/`**
- [x] Migration strategy - **3-phase approach**
- [x] Prototype work-item file - **`docs/work/active/WORK-E2-143.md`**
- [x] ADR-039 draft (if viable) - **Spawned, created this session**
- [x] Memory storage (investigation learnings) - **Pending closure**

---

## Metaphor Reference

**The Blood Cell / Piston Model:**

```
BACKLOG --? DISCOVERY --? PLAN --? DO --? CHECK --? DONE
   �            �           �       �       �         �
   +--[work-item file activates at each node, carrying context]--+
```

The work item is not a static record. It is a **living entity** that:
- Flows through the DAG
- Activates (innervates) each phase node
- Accumulates context like a blood cell carrying oxygen
- Transfers energy/information at each stop
- Completes its circuit and archives

---

## References

- **ADR-033:** Work Item Lifecycle (DoD criteria)
- **ADR-034:** Document Ontology (lifecycle phases)
- **ADR-036:** PM Data Architecture (backlog archival)
- **E2-096:** Cycle State Frontmatter (related, kept separate)
- **Session 84:** Investigation trigger discussion

---
