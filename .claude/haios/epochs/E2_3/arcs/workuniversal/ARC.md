# generated: 2026-01-18
# System Auto: last updated on: 2026-01-21T18:28:40
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
| CH-001 | SchemaDesign | **Complete** | TRD approved (Session 218) |
| CH-002 | TemplateUpdate | **Complete** | Template matches TRD (verified Session 218) |
| CH-003 | WorkEngineAdapt | **Complete** | WorkEngine has backward compat, `type` falls back to `category` |
| CH-004 | ScaffoldUpdate | **Complete** | `get_next_work_id()` generates WORK-XXX |
| CH-005 | ValidationRules | Deferred | Basic validation exists; advanced rules post-migration |

---

## Current State

- TRD-WORK-ITEM-UNIVERSAL.md **APPROVED** (Session 218)
- WORK-001 through WORK-004 created (universal format)
- WorkEngine already implements backward compat (type falls back to category)

---

## Resolved Questions (Session 218)

| Question | Decision | Rationale |
|----------|----------|-----------|
| WHY sequential IDs? | Sequential (WORK-XXX) | Type as field, not prefix. Human-readable. Epoch-agnostic. |
| WHY this type taxonomy? | 5 types (feature, investigation, bug, chore, spike) | Already in WorkEngine. Backward compat with category. |
| acceptance_criteria duplication? | Both serve different purposes | Frontmatter for validation tools, body for agent checkboxes. |

Memory refs: 82144, 81612

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
