---
template: work_item
id: E2-170
title: "Backfill Work Items from Archived Backlog"
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-24
milestone: M7-Tooling
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: [E2-021]
enables: [M7-Tooling]
related: [E2-151]
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T11:08:17
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T11:57:34
---
# WORK-E2-170: Backfill Work Items from Archived Backlog

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-151 migrated backlog items to work files, but only created placeholder files. The detailed content (Context, Deliverables, Related items, Session info) remains in backlog.md and backlog_archive.md.

**Impact:**
- Work files have "[Problem and root cause]" placeholders
- No memory_refs connections
- Milestone/related fields not populated from backlog
- Can't use work files as source of truth until backfilled

**Root cause:** Migration script scaffolded templates but didn't parse/copy backlog content.

---

## Current State

- 73 work files in `docs/work/active/`
- Most have placeholder content
- Source data exists in `docs/pm/backlog.md` and `docs/pm/backlog_archive.md`

---

## Deliverables

- [ ] Script to parse backlog.md entry for a given ID
- [ ] Script to parse backlog_archive.md entry for a given ID
- [ ] Extract: Context, Action/Deliverables, Related, Session, spawned_by, Milestone
- [ ] Update work file: Context section, Deliverables section
- [ ] Update work file: milestone, related, spawned_by fields in frontmatter
- [ ] Just recipe: `just backfill <id>` or `just backfill-all`
- [ ] Verify: Sample of 5 work files correctly populated

---

## History

### 2025-12-24 - Created (Session 110)
- Discovered during M7-Tooling review
- Work files are placeholders, need content from backlog sources

---

## References

- [Related documents]
