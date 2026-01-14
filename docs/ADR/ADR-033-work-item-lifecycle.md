---
template: architecture_decision_record
status: accepted
date: 2025-12-10
adr_id: ADR-033
title: "Work Item Lifecycle Governance"
author: Hephaestus
session: 57
lifecycle_phase: decide
decision: accepted
approved_by: Operator
approved_date: 2025-12-10
---
# generated: 2025-12-10
# System Auto: last updated on: 2025-12-11 22:53:07
# ADR-033: Work Item Lifecycle Governance

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-10
> **Decision:** Option C - Full Governance Enforcement
> **Approved:** 2025-12-10 by Operator

---

## Context

HAIOS operates through **work items** - backlog entries (E2-xxx) that spawn lifecycle documents: plans, checkpoints, handoffs, reports, ADRs. While individual templates work well, three problems emerged in Session 56:

1. **No genealogy tracking** - A backlog item spawns a plan, which produces checkpoints, which may trigger investigations. But there's no formal parent-child linkage. Cannot answer: "What documents exist for E2-015?"

2. **Ambiguous "done"** - When is a work item complete? Code works? Tests pass? Plan status updated? The answer varies by agent, session, and context. No Definition of Done (DoD).

3. **Status inconsistency** - Templates use `complete` vs `completed` inconsistently. Report template allows `completed`, plan template allows `complete`. Queries and automation break on this.

**Evidence:**
- E2-015 plan said "add `backlog_ids` to checkpoint template" but wasn't done - discovered Session 56
- haios-status.json showed `backlog_id: null` for most plans until E2-015 retrofit (Session 49)
- Checkpoint template lacked `backlog_ids` field entirely until Session 56 fix

---

## Decision Drivers

- **Traceability:** Must answer "what spawned from this work item?" and "what work item does this document serve?"
- **Completion clarity:** Agent and operator must agree on what "done" means
- **WHY preservation:** Most valuable knowledge is reasoning (why), not just outcome (what)
- **Automation enablement:** UpdateHaiosStatus.ps1 should build work item trees
- **Backward compatibility:** Existing documents should continue to validate

---

## Considered Options

### Option A: Implicit Tracking (Status Quo)
**Description:** Continue with filename conventions and manual tracking. No schema changes.

**Pros:**
- No implementation work
- Existing docs unchanged

**Cons:**
- Genealogy queries impossible
- DoD remains undefined
- Status inconsistency persists

### Option B: Explicit Parent-Child Fields
**Description:** Add `parent_id` and `backlog_ids` fields to all templates. DoD defined but not enforced.

**Pros:**
- Genealogy queries become possible
- Backward compatible (new fields optional)
- Clear documentation of expectations

**Cons:**
- Manual discipline required
- No enforcement of DoD

### Option C: Full Governance Enforcement (Recommended)
**Description:** Explicit fields + DoD definition + automation hooks.

**Pros:**
- Complete traceability
- Clear completion criteria
- Automated validation possible
- Status normalized

**Cons:**
- Implementation effort
- May slow down rapid iteration
- Retrofitting existing docs

---

## Decision

**Adopt Option C: Full Governance Enforcement**

### 1. Work Item Definition

A **Work Item** is the atomic unit of governance. It is identified by a backlog ID (e.g., `E2-031`) and has a lifecycle:

```
PROPOSED -> RESEARCHING -> READY -> IMPLEMENTING -> COMPLETED/CANCELLED
```

A work item spawns **lifecycle documents**:
- **Plan** - Implementation specification (`parent_id` = backlog_id)
- **Checkpoint** - Session progress (`backlog_ids` = array of items worked)
- **Handoff** - Investigation/task transfer (`backlog_ids` = related items)
- **Report** - Findings documentation (`backlog_ids` = related items)
- **ADR** - Architectural decision (`backlog_ids` = triggering items)

### 2. Parent-Child Tracking Schema (Vertical Spawning)

| Template | Parent Field | Semantics |
|----------|--------------|-----------|
| `implementation_plan` | `backlog_id` (singular) | Plan implements this work item |
| `checkpoint` | `backlog_ids` (array) | Session touched these work items |
| `checkpoint` | `parent_id` (optional) | Plan being executed |
| `handoff` | `backlog_ids` (array) | Related work items |
| `report` | `backlog_ids` (array) | Related work items |
| `architecture_decision_record` | `backlog_ids` (array) | Work items that triggered this decision |

**Field additions already completed (Session 56):**
- `backlog_ids` added to checkpoint template
- `parent_id` added to validator for checkpoint and implementation_plan

### 2b. Sibling Spawning (Horizontal Relationships)

Work items can spawn NEW work items, not just documents. This is distinct from parent-child (containment) - this is generation.

**Example (Session 61):**
```
INV-006 (investigation)
  |-- spawns --> ADR-034 (new architectural decision)
  |-- spawns --> E2-032 (new implementation task)
  +-- unblocks --> E2-009 (was blocked, now can proceed)
```

| Relationship | Semantics | Field Location |
|--------------|-----------|----------------|
| `spawned_by` | This work item was created because of X | Backlog item |
| `blocks` | X cannot proceed until this completes | Backlog item |
| `blocked_by` | Cannot proceed until X completes | Backlog item |

**Governance rules:**
1. **Investigations MUST declare spawned items** - Before closing an INV-* item, all spawned work items must exist and be linked
2. **Blocked items should reference blocker** - Use `blocked_by` field, not just prose
3. **`/close` validates spawning** - Warns if spawned_by references don't exist

**Closure Completeness Constraint:**
> An investigation cannot be complete until all work items it spawned exist and reference it via `spawned_by`.

This is analogous to referential integrity - if INV-006 spawns E2-032, then E2-032 MUST have `spawned_by: INV-006`.

### 3. Definition of Done (DoD)

A work item is **COMPLETE** when ALL criteria are met:

| Criterion | Verification | Rationale |
|-----------|--------------|-----------|
| **Tests pass** | Automated test suite | Functional correctness |
| **WHY captured** | Memory storage with reasoning | Enables future agents to make better decisions |
| **Docs current** | CLAUDE.md, READMEs updated | Discoverability |
| **Traced files complete** | All spawned docs have completion status | Audit trail |

**WHY is most important.** Tests verify WHAT works. Docs explain HOW. But WHY - the reasoning behind decisions - is what compounds across sessions. Future agents can query "why did we choose X over Y?" and make informed decisions.

### 4. Status Normalization

Standardize on **`complete`** (not `completed`) across all templates:

| Template | Current | Normalized |
|----------|---------|------------|
| implementation_plan | `complete` | `complete` (unchanged) |
| checkpoint | `complete` | `complete` (unchanged) |
| report | `completed` | `complete` |
| handoff | `completed` | `complete` |
| backlog_item | `completed` | `complete` |

---

## Consequences

**Positive:**
- Genealogy queries enabled: "What documents exist for E2-015?"
- Clear completion criteria reduce ambiguity
- WHY preservation creates compounding knowledge
- Status automation becomes reliable

**Negative:**
- Retrofitting existing docs with `backlog_ids` requires effort
- DoD enforcement may slow iteration during exploration
- Status normalization requires validator update

**Neutral:**
- Existing documents without `backlog_ids` remain valid (field optional)
- DoD is documented but soft-enforced initially

---

## Implementation

Tracked via E2-031:

- [x] Add `backlog_ids` to checkpoint template (Session 56)
- [x] Add `parent_id` to validator OptionalFields (Session 56)
- [ ] Normalize status values in validator (`completed` -> `complete`)
- [ ] Update UpdateHaiosStatus.ps1 to build work item trees
- [ ] Add DoD section to backlog.md format
- [ ] Create `/close <backlog_id>` command for DoD enforcement
- [ ] Document WHY capture workflow in CLAUDE.md

---

## Related Decisions

- **ADR-030:** Document Taxonomy (foundation for template types)
- **ADR-031:** Workspace Awareness (surfaces outstanding work)
- **ADR-032:** Memory-Linked Work Governance (WHY capture mechanism)
- **E2-015:** Lifecycle ID Propagation (parent-child field implementation)
- **E2-023:** Work Loop Closure Automation (enforcement mechanism)

---

## Memory References

This ADR is supported by:
- **Session 56 checkpoint:** Work item lifecycle design discussion
- **Concepts 65008-65034:** Session 56 insights stored to memory

---
