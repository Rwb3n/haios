# TRD — ADR-OS-008: Narrative Markdown Reports

* **Status:** Draft
* **Owner(s):** Reporting & Observability Team
* **Created:** g74
* **Source ADR:** ADR-OS-008
* **Clarification:** ADR-OS-008_clarification.md
* **Trace ID:** trace://trd-008/g74
* **Vector Clock:** vc://trd@74:7

---

## Executive Summary
Mandates automated generation of human-readable Markdown reports (Analysis, Validation, Progress Review) with traceability identifiers.

## Normative Requirements
| Req | Statement |
|----|-----------|
| R1 | Reports **MUST** embed `trace_id`, `g` snapshot, `vector_clock`. |
| R2 | Default cadence for Progress Review reports **SHOULD** be weekly unless overridden. |
| R3 | Report templates **MUST** be versioned; migration scripts required on major change. |

## Architecture Overview
Report generator pulls data → renders Markdown via Jinja → commits under `docs/CHANGELOG/reports/` → registers in registry.

## Implementation Guidelines
- Use template files under `docs/templates/report_*`.
- Archive old reports to cold storage after policy window.

## Test Strategy
- Lint generated Markdown; link checker.
- Diff regression test on template change.

## SLIs
- `report_generation_failures_total` == 0.

## Traceability
- adr_source: ADR-OS-008
- clarification_source: ADR-OS-008_clarification.md
- trace_id: trace://trd-008/g74
- vector_clock: vc://trd@74:7
- g_created: 74 