# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T16:51:41
# Arc: WorkUniversal

## Arc Definition

**Arc ID:** WorkUniversal
**Epoch:** E2.3 (The Pipeline)
**Name:** Universal Work Item Structure
**Status:** Active
**Pressure:** [volumous] - thematic exploration

---

## Theme

Define and implement the universal work item structure for pipeline portability.

**The Problem:**
- Current IDs encode type (E2-XXX, INV-XXX)
- Fields are HAIOS-specific (milestone, spawned_by_investigation)
- Not portable to other projects

**The Goal:**
- Sequential IDs (WORK-001)
- Type as field
- Pipeline traceability fields (requirement_refs, source_files, artifacts)
- Extensible via extensions block

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | SchemaDesign | Active | Define universal schema (TRD exists, needs approval) |
| CH-002 | TemplateUpdate | Planned | Update work_item.md template |
| CH-003 | WorkEngineAdapt | Planned | Handle new fields in WorkEngine |
| CH-004 | ScaffoldUpdate | Planned | New ID generation (WORK-XXX) |
| CH-005 | ValidationRules | Planned | Validate new required fields |

---

## Current State

- TRD-WORK-ITEM-UNIVERSAL.md drafted (Session 206)
- WORK-001 created (first universal work item)
- **Design NOT approved** - gaps identified:
  - No grounded rationale for key decisions
  - Designed before pipeline stages exist
  - acceptance_criteria duplication (frontmatter vs body)

---

## Open Questions

| Question | Options | Decision |
|----------|---------|----------|
| WHY sequential IDs? | UUID, semantic, sequential | Pending rationale |
| WHY this type taxonomy? | 5 types, more, fewer | Pending rationale |
| Source of truth for acceptance_criteria? | Frontmatter, body, both | Pending resolution |

---

## Exit Criteria

- [ ] Schema design approved with rationale
- [ ] Template updated
- [ ] WorkEngine handles new fields
- [ ] First work items using universal structure

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (draft)
- @docs/work/active/WORK-001/WORK.md (first instance)
- @.claude/haios/epochs/E2_3/observations/SESSION-206.md (OBS-206-003)
