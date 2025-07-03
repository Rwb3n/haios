# TRD — ADR-OS-005: Configuration-Driven Directory Structure

* **Status:** Draft
* **Owner(s):** Platform Configuration Team
* **Created:** g74
* **Source ADR:** ADR-OS-005
* **Clarification:** ADR-OS-005_clarification.md
* **Trace ID:** trace://trd-005/g74
* **Vector Clock:** vc://trd@74:4

---

## Executive Summary
Centralises all operational paths in `haios.config.json` to ensure portability and clear separation between OS internals and project artifacts.

## Normative Requirements
| Req | Statement |
|-----|-----------|
| R1 | `haios.config.json` **MUST** include `config_schema_version` and `$schema` URL. |
| R2 | Unknown keys **MUST** raise error unless `allowUnknownKeys=true`. |
| R3 | CLI `haios init --scaffold` **SHALL** support `--dry-run` and `--force`. |

## Architecture Overview
CLI loader parses config, validates against JSON Schema; runtime helpers normalize paths and enforce repo-root containment.

## Implementation Guidelines
- Validate with `jsonschema` at startup.
- Block symlink traversal in control directories.

## Test Strategy
- Unit tests: invalid key, path escape, schema mismatch.
- E2E: scaffold regeneration dry-run.

## SLIs
- `config_load_failures_total` == 0.

## Traceability
- adr_source: ADR-OS-005
- clarification_source: ADR-OS-005_clarification.md
- trace_id: trace://trd-005/g74
- vector_clock: vc://trd@74:4
- g_created: 74 