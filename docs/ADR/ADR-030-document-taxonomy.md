---
template: architecture_decision_record
status: accepted
date: 2025-12-07
adr_id: ADR-030
title: "Document Taxonomy and Lifecycle Classification"
author: Hephaestus
session: 39
decision: "Option D - Hybrid (type + lifecycle_phase + subtype)"
approved_by: Operator
approved_date: 2025-12-07
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 12:29:40
# ADR-030: Document Taxonomy and Lifecycle Classification

@docs/README.md
@docs/epistemic_state.md

> **Status:** ACCEPTED
> **Date:** 2025-12-07
> **Decision:** Option D - Hybrid (type + lifecycle_phase + subtype)
> **Approved:** 2025-12-07 by Operator

---

## Archaeological Reference

This ADR supersedes and consolidates decisions from the HAIOS-RAW archaeological corpus:
- **ADR-OS-021** - Original template format mandate (`adr_os_template.md`)
- **ADRs 023-029** - Foundational policy ADRs (referenced in memory, Concept 34064)
- **ADR-OS-065** - Proposed v3 template adoption (never finalized)

These archaeological ADRs exist only in memory (via haios-etl processing). As of Epoch 2, ADR-030 is the first live ADR in the governance system.

---

## Context

The current template validator has a fixed list of document types that doesn't match what we're actually creating. For example:

**Validator accepts:** `architecture_decision_record, backlog_item, checkpoint, directive, guide, implementation_plan, implementation_report, meta_template, readme, verification`

**What we create:** `report, investigation, analysis, proposal, plan, checkpoint, handoff`

This causes validation errors (e.g., "Unknown template type 'report'") and indicates a systemic mismatch between the taxonomy and actual usage.

Additionally, we've defined a file lifecycle model with phases:
```
OBSERVE -> CAPTURE -> DECIDE -> PLAN -> EXECUTE -> VERIFY -> COMPLETE
```

The question is: how should document types relate to lifecycle phases?

---

## Decision Drivers

- **Validation errors are noise** - Current mismatches produce errors that reduce trust in the system
- **Lifecycle phases are functional** - They describe WHAT the document DOES, not its format
- **Template types are structural** - They describe HOW the document is formatted
- **Explosion of types is unmaintainable** - Creating `report_investigation`, `report_analysis`, `report_evaluation` etc. doesn't scale
- **Queries need to work** - "Find all documents in DECIDE phase" should be possible
- **Governance needs to enforce** - Commands like `/new-report` need clear scope

---

## Considered Options

### Option A: Flat Type List (Current Approach Extended)

**Description:** Add all variants as separate types to the validator.

```yaml
valid_types:
  - report
  - report_investigation
  - report_analysis
  - report_evaluation
  - plan
  - plan_implementation
  - proposal
  - ...
```

**Pros:**
- Explicit - each type is unambiguous
- Simple validation logic

**Cons:**
- Type explosion - N document types * M variants = N*M entries
- Hard to maintain
- Doesn't capture lifecycle semantics

### Option B: Base Type + Variant Field

**Description:** Use a primary `template` field plus a `variant` qualifier.

```yaml
template: report
variant: investigation | analysis | evaluation | status
```

**Pros:**
- Reduces type count
- Variant is optional for simple cases
- Commands can target base type (`/new-report`) with optional variant

**Cons:**
- Two fields to validate
- Variant values not standardized across types

### Option C: Lifecycle Phase as Primary Classifier

**Description:** Make `lifecycle_phase` the primary field, with `template` as secondary.

```yaml
lifecycle_phase: capture     # OBSERVE | CAPTURE | DECIDE | PLAN | EXECUTE | VERIFY
template: report            # Format/structure
```

**Pros:**
- Aligns with lifecycle model
- Queries like "find all DECIDE phase docs" become natural
- Phase determines governance rules (e.g., "DECIDE phase requires approval")

**Cons:**
- Breaking change from current approach
- Phase may not always be clear at creation time
- Some documents span phases (e.g., checkpoint summarizes EXECUTE)

### Option D: Hybrid - Type + Phase Metadata

**Description:** Keep `template` as primary classifier, add `lifecycle_phase` as queryable metadata.

```yaml
template: report            # Primary - determines structure
lifecycle_phase: capture    # Metadata - for indexing/queries
subtype: investigation      # Optional - further qualification
```

**Pros:**
- Backward compatible with existing types
- Lifecycle phase is additive, not required
- Flexible - can add phase later as document progresses
- Commands work naturally (`/new-report --phase=capture`)

**Cons:**
- Three fields is more complex than one
- Phase might drift from reality if not auto-updated

---

## Decision

**Recommended: Option D (Hybrid - Type + Phase Metadata)**

Rationale:
1. **Backward compatible** - existing documents don't break
2. **Lifecycle is metadata** - can be added/updated without changing structure
3. **Queries work both ways** - by type AND by phase
4. **Governance can layer** - enforce phase-specific rules without changing templates

**Validator changes:**
- Add missing base types: `report`, `proposal`, `handoff`, `investigation`
- Add optional fields: `lifecycle_phase`, `subtype`
- Keep existing types for backward compatibility

**Lifecycle phase values:**
```
observe   - Gathering information, investigating
capture   - Documenting findings, preserving state
decide    - Choosing approach, recording rationale
plan      - Specifying implementation
execute   - (not a document phase - this is code)
verify    - Evaluating outcomes
complete  - Archived, learnings extracted
```

---

## Consequences

**Positive:**
- Validation errors for current documents resolved
- Lifecycle queries enabled without breaking changes
- Clear path for adding phase-based governance

**Negative:**
- Validator schema needs update
- Documentation needs to explain three fields
- Risk of inconsistent phase tagging if not automated

**Neutral:**
- Existing documents get `lifecycle_phase: null` until updated
- New templates include phase in YAML front matter

---

## Implementation

- [ ] Update ValidateTemplate.ps1 to accept new types: `report`, `proposal`, `handoff`, `investigation`
- [ ] Add `lifecycle_phase` as optional valid field
- [ ] Add `subtype` as optional valid field
- [ ] Update haios-status.json `valid_templates` list
- [ ] Create/update templates to include lifecycle_phase
- [ ] Update CLAUDE.md with taxonomy documentation

---
