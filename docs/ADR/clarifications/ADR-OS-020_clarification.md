# ADR Clarification Record: ADR-OS-020

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Default runtime.mode is STRICT; CLI `--mode` override respected only in non-CI environments.
- DEV_FAST artifacts carry `"dev_mode": true` flag in registry and filename suffix `_devfast`.
- Validators block mixing modes: STRICT plan cannot depend on devfast artifacts.
- Mode setting is logged at engine startup with g event and trace id for audit.
- CI job enforces STRICT via environment variable `HAIOS_FORCE_MODE=STRICT`.

## Dependencies & Risks
- **Mode Drift:** Developers may forget to switch back to STRICT before commit; pre-commit hook warns.
- **Artifact Pollution:** Devfast files may leak into repository; CI fails if detected.
- **Security Loophole:** Devfast skips some checks; misuse in shared env risky; enforcement via config.
- **Complex Config:** Future additional modes could complicate matrix; document contribution guidelines.
- **User Confusion:** Clear docs and CLI help required to explain behaviours.

## Summary
ADR-OS-020 defines two runtime modes—STRICT and DEV_FAST—enabling developers to trade safety for speed locally while preserving rigorous policy in CI and production through artifact labelling and validator enforcement.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | How does pre-commit hook detect leftover devfast artifacts before push? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | Will the engine refuse to run in DEV_FAST if budgets are undefined? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Can individual tasks request STRICT checks even in DEV_FAST plan (e.g., snapshot)? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | What visual indicator will cockpit UI display for mode (e.g., banner colour)? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | Is telemetry reduced in DEV_FAST to lower overhead, and how is that flagged in traces? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix H CI policy step `devfast_artifact_scan` enforces pollution guard.
- README update will include mode explanation and developer workflow examples.

## Traceability
- adr_source: ADR-OS-020
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 