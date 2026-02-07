---
template: work_item
id: E2-269
title: manifest.yaml Creation
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-05'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-057
blocked_by: []
blocks: []
enables:
- E2-270
- E2-271
related:
- INV-057
- INV-052
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 22:28:53
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T22:29:34'
---
# WORK-E2-269: manifest.yaml Creation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** HAIOS cannot be distributed as a portable plugin because no `manifest.yaml` exists to declare plugin components (commands, skills, agents, hooks).

**Root cause:** SECTION-18-PORTABLE-PLUGIN-SPEC.md defines the manifest schema but was never implemented. Components exist in Claude CLI target paths but not in LLM-agnostic source format.

**Source:** INV-057 investigation (Session 172)

---

## Current State

Work item in BACKLOG node. Ready for planning.

---

## Deliverables

- [ ] Create `.claude/haios/manifest.yaml` per SECTION-18 schema
- [ ] Declare all 18 commands in manifest
- [ ] Declare all 15 skills in manifest
- [ ] Declare all 7 agents in manifest
- [ ] Declare all 4 hook handlers in manifest
- [ ] Add plugin metadata (name, version, description)
- [ ] Add dependency declarations (MCP servers, Python packages)

---

## History

### 2026-01-04 - Created (Session 172)
- Spawned from INV-057 investigation
- Purpose: Create plugin manifest per SECTION-18-PORTABLE-PLUGIN-SPEC.md

---

## References

- @docs/work/active/INV-052/SECTION-18-PORTABLE-PLUGIN-SPEC.md
- INV-057: Commands Skills Templates Portability investigation
