# ADR Clarification Record: ADR-OS-026

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Registry heartbeats every 15 s; missing 3 heartbeats → UNHEALTHY.
- /health endpoint returns JSON {status, version, g, uptime_seconds} with 200 OK.
- Status stream delivered via NATS subject `topology.status` (JetStream durable).
- Registry HA through raft–based leader election; at least 3 replicas in prod.
- Subscribers cache last status per service for 60 s fallback.

## Dependencies & Risks
- **Registry Outage:** Loss of quorum halts registration; fallback read-only mode using last snapshot.
- **Heartbeat Flood:** Thousands of agents may overload; adaptive backoff supported.
- **False Positives:** Short GC pauses might miss heartbeat; tolerate one skip before mark degraded.
- **Security:** Status stream messages signed to prevent spoofing.
- **Config Drift:** Different heartbeat intervals cause noisy health; central config enforced.

## Summary
ADR-OS-026 defines dynamic topology management through a HA agent registry, standardized /health checks, periodic heartbeats, and a push-based status stream, enabling rapid failure detection and adaptive scaling.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What JSON schema version governs /health response fields? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are registry replicas discovered and bootstrap elected? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Will degraded services still receive traffic or be shadowed? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | How is heartbeat interval negotiated during high load? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | What dashboard visualizes overall system topology and health? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix E includes Prometheus rules `haios_service_up` utilising /health scrape.
- Future: explore gossip-based SWIM protocol to replace central polling.

## Traceability
- adr_source: ADR-OS-026
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 