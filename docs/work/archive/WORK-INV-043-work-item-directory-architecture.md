---
template: work_item
id: INV-043
title: Work Item Directory Architecture
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: high
effort: large
category: investigation
spawned_by: S127-discussion
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: discovery
node_history:
- node: backlog
  entered: 2025-12-27 15:13:26
  exited: '2025-12-27T17:41:05.791050'
- node: discovery
  entered: '2025-12-27T17:41:05.791050'
  exited: null
cycle_docs:
  discovery: docs/investigations/INVESTIGATION-INV-043-work-item-directory-architecture.md
memory_refs: []
documents:
  investigations:
  - docs/investigations/INVESTIGATION-INV-043-work-item-directory-architecture.md
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T18:05:54'
---
# WORK-INV-043: Work Item Directory Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work item artifacts are scattered across directories (work/, investigations/, plans/). This creates issues:

1. **Investigations are monolithic** - Single investigation tries to do too much; first pass often misses things, requiring "another pass"
2. **No layered sourcing** - Can't separate web research vs memory query vs codebase analysis into distinct investigations
3. **No iterative refinement** - Initial exploration → refined deep-dive → synthesis is natural but not supported
4. **Investigation spawning** - Investigation A spawning Investigation B is awkward with current flat structure
5. **Reports template unused** - No good place for bugs, bandaids, unexpected events

**Root Cause:** Work items are files, not directories. All related artifacts should live together.

**Proposed Structure:**
```
docs/work/
  active/
    E2-208/
      WORK.md                    # Single source of truth
      investigations/
        001-initial.md           # Broad sweep
        002-memory-deep-dive.md  # Focused pass
        003-synthesis.md         # Combines findings
      plans/
        001-implementation.md
      reports/
        001-bug-discovered.md
        002-bandaid-applied.md
  archive/
    E2-151/
      ...
```

**Checkpoints remain at session level** - they span work items.

---

## Current State

Work item in BACKLOG node. Ready for investigation.

---

## Deliverables

- [ ] Design directory structure and naming conventions
- [ ] Design investigation subtypes (landscape, deep-dive, synthesis, etc.)
- [ ] Design report template revival (bugs, bandaids, events)
- [ ] Identify tooling that needs glob pattern updates (status.py, plan_tree.py, scaffold, validate)
- [ ] Design migration strategy (archive completed, only migrate active)
- [ ] Create ADR documenting the architecture decision
- [ ] Spawn implementation work items

---

## History

### 2025-12-27 - Created (Session 127)
- Spawned from S127 discussion about fundamental work infrastructure enhancement
- Key insight: investigations need to be decomposable and iterable
- Reports template revival for bugs/bandaids/events

---

## References

- Related: INV-021 (Work Item Taxonomy), INV-030 (Milestone Architecture)
- Related: E2-069 (Roadmap and Milestones Structure)
- May obsolete: E2-161 (Auto-link Documents) - linking becomes implicit via directory
