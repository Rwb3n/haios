# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_012_md",
        "g_annotation_created": 12,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 12, "identifier": "Hybrid_AI_OS" },
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

# ADR-OS-012: Dynamic Agent Management

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

For the Hybrid_AI_OS to evolve into a truly autonomous and adaptable system, especially one supporting multiple specialized AI agents ("vessels"), the management of these agents cannot be a static, hardcoded configuration. The system requires a dynamic way to register, configure, and monitor the agent personas available for executing tasks. This mechanism needs to be robust, transparent, and controllable via OS-level operations, aligning with the potential for a "cockpit" UI for human supervision.

## Assumptions

*   [ ] The "Index + Individual File" pattern is performant enough for the expected number of agents.
*   [ ] OS-level actions provide a sufficient security model for managing agent lifecycles.
*   [ ] The agent registry and cards are versioned and auditable for all changes.
*   [ ] The system can detect and recover from registry or card corruption or partial updates.
*   [ ] The agent management process is robust against concurrency and race conditions.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** "Distributed Systems Implications" section addresses security, topology & health, partition tolerance, and observability for agent registry.
- **Self-Critique:** Agent registry as CP system may impact availability during partitions; needs careful consideration.

### Scalability v1.0
- **Compliance Proof:** "Index + Individual File" pattern prevents single monolithic registry file that would become contention point.
- **Self-Critique:** Index file could still become contention point if many processes check it frequently.

### Dynamic Configuration v1.0
- **Compliance Proof:** Runtime agent management without restarting OS or manual config file editing.
- **Self-Critique:** Requires high-privilege "Supervisor" agent, creating potential single point of failure.

### Service Discovery v1.0
- **Compliance Proof:** Agent registry serves as source of truth for service discovery with self-registration and health propagation.
- **Self-Critique:** Polling superseded by subscription model but implementation complexity increases.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about Index pattern performance, OS-level security sufficiency, and agent lifecycle management.
- **Self-Critique:** Only three assumptions listed; dynamic agent management likely has more implicit assumptions about concurrency and failure modes.

## Decision

**Decision:**

> We will implement a dynamic, file-based agent management system using the established **"Index + Individual File"** pattern. This system will consist of two new types of OS Control Files:
> 
> 1.  **`os_root/agent_registry.txt` (The Index):** A single, top-level file that serves as an index of all known and available agent personas. It will map `persona_id`s to the file path of their detailed "Agent Card" and mirror key status information for quick lookups.
> 2.  **`os_root/agents/persona_<id>.txt` (The Agent Card):** Individual, detailed files for each agent persona. Each "Agent Card" will contain the complete configuration for that role, including its capabilities, currently assigned AI model, model-specific parameters, operational status, and a history log.

## Rationale

1.  **Scalability & Performance**
    *   Self-critique: The index file (`agent_registry.txt`) could still become a contention point if many processes need to check it frequently.
    *   Confidence: High
2.  **Dynamic & Controllable**
    *   Self-critique: Requires a high-privilege "Supervisor" agent, creating a potential single point of failure or control bottleneck.
    *   Confidence: High
3.  **Consistency with OS Design Patterns**
    *   Self-critique: Over-reliance on one pattern might lead to ignoring a better-suited pattern for a specific problem in the future.
    *   Confidence: High
4.  **Rich, Granular Configuration**
    *   Self-critique: Could lead to overly complex Agent Cards that are difficult to manage or audit manually.
    *   Confidence: High

## Alternatives Considered

1.  **Static Configuration (`haios.config.json`)**: Placing the agent roster in the main config file. Rejected as too rigid, not suitable for dynamic runtime changes, and less scalable for detailed agent configurations.
    *   Confidence: High
2.  **Single Monolithic Registry File**: A single file containing all details for all agents. Rejected because it could become very large and unwieldy to parse and update, violating the principle of isolating detailed records.
    *   Confidence: High

## Consequences

*   **Positive:** Provides a flexible and scalable system for managing a fleet of diverse AI agents. Enables runtime configuration of agents without restarting the OS or manually editing project configuration files. Keeps the core `haios.config.json` clean and focused on static, foundational project settings. Creates a clear, auditable trail for changes to agent configurations via updates to these OS Control Files.
*   **Negative:** Introduces two new OS Control File schemas that need to be defined and managed. Requires the OS to have a privileged "manager" capability to modify the agent registry and cards.

## Clarifying Questions

* What is the process for recovering from a corrupted or partially updated agent registry or Agent Card file? 
* How are concurrent updates to the agent registry and Agent Cards coordinated to prevent race conditions or data loss?
* What mechanisms are in place to audit and roll back unauthorized or erroneous changes to agent configurations?
* How does the system handle the addition or removal of agent personas at runtime, especially under high load or during network partitions?
* What are the escalation and notification procedures if the "Supervisor" agent fails or becomes unavailable?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
