# ADR Clarification Record: ADR-OS-022

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Inventory arrays embedded in annotation blocks must not exceed 1 000 items; GC trims older EXPIRED entries.
- Delta logs are append-only; size capped at 2 MB before rotation to `inventory_delta_<g>_arch1.log`.
- Janitor cleanup cadence default 100 global events, configurable via `haios.config.json.inventory.gc_interval_g`.
- Reservation TTL default 30 minutes if `ttl_seconds` absent.
- Builder agents have read-only access; any write attempt raises `PERMISSION_DENIED` Issue.

## Dependencies & Risks
- **Zombie Reservations:** Agents crash after RESERVE; janitor must roll back; monitor orphan rate.
- **Merge Conflicts:** Manual edits to annotation may conflict with delta replay; automated patcher preferred.
- **Bloat:** Large code snippets inflate annotation; guideline recommends storing pointer to file instead.
- **Concurrency:** Simultaneous RESERVE events could race; optimistic g ordering resolves but edge cases logged.
- **Schema Evolution:** Adding new lifecycle states requires migrator script and CI schema bump.

## Summary
ADR-OS-022 introduces a two-tier Mechanical Inventory Buffer stored in annotation blocks with append-only delta logs, enabling agents to reuse resources, prevent redundant work, and maintain auditability.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What tooling visualizes current inventory and reservation status for supervisors? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are large binary artifacts referenced—stored externally with hash pointer or base64 in inventory? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Can inventory items be shared across initiatives, and how is namespace collision avoided? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What audit metrics track inventory churn and janitor rollbacks? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How does delta log replay handle out-of-order events after partition healing? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix D schema updates include inventory v2.1 fields.
- Future: integrate UI to manually expire or promote inventory items.

## Traceability
- adr_source: ADR-OS-022
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 