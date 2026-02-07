---
template: work_item
id: E2-212
title: Work Directory Structure Migration
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-28
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: INV-043
spawned_by_investigation: INV-043
blocked_by: []
blocks: []
enables:
- E2-213
- E2-214
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 18:03:37
  exited: null
cycle_docs: {}
memory_refs:
- 79850
- 79851
- 79852
- 79853
- 79854
- 79855
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-28T11:09:26'
---
# WORK-E2-212: Work Directory Structure Migration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work item artifacts are scattered across directories. INV-043 confirmed E2-091 spans 14+ files across 4 directories.

**Solution:** Full Co-location (Option A from INV-043) - each work item becomes a directory containing all its artifacts:

```
docs/work/active/{id}/
  WORK.md                    # Main work file (renamed from WORK-{id}-*.md)
  investigations/
    001-landscape.md         # Subtype: broad survey
    002-deep-dive.md         # Subtype: focused analysis
    003-synthesis.md         # Subtype: combining findings
  plans/
    PLAN.md                  # Implementation plan
  reports/
    001-bug-*.md             # Bug reports
    002-bandaid-*.md         # Temporary workarounds
```

**Migration:** Active work items migrate to directory structure. Completed items in archive stay as-is.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Create directory structure: `docs/work/active/{id}/` with subdirs
- [ ] Update `scaffold.py` to create work directories and WORK.md
- [ ] Update `work_item.py` glob patterns for directory structure
- [ ] Update `status.py` work file discovery (8+ patterns)
- [ ] Update `plan_tree.py` glob pattern
- [ ] Update `audit.py` glob patterns
- [ ] Update `/new-plan` to scaffold into `{id}/plans/PLAN.md`
- [ ] Update `/new-investigation` to scaffold into `{id}/investigations/NNN-*.md`
- [ ] Migration script for active work items
- [ ] Update `/close` to move entire directory to archive

---

## History

### 2025-12-27 - Created (Session 129)
- Spawned from INV-043 (Work Item Directory Architecture)
- Updated to Option A (Full Co-location) per operator feedback

---

## References

- Spawned by: INV-043 (Work Item Directory Architecture)
- Related: E2-213 (Investigation Subtype Field)
- Related: E2-214 (Report Subtype Field)
