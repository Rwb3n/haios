---
template: architecture_decision_record
status: accepted
date: 2025-12-23
adr_id: ADR-039
title: "Work-Item-as-File-Architecture"
author: Hephaestus
session: 105
lifecycle_phase: decide
decision: accepted
spawned_by: INV-024
blocked_by: []
related: [ADR-033, ADR-034, ADR-036, INV-022, INV-024]
milestone: Future
backlog_id: ADR-039
memory_refs: []
version: "1.1"
generated: 2025-12-23
last_updated: 2025-12-24T09:33:53
---
# ADR-039: Work-Item-as-File-Architecture

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-024-work-item-as-file-architecture.md
@docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md

> **Status:** Accepted
> **Date:** 2025-12-23
> **Decision:** Migrate work items from backlog.md entries to individual files

---

## Context

**Current State:**
- Work items are text entries in monolithic `backlog.md` (1,224 lines, 62 items)
- Context scattered across spawned documents (E2-091 spans 14 files)
- Only 7/62 items have explicit Plan/Investigation links
- Status drift risk: backlog entry may not match plan file status

**Pain Points (INV-024 findings):**
| Pain Point | Measurement |
|------------|-------------|
| Backlog bloat | 1,224 lines, hard to navigate |
| Context scattering | Single item context in 14+ files |
| Low cross-references | 89% of items lack explicit links |
| Status drift | Dual sources of truth |

**Prior Work:**
- **INV-022:** Designed Work-Cycle-DAG architecture with Work File Schema v2
- **INV-024:** Validated feasibility, pain points, and created prototype
- **ADR-036:** Established lean architecture pattern (archive + query)

---

## Decision Drivers

- **Single Source of Truth:** Work item status should live in one place
- **Context Accumulation:** Work history should accumulate in one file
- **Navigation:** Finding work item context should be O(1) not O(n)
- **Lifecycle Visibility:** Current phase should be explicit in file location
- **Tooling Compatibility:** Must work with existing hooks, commands, status generator

---

## Considered Options

### Option A: Status Quo (Backlog.md)
**Description:** Keep work items as text entries in monolithic backlog.md

**Pros:**
- No migration effort
- Single file to search

**Cons:**
- 1,224 lines and growing
- Context scattered across 14+ files per item
- Status drift between backlog and spawned docs
- No lifecycle visibility

### Option B: Work-Item-as-File (ADOPTED)
**Description:** Each work item is a file that traverses lifecycle phases, accumulating context.

**Pros:**
- Single source of truth per item
- Context accumulates in one file
- Lifecycle visible in directory structure
- DAG edges in frontmatter enable dependency queries
- Adopts proven INV-022 schema

**Cons:**
- Migration effort required
- More files to manage (but fewer lines per file)
- Tooling updates needed

---

## Decision

**Adopt Work-Item-as-File Architecture** as designed in INV-022 and validated in INV-024.

### Schema (INV-022 Work File Schema v2)

```yaml
---
template: work_item
id: E2-xxx
title: "Work Item Title"
status: active | blocked | complete | archived

# Ownership
owner: Hephaestus
created: 2025-12-23
closed: null

# Classification
milestone: M5-Plugin
priority: high | medium | low
effort: low | medium | high
category: implementation | investigation | adr | maintenance

# DAG Edges
spawned_by: Session-105
blocked_by: []
blocks: []
enables: []
related: []

# NODE-CYCLE STATE
current_node: backlog | discovery | design | plan | implement | close
node_history: [...]
cycle_docs: {}

# Context accumulation
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
---
```

### Directory Structure

```
docs/work/
├── active/      # status: active
├── blocked/     # status: blocked
└── archive/     # status: complete | archived
```

Files move between directories on status change, providing visual lifecycle.

---

## Consequences

**Positive:**
- Single source of truth per work item
- Context accumulates in one file (no scattering)
- O(1) navigation to work item context
- Lifecycle visible in directory structure
- Enables future Work-Cycle-DAG automation (INV-022)

**Negative:**
- Migration effort (3-phase approach)
- Tooling updates required (/close, cascade, status generator)
- More files in docs/work/ (but each file is self-contained)

**Neutral:**
- backlog.md becomes legacy index (read-only)
- Query patterns change (glob docs/work/ vs grep backlog.md)

---

## Implementation

### Phase 1: Infrastructure (E2-150)
- [ ] Create `docs/work/{active,blocked,archive}/` directories
- [ ] Create `work_item` template in `.claude/templates/`
- [ ] Add `/new-work` command (or extend existing)
- [ ] Update status.py to scan `docs/work/`

### Phase 2: Migration (E2-151)
- [ ] Script to parse backlog.md and extract entries
- [ ] Create WORK-{id}.md files in `docs/work/active/`
- [ ] Preserve original content as `## Context`
- [ ] Retain backlog.md as legacy index (read-only)

### Phase 3: Cutover (E2-152)
- [x] Update `/close` to modify work file status, move to archive/
- [x] Update cascade to scan work files for blocked_by
- [x] Update status generator to read from docs/work/
- [ ] Add PreToolUse warning for backlog.md writes

### Phase 4: Enforcement (E2-160)
- [ ] L3 gate in scaffold.py: require work file before investigations/plans
- [ ] Block `scaffold_template()` for `investigation`, `implementation_plan` if no `WORK-{id}-*.md` exists
- [ ] User-friendly error: "Work file required. Run '/new-work {id} title' first."
- [ ] Tests for gate logic

**Rationale:** INV-020 established L3 (gated) enforcement is highly effective vs L2 (prompted).
Without this gate, documents can be created that bypass the work file lifecycle entirely,
making scaffold-on-entry (E2-154) and exit gates (E2-155) ineffective.

---

## References

- **INV-022:** Work-Cycle-DAG Unified Architecture (Memory 77119, 77261)
- **INV-024:** Work Item as File Investigation (this ADR's source)
- **ADR-033:** Work Item Lifecycle Governance
- **ADR-034:** Document Ontology
- **ADR-036:** PM Data Architecture
- **Prototype:** `docs/work/active/WORK-E2-143.md`

---
