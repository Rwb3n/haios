---
template: work_item
id: WORK-067
title: HAIOS Portable Schema Architecture Investigation
type: investigation
status: active
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-065
chapter: null
arc: configuration
closed: null
priority: high
effort: medium
traces_to:
- L0.12
acceptance_criteria:
- Schema location strategy defined (where do portable schemas live?)
- Template reference pattern defined (how do templates consume schemas?)
- Project bootstrap pattern defined (how does new project get HAIOS schemas?)
- Core vs project-specific boundary defined
blocked_by: []
blocks:
- WORK-066
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 21:19:30
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82952
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T21:20:15'
---
# WORK-067: HAIOS Portable Schema Architecture Investigation

@docs/work/active/WORK-065/WORK.md
@docs/work/active/WORK-066/WORK.md

---

## Context

**Problem:** HAIOS must be portable to other projects, but schemas are scattered and inconsistent.

**Evidence (WORK-065 finding):**
- `current_node` enum defined in 3 places with 3 different values:
  - TRD-WORK-ITEM-UNIVERSAL: `backlog|planning|in_progress|review|complete`
  - GovernanceLayer: `backlog|discovery|plan|implement|close|complete`
  - L5-execution.md: `backlog|ready|in_progress|blocked|complete`
- Chapter status defined inline in template: `Planned | Approved | In Progress | Complete`
- No central schema registry
- No portability consideration

**Why it matters:**
- New project adopting HAIOS wouldn't know which enums are authoritative
- Schema drift causes bugs (94% of work items stuck at `backlog`)
- Adding new enum values (e.g., `Implemented-Deficient`) requires updating multiple files

**Questions to investigate:**
1. Where should portable schemas live? (haios.yaml? Separate schema file? In-code?)
2. How do templates reference schemas without hardcoding paths?
3. How does a new project bootstrap HAIOS schemas?
4. What's the boundary between "core HAIOS" (portable) and "project-specific"?
5. Should schemas be YAML, JSON Schema, or prose markdown?

---

## Deliverables

- [ ] **Schema location strategy** - Where portable schemas live, why
- [ ] **Template reference pattern** - How templates consume schemas (import? inline?)
- [ ] **Bootstrap pattern** - How new project initializes HAIOS schemas
- [ ] **Core/project boundary** - What's portable vs project-specific
- [ ] **Schema format recommendation** - YAML, JSON Schema, or markdown

---

## History

### 2026-02-01 - Created (Session 276)
- Spawned from discussion during E2.4 update
- WORK-065 revealed schema scatter problem
- Operator identified portability requirement
- Blocks WORK-066 (need schema decision before implementing queue_position)

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (current work item schema)
- @.claude/templates/chapter.md (inline status enum)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
- @.claude/haios/manifesto/L5-execution.md:76-87 (work DAG)
- @.claude/haios/config/haios.yaml (current config approach)
