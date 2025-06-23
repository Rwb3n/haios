# ADR-OS-028: Partition Tolerance and Split-Brain Protocol

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

The current architecture does not have an explicit, system-wide protocol for how to behave during a network partition. Different components might make different choices, leading to inconsistent state and a "split-brain" scenario where different parts of the system operate on conflicting data. This ADR formalizes the trade-offs (per the CAP theorem) for each major component and defines a protocol for detection, behavior during a partition, and state reconciliation after the partition heals.

## Assumptions

* [ ] The system has a reliable mechanism (e.g., from ADR-026) to detect network partitions.
* [ ] For any stateful component, we can clearly define whether it should prioritize Consistency (CP) or Availability (AP) during a partition.
* [ ] Automated tools can be built to assist in the reconciliation of conflicting states after a partition is resolved.
* [ ] The partition tolerance and reconciliation protocol is robust against split-brain, quorum loss, and reconciliation errors.
* [ ] The system can detect and recover from partition protocol misconfiguration or consensus library failures.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

## Decision

**Decision:**

> We will implement a formal protocol for network partition tolerance.
> 1.  **Explicit CAP Trade-off:** Every stateful service or component (e.g., agent registry, plan executor) MUST declare its strategy in the face of a partition:
>     *   **CP (Consistency/Partition Tolerance):** The component will become unavailable (e.g., read-only or fully down) rather than serve potentially stale or conflicting data. This is the default for critical state like the agent registry.
>     *   **AP (Availability/Partition Tolerance):** The component will remain available for reads and writes, accepting that its state may diverge from other partitions. This is suitable for non-critical, eventually consistent data like logs.
> 2.  **Split-Brain Prevention:** For all CP components, a quorum-based mechanism (e.g., Raft, Paxos) MUST be used to ensure that only the majority partition can accept writes, preventing a split-brain scenario.
> 3.  **State Reconciliation:** For AP components, a formal, semi-automated process for reconciling divergent data MUST be defined. This may involve "last-write-wins" strategies, CRDTs, or escalating to a human operator for manual merging.

**Confidence:** High

## Rationale

1. **Guarantees Predictable Behavior**
   * Self-critique: Implementing quorum-based consensus protocols like Raft is extremely difficult and complex. Using a proven, off-the-shelf library (e.g., etcd, Zookeeper) is a much safer approach than building our own.
   * Confidence: High
2. **Prevents Data Corruption**
   * Self-critique: For some complex data types, automatic reconciliation is impossible. The plan for manual escalation must be robust and well-documented.
   * Confidence: High
3. **Makes Trade-offs Explicit**
   * Self-critique: Forcing a binary CP/AP choice might be too simplistic for some components that could offer more nuanced behavior (e.g., allow stale reads but block writes).
   * Confidence: Medium

## Alternatives Considered

1. **Assume No Partitions**: Ignoring the possibility of network partitions.
   * Brief reason for rejection: In any real-world distributed system, partitions are a certainty. Ignoring them guarantees data corruption and unpredictable failures.
   * Confidence: High
2. **Always Prioritize Availability (AP)**: Let all components remain writeable during a partition.
   * Brief reason for rejection: This inevitably leads to split-brain scenarios for critical state, resulting in data loss and a system that is impossible to reason about.
   * Confidence: High

## Consequences

* **Positive:** Makes the system resilient to network partitions. Prevents catastrophic data corruption due to split-brain. Forces a clear, conscious decision about the trade-offs between consistency and availability for every component.
* **Negative:** Significantly increases the complexity of the architecture, especially for CP components that require a consensus system. The reconciliation process for AP components can be complex to design and implement.

## Clarifying Questions

* What is the standard consensus library/protocol (e.g., Raft via etcd) that will be used for CP components, and how will upgrades or migrations be managed?
* What specific data reconciliation strategies (e.g., last-write-wins, CRDTs, manual merge) will be used for the initial set of AP components, and how are conflicts audited and resolved?
* How are clients (agents) made aware that a service is currently unavailable due to a partition, and what is the failover or retry policy?
* What mechanisms are in place for partition detection, recovery, and audit of partition events across the system?
* How will the partition tolerance protocol and component CAP trade-offs be evolved as new requirements or technologies emerge?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
