# ADR Clarification Record: ADR-OS-028

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- state.partition_status field enumerates CONSISTENT | PARTITIONED | RECONCILING.
- Minority partition enters read-only mode; mutating operations raise PARTITION_ERROR.
- Healing detected via successful gossip ping 3x; RECONCILING tasks merge vc and g counters.
- Snapshot taken pre-reconcile to enable rollback if merge fails.
- Partition detection uses heartbeat absence >45 s.

## Dependencies & Risks
- **Split Brain:** Concurrent writes in partitions risk divergence; read-only enforcement critical.
- **Delayed Detection:** Long heartbeat interval delays partition awareness; tune per deployment.
- **Merge Conflicts:** Irreconcilable changes may require manual resolution; create ISSUE partition_conflict.
- **Performance:** Gossip pings add network chatter; batch round trips.
- **Testing:** Simulating partitions in CI requires network emulation.

## Summary
ADR-OS-028 defines partition tolerance strategy: detect network partitions via heartbeat, switch minority partitions to read-only, and reconcile state using vector clocks and snapshots upon healing to maintain consistency.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What automated tests verify read-only enforcement during partition? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How is g counter advanced in minority partition without writes? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | What UI signal alerts operators to PARTITIONED state? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | Can tasks be explicitly marked partition-tolerant to continue? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How long will RECONCILING mode last before forced human intervention? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix B incident response includes partition healing runbook.

## Traceability
- adr_source: ADR-OS-028
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 