---
template: work_item
id: E2-200
title: Create invariants.md with Extracted Evergreen Facts
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-037
spawned_by_investigation: INV-037
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 10:50:14
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T11:18:17'
---
# WORK-E2-200: Create invariants.md with Extracted Evergreen Facts

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** INV-037 confirmed significant evergreen invariants are buried in archives (Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs) and never surfaced to agent at coldstart.

**Root cause:** Historical philosophical content was deprecated but never extracted into an accessible L1 context file.

---

## Current State

Work item in BACKLOG node. Ready for implementation.

---

## Deliverables

- [ ] Create `.claude/config/invariants.md` with extracted evergreen facts
- [ ] Include: Certainty Ratchet, Three Pillars, SDD Framework, Governance Flywheel
- [ ] Include: Universal Idempotency, 5-Phase Loop, Structured Mistrust
- [ ] Format for agent consumption (concise, actionable)
- [ ] Update `.claude/config/README.md` to reference new file

---

## History

### 2025-12-26 - Created (Session 121)
- Spawned from INV-037 H2 finding (buried treasure confirmed)
- Scope: Extract evergreen facts from deprecated/archived files

---

## References

- INV-037: Context Level Architecture and Source Optimization
- Source files: Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW/system/canon/ADR/
