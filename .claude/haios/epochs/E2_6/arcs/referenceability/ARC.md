# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T12:50:00
# Arc: Referenceability

## Definition

**Arc ID:** referenceability
**Epoch:** E2.6
**Theme:** Portable schemas, structured configuration, clear interface contracts
**Status:** Complete

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
| CH-035 | SchemaLocationStrategy | WORK-067 (complete) | REQ-REFERENCE-001 | None |
| CH-036 | TemplateBootstrapPattern | WORK-067 findings + spawned impl | REQ-REFERENCE-002 | CH-035 |
| CH-037 | ManifestDriftPrevention | WORK-135 | REQ-PORTABLE-001 | None |

---

## Exit Criteria

- [x] Schema location strategy documented (WORK-067: `.claude/haios/schemas/` with core/ and project/ tiers)
- [x] Template reference pattern defined (WORK-067: `{{schema:domain.key}}` resolved at scaffold time)
- [x] Bootstrap pattern for new projects defined (WORK-067: copy core/, create project/, add schemas: to haios.yaml)
- [x] Core vs project-specific boundary clear (WORK-067: TRD enums = core ~10, HAIOS enums = project ~35)
- [x] Manifest drift detectable automatically (WORK-135 S381: manifest auto-sync mechanism, diff detection, roundtrip validation)

---

## References

- @docs/work/active/WORK-067/WORK.md
- @docs/work/active/WORK-135/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-REFERENCE-*)
