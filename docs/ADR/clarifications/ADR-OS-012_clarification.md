# ADR Clarification Record: ADR-OS-012

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Agent registry index (`agent_registry.txt`) is loaded into memory cache at startup with TTL 60s.
- New agent cards must pass schema validation (`agent_card_schema.md`) before being referenced in registry.
- Only Supervisor agent can mutate registry; all changes signed and include `g` event ID.
- Registry modifications are atomic: write temp file then move.
- Max agents supported in CP mode: 500; beyond triggers sharded registries roadmap.

## Dependencies & Risks
- **Single Index Hotspot:** Frequent reads may cause contention; caching mitigates but eventual consistency lag risk.
- **Corruption:** Partial write could orphan card; recovery script scans and repairs inconsistencies.
- **Privilege Escalation:** Compromised Supervisor could alter agents; multifactor approval or commit-signing required.
- **Card Bloat:** Overly verbose agent history sections may slow parsing; consider log rotation field.
- **Partition Scenario:** Minority partitions operate with stale registry; tasks requiring missing persona are BLOCKED.

## Summary
ADR-OS-012 designs a dynamic "Index + Individual File" agent management system: a central registry lists all persona IDs and paths, while detailed Agent Cards capture configuration, capabilities, and status. This allows runtime addition, update, or retirement of specialized agents without OS restart.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What hashing or checksum verifies Agent Card integrity on load? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are long-lived agent state (e.g., fine-tuned weights) referenced or stored relative to card? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Can the registry support soft-deleting agents for historical audit while preventing assignment? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What is the policy for rolling back a faulty agent card deployment? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How will sharding strategy evolve when agent count exceeds single index capacity? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix G Frameworks Registry ties into persona capability tags.
- Cockpit UI roadmap includes live agent health dashboard fed by registry events.
- Future enhancement: event-stream subscription model replacing polling for registry updates.

## Traceability
- adr_source: ADR-OS-012
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 