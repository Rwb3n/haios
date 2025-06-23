# ADR Clarification Record: ADR-OS-024

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Primary message bus for Phase-1: NATS JetStream running locally via Docker compose.
- Event schema uses CloudEvents v1.0 with mandatory fields: id, source, type, specversion, time, trace_id.
- Saga coordinator agent persists state in `os_root/sagas/` with idempotent updates.
- Dead-letter queue retention 7 days; monitored by alert.
- Consumers must ack within 30s or message redelivered with exponential delay.

## Dependencies & Risks
- **Bus Downtime:** Single-node NATS may fail; dev environment acceptable, prod requires cluster.
- **Schema Evolution:** Event version bumps may break consumers; adopt versioned type names.
- **Message Loss:** JetStream persistence mitigates; still need periodic snapshot.
- **Debug Complexity:** Asynchronicity complicates trace; OpenTelemetry baggage carries trace_id.
- **Out-of-Order:** Consumers design for idempotent handling; event numbering optional.

## Summary
ADR-OS-024 establishes standard asynchronous communication patterns using NATS JetStream, CloudEvents schemas, and saga coordination to achieve eventual consistency and decoupled workflows across HAiOS agents.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What naming convention prefixes event `type` field to indicate domain? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How will multi-tenant message bus namespaces be organized in future phases? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Should saga state be stored in exec_status files or separate store? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What tooling visualizes saga progress for supervisors? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How are compensating actions audited and linked to original events? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix G Frameworks Registry will include event naming standard reference.
- Future: evaluate Kafka for Phase-2 distributed deployment.

## Traceability
- adr_source: ADR-OS-024
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 