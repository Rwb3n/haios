# TRD — ADR-OS-003: EmbeddedAnnotationBlock Strategy

* **Status:** Draft
* **Owner(s):** Metadata & Tooling Team
* **Created:** g74
* **Source ADR:** ADR-OS-003
* **Clarification:** ADR-OS-003_clarification.md
* **Trace ID:** trace://trd-003/g74
* **Vector Clock:** vc://trd@74:2

---

## Executive Summary
Defines mandatory JSON metadata block `EmbeddedAnnotationBlock` embedded at the top of every text-editable artifact, enabling self-describing files and automated governance.

## Normative Requirements
| Req | Statement |
|-----|-----------|
| R1 | Every text-editable artifact **MUST** contain a valid `EmbeddedAnnotationBlock`. |
| R2 | Non-text artifacts **SHALL** provide sibling `.meta.json` annotation. |
| R3 | Annotation updates **MUST** include `trace_id`, `vector_clock`, `g_annotation_created`. |

## Architecture Overview
`Artifact` ↔ `AnnotationBlock` linkage stored in `global_registry_map.txt`; CI linters validate presence & schema.

## Implementation Guidelines
- Use comment syntax compatible with host language (`#`, `//`, `<!-- -->`).
- Protect block with optimistic-lock on `v_file_instance`.

## Test Strategy
- Linter unit tests: malformed / missing block.
- Concurrent write test with CRDT merge.

## SLIs
- `annotation_validation_errors_total` should be 0.

## Traceability
- adr_source: ADR-OS-003
- clarification_source: ADR-OS-003_clarification.md
- trace_id: trace://trd-003/g74
- vector_clock: vc://trd@74:2
- g_created: 74 