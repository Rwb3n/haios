# ADR-OS-001 Clarification — Human Override of Automatic Rollback
**Subject:** Human override of automatic rollback triggered by validation failure.
**Status:** ✅ Accepted
**Decision Date:** 2025-06-28
**Participants:** Architect-1, Architect-2

---

## 1  |  Clarifying Question

Can a human override the automatic rollback triggered by a validation failure?

## 2  |  Consensus Answer

Yes, a human with `SUPERVISOR` role privileges can override an automatic rollback by submitting a formal, audited "Validation-Override Request." This request is processed as a standard event within the system's state machine, ensuring that the override itself is a traceable, governed action rather than an uncontrolled manual intervention. The process includes automated risk checks and requires explicit approval, maintaining system integrity and auditability.

### 2.1 Core Mechanics

*   **Request Initiation:**
    *   An override is initiated by creating a `REQUEST` artifact of subtype `override_validation_failure` via a CLI or UI.
    *   The request must be created by an agent with the `SUPERVISOR` role, and the request payload must be signed with the agent's X.509 certificate.
    *   The request includes a `risk_checklist.json` that codifies the override's risk profile.
*   **Automated Governance:**
    *   A `Gatekeeper` agent automatically validates the request against several criteria:
        *   The creator's role must be `SUPERVISOR`.
        *   The signature must match the agent's registered certificate.
        *   The `risk_checklist.json` must not violate any predefined high-risk policies (e.g., overriding a security test failure).
    *   Requests that fail validation are automatically rejected.
*   **State Machine Integration:**
    *   Upon submission, a `Supervisor` agent sets an `override.pending` flag in the system's state, using an optimistic lock to prevent race conditions with the rollback process.
    *   If the `Gatekeeper` approves the request, the state machine transitions to the desired phase, skipping the rollback. Synthetic phase-complete events are generated for any skipped phases to maintain a contiguous event log.
    *   If the request is rejected, the `override.pending` flag is cleared, and the automatic rollback proceeds.
*   **Auditability and Traceability:**
    *   The entire override process, from request to approval/rejection, is captured in the system's immutable audit trail.
    *   The original `Validation Report` is annotated with a reference to the override request.
    *   A `REMEDIATION-plan` stub is automatically scheduled to ensure the root cause of the validation failure is addressed.

## 3  |  Rationale

This approach provides a necessary escape hatch for exceptional circumstances while preventing uncontrolled manual changes. By integrating the override mechanism into the native state machine and subjecting it to the same governance and auditability as any other system event, it upholds the core principles of determinism, traceability, and defense-in-depth. The automated risk checklist ensures that low-risk overrides are expedited while high-risk changes are systematically prevented.

## 4  |  Implications

*   **Schema:** Requires extensions to the `REQUEST` artifact schema and the system's state schema.
*   **Services:** Requires a `Gatekeeper` agent and a `Supervisor` agent with the necessary permissions.
*   **Tooling:** Requires CLI and/or UI support for creating and signing override requests.

## 5  |  Alternatives Considered

*   **No override:** This was rejected as it would not be practical in all situations.
*   **Uncontrolled override:** Allowing any user to manually edit the state file was rejected as it would violate the principles of traceability and auditability.

## 6  |  Decision

The proposed mechanism for a formal, audited "Validation-Override Request" is accepted.

## 7  |  Changelog

| Date       | Description                                                   | Author      |
| ---------- | ------------------------------------------------------------- | ----------- |
| 2025-06-28 | Initial proposal.                                             | Architect-1 |
| 2025-06-28 | Refinements to address authorization, race conditions, etc.   | Architect-2 |
| 2025-06-28 | Final acceptance.                                             | Architect-2 |