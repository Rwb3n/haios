---
id: query
epoch: E2.8
theme: The agent should not search what it can query
status: Planning
started: 2026-02-17 (Session 393)
chapters:
- id: CH-061
  title: ColdstartContextInjection
  work_items:
  - WORK-162 (complete)
  - WORK-180
  requirements:
  - REQ-CONFIG-001
  - L3.3
  dependencies: []
  status: In Progress
- id: CH-062
  title: ProgressiveContracts
  work_items:
  - New
  requirements:
  - REQ-ASSET-001
  dependencies: []
  status: Complete
exit_criteria:
- text: Lightweight coldstart variant exists for housekeeping sessions
  checked: false
- text: Contracts designed for progressive disclosure (agent reads what it needs,
    not everything)
  checked: false
- text: Context loading uses engine functions and memory before file reads
  checked: false
---
# generated: 2026-02-17
# System Auto: last updated on: 2026-02-17T21:00:00
# Arc: Query

## Definition

**Arc ID:** query
**Epoch:** E2.8
**Theme:** The agent should not search what it can query
**Status:** Planning
**Started:** 2026-02-17 (Session 393)

---

## Purpose

Extend engine functions for context loading. Memory-first retrieval. Progressive disclosure in contracts. The agent should get exactly the context it needs via structured queries, not by loading entire files and searching through them.

**The Context Problem:** Most tokens are spent on context loading (mem:85459). Coldstart is overkill for housekeeping sessions (mem:84835, 84836). Context switching between ceremony phases costs tokens with no work output (mem:85815).

Progressive disclosure means: load summary first, details on demand. Engine functions (HierarchyQueryEngine, ConfigLoader) provide the query layer — this arc extends them for context loading.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CONFIG-001 | All paths defined in haios.yaml, accessed via ConfigLoader |
| REQ-ASSET-001 | Each lifecycle produces typed, immutable asset |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-061 | ColdstartContextInjection | WORK-162 (complete), WORK-180 | REQ-CONFIG-001, L3.3 | None | In Progress |
| CH-062 | ProgressiveContracts | New | REQ-ASSET-001 | None | Complete |

---

## Exit Criteria

- [ ] Lightweight coldstart variant exists for housekeeping sessions
- [ ] Contracts designed for progressive disclosure (agent reads what it needs, not everything)
- [ ] Context loading uses engine functions and memory before file reads

---

## Notes

- HierarchyQueryEngine (WORK-157, closed S393) provides the foundation — get_arcs(), get_chapters(), get_work()
- ConfigLoader (WORK-158, closed S393) provides path resolution — zero hardcoded paths
- Lightweight coldstart could be a tiered system: full (new work), light (continuation), minimal (housekeeping)

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CONFIG-*, REQ-ASSET-*)
- Memory: 84835, 84836 (coldstart overhead), 85459 (most tokens on context loading), 85815 (context switching)
