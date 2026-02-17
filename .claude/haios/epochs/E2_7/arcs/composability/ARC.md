# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16T19:00:00
# Arc: Composability

## Definition

**Arc ID:** composability
**Epoch:** E2.7
**Theme:** Compose, don't concatenate — flat metadata, template composability, recipe rationalization
**Status:** Active

---

## Purpose

Make building blocks composable. Arcs and chapters move to flat storage with metadata relationships. Plan templates fracture by work type. Lifecycles adapt to work type. The 71 recipes get grouped, aliased, and composed into a rational surface area.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-ASSET-001 | Each lifecycle produces typed, immutable asset |
| REQ-ASSET-003 | Assets can be piped to next lifecycle OR stored |
| REQ-ASSET-004 | Asset schema is lifecycle-specific |
| REQ-CONFIG-001 | All paths defined in haios.yaml, accessed via ConfigLoader |
| REQ-CONFIG-003 | Config follows single-source-of-truth principle |
| REQ-CONFIG-004 | Config is portable (relative paths, no machine-specific) |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-046 | FlatMetadataMigration | WORK-158 | REQ-CONFIG-001, REQ-CONFIG-003 | None | Planning |
| CH-047 | TemplateComposability | WORK-152, WORK-155 | REQ-ASSET-001, REQ-ASSET-004 | None | Complete |
| CH-048 | RecipeRationalization | New (TBD) | REQ-CONFIG-004 | CH-046 (flat metadata enables recipe simplification) | Planning |

---

## Exit Criteria

- [ ] Arcs and chapters stored flat with metadata relationships (not filesystem hierarchy)
- [x] Plan templates fractured by work type with type-specific sections (CH-047, WORK-152/155 closed S390)
- [x] Lifecycle adapts to work type (skip gates, computable predicates) (CH-047, WORK-155 closed S390)
- [ ] Recipe surface area rationalized (grouped, documented, composable)
- [ ] ConfigLoader used for all path resolution (zero hardcoded paths)

---

## Notes

- WORK-093 (Lifecycle Asset Types) already complete from E2.6 — typed I/O exit criterion partially satisfied
- CH-048 depends on CH-046: once metadata is flat, recipes can compose over metadata instead of paths
- 17 hardcoded paths identified for ConfigLoader migration (from E2.5 deferred arcs)

---

## References

- @docs/work/active/WORK-152/WORK.md (plan template fracturing)
- @docs/work/active/WORK-155/WORK.md (lifecycle type-awareness)
- @docs/work/active/WORK-093/WORK.md (lifecycle assets — complete)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-*, REQ-CONFIG-*)
