# ADR-OS-001 Clarification — Human Override of Phase Transitions
**Subject:** Human override of phase transitions in the five-phase loop.
**Status:** ✅ Accepted
**Decision Date:** 2025-06-28
**Participants:** Architect-1, Architect-2, Governance Chair

---

## 1  |  Clarifying Question

How can an authorised human operator deterministically skip forward, rewind, or pause/abort a phase in the five-phase HAiOS loop while maintaining governance, auditability, and safety guarantees?

## 2  |  Consensus Answer

The platform will use a “Signed Override Request” (SOR) protocol. This protocol defines a formal, auditable process for human intervention in the state machine.

### 2.1 Core Mechanics

| Step | Artefact (location `control/`)                           | Human Role(s)                          | Enforced By                                    |
|------|---------------------------------------------------------|----------------------------------------|------------------------------------------------|
| **1 Initiate** | `override_request_<g>.txt` | Supervisor (or delegate) via CLI / Cockpit (WebAuthn + OTP) | —
| **2 Validate** | automatic `override_approved_<g>.flag` (or `override_failed_<g>.txt`) | — | **Override-Validator** side-car<br>– verifies dual signatures, HLC freshness, quotas, locked-file policies, gate taxonomy & compensation bundle |
| **3 Commit** | atomic swap of `state.txt.ph` (Raft-majority) | — | **Engine** |
| **4 Announce** | `override_<g>.event`, Slack/Email | — | **Notifier** |
| **5 Audit Close** | append JSON to `audit.log` | — | **Auditor Agent** |

### 2.2 Key Safeguards

*   **Time & Freshness:** Hybrid-Logical Clock (HLC) to prevent replay attacks and handle network partitions.
*   **Gate-Aware Overrides:** A hard gate taxonomy (`WAIVABLE` vs. `NON_WAIVABLE`) to prevent bypassing critical checks.
*   **Transactional Rewind Compensation:** An all-or-nothing compensation mechanism to ensure that rewinds leave the system in a consistent state.
*   **Quorum & Quorum-Change Safety:** Dual-signature requirement for quorum changes to prevent malicious overrides.
*   **Rate Limiting & Flood Protection:** Cluster-wide and per-node rate limiting to prevent denial-of-service attacks.

## 3  |  Rationale

This protocol provides a deterministic and auditable mechanism for human intervention, which is a requirement of ADR-OS-001. It maintains the integrity of the system by ensuring that all overrides are subject to the same governance and safety checks as automated transitions.

## 4  |  Implications

*   **Schema:** Requires new schemas for SORs, compensation plans, and various policy files.
*   **Services:** Requires a new `Override-Validator` service and a `Blueprint Promotion Service`.
*   **Tooling:** Requires CLI and UI support for creating, signing, and managing SORs.

## 5  |  Alternatives Considered

*   **Direct CLI flag to mutate state:** Rejected as it would be unauditable and bypass governance.
*   **Database-backed override queue:** Rejected as it would contradict the file-centric design of the system.

## 6  |  Decision

The Signed Override Request (SOR) protocol is accepted as the authoritative mechanism for human intervention in the five-phase loop.

## 7  |  Changelog

| Date (UTC) | Version | Significant Changes                                                                            |
| ---------- | ------- | ---------------------------------------------------------------------------------------------- |
| 2025-06-28 | v1.0    | Initial SOR design.                                                                            |
| 2025-06-28 | v1.1    | Added HLC, gate-aware overrides, compensation bundle.                                          |
| 2025-06-28 | v1.2    | Dual-sign quorum change, NON_WAIVABLE taxonomy, mandatory compensation.                        |
| 2025-06-28 | v1.3    | Locked taxonomy, transactional saga, cluster rate-limit, policy revocation.                    |