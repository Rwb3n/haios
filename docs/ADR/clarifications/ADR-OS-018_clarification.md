# ADR Clarification Record: ADR-OS-018

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- State snapshots are written every 60s or on graceful shutdown signal.
- Snapshot files stored under `os_root/snapshots/` using naming `snapshot_<g>.tar.zst`.
- Recovery process validates checksums and embedded version before replaying state.
- Secrets vault (`vault/secrets.json.gpg`) initialized with age-encryption; only supervisor key decrypts.
- Kill-switch flags monitored each event loop; emergency stop sets state.st to `BLOCK_INPUT`.

## Dependencies & Risks
- **Snapshot Size:** Large workspaces may bloat snapshot archives; compression ratio tuning required.
- **Partial Snapshot:** Power loss mid-write could corrupt archive; write to temp then atomic rename.
- **Key Loss:** Losing supervisor private key renders vault unusable; offsite backup policy.
- **OPA Policy Drift:** Outbound whitelist may block legitimate new services until policy update.
- **Resource Limits:** Overly strict CPU/mem limits could kill long-running tasks; guideline for sizing.

## Summary
ADR-OS-018 mandates periodic execution state snapshots, a secrets vault, kill-switch controls, resource limits, and outbound network policies to ensure recoverability and single-node zero-trust security foundation.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What snapshot retention count or age policy prevents disk exhaustion? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are snapshot restores audited to prevent rollback attacks? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Can partial plan progress be resumed post-recovery without re-running completed tasks? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What is the procedure for rotating secrets without downtime? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How will kill-switch events propagate to distributed agents in Phase 2? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix B contains incident response playbook referencing kill-switch flags.
- Appendix H CI step `snapshot_integrity` verifies archive round-trip restore.

## Traceability
- adr_source: ADR-OS-018
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 