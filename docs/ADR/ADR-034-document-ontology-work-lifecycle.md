---
template: architecture_decision_record
status: accepted
date: 2025-12-11
adr_id: ADR-034
title: "Document Ontology and Work Lifecycle"
author: Hephaestus
session: 61
lifecycle_phase: decide
decision: "Option C - Canonical Prefixes with Aliases"
approved_by: Operator
approved_date: 2025-12-11
---
# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 22:01:10
# ADR-034: Document Ontology and Work Lifecycle

@docs/README.md
@docs/epistemic_state.md

> **Status:** ACCEPTED
> **Date:** 2025-12-11
> **Decision:** Option C - Canonical Prefixes with Aliases
> **Approved:** 2025-12-11 by Operator

---

## Context

INV-006 (Session 60-61) audited the document taxonomy across `docs/` and found:

1. **14+ distinct file prefixes** in `docs/handoff/` alone (INVESTIGATION, INQUIRY, TASK, EVALUATION, VALIDATION, COMPLETION, GAP-CLOSER, PROTOTYPE, PROPOSAL, etc.)
2. **No canonical "Analysis/Discovery" phase** - work items jump from "created" to "planning" with no structured investigation phase
3. **ADR-030 lifecycle phases incomplete** - defined `observe -> capture -> decide -> plan -> execute -> verify -> complete` but "observe" has no documents and "discovery/analysis" is missing entirely
4. **E2-009 blocked** - cannot enforce "Plan-First" until we define what legitimately precedes planning

The current state is ad-hoc naming that:
- Confuses agents (which prefix to use?)
- Defeats queries (can't find "all analysis work")
- Prevents governance (can't enforce "investigate before plan")

---

## Decision Drivers

- **Lifecycle clarity** - Work items need a defined path from creation to closure
- **Prefix consolidation** - 14+ prefixes should reduce to 5-6 canonical ones
- **Governance enablement** - E2-009 needs to enforce sequence (can't plan without prior analysis)
- **Query support** - Must be able to find "all discovery phase documents"
- **Backward compatibility** - Existing documents should remain valid
- **ADR-030 alignment** - Build on existing hybrid (template + lifecycle_phase) decision

---

## Considered Options

### Option A: Keep Current Chaos
**Description:** Document the existing prefixes, don't enforce consolidation.

**Pros:**
- No migration effort
- No breaking changes

**Cons:**
- E2-009 remains blocked
- Queries remain unreliable
- New agents will invent more prefixes

### Option B: Strict Enforcement
**Description:** Mandate 5 prefixes only, reject all others.

**Pros:**
- Clean taxonomy
- Easy to enforce

**Cons:**
- Large migration burden
- May lose semantic nuance (PROTOTYPE vs INVESTIGATION)

### Option C: Canonical Prefixes with Aliases (Recommended)
**Description:** Define 5-6 canonical prefixes mapped to lifecycle phases. Existing prefixes become recognized aliases that map to canonical forms.

**Pros:**
- Clear taxonomy going forward
- Backward compatible
- Preserves existing document validity
- Enables gradual migration

**Cons:**
- Alias mapping adds complexity
- Two ways to express same thing initially

---

## Decision

**Option C: Canonical Prefixes with Aliases**

### Work Item Lifecycle (7 phases)

```
BACKLOG -> DISCOVERY -> DESIGN -> PLAN -> IMPLEMENT -> VERIFY -> CLOSE
```

| Phase | What Happens | Document Type | Canonical Prefix |
|-------|--------------|---------------|------------------|
| BACKLOG | Work identified | Backlog item | (in backlog.md) |
| DISCOVERY | Analysis, investigation, research | Investigation report | `INVESTIGATION-` |
| DESIGN | Architecture decisions | ADR | `ADR-` |
| PLAN | Implementation specification | Plan | `PLAN-` |
| IMPLEMENT | Code written | (code, not docs) | N/A |
| VERIFY | Testing, evaluation | Report | `REPORT-` |
| CLOSE | Completion, learnings extracted | Closure summary | (via `/close`) |

**Session documents (orthogonal to lifecycle):**
| Type | Canonical Prefix | Purpose |
|------|------------------|---------|
| Checkpoint | `SESSION-` or date-based | Capture session state |

**Note:** `HANDOFF-` is **deprecated**. The handoff pattern (session-to-session transfer) is now fully replaced by:
- Checkpoints for session state
- Backlog.md for work item tracking
- Memory system for learnings
- `/coldstart` for context restoration

### Prefix Alias Mapping

Existing prefixes map to canonical forms:

| Legacy Prefix | Maps To | Rationale |
|---------------|---------|-----------|
| INQUIRY | INVESTIGATION | Same phase (discovery) |
| RESEARCH | INVESTIGATION | Same phase (discovery) |
| RESEARCH-HANDOFF | INVESTIGATION | Same phase (discovery) |
| GAP-CLOSER | INVESTIGATION | Analyzing gaps = discovery |
| PROTOTYPE | INVESTIGATION | Exploratory work = discovery |
| EVALUATION | REPORT | Evaluating outcomes = verify phase |
| VALIDATION | REPORT | Validating results = verify phase |
| COMPLETION | (use /close) | Completion is a status, not a document |
| TASK | INVESTIGATION or direct work | Depends on content |
| PROPOSAL | ADR or INVESTIGATION | Depends on scope |
| DOC-UPDATE-HANDOFF | (deprecated) | Use checkpoint or backlog |
| HANDOFF | (deprecated) | Use checkpoint + backlog + memory |

### Template to Lifecycle Mapping

| Template | Lifecycle Phase | When to Use |
|----------|-----------------|-------------|
| `investigation` | discovery | Starting analysis work |
| `architecture_decision_record` | design | Recording architectural choices |
| `implementation_plan` | plan | Specifying how to build |
| `report` | verify | Documenting outcomes |
| `checkpoint` | (any) | Capturing session state |

**Deprecated templates:**
- `handoff` - Replaced by checkpoint + backlog + memory
- `handoff_investigation` - Rename to `investigation`

### Governance Rules (for E2-009)

1. **Plan requires prior Discovery** - Cannot create PLAN-* without linked INVESTIGATION-* or ADR-*
2. **Discovery can be skipped** - For trivial work items (operator discretion)
3. **Phase field required** - New documents must include `lifecycle_phase` in frontmatter
4. **Alias recognition** - Validator accepts legacy prefixes, maps to canonical for queries

---

## Consequences

**Positive:**
- E2-009 can now be implemented as "Lifecycle Sequence Enforcement"
- Clear guidance for agents on which prefix to use
- Queries work: "find all DISCOVERY phase docs" includes legacy INQUIRY, RESEARCH, etc.
- Gradual migration path - no forced renames

**Negative:**
- Alias mapping adds validator complexity
- Two prefixes may refer to same thing during transition
- Documentation needs updating

**Neutral:**
- Existing documents remain valid with legacy prefixes
- New documents should use canonical prefixes
- haios-status.json tracks both

---

## Implementation

- [ ] Update ValidateTemplate.ps1 with alias mapping table
- [ ] Rename `handoff_investigation` template to `investigation`
- [ ] Deprecate `handoff` template (keep for backward compat, warn on use)
- [ ] Replace `/new-handoff` with `/new-investigation` command
- [ ] Add `lifecycle_phase` validation (warn if missing on new files)
- [ ] Update E2-009 from "Plan-First" to "Lifecycle Sequence Enforcement"
- [ ] Create E2-032 backlog item for governance implementation
- [ ] Update CLAUDE.md with canonical prefix guidance
- [ ] Archive docs/handoff/HANDOFF_TYPES.md (obsolete)

---

## References

- **INV-006** - Document Ontology & Work Lifecycle Audit (Session 60-61)
- **ADR-030** - Document Taxonomy and Lifecycle Classification (foundation)
- **ADR-033** - Work Item Lifecycle Governance (DoD, /close command)
- **E2-009** - Plan-First Enforcement (blocked, needs redesign)

---
