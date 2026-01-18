---
template: work_item
id: E2-213
title: Investigation Subtype Field
status: archived
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
  entered: 2025-12-27 18:03:39
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2026-01-18T21:56:50'
---
# WORK-E2-213: Investigation Subtype Field

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Investigations are monolithic. No way to do landscape scan → deep-dive → synthesis as separate passes.

**Solution:** Add `subtype` field to investigation template and support numbered naming convention within work directories:

```
docs/work/active/{id}/investigations/
  001-landscape.md         # subtype: landscape (broad survey)
  002-deep-dive.md         # subtype: deep-dive (focused analysis)
  003-synthesis.md         # subtype: synthesis (combining findings)
```

**Subtypes:**
| Subtype | Purpose |
|---------|---------|
| `landscape` | Broad survey, identify areas of interest |
| `deep-dive` | Focused analysis on specific hypothesis |
| `synthesis` | Combine findings from prior investigations |

---

## Current State

Work item in BACKLOG node. Blocked by E2-212 (directory structure must exist first).

---

## Deliverables

- [ ] Add `subtype` field to investigation template frontmatter
- [ ] Update `validate.py` to validate subtype values
- [ ] Update `/new-investigation` to accept subtype parameter
- [ ] Update scaffold to create numbered files in work directory
- [ ] Document investigation subtype workflow

---

## History

### 2025-12-27 - Created (Session 129)
- Spawned from INV-043 (Work Item Directory Architecture)
- Updated to work within work directory structure (Option A)

---

## References

- Spawned by: INV-043 (Work Item Directory Architecture)
- Blocked by: E2-212 (Work Directory Structure Migration)
- Related: E2-214 (Report Subtype Field)
