---
template: work_item
id: INV-041
title: Single Source Path Constants Architecture
status: complete
owner: Hephaestus
created: 2025-12-28
closed: '2026-02-02'
milestone: M7c-Governance
priority: medium
effort: medium
category: investigation
spawned_by: E2-212
spawned_by_investigation: null
arc: configuration
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
memory_refs:
- 83179
- 83180
- 83181
- 83182
- 83190
- 83191
- 83192
- 83193
- 83194
- 83195
- 83196
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2026-02-02T17:01:48'
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

**COMPLETE** - Session 290

---

## Deliverables

- [x] Inventory all path pattern definitions across codebase
- [x] Evaluate consolidation options (Python constants, YAML config, template variables)
- [x] Consider LLM-consumable vs code-consumable formats
- [x] Propose single source architecture
- [x] Assess migration complexity

---

## Findings (Session 290)

### Evidence Gathered

| Source | Finding |
|--------|---------|
| Grep analysis | **59 markdown files** + **11 Python files** contain hardcoded paths |
| `scaffold.py` | `TEMPLATE_CONFIG` centralizes template paths (8 types) |
| `work_engine.py` | `WORK_DIR`, `ACTIVE_DIR`, `ARCHIVE_DIR` module constants |
| `context_loader.py` | `MANIFESTO_PATH`, `STATUS_PATH`, `CONFIG_PATH` constants |
| `haios.yaml` | Already has partial path centralization in `epoch` section |
| `config.py` | `ConfigLoader` singleton exists for config access |

### Path Categories

| Category | Example | Current Location |
|----------|---------|------------------|
| Work paths | `docs/work/active` | work_engine.py, skills |
| Template paths | `.claude/templates` | scaffold.py |
| Document paths | `docs/checkpoints` | scaffold.py, skills |
| Plugin paths | `.claude/skills` | various modules |

### Architecture Decision

**Extend haios.yaml with `paths:` section, consumed via ConfigLoader.paths**

```yaml
paths:
  work_dir: "docs/work"
  work_active: "docs/work/active"
  work_item: "docs/work/active/{id}/WORK.md"
  templates: ".claude/templates"
  skills: ".claude/skills"
```

### Key Insights

1. **Dual format needed**: Paths as strings with `{placeholder}` syntax serve both:
   - Python: `ConfigLoader.get_path("work_item", id="X")` returns Path object
   - Prose: Raw strings with placeholders for LLM consumption

2. **TEMPLATE_CONFIG stays separate**: It's template-specific, not general path registry

3. **Staged migration**:
   - Phase 1-3: Python modules (11 files) - testable, low risk
   - Phase 4: Prose consumers (59 files) - higher effort, needs pattern design

### Spawned Work

- **WORK-080**: Single Source Path Constants Implementation (pending creation)

---

## History

### 2026-02-02 - Completed (Session 290)
- Investigation complete with architecture recommendation
- Evidence: 70+ files with hardcoded paths (59 md, 11 py)
- Decision: Extend haios.yaml with `paths:` section + ConfigLoader.paths
- Spawned: WORK-080 for implementation
- Memory refs: 83179-83182

### 2025-12-28 - Created (Session 132)
- Spawned from E2-212 closure gap analysis
- Identified pattern: path conventions scattered across 10+ files

---

## References

- Spawned by: E2-212 (Work Directory Structure Migration)
- Related: INV-040 (Automated Stale Reference Detection) - would benefit from centralized patterns
- Related: E2-076 (DAG Governance Architecture) - mentions pattern fields
- **Arc:** Chariot ARC-004 (PathAuthority) - recipes own paths, agent doesn't hardcode (S190)
