# ADR Clarification Record: ADR-OS-027

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Vector clock field `vc` added to all status events and delta logs.
- g counter provides total ordering within single node; between nodes vector clocks resolve causality.
- Clock skew tolerated up to 1 s for trace timestamps; NTP sync recommended.
- Merge strategy: when two divergent event logs detected, reconciliation task merges by vc dominance.
- Tooling `vc_merge.py` shipped in scripts/ for conflict resolution.

## Dependencies & Risks
- **Vector Size:** Many nodes enlarge vc; compression algorithm delta-encodes zeros.
- **Complex Reconciliation:** Manual intervention may be needed on three-way conflict.
- **Performance:** vc comparison adds cpu overhead; negligible for <50 nodes.
- **Skew:** Unsynced clocks affect human-readable time but not vc causality.
- **Data Loss:** Log truncation could lose vc history; periodic snapshot includes last vc.

## Summary
ADR-OS-027 mandates logical vector clocks attached to every state-changing event, supplementing the monotonic g counter to ensure causal ordering across distributed nodes.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What max node count is supported before vc becomes unwieldy? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are vc fields represented in JSON—array or map of node id to g? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Will reconciliation be automated or require human approval? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | How does vc integrate with OpenTelemetry span relationships? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | What testing ensures vc merge logic handles all edge cases? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix E provides algorithm pseudocode for vc compare & merge.

## Traceability
- adr_source: ADR-OS-027
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 