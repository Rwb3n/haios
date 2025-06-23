# ADR-OS-023: Universal Idempotency and Retry Policy

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

The current architecture has some provisions for retries (ADR-OS-011) but lacks a universal, enforceable policy for idempotency and robust retry mechanisms like exponential backoff and circuit breakers. This gap can lead to "retry storms," redundant processing, and inconsistent state when operations are repeated due to transient network failures. This ADR mandates a cross-cutting policy to ensure all external and internal API calls are safe to retry.

## Assumptions

* [ ] Standard libraries for implementing exponential backoff and circuit breakers are available and can be integrated into the core engine.
* [ ] The overhead of managing idempotency keys and state is acceptable for the increased reliability.
* [ ] All stateful services can provide a mechanism to detect and reject replayed requests.
* [ ] The idempotency and retry policy is robust against key collisions, replay attacks, and partial failures.
* [ ] The system can detect and recover from retry/circuit breaker misconfiguration or state corruption.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision

**Decision:**

> We will mandate universal idempotency for all external and internal API calls and enforce a standardized retry policy.
> 1.  **Idempotency:** All mutable API endpoints MUST require an `Idempotency-Key`. The service is responsible for storing the result of the first successful call for that key and returning the cached response for any subsequent retries.
> 2.  **Retry Policy:** All clients (agents, services) initiating network calls MUST wrap them in a retry mechanism that implements exponential backoff with jitter and a circuit breaker pattern.
> 3.  **Standard:** This policy applies to both OS-level internal communications and any external service interactions managed by an agent.

**Confidence:** High

## Rationale

1. **Preventing Duplicate Mutations**
   * Self-critique: Enforcing idempotency adds complexity to both the client (must generate and send keys) and the server (must store and check keys). For some purely read-only operations, this is unnecessary overhead.
   * Confidence: High
2. **Avoiding Retry Storms**
   * Self-critique: A poorly configured circuit breaker (e.g., threshold too low) could trip too easily, reducing availability. Configuration must be carefully managed.
   * Confidence: High
3. **System-wide Consistency**
   * Self-critique: Mandating this everywhere could be overly rigid. There might be rare cases where a different, specialized retry policy is needed. The framework should allow for controlled exceptions.
   * Confidence: Medium

## Alternatives Considered

1. **Ad-hoc Implementation**: Allow each agent/service to implement its own retry logic.
   * Brief reason for rejection: Leads to inconsistent behavior, is difficult to audit, and almost guarantees that some components will have naive or dangerous retry logic.
   * Confidence: High
2. **No Retries**: Simply let operations fail and escalate immediately.
   * Brief reason for rejection: Not resilient to transient failures, which are common in distributed systems. This would lead to poor availability and unnecessary escalations.
   * Confidence: High

## Consequences

* **Positive:** Drastically improves the system's resilience to transient network failures. Prevents data corruption and inconsistent state from duplicated operations. Creates predictable, system-wide behavior for error handling.
* **Negative:** Increases the implementation complexity for all network-facing components. Requires a shared library or standard for generating idempotency keys and managing retry state.

## Clarifying Questions

* What is the standard format and TTL for an idempotency key?
* How are the default parameters for exponential backoff and circuit breakers configured and potentially overridden?
* How do we handle idempotent retries for long-running, multi-step operations (sagas)?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
