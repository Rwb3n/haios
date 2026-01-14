---
template: work_item
id: INV-041
title: Single Source Path Constants Architecture
status: active
owner: Hephaestus
created: 2025-12-28
closed: null
milestone: M7c-Governance
priority: medium
effort: medium
category: investigation
spawned_by: E2-212
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 11:16:21
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T11:27:40'
---
# WORK-INV-041: Single Source Path Constants Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Path patterns are defined in multiple places across the codebase, leading to drift when conventions change.

**Evidence from E2-212:**
- `docs/plans/PLAN-{id}-*.md` appeared in 10+ files (skills, agents, commands, config, hooks)
- New pattern `docs/work/active/{id}/plans/PLAN.md` required updating each file individually
- No single source of truth for path conventions

**Current scattered definitions:**
- `.claude/lib/scaffold.py` - TEMPLATE_CONFIG dict
- `.claude/config/node-cycle-bindings.yaml` - pattern fields
- `.claude/skills/*.md` - hardcoded paths in prose
- `.claude/commands/*.md` - hardcoded paths in examples

**Root cause:** Each layer defines its own path strings. When a pattern changes, all consumers must be manually updated.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Inventory all path pattern definitions across codebase
- [ ] Evaluate consolidation options (Python constants, YAML config, template variables)
- [ ] Consider LLM-consumable vs code-consumable formats
- [ ] Propose single source architecture
- [ ] Assess migration complexity

---

## History

### 2025-12-28 - Created (Session 132)
- Spawned from E2-212 closure gap analysis
- Identified pattern: path conventions scattered across 10+ files

---

## References

- Spawned by: E2-212 (Work Directory Structure Migration)
- Related: INV-040 (Automated Stale Reference Detection) - would benefit from centralized patterns
- Related: E2-076 (DAG Governance Architecture) - mentions pattern fields
