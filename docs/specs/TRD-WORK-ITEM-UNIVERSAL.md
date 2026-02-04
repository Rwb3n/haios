# generated: 2026-01-18
# System Auto: last updated on: 2026-02-04T21:11:31
# TRD: Universal Work Item Structure

Status: APPROVED
Created: Session 206
Approved: Session 218
Purpose: Define the canonical work item structure for the doc-to-product pipeline

---

## Problem Statement

Current work items are HAIOS-specific:
- ID prefixes encode type (`E2-XXX`, `INV-XXX`)
- Fields assume HAIOS context (`milestone`, `spawned_by_investigation`)
- Not portable to other projects

The pipeline needs work items that:
- Are generic (work for any project)
- Link to source requirements (traceability)
- Support the INGEST → PLAN → BUILD → VALIDATE flow

---

## Design Principles

1. **Type is a field, not a prefix** - `type: feature` not `FEAT-001`
2. **IDs are sequential** - `WORK-001`, `WORK-002` (simple, no semantics)
3. **Requirements are first-class** - `requirement_refs` links to source specs
4. **Portable** - No HAIOS-specific fields in core structure
5. **Extensible** - Project-specific fields go in `extensions` block

---

## Rationale (Session 218 Deep-Dive)

### WHY Sequential IDs?

| Approach | Pros | Cons |
|----------|------|------|
| **Semantic (E2-XXX)** | Type visible | Type encoded twice, refactoring changes IDs, epoch coupling |
| **UUID** | Globally unique | Not human-readable, hard to reference |
| **Sequential (WORK-001)** | Human-readable, simple | No semantic info (but type is queryable) |

**Decision:** Sequential because:
- **Type as field** - Queryable, changeable without ID change
- **Epoch as field** - Work items survive epoch transitions
- **Human-readable** - Easy to reference in conversation

Memory refs: 82144, 81612

### WHY This Type Taxonomy?

5 types: `feature`, `investigation`, `bug`, `chore`, `spike`

**Evidence:** WorkEngine already implements this (line 91). Backward compatible with `category` field.

**Actual usage (62 items):**
- 48 `implementation` → maps to `feature`
- 9 `investigation` → same
- Others unused but needed for pipeline portability

### Acceptance Criteria vs Deliverables

| Field | Location | Purpose | Consumer |
|-------|----------|---------|----------|
| `acceptance_criteria` | Frontmatter | Validation target | Automated tools |
| `## Deliverables` | Body | Work tracking | Agent checkboxes |

**They serve different purposes.** Not duplication.

---

## Universal Work Item Schema

### Frontmatter (YAML)

```yaml
---
# === IDENTITY ===
template: work_item
id: WORK-001                    # Sequential ID (no type prefix)
title: "Implement OAuth2 flow"
type: feature                   # feature|investigation|bug|chore|spike

# === STATUS ===
status: active                  # active|blocked|complete|archived
created: 2026-01-18
closed: null

# === OWNERSHIP ===
owner: null                     # Agent or human responsible

# === PRIORITIZATION ===
priority: high                  # critical|high|medium|low
effort: medium                  # small|medium|large|unknown

# === TRACEABILITY (Pipeline Integration) ===
requirement_refs: []            # Links to source requirements [REQ-001, REQ-002]
source_files: []                # Source docs this came from [specs/auth.md:15-42]
acceptance_criteria: []         # From requirements, verifiable statements

# === DEPENDENCIES ===
blocked_by: []                  # Work items that must complete first
blocks: []                      # Work items waiting on this
enables: []                     # Work items this unlocks (softer than blocks)

# === LIFECYCLE ===
queue_position: backlog         # WORK-066: backlog|in_progress|done (work selection state)
cycle_phase: backlog            # WORK-066: backlog|plan|implement|check|done (lifecycle phase)
current_node: backlog           # DEPRECATED: use cycle_phase (kept for backward compat)
node_history:
  - node: backlog
    entered: 2026-01-18T16:00:00
    exited: null

# === ARTIFACTS ===
artifacts: []                   # Produced files [src/auth/oauth.py, tests/test_oauth.py]
cycle_docs: {}                  # Plans, findings, observations

# === MEMORY ===
memory_refs: []                 # Concept IDs from memory system

# === EXTENSIONS (Project-Specific) ===
extensions: {}                  # Project can add custom fields here

# === META ===
version: "2.0"                  # Schema version
generated: 2026-01-18
last_updated: 2026-01-18T16:00:00
---
```

### Body (Markdown)

```markdown
# WORK-001: Implement OAuth2 flow

---

## Context

[Problem statement - what and why]

---

## Acceptance Criteria

<!-- Copied from requirement_refs, made explicit -->
- [ ] OAuth2 authorization flow completes successfully
- [ ] Tokens stored securely (encrypted at rest)
- [ ] Refresh token rotation implemented

---

## Deliverables

- [ ] `src/auth/oauth.py` - OAuth2 client implementation
- [ ] `tests/test_oauth.py` - Unit tests
- [ ] Documentation updated

---

## History

### 2026-01-18 - Created
- Extracted from REQ-001 (specs/auth.md:15-42)

---

## References

- @specs/auth.md (source requirement)
```

---

## Changes from Current Template

| Field | Current | Universal | Reason |
|-------|---------|-----------|--------|
| `id` | `E2-XXX`, `INV-XXX` | `WORK-001` | Type not in ID |
| `type` | Implied by prefix | Explicit field | Queryable, portable |
| `milestone` | HAIOS-specific | Removed | Use `extensions` if needed |
| `spawned_by` | HAIOS-specific | Removed | Use `requirement_refs` |
| `spawned_by_investigation` | HAIOS-specific | Removed | Use `requirement_refs` |
| `category` | `implementation` | Renamed to `type` | Clearer semantics |
| `requirement_refs` | NEW | Links to source specs | Pipeline traceability |
| `source_files` | NEW | Where requirement came from | Provenance |
| `acceptance_criteria` | NEW | Verifiable statements | Validation target |
| `artifacts` | NEW | What was produced | Build output |
| `extensions` | NEW | Project-specific fields | Extensibility |
| `operator_decisions` | HAIOS-specific | Removed | Use `extensions` if needed |
| `documents.investigations` | HAIOS-specific | Removed | Use `cycle_docs` |

---

## ID Generation

Sequential within project:
```
WORK-001, WORK-002, WORK-003, ...
```

**Implementation:**
- Read highest existing ID from work directory
- Increment by 1
- No gaps (if WORK-003 deleted, next is still WORK-004)

**Migration:**
- Existing `E2-XXX` and `INV-XXX` items keep their IDs (archived)
- New items use `WORK-XXX` format
- No renaming of historical items

---

## Type Taxonomy

| Type | Purpose | Example |
|------|---------|---------|
| `feature` | New functionality | "Implement OAuth2" |
| `investigation` | Research, discovery | "Evaluate auth libraries" |
| `bug` | Fix broken behavior | "Fix token expiration" |
| `chore` | Maintenance, cleanup | "Update dependencies" |
| `spike` | Time-boxed exploration | "Prototype WebSocket approach" |

---

## Lifecycle Nodes

### Queue Position (WORK-066)

Work selection pipeline state - orthogonal to lifecycle phase:

```
backlog → in_progress → done
```

| Position | Meaning |
|----------|---------|
| `backlog` | Available for selection |
| `in_progress` | Currently being worked (single active constraint) |
| `done` | Work complete, closed |

### Cycle Phase (WORK-066)

Lifecycle phase within a work item (replaces current_node):

```
backlog → plan → implement → check → done
                    ↑          │
                    └──────────┘
                    (rework if check fails)
```

| Phase | Meaning |
|-------|---------|
| `backlog` | Identified, not started |
| `plan` | Being decomposed/planned |
| `implement` | Actively being built |
| `check` | Awaiting validation |
| `done` | Done, acceptance criteria met |

### Legacy current_node (DEPRECATED)

The `current_node` field is deprecated but kept for backward compatibility. New code should use `cycle_phase`. Legacy values map as follows:

| current_node | cycle_phase |
|--------------|-------------|
| `backlog` | `backlog` |
| `planning` | `plan` |
| `in_progress` | `implement` |
| `review` | `check` |
| `complete` | `done` |

---

## Validation Rules

**On creation:**
- `id` must be unique
- `title` must be non-empty
- `type` must be valid enum
- `requirement_refs` should be populated (warning if empty)

**On transition to complete:**
- All `acceptance_criteria` must be checked
- All `deliverables` must be checked
- `artifacts` should be non-empty (warning if empty)

---

## Migration Path

1. **New items:** Use universal structure immediately
2. **Active E2/INV items:** Keep as-is until complete, then archive
3. **Archived items:** No migration (historical record)

---

## Implementation Tasks

1. Update `work_item.md` template with universal structure
2. Update WorkEngine to handle new fields
3. Update scaffold functions for new ID format
4. Update validation to check new required fields
5. Test with first universal work item (WORK-001)

---

## References

- S26: Pipeline Architecture (traceability requirements)
- Form CH-006: WorkUniversality (original chapter)
- Current template: `.claude/templates/work_item.md`
