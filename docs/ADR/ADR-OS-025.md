# ADR-OS-025: Zero-Trust Internal Security Baseline

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

While ADR-OS-018 establishes a strong security baseline for the OS runtime, it does not explicitly mandate a "zero-trust" posture for internal communications. Agents and services may implicitly trust calls from within the same network, creating a potential vulnerability if one component is compromised. This ADR formalizes a zero-trust model, requiring that no communication is trusted by default, regardless of its origin.

## Assumptions

* [ ] A lightweight, fast, and secure mechanism for issuing and validating internal access tokens (e.g., JWT, PASETO) is available.
* [ ] The performance overhead of authenticating and authorizing every internal API call is acceptable.
* [ ] Mutual TLS (mTLS) can be practically implemented across all internal services to encrypt traffic and verify service identity.
* [ ] The zero-trust security model is robust against token forgery, replay attacks, and certificate compromise.
* [ ] The system can detect and recover from token/certificate misconfiguration or authority compromise.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-018, ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision

**Decision:**

> We will enforce a zero-trust security model for all internal, agent-to-agent, and service-to-service communication.
> 1.  **Authentication:** Every internal API request MUST present a valid, short-lived authentication token. Services MUST validate this token before processing any request.
> 2.  **Authorization:** Services MUST enforce least-privilege access, authorizing the validated token holder to perform only the requested action on the specific resource.
> 3.  **Encryption:** All internal network traffic MUST be encrypted using mutual TLS (mTLS), ensuring both client and server can verify each other's identity.

**Confidence:** High

## Rationale

1. **Defense in Depth**
   * Self-critique: A compromised token-issuing authority would be a critical failure point, allowing widespread unauthorized access. This component must be exceptionally secure.
   * Confidence: High
2. **Contains Blast Radius**
   * Self-critique: The complexity of managing certificates for mTLS and rotating tokens can be high. This requires significant automation and robust PKI infrastructure.
   * Confidence: Medium
3. **Explicit Trust Boundaries**
   * Self-critique: Moving from implicit trust to explicit zero-trust requires a significant engineering investment and a cultural shift for developers.
   * Confidence: High

## Alternatives Considered

1. **Network Perimeter Security**: Relying on firewalls and network segmentation to secure the internal network.
   * Brief reason for rejection: This is a classic "castle-and-moat" model. Once an attacker is inside the perimeter, they can move laterally with little resistance. It is not sufficient for a modern, dynamic system.
   * Confidence: High
2. **API Keys**: Using static, long-lived API keys for service-to-service authentication.
   * Brief reason for rejection: Long-lived credentials are a significant security risk. They are more likely to be leaked and are not easily revocable in case of a breach.
   * Confidence: High

## Consequences

* **Positive:** Drastically improves the security posture by eliminating implicit trust. Limits the "blast radius" of a compromised component. Provides a clear, auditable trail of all internal actions.
* **Negative:** Introduces performance overhead for token validation and mTLS handshakes on every call. Increases the complexity of the CI/CD pipeline, which must manage secrets and certificate distribution.

## Clarifying Questions

* What token format (e.g., JWT) and which claims are mandatory for internal authentication?
* What is the chosen solution for Certificate Authority and automated certificate rotation for mTLS?
* How are initial "bootstrap" credentials securely delivered to a new agent or service?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
