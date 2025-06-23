# ADR Clarification Record: ADR-OS-025

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Internal requests authenticated via short-lived PASETO tokens (TTL 5 min) issued by an in-process AuthService.
- Mutual TLS certificates issued by local CA rotated every 24 h by Supervisor automation.
- Service ACLs defined in `os_root/security/policies/rbac.yaml` and enforced by side-car middleware.
- Bootstrap secrets delivered via age-encrypted file unlocked by operator during install.
- Token validation cache (LRU, 1 k entries) keeps latency <2 ms per call.

## Dependencies & Risks
- **PKI Complexity:** Certificate issuance failures may block service start; fallback self-signed dev mode.
- **Token Replay:** Clock skew could allow reuse; include nonce + store last 100 nonces per service.
- **Performance:** mTLS handshake adds latency; enable HTTP/2 keep-alive.
- **Secret Leakage:** Misconfigured logging may print tokens; log filter middleware strips Authorization headers.
- **Revocation:** Compromised tokens require immediate invalidation; implement in-memory deny list broadcast via NATS.

## Summary
ADR-OS-025 enforces zero-trust by requiring PASETO tokens, mutual TLS, and least-privilege RBAC for all internal calls, eliminating implicit trust and shrinking blast radius.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | Which PASETO version (v2 local/public) will be standard? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are token signing keys rotated and distributed securely? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Will service meshes (e.g., Linkerd) replace custom mTLS in Phase-2? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | How does RBAC policy file get validated and loaded at runtime? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | What monitoring alerts fire on repeated auth failures indicating attack? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix H security policy references zero-trust enforcement scripts.
- Future: integrate SPIFFE/SPIRE for automated workload identity.

## Traceability
- adr_source: ADR-OS-025
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 