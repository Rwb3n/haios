---
template: work_item
id: INV-039
title: Information Architecture Policy Audit
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
priority: medium
effort: medium
category: investigation
spawned_by: INV-038
spawned_by_investigation: INV-038
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 14:02:06
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T14:27:47'
---
# WORK-INV-039: Information Architecture Policy Audit

@docs/README.md
@docs/epistemic_state.md

---

## Context

After completing INV-037 (Context Level Architecture) and INV-038 (L1 Invariants Audit), we have established an L1/L2/L3 framework. Now we need to audit the current information architecture to assess:

1. **Useful:** What content is working well and should be preserved?
2. **Redundant:** What content is duplicated across files and should be consolidated?
3. **Missing:** What content gaps exist that need to be filled?

Key files in scope:
- `.claude/config/invariants.md` (L1 - 100 lines)
- `CLAUDE.md` (L2 operational - 161 lines)
- `docs/epistemic_state.md` (L2 patterns - 109 lines)
- `.claude/haios-status-slim.json` (L2 status)
- Coldstart file selection and loading order

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Map current content across L1/L2/L3 files (what's where)
- [ ] Identify redundancies (content duplicated across files)
- [ ] Identify gaps (content missing from appropriate level)
- [ ] Assess coldstart token budget (how much context loaded)
- [ ] Recommend consolidation/migration actions

---

## History

### 2025-12-26 - Created (Session 122)
- Initial creation
- Spawned from INV-038 (third round of L1 architecture work)
- Scope: Audit useful/redundant/missing content in IA policy

---

## References

- INV-037: Context Level Architecture (L1/L2/L3 framework)
- INV-038: L1 Invariants Completeness Audit (validated invariants.md)
- E2-202: Enhanced invariants.md (now 100 lines)
- `.claude/commands/coldstart.md`: Current file loading order
