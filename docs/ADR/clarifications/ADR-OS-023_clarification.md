# ADR Clarification Record: ADR-OS-023

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- All mutable API endpoints require `Idempotency-Key` header; keys UUIDv7 with 24h TTL.
- Client libraries provide retry wrapper implementing exponential backoff (base 1s, factor 2, jitter 0-0.5).
- Circuit breaker trips after 5 consecutive failures or 30s rolling error rate >50%.
- Idempotency key store uses os_root/kv/idempotency_<g>.sqlite for Phase-1.
- GET/HEAD requests exempt but still include trace_id for linkage.

## Dependencies & Risks
- **Key Store Size:** High throughput may bloat SQLite; pruning job deletes keys past TTL.
- **Replay Attacks:** Attacker reuses key; include HMAC of user token in key or signed header.
- **Complex Integration:** External APIs lacking idempotency require adapter or compensation logic.
- **Configuration Drift:** Services may deviate from standard parameters; linter tests contract.
- **Latency:** Extra lookup adds ms latency; acceptable for reliability gains.

## Summary
ADR-OS-023 enforces universal idempotency using Idempotency-Key headers and standardized exponential-backoff retry with circuit breakers, ensuring safe operation and preventing duplicate side-effects across all OS communications.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | Should idempotency keys be namespaced per endpoint or global? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How will key storage migrate from SQLite to distributed store in Phase-2? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Can read-modify-write operations use same key for GET and subsequent POST? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What metrics monitor retry attempts and circuit breaker trips? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How are long-running saga steps made idempotent across partial failures? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix H CI test `idempotency_enforcement` checks mandatory header on integration tests.
- CostMeter records additional CPU cost for retries for budget tracking.

## Traceability
- adr_source: ADR-OS-023
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 