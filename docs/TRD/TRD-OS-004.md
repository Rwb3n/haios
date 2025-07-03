# TRD — ADR-OS-004: Global Event & Version Counters

* **Status:** Draft
* **Owner(s):** Concurrency & State Team
* **Created:** g74
* **Source ADR:** ADR-OS-004
* **Clarification:** ADR-OS-004_clarification.md
* **Trace ID:** trace://trd-004/g74
* **Vector Clock:** vc://trd@74:3

---

## Executive Summary
Specifies dual-counter strategy: monotonic global event counter `g` (ordering/audit) and per-file version counter `v` (optimistic lock).

## Normative Requirements
| Req | Statement |
|-----|-----------|
| R1 | Every state-changing write **MUST** increment `g` exactly once. |
| R2 | Any file mutation **MUST** include `v` compare-and-swap. |
| R3 | Reconciliation job **MUST** repair gaps or duplicates in `g`. |

## Architecture Overview
```mermaid
sequenceDiagram
    participant Agent
    participant State
    Agent->>State: read g,v
    Agent->>State: write if v matches; g++
```

## Implementation Guidelines
- Raft leader performs atomic `g` increment; replicas read-only.
- Use `atomic_write` wrapper with `v` check.

## Test Strategy
- Stress test 10k ops/s; assert monotonic g.
- Partition test: minority replicas read-only.

## SLIs
- `counter_gap_detected_total` == 0.

## Traceability
- adr_source: ADR-OS-004
- clarification_source: ADR-OS-004_clarification.md
- trace_id: trace://trd-004/g74
- vector_clock: vc://trd@74:3
- g_created: 74 