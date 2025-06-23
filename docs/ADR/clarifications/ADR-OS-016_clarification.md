# ADR Clarification Record: ADR-OS-016

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- `exec_status_<g>.txt` writes are append-only events to minimize merge conflicts.
- A background StatusWriter agent batches updates every 2 seconds or 10 events, whichever first.
- Status file schema (`exec_status_schema.md`) includes vector_clock and trace_id per event.
- Maximum status file size before rotation: 5 MB; older events archived to `exec_status_<g>_archive_*.txt`.
- state.txt `current_exec_status_id_ref` is updated atomically with plan switch.

## Dependencies & Risks
- **Write Contention:** High-frequency updates could still collide; batching + append-only mitigates.
- **Desync:** If state.txt points to wrong status file, dashboards misreport; health monitor validates linkage hourly.
- **Corruption:** Partial writes risk JSON breakage; writer uses temp + fsync and validation pass.
- **Scalability:** Many parallel plans may spawn numerous status files; indexing service required in future.
- **Observability Overhead:** Excessive event detail inflates status size; configurable verbosity levels.

## Summary
ADR-OS-016 separates mutable execution telemetry from immutable plans via dedicated `exec_status_<g>.txt` files written in an append-only event stream, referenced from state.txt, allowing real-time progress tracking while preserving plan immutability.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What JSON event schema fields are mandatory for every status entry? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How will multi-agent concurrent updates coordinate append offsets safely on network file systems? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Will there be a gRPC or WebSocket stream to subscribe to status updates instead of file polling? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What archival strategy compresses rotated status files to save space? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How are status events reconciled after partition healing to ensure correct ordering? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix E Observability reports will summarize data pulled from status files.
- Potential enhancement: migrate status storage to an event log (e.g., Loki) with file gateway for backward compatibility.

## Traceability
- adr_source: ADR-OS-016
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 