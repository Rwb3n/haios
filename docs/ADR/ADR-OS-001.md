# ADR-OS-001: Core Operational Loop & Phasing

* **Status**: Proposed
* **Date**: 2025-06-06
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

The Hybrid_AI_OS requires a predictable, structured, and traceable process for managing complex projects from user request to completion. 
An ad-hoc or purely reactive model would lead to inconsistencies, poor traceability, and difficulty in coordinating autonomous agents. 
We need a defined operational lifecycle that provides clear states, transitions, and objectives for the OS and its agents at every step.

## Assumptions

* [ ] The OS always persists `state.txt.ph` atomically between phases.
* [ ] Agent health checks succeed before phase transitions.
* [ ] All agents have access to a consistent view of the current phase state.
* [ ] Phase transitions are triggered only after all required objectives of the current phase are met.
* [ ] The state machine governing phase transitions is free of deadlocks and livelocks.
* [ ] Human intervention points are clearly defined and respected by the OS.
* [ ] All artifacts required for a phase transition are available and valid at the time of transition.
* [ ] Distributed traceability (e.g., `trace_id`) is reliably propagated across all phase transitions and agent actions.
* [ ] The OS can recover gracefully from partial failures during phase transitions.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-024, etc.) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Theory of Constraints (ToC) v1.0
- **Compliance Proof:** The five-phase loop explicitly identifies bottlenecks at phase transitions, enabling systematic identification and resolution of constraints in the workflow.
- **Self-Critique:** Requires robust monitoring to accurately identify bottlenecks, which adds overhead.

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** The operational loop uses exactly five phases with clear, single-purpose objectives for each phase.
- **Self-Critique:** The phased approach might be too rigid for highly dynamic or exploratory tasks.

### Explicit Diagramming v1.0
- **Compliance Proof:** State machine diagram showing phase transitions is implied by the five-phase description.
- **Self-Critique:** **NON-COMPLIANCE:** Actual state transition diagram is missing and should be added.
- **Mitigation:** Future revision will include explicit state machine diagram.

### Distributed Systems Principles v1.0
- **Compliance Proof:** The "Distributed Systems Implications" section explicitly addresses idempotency, asynchronicity, event ordering, partition tolerance, and observability.
- **Self-Critique:** Implementation details for partition tolerance during phase transitions need further specification.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation.
- **Self-Critique:** Only three assumptions listed; operational loop likely has more implicit assumptions that should be surfaced.

## Decision

**Decision:**

> We will adopt a five-phase, event-driven operational loop: **ANALYZE, BLUEPRINT, CONSTRUCT, VALIDATE, and IDLE**. 
> The OS will transition between these phases based on the completion of prior phase objectives, the state of planning artifacts, and explicit user directives. 
> This loop provides the foundational state machine for all OS operations. The current phase is tracked in `state.txt.ph`.
>
> ### Distributed Systems Implications
>
> The execution of this operational loop and the transitions between phases MUST adhere to the following cross-cutting policies to ensure robustness in a distributed environment:
>
> *   **Idempotency & Retries (ADR-OS-023):** All actions that mutate state during a phase transition MUST be idempotent to prevent errors from transient failures.
> *   **Asynchronicity (ADR-OS-024):** While the loop is logically sequential, communication *within* a phase (e.g., an agent performing a task) MAY be asynchronous. Handoffs between phases, however, are major state transitions that are typically resolved before the next phase begins.
> *   **Event Ordering (ADR-OS-027):** All events generated within the loop MUST be timestamped according to the event ordering policy, using vector clocks where causality is critical.
> *   **Partition Tolerance (ADR-OS-028):** The core state management (`state.txt`) is a CP system. In a network partition, it will prioritize consistency, potentially halting phase transitions until the partition is resolved.
> *   **Observability (ADR-OS-029):** Every phase transition and significant action within a phase MUST be part of a distributed trace, propagating the `trace_id`.

**Confidence:** Medium

## Rationale

1. **Clarity & Predictability**
   * Self-critique: The phased approach might be too rigid for highly dynamic or exploratory tasks.
   * Confidence: High
2. **Separation of Concerns**
   * Self-critique: Increased complexity in coordinating handoffs between specialized agents for each phase.
   * Confidence: High
3. **Quality Gates**
   * Self-critique: Transitions could become bottlenecks if validation processes are slow or overly strict.
   * Confidence: Medium
4. **Alignment with Software Development**
   * Self-critique: The analogy might not perfectly fit all types of AI-driven projects, leading to conceptual friction.
   * Confidence: Medium
5. **Supports Theory of Constraints**
   * Self-critique: Requires robust monitoring to accurately identify bottlenecks, which adds overhead.
   * Confidence: Medium
6. **Detailed Phase Definitions**
   * Self-critique: The defined transitions might not cover all edge cases or failure modes, requiring future refinement.
   * Confidence: Medium

## Alternatives Considered

1. **Monolithic "Do Task" Model**: A single phase where the AI takes a request and tries to do everything (analyze, plan, code, test) in one go. Rejected due to lack of traceability, scalability, and control for complex tasks.
   * Confidence: High
2. **Purely Agile/Kanban Model**: A board of "tasks" without the strategic `Initiative Plan` layer. Rejected as it lacks the high-level strategic planning and lifecycle stage management needed for long-term, multi-stage projects. Our model incorporates Kanban/TOC principles *within* the structured phases.
   * Confidence: High

## Consequences

* **Positive:** Provides a highly structured and auditable workflow. Enforces a "plan before doing" and "verify after doing" discipline. Creates clear points for potential human intervention or review. Modular design supports specialized AI agents for each phase.
* **Negative:** Can introduce overhead for very small, simple tasks compared to a purely conversational approach. The effectiveness of the loop relies heavily on the quality of the artifacts generated in each phase.

## Clarifying Questions

* How will the OS handle tasks that require jumping back to a previous phase (e.g., a validation failure requiring more construction)?
* What is the mechanism for a human to override a phase transition?
* How are partial or failed phase transitions detected and recovered, especially in distributed or partially available environments?
* What are the escalation and notification procedures if a phase transition is blocked or deadlocked?
* How does the OS ensure traceability and auditability of all phase transitions, including manual overrides?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
