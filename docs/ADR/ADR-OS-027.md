# ADR-OS-027: Global and Vector Clock Event Ordering

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

The OS currently uses a global event counter (`g`) to provide a total ordering of events. While simple, this centralized counter can become a bottleneck and does not adequately capture the causal relationships between events in a distributed system (e.g., event B was caused by event A, even if they occurred on different agents). This ADR specifies when to use the global counter versus more sophisticated logical clocks to preserve causality.

## Assumptions

* [ ] The overhead of maintaining and transmitting vector clocks is acceptable for the operations that require strict causal ordering.
* [ ] Developers and agents can correctly identify workflows where simple ordering is insufficient and causal history is required.
* [ ] A standard library for implementing Lamport timestamps and vector clocks is available.
* [ ] The event ordering policy is robust against clock drift, agent restarts, and vector clock overflows.
* [ ] The system can detect and recover from event ordering/counter misconfiguration or corruption.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision

**Decision:**

> We will augment the existing global counter with a formal policy for using logical clocks where causality is critical.
> 1.  **Global Counter (`g`):** The default mechanism for timestamping and ordering events where a simple, total order is sufficient. It remains the standard for artifact versioning and logging.
> 2.  **Lamport Timestamps:** For distributed workflows that require a total ordering of events without a central coordinator (e.g., distributed transactions), Lamport timestamps MUST be used.
> 3.  **Vector Clocks:** For workflows where it is essential to know if an event A "happened before" event B (causality), vector clocks MUST be attached to all relevant events and messages. This is critical for debugging and for systems that need to reconcile concurrent, independent state changes.

**Confidence:** Medium

## Rationale

1. **Preserving Causality**
   * Self-critique: Vector clocks can grow large in systems with many agents, adding significant overhead to every message. Their use should be limited to where they are strictly necessary.
   * Confidence: High
2. **Enabling Correct State Reconciliation**
   * Self-critique: Reasoning about vector clocks is notoriously difficult for humans. This increases the cognitive load on developers and makes debugging more complex if not supported by good tooling.
   * Confidence: High
3. **Choosing the Right Tool for the Job**
   * Self-critique: The policy requires agents/developers to make a nuanced choice between three different clock types. Incorrectly choosing a weaker clock could lead to subtle and hard-to-diagnose bugs.
   * Confidence: Medium

## Alternatives Considered

1. **Global Counter Everywhere**: The current model.
   * Brief reason for rejection: Does not capture causality, which is a fundamental requirement for reasoning about and debugging distributed workflows. It can lead to incorrect state reconciliation.
   * Confidence: High
2. **Physical Clocks (NTP)**: Relying on synchronized physical clocks to order events.
   * Brief reason for rejection: Clock skew between servers makes physical clocks unreliable for determining the precise order of events in a distributed system. Logical clocks are designed to solve this problem.
   * Confidence: High

## Consequences

* **Positive:** Enables the system to correctly reason about causal relationships between events. Prevents a large class of subtle bugs related to event ordering and concurrent state updates. Provides a robust foundation for building more complex, reliable distributed workflows.
* **Negative:** Increases the complexity of the event/messaging infrastructure. Adds overhead to messages carrying vector clocks. Requires developers to be trained on the proper use of logical clocks.

## Clarifying Questions

* What is the standard library and data structure for representing vector clocks?
* How does the system handle a "new" agent joining and initializing its vector clock?
* What visualization tools will be provided to help developers debug causal event histories?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
