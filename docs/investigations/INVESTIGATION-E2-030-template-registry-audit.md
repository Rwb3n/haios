---
template: investigation
status: complete
date: 2025-12-13
backlog_id: E2-030
title: "Investigation: Template Registry Audit"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:55:53
# Investigation: Template Registry Audit

@docs/README.md
@docs/epistemic_state.md

---

## Context

E2-008 (Session 40) added template types to the validator to stop validation errors. This was ADDITIVE - making the system recognize more types. E2-030 questions whether all 14 types are actually needed.

**Related:** E2-008 (Schema Sync), E2-029 (New Backlog Command), ADR-034 (Ontology Cleanup)

---

## Objective

Audit each of the 14 template types for:
1. Actual usage in codebase
2. Existence of corresponding `/new-*` command
3. Deprecation status per ADR-034
4. Recommend removal, deprecation, or retention

---

## Scope

### In Scope
- 14 template types in ValidateTemplate.ps1
- `/new-*` commands in `.claude/commands/`
- Template files in `.claude/templates/`
- ADR-034 deprecation guidance

### Out of Scope
- Changing template structures (field requirements)
- Creating new commands (that's E2-029)

---

## Findings

### Template Usage Audit

| Template Type | Files Using | Has Command | Template File | Status |
|---------------|-------------|-------------|---------------|--------|
| checkpoint | 50+ | /new-checkpoint | Yes | **ACTIVE** |
| implementation_plan | 35+ | /new-plan | Yes | **ACTIVE** |
| implementation_report | 8 | No | No | **ACTIVE** |
| architecture_decision_record | 6 | /new-adr | Yes | **ACTIVE** |
| readme | 5 | No | No | **ACTIVE** |
| handoff_investigation | 5 | No | Yes (deprecated) | **DEPRECATED** |
| investigation | 4 | /new-investigation | Yes | **ACTIVE** |
| report | 3 | /new-report | Yes | **ACTIVE** |
| handoff | 6+ | /new-handoff | No | **DEPRECATED** |
| proposal | 1 | No | No | **LOW USE** |
| directive | 1 | No | No | **LOW USE** |
| guide | 1 | No | No | **LOW USE** |
| verification | 0 | No | No | **UNUSED** |
| meta_template | 0 | No | No | **UNUSED** |
| backlog_item | 0 | No (E2-029) | No | **SPECIAL** |

### Categories

**1. Core Active (6 types)** - Well used, have commands:
- checkpoint, implementation_plan, architecture_decision_record, investigation, report

**2. Active but No Command (3 types)** - Used, no command:
- implementation_report (8 uses - reports in docs/reports/)
- readme (5 uses - various README.md files)
- backlog_item (special - backlog.md format, E2-029 planned)

**3. Deprecated per ADR-034 (2 types):**
- handoff - "Replaced by checkpoint + backlog + memory"
- handoff_investigation - "Rename to investigation"

**4. Low Use (3 types)** - 1 file each, no command:
- directive - 1 file (2025-12-07-01-TASK-documentation-sync.md)
- guide - 1 file (TRD-SYNTHESIS-EXPLORATION.md)
- proposal - 1 file (2025-12-04-PROPOSAL-extraction-type-improvement.md)

**5. Unused (2 types)** - 0 files, no command:
- verification - Never used
- meta_template - Never used

### Key Observations

1. **handoff_investigation template has deprecation notice** (line 13) but validator still lists it as valid type

2. **No /new-handoff command file exists** but validator recognizes `handoff` type

3. **backlog_item is orphaned** - Validator expects YAML frontmatter but backlog.md uses markdown format (no frontmatter)

4. **implementation_report vs report confusion** - Both exist, usage overlaps

---

## Recommendations

### Immediate Actions (Remove)

1. **Remove `verification`** from validator - 0 usage, never implemented
2. **Remove `meta_template`** from validator - 0 usage, never implemented

### Short-Term (Deprecate with Warning)

3. **Add deprecation warning** for `handoff` in validator (already deprecated per ADR-034)
4. **Add deprecation warning** for `handoff_investigation` in validator (already has notice in template file)

### Medium-Term (Review)

5. **Merge `implementation_report` into `report`** - Both serve verification phase, report is simpler
6. **Review `directive`** - Single usage, may be obsolete
7. **Review `guide`** - Single usage for TRD doc, may be overspecialized
8. **Review `proposal`** - Could be folded into `investigation` or `architecture_decision_record`

### No Change Needed

- `backlog_item` - Keep for E2-029, will get `/new-backlog-item` command
- `readme` - Valid for README.md files, doesn't need command

---

## Spawned Work Items

- [ ] E2-038: Remove unused template types (verification, meta_template)
- [ ] E2-039: Add validator deprecation warnings for handoff types
- [ ] E2-040: Consolidate implementation_report into report (optional)

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Recommendations (above)
- [x] Memory storage (concepts 71275-71283)

---

## References

- E2-008: Template Validation Schema Sync (Session 40)
- E2-029: /new-backlog-item Command (pending)
- ADR-034: Document Ontology and Work Lifecycle
- ValidateTemplate.ps1 lines 30-125

---
