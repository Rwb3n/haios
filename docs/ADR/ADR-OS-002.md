# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_002_md",
        "g_annotation_created": 5,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 5, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 4, "identifier": "Framework_Compliance_Retrofit" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "adr_os_032_md"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-002: Hierarchical Planning Model

* **Status**: Proposed
* **Date**: 2025-06-06
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

Complex projects require more than a simple, flat list of tasks. 
To ensure strategic alignment, provide context to agents, and manage large scopes, a multi-layered planning approach is necessary. 
We need a structure that connects high-level strategic intent to the granular, tactical work performed by coding agents.

## Assumptions

* [ ] The planning hierarchy maps directly to agent specialization (e.g., strategic vs. tactical agents).
* [ ] The overhead of creating multiple planning artifacts is justified by the gain in traceability and context scoping.
* [ ] All agents can interpret and act upon their assigned planning layer without ambiguity.
* [ ] The linkage between planning artifacts (e.g., Request → Analysis → Initiative → Execution) is reliably maintained and observable.
* [ ] The system can handle asynchronous creation and linkage of planning artifacts without loss of context or traceability.
* [ ] The planning artifact store is always available and consistent, or recovers gracefully from partitions.
* [ ] Supervisor Agent(s) have sufficient capability to manage transitions and relationships between planning layers.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-024, ADR-OS-027, ADR-OS-028, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Theory of Constraints (ToC) v1.0
- **Compliance Proof:** The hierarchical planning model identifies bottlenecks at each planning level and enables optimization by separating strategic constraints from tactical ones.
- **Self-Critique:** Requires sophisticated "Supervisor Agent" to manage transitions, which could become a bottleneck itself.

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** Four-tier hierarchy (Request -> Analysis -> Initiative -> Execution) provides necessary complexity without over-engineering.
- **Self-Critique:** Might feel heavyweight for trivial one-off tasks; balance between simplicity and structure needs refinement.

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Strategic context is captured once in Initiative Plan and referenced by multiple Execution Plans, avoiding duplication.
- **Self-Critique:** Context-loading logic might still require higher-level plan information, potentially creating coupling.

### Explicit Diagramming v1.0
- **Compliance Proof:** Hierarchical flow diagram showing Request -> Analysis -> Initiative -> Execution is implied.
- **Self-Critique:** **NON-COMPLIANCE:** Actual hierarchy diagram is missing and should be added.
- **Mitigation:** Future revision will include explicit planning hierarchy diagram.

### Distributed Systems Principles v1.0
- **Compliance Proof:** The "Distributed Systems Implications" section addresses asynchronicity, event ordering, partition tolerance, and observability for planning artifacts.
- **Self-Critique:** Planning artifact store as CP system may impact availability during partitions.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation.
- **Self-Critique:** Only three assumptions listed; hierarchical planning likely has more implicit assumptions about agent capabilities and coordination.

### Traceability v1.0
- **Compliance Proof:** "Golden thread" from request to execution ensures full traceability through the planning hierarchy.
- **Self-Critique:** If not enforced, the "golden thread" can be broken, negating the primary benefit.

## Decision

**Decision:**

> We will adopt a multi-tiered, hierarchical planning model that flows from a high-level `Request` down to specific `Execution Plans`. The primary artifacts in this hierarchy are: **`Request` -> `Analysis Report` -> `Initiative Plan` -> `Execution Plan`**. This structure ensures that all work is traceable back to a strategic objective and an originating request.
>
> ### Distributed Systems Implications
>
> The relationships and state transitions between these planning artifacts must be managed with the following considerations:
>
> *   **Asynchronicity (ADR-OS-024):** The creation and linkage of these artifacts may be an asynchronous process. For example, submitting a `Request` may immediately return an ID, while the subsequent `Analysis Report` is generated in the background.
> *   **Event Ordering (ADR-OS-027):** The causal link between planning artifacts (e.g., this `Execution Plan` was created by that `Initiative Plan`) must be captured using appropriate logical clocks.
> *   **Partition Tolerance (ADR-OS-028):** The planning artifact store must behave as a CP system. In a partition, it may become impossible to create new plans or link existing ones until consistency is restored.
> *   **Observability (ADR-OS-029):** Every step in the planning hierarchy's lifecycle (creation, update, linkage) must be part of a distributed trace, ensuring the "golden thread" from request to execution is fully observable.

**Confidence:** High

## Rationale

1. **Traceability**
   * Self-critique: If not enforced, the "golden thread" can be broken, negating the primary benefit.
   * Confidence: High
2. **Context Scoping**
   * Self-critique: An agent might still require context from a higher-level plan, leading to more complex context-loading logic.
   * Confidence: High
3. **Separation of Strategic and Tactical Concerns**
   * Self-critique: A rigid separation might hinder agility if a tactical discovery requires immediate strategic reprioritization.
   * Confidence: Medium
4. **Enables Phased Rollout**
   * Self-critique: Defining clear, non-overlapping `initiative_lifecycle_stages` can be challenging for highly interconnected systems.
   * Confidence: Medium
5. **Hierarchy Components & Flow**
   * Self-critique: The strict flow could be inefficient for urgent, small-scale bug fixes.
   * Confidence: Medium

## Alternatives Considered

1. **Flat Task List**: A single global list of tasks or issues. Rejected because it lacks strategic context, makes prioritization difficult for large projects, and offers poor traceability for the "why" behind a task.
   * Confidence: High
2. **Two-Tiered (Plan -> Tasks)**: A simpler model with just plans and tasks. Rejected because it merges strategic ("what is the overall goal of this 6-month project?") and tactical ("what specific files do I change today?") planning into a single artifact, which becomes unwieldy and lacks the phased lifecycle management provided by the `Initiative Plan` layer.
   * Confidence: High

## Consequences

* **Positive:** Creates a highly structured and organized project management system. Enforces strategic alignment for all tactical work. Provides appropriate levels of abstraction for different agents or human roles. The structured artifacts at each level serve as durable, long-term memory for the project.
* **Negative:** Introduces overhead; creating all these planning artifacts for a very trivial one-off task might feel heavyweight. Requires a sophisticated "Supervisor Agent" to manage the transitions and relationships between these planning layers.

## Clarifying Questions

* How will the system handle a `Request` that spawns multiple, independent `Initiative Plans`?
* What is the process for archiving or closing out a completed `Initiative Plan` and its children?
* How are planning artifact linkages (e.g., parent-child relationships) validated and repaired if broken?
* What is the recovery process if the planning artifact store becomes inconsistent or partially unavailable?
* How does the system ensure that context and traceability are preserved during asynchronous or concurrent plan creation?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
