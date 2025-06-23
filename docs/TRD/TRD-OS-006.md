# TRD — ADR-OS-006: Schema-Based Scaffolding System

* **Status:** Draft
* **Owner(s):** Scaffolding & Templates Team
* **Created:** g74
* **Source ADR:** ADR-OS-006
* **Clarification:** ADR-OS-006_clarification.md
* **Trace ID:** trace://trd-006/g74
* **Vector Clock:** vc://trd@74:5

---

## Executive Summary
Defines JSON-schema "Scaffold Definition" files that drive creation of new components from `project_templates/`, embedding annotations automatically and ensuring repeatability.

## Normative Requirements
| Req | Statement |
|----|-----------|
| R1 | Each Scaffold Definition **MUST** validate against `scaffold_definition_schema.md`. |
| R2 | Scaffold execution **MUST** be idempotent. |
| R3 | Rollback mechanism **MUST** remove partial artifacts on failure. |

## Architecture Overview
Scaffold executor stages files in temp dir → validates → atomic commit → emits telemetry.

## Implementation Guidelines
- Use transactional FS lib with journal.
- Placeholder linter mandatory; compile test optional flag.

## Test Strategy
- Unit test placeholder rendering.
- Resume after mid-failure scenario.

## SLIs
- `scaffold_success_rate` ≥ 99%.

## Traceability
- adr_source: ADR-OS-006
- clarification_source: ADR-OS-006_clarification.md
- trace_id: trace://trd-006/g74
- vector_clock: vc://trd@74:5
- g_created: 74 