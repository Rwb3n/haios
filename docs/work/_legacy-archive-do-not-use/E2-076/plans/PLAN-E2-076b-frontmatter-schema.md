---
template: implementation_plan
status: complete
date: 2025-12-14
backlog_id: E2-076b
title: "Frontmatter Schema (DAG Edge Fields)"
author: Hephaestus
lifecycle_phase: plan
session: 75
parent_plan: E2-076
spawned_by: PLAN-E2-076
absorbs: [E2-070, INV-013]
related: [E2-076, E2-076d, E2-076e, ADR-033, E2-069]
version: "1.1"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-16 18:19:25
# Implementation Plan: Frontmatter Schema (DAG Edge Fields)

@docs/README.md
@docs/epistemic_state.md
@docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md

---

## Goal

Standardize DAG edge fields (`spawned_by`, `blocked_by`, `related`, `milestone`) across all template types, enabling machine-traversable dependency graphs and cascade hook detection.

---

## Current State vs Desired State

### Current State

```powershell
# .claude/hooks/ValidateTemplate.ps1:32-75
# Edge fields are inconsistent across templates:

"backlog_item" = @{
    OptionalFields = @("spawned_by", "blocks", "blocked_by", "memory_refs")  # Has edges
}
"architecture_decision_record" = @{
    OptionalFields = @("spawned_by", "spawns", ...)  # Partial edges
}
"investigation" = @{
    OptionalFields = @("spawned_by", "spawns")  # Partial edges
}
"checkpoint" = @{
    OptionalFields = @("parent_id", ...)  # No standard edges
}
"implementation_plan" = @{
    OptionalFields = @("parent_id", ...)  # No standard edges
}
```

**Behavior:** Some templates have edge fields, others don't. Naming is inconsistent (`parent_id` vs `spawned_by`).

**Result:**
- Cascade hooks can't reliably find dependencies
- Graph traversal requires special-casing per template type
- `blocked_by` only exists on backlog_item

### Desired State

```powershell
# All templates have consistent edge fields
$commonEdgeFields = @("spawned_by", "blocked_by", "related", "milestone", "parent_plan")

"checkpoint" = @{
    OptionalFields = @(..., "spawned_by", "blocked_by", "related", "milestone")
}
"implementation_plan" = @{
    OptionalFields = @(..., "spawned_by", "blocked_by", "related", "milestone", "parent_plan")
}
# etc.
```

**Behavior:** All document types can participate in DAG as nodes with typed edges

**Result:**
- Cascade hooks work uniformly
- Graph is fully traversable
- Dependencies are machine-readable

---

## Edge Field Definitions

| Field | Type | Semantics | Cascade Behavior |
|-------|------|-----------|------------------|
| `spawned_by` | string (ID) | Parent that created this item | Informational only |
| `blocked_by` | string/array | Items that must complete first | **UNBLOCK**: On blocker COMPLETE, this becomes READY |
| `related` | array | Bidirectional reference | **RELATED**: On complete, surface "may need review" |
| `milestone` | string | Milestone this contributes to | **MILESTONE**: On COMPLETE, recalculate milestone % |
| `parent_plan` | string | For subplans - links to master plan | Informational, enables rollup |

### Cascade Integration (E2-076e)

These edge fields enable the four cascade types defined in the parent plan:

| Edge Field | Cascade Type | CascadeHook.ps1 Function |
|------------|--------------|--------------------------|
| `blocked_by` | Unblock | `Get-UnblockedItems` scans for this field |
| `related` | Related | `Get-RelatedItems` scans for this field |
| `milestone` | Milestone | `Get-MilestoneDelta` uses this to calculate % |
| (body refs) | Substantive | `Get-SubstantiveReferences` scans CLAUDE.md/README |

Without standardized edge fields, CascadeHook.ps1 cannot reliably detect dependencies.

### Edge Field Format

```yaml
# Single value
spawned_by: INV-016

# Single value (blocked_by often single)
blocked_by: E2-076a

# Array format (when multiple)
blocked_by: [E2-076a, E2-076d]
related: [E2-069, INV-011, INV-012]

# Milestone reference
milestone: M2-Governance
```

---

## Current Template Audit

| Template | spawned_by | blocked_by | related | milestone | parent_plan | Action |
|----------|------------|------------|---------|-----------|-------------|--------|
| checkpoint | No | No | No | No | No | Add all |
| implementation_plan | No | No | No | No | No | Add all |
| architecture_decision_record | Yes | No | No | No | No | Add blocked_by, related, milestone |
| investigation | Yes | No | No | No | No | Add blocked_by, related, milestone |
| report | No | No | No | No | No | Add all |
| readme | No | No | No | No | No | Add spawned_by, related only |
| backlog_item | Yes | Yes | No | No | No | Add related, milestone |

---

## Implementation Steps

### Step 1: Update ValidateTemplate.ps1 Registry
- [ ] Add `spawned_by` to: checkpoint, implementation_plan, report
- [ ] Add `blocked_by` to: checkpoint, implementation_plan, architecture_decision_record, investigation, report
- [ ] Add `related` to: all templates
- [ ] Add `milestone` to: checkpoint, implementation_plan, architecture_decision_record, investigation, backlog_item
- [ ] Add `parent_plan` to: implementation_plan (for subplans)

### Step 2: Update Template Files
- [ ] `.claude/templates/checkpoint.md` - Add edge fields to frontmatter
- [ ] `.claude/templates/implementation_plan.md` - Add edge fields
- [ ] `.claude/templates/architecture_decision_record.md` - Add missing fields
- [ ] `.claude/templates/investigation.md` - Add missing fields
- [ ] `.claude/templates/report.md` - Add edge fields

### Step 3: Document Edge Semantics
- [ ] Add edge field definitions to ADR-038 (E2-076a)
- [ ] Update CLAUDE.md with edge field reference table

### Step 4: Verification
- [ ] Run `/validate` on each template - should pass
- [ ] Test that existing documents still validate
- [ ] Test cascade hook can find blocked_by references

---

## Detailed Design

### ValidateTemplate.ps1 Changes

```powershell
# New common edge fields to add to OptionalFields arrays
$dagEdgeFields = @("spawned_by", "blocked_by", "related", "milestone")

# Updated registry entries:
"checkpoint" = @{
    RequiredFields = @("template", "status", "date", "version", "author", "project_phase")
    OptionalFields = @(
        "previous_checkpoint", "directive_id", "title", "session",
        "lifecycle_phase", "subtype", "backlog_ids", "parent_id",
        # DAG edge fields (E2-076b)
        "spawned_by", "blocked_by", "related", "milestone", "prior_session", "memory_refs"
    )
    AllowedStatus = @("draft", "active", "complete", "archived")
}

"implementation_plan" = @{
    RequiredFields = @("template", "status", "date", "directive_id")
    OptionalFields = @(
        "version", "author", "plan_id", "title", "session", "priority",
        "lifecycle_phase", "subtype", "backlog_id", "parent_id",
        "completed_session", "completion_note",
        # DAG edge fields (E2-076b)
        "spawned_by", "blocked_by", "related", "milestone", "parent_plan"
    )
    AllowedStatus = @("draft", "approved", "rejected", "complete")
}
```

### Template Frontmatter Example

```yaml
---
template: implementation_plan
status: draft
date: 2025-12-14
backlog_id: E2-076e
title: "Cascade Hooks"
# DAG edge fields
spawned_by: PLAN-E2-076
blocked_by: [E2-076b, E2-076d]
related: [E2-076, ADR-033]
milestone: M2-Governance
parent_plan: E2-076
---
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Array vs single value | Support both | Single for common case, array for complex dependencies |
| Field naming | Use `spawned_by` not `parent_id` | Clearer semantics, consistent across templates |
| Milestone as string | Yes | Simple ID reference, not structured object |
| Add to OptionalFields | Yes | Don't break existing documents that lack edges |

---

## Tests First (TDD)

### Test 1: New Fields Accepted
```bash
# Create test file with new edge fields
# Run /validate
# Expected: Pass without "unknown field" warning
```

### Test 2: Backward Compatibility
```bash
# Existing documents without edge fields
# Run /validate
# Expected: Still pass (fields are optional)
```

### Test 3: Array Format Accepted
```bash
# Test blocked_by: [E2-076a, E2-076d]
# Expected: Parses without error
```

---

## Verification

- [ ] All 7 template types updated in ValidateTemplate.ps1
- [ ] Template files (.claude/templates/*.md) have edge fields
- [ ] Existing documents validate without regression
- [ ] Edge fields documented in ADR-038

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing documents | Medium | Fields are optional, not required |
| YAML array parsing | Low | ValidateTemplate already handles arrays |
| Documentation drift | Low | Edge semantics in ADR-038, single source of truth |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 75 | 2025-12-14 | - | Draft | Subplan created |
| 79 | 2025-12-16 | SESSION-79 | Complete | Implementation complete |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/ValidateTemplate.ps1` | All templates have edge fields in OptionalFields | [x] | 7 templates updated |
| `.claude/templates/checkpoint.md` | Has spawned_by, blocked_by, related, milestone | [x] | Added as comments |
| `.claude/templates/implementation_plan.md` | Has edge fields + parent_plan | [x] | Added as comments |
| `docs/plans/PLAN-E2-076-*.md` | Documents edge field semantics | [x] | E2-076 parent plan has edge definitions |

**Verification Commands:**
```bash
# Validate a plan with edge fields
powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath "docs/plans/PLAN-E2-076e-cascade-hooks.md" -VerboseOutput
# Result: PASS - all edge fields accepted

# Backward compatibility - old checkpoint
powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath "docs/checkpoints/2025-12-06-SESSION-34-documentation-hardening.md"
# Result: PASS - old docs still valid
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | ValidateTemplate.ps1, 5 templates |
| Existing documents still validate? | Yes | Tested old checkpoint |
| Any deviations from plan? | Yes | ADR-038 skipped - edge semantics in E2-076 parent plan |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (validation works)
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current (edge semantics in E2-076 parent plan)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## Dependencies

### Blocked By
- None (E2-076a blocker removed Session 78 - ADR content already in E2-076 main plan)

### Blocks
- **E2-076e** (Cascade Hooks) - Needs edge fields to detect blocked_by relationships

### Absorbs (Session 78 Consolidation)
- **E2-070** (Backlog Item Milestone Linking) - Same scope: add milestone field to templates
- **INV-013** (Spawning Mechanism Consistency Audit) - Same scope: normalize spawning fields

---

## References

- **Parent Plan:** `docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md`
- **Related:** ADR-033 (Work Item Lifecycle), ADR-034 (Document Ontology)
- **Memory:** Concepts 50372, 71375 (DAG structure)

---
