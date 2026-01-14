---
template: work_item
id: E2-214
title: Report Subtype Field
status: active
owner: Hephaestus
created: 2025-12-27
closed: null
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: INV-043
spawned_by_investigation: INV-043
blocked_by:
- E2-212
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 18:03:41
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T18:13:40'
---
# WORK-E2-214: Report Subtype Field

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Report template exists but is underutilized. No good "home" for bugs, bandaids, unexpected events discovered during work.

**Solution:** Add `subtype` field to report template and scaffold reports into work directory:

```
docs/work/active/{id}/reports/
  001-bug-powershell-hook.md      # subtype: bug
  002-bandaid-temp-fix.md         # subtype: bandaid
  003-event-session-recovery.md   # subtype: event
```

**Subtypes:**
| Subtype | Purpose |
|---------|---------|
| `bug` | Document a discovered bug |
| `bandaid` | Temporary workaround documentation |
| `event` | Capture a significant event |
| `decision` | Micro-decision (smaller than ADR) |
| `analysis` | Data analysis / audit results |

---

## Current State

Work item in BACKLOG node. Blocked by E2-212 (directory structure must exist first).

---

## Deliverables

- [ ] Add `subtype` field to report template frontmatter
- [ ] Update `validate.py` to validate subtype values
- [ ] Create `/new-report` command (or update existing)
- [ ] Update scaffold to create numbered files in work directory
- [ ] Document report subtype workflow

---

## History

### 2025-12-27 - Created (Session 129)
- Spawned from INV-043 (Work Item Directory Architecture)
- Updated to work within work directory structure (Option A)

---

## References

- Spawned by: INV-043 (Work Item Directory Architecture)
- Blocked by: E2-212 (Work Directory Structure Migration)
- Related: E2-213 (Investigation Subtype Field)
