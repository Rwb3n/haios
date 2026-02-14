# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T12:50:00
# Arc: Referenceability

## Definition

**Arc ID:** referenceability
**Epoch:** E2.6
**Theme:** Portable schemas, structured configuration, clear interface contracts
**Status:** Planning

---

## Purpose

Every schema, template, and configuration must be referenceable from a single root. Currently schemas are scattered (3 definitions of `current_node` enum, no central registry), templates duplicate schema definitions, and new projects have no bootstrap path.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-REFERENCE-001 | Schema location strategy defined (central registry vs distributed) |
| REQ-REFERENCE-002 | Templates consume schemas via reference, not duplication |
| REQ-PORTABLE-001 | System health queryable, manifest in sync |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies |
|-------|-------|------------|--------------|--------------|
| CH-035 | SchemaLocationStrategy | WORK-067 (EXPLORE/HYPOTHESIZE) | REQ-REFERENCE-001 | None |
| CH-036 | TemplateBootstrapPattern | WORK-067 (VALIDATE/CONCLUDE) | REQ-REFERENCE-002 | CH-035 |
| CH-037 | ManifestDriftPrevention | WORK-135 | REQ-PORTABLE-001 | None |

---

## Exit Criteria

- [ ] Schema location strategy documented (where schemas live, how discovered)
- [ ] Template reference pattern defined (consume, not duplicate)
- [ ] Bootstrap pattern for new projects defined
- [ ] Core vs project-specific boundary clear
- [ ] Manifest drift detectable automatically

---

## References

- @docs/work/active/WORK-067/WORK.md
- @docs/work/active/WORK-135/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-REFERENCE-*)
