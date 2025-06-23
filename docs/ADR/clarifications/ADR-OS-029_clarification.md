# ADR Clarification Record: ADR-OS-029

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Every function boundary propagates trace_id via OpenTelemetry context vars.
- Root span name pattern: `haios.<phase>.<plan_id>`.
- Traces exported to OTLP endpoint `http://localhost:4318` in dev; configurable.
- Sampling rate 100% in STRICT, 10% in DEV_FAST unless error spans.
- Logs include trace_id in structured JSON field for correlation.

## Dependencies & Risks
- **High Volume:** 100% sampling may overwhelm collector; adaptive sampling roadmap.
- **Missing Context:** Legacy code paths may drop context; tracer lint scans import graph.
- **Sensitive Data:** PII must be scrubbed from span attributes; allowlist enforced.
- **Exporter Failure:** If OTLP unavailable, spans buffered to disk up to 100 MB.
- **Overhead:** Tracing adds ~5 µs per span; acceptable.

## Summary
ADR-OS-029 mandates universal trace propagation through OpenTelemetry, ensuring every event, metric, and log carries a trace_id for end-to-end observability and debugging.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | Will span batching be enabled to reduce network overhead? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are trace IDs persisted in snapshots to resume correlation after restart? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | What tools visualize traces for non-HTTP internal events? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | How are sensitive attributes redacted before export? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | What SLA defines acceptable trace export lag? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix H observability defines alert when trace error ratio >3%.

## Traceability
- adr_source: ADR-OS-029
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 