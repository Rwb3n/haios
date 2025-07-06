# ADR-OS-017: Phase 1 - MVP Engine & Tooling

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

The architectural foundation of the Hybrid AI Operating System (HAiOS) is now fully specified across a comprehensive set of ADRs (001-016) and supporting documentation. The next logical step is to transition from architectural definition to implementation. A minimal, viable implementation is required to validate the core concepts in practice and provide a foundational toolset for both human operators and future agent development.

## Assumptions

*   [ ] A command-line executable is a sufficient interface for the MVP.
*   [ ] A simple, sequential `SCAFFOLDING` plan is complex enough to validate the core OS loop.
*   [ ] The defined schemas are stable enough to build the initial tooling against.
*   [ ] The MVP engine can be extended to support agent integration and concurrency in future phases.
*   [ ] The system can detect and recover from MVP execution or plan validation failures.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-024, ADR-OS-027, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** DAG-based dependency management addresses ordering and consistency in distributed task execution; prevents race conditions.
- **Self-Critique:** Missing explicit handling of partial failures and dependency chain recovery in distributed environment.

### Theory of Constraints v1.0
- **Compliance Proof:** Dependency resolution identifies critical path and bottlenecks in task execution flow; optimizes overall throughput.
- **Self-Critique:** Current design doesn't explicitly address resource constraints or parallel execution optimization within dependency chains.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about DAG modeling, algorithm efficiency, and agent dependency checking capabilities.
- **Self-Critique:** Only three assumptions listed; dependency management likely has more implicit assumptions about task atomicity and state consistency.

### Fail-Safe Design v1.0
- **Compliance Proof:** Dependency blocking prevents execution of tasks with unmet prerequisites; circular dependency detection prevents infinite loops.
- **Self-Critique:** Dependency resolution failures could block entire execution chains; needs robust fallback and recovery mechanisms.

### Traceability v1.0
- **Compliance Proof:** Dependency relationships and resolution decisions are logged for audit trail and debugging.
- **Self-Critique:** Trace data might not capture enough context about why specific dependencies were defined or how they evolved.

### Hierarchical Organization v1.0
- **Compliance Proof:** Task dependencies create natural hierarchical structure with clear parent-child relationships and execution levels.
- **Self-Critique:** Deep dependency hierarchies might become difficult to visualize and debug; could benefit from flattening strategies.

## Decision

**Decision:**

> We will formally initiate **Phase 1: Core OS Engine & Tooling**. The singular goal of this phase is to build the **Minimum Viable Product (MVP)** of the HAiOS orchestrator.
>
> This MVP will be a command-line executable (the "engine") capable of performing a single, complete, end-to-end `SCAFFOLDING` Execution Plan. It must be able to read and write all necessary OS Control Files according to their ratified schemas, demonstrating the core operational loop in its simplest form.
>
> ### Distributed Systems Implications
>
> Although this MVP focuses on a single-node, sequential "happy path," its implementation MUST be built in alignment with the core distributed systems principles to serve as a valid foundation.
>
> *   **Idempotency (ADR-OS-023):** All MVP actions that create or modify files (e.g., creating a directory, injecting an annotation block) MUST be idempotent. Rerunning a partially completed plan must not cause errors.
> *   **Asynchronicity (ADR-OS-024):** While the MVP engine itself will run sequentially, its internal APIs for state and file I/O should be designed with asynchronicity in mind to facilitate the transition to a truly concurrent model.
> *   **Event Ordering (ADR-OS-027):** Every significant action taken by the engine (e.g., "starting task," "created file," "updated registry") MUST be associated with the global event counter (`g`), even in this simple implementation.
> *   **Observability (ADR-OS-029):** The entire MVP run MUST produce a distributed trace. A root span should be created when the engine starts, and every major step (reading config, executing task, writing status) must be a child span, propagating the `trace_id` throughout.

**Confidence:** High

## Rationale

1.  **De-risking Core Concepts**
    *   Self-critique: A "thin slice" might hide unforeseen complexities that only emerge when handling multiple, concurrent, or more diverse plan types.
    *   Confidence: High
2.  **Delivering Immediate Utility**
    *   Self-critique: The utility is limited until agents are integrated; a human still needs to write the initial plans manually.
    *   Confidence: High
3.  **Foundation for Agent Integration**
    *   Self-critique: The interfaces defined in the MVP might need significant refactoring once real agent integration begins, if initial assumptions are wrong.
    *   Confidence: Medium
4.  **Focus on the "Happy Path"**
    *   Self-critique: Deferring complex error handling might lead to architectural decisions that make robust error handling harder to implement later.
    *   Confidence: Medium

## Alternatives Considered

*No formal alternatives were considered as this decision represents the natural progression from architectural definition to implementation.*

## Consequences

*   **Positive:** Provides a tangible, testable product at the end of the phase. Creates the core modules (ConfigLoader, StateManager, TaskRunner) that will be the building blocks for the more complex, agent-driven system in Phase 2. Forces us to confront any practical implementation challenges with our file-based approach early on.
*   **Negative:** None specified in the original document.

## Scope & Key Deliverables

The scope of the Phase 1 MVP is strictly limited to the following capabilities:

1.  **Schema Tooling:**
    *   **Deliverable:** A set of formal `JSON Schema` files (`*.schema.json`) translated from our Markdown documentation for all defined OS Control Files and the `EmbeddedAnnotationBlock`.
    *   **Deliverable:** A validation utility that can programmatically check a given OS Control File against its corresponding schema.

2.  **Configuration & State Management:**
    *   **Deliverable:** A `ConfigLoader` module capable of reading and parsing `haios.config.json` to determine operational paths.
    *   **Deliverable:** A `StateManager` module that can read, write, and safely update `state.txt`, correctly implementing the optimistic locking (`v` counter) mechanism.

3.  **Core Orchestrator Engine (MVP):**
    *   **Deliverable:** A command-line executable (e.g., `npx haios-engine run-plan <plan_id>`).
    *   **Functionality:**
        a.  Reads `state.txt` and the specified `exec_plan_<g>.txt`.
        b.  Creates the corresponding `exec_status_<g_plan>.txt`.
        c.  Performs a basic **Pre-Execution Readiness Check** for the plan's tasks (e.g., verifies that referenced `Scaffold Definition` and `Template` files exist).
        d.  Executes the tasks in the `SCAFFOLDING` plan sequentially. This involves:
            i.   Creating directories.
            ii.  Copying boilerplate from `project_templates/`.
            iii. Injecting a complete `EmbeddedAnnotationBlock` into new artifacts.
            iv.  Registering new artifacts in `global_registry_map.txt`.
        e.  Updates the `exec_status_*.txt` file as tasks are completed.
        f.  Upon completion, transitions the OS `state.txt` appropriately.

## Exclusions (Out of Scope for Phase 1)

*   Integration with actual LLM-based AI agents. The MVP engine will be a deterministic script runner that *simulates* an agent's actions.
*   The full `ANALYZE` or `BLUEPRINT` phases. The `init_plan` and `exec_plan` files for the MVP test case will be created manually.
*   The full `VALIDATE` phase. The MVP will stop after `CONSTRUCT`.
*   Advanced error handling, remediation planning, and critique loops.
*   The "Cockpit" UI.

## Success Criteria ("Definition of Done" for Phase 1)

*   The OS engine executable can be successfully run against a project initialized with our standard directory scaffold.
*   Given a manually created `SCAFFOLDING` `Execution Plan`, the engine correctly creates all specified directories and files in the `project_workspace`.
*   All newly created artifacts contain a valid, fully populated `EmbeddedAnnotationBlock`.
*   `global_registry_map.txt` and `exec_status_*.txt` are accurately created and updated.
*   The final `state.txt` correctly reflects the completion of the process.

## Clarifying Questions

*   What programming language and key libraries will be used for the MVP engine, and how will this choice impact future extensibility and agent integration?
*   How will the initial, manual `Execution Plan` be validated before the engine runs it, and what is the process for updating or migrating plans as schemas evolve?
*   How will the MVP engine handle partial failures, dependency chain recovery, and error reporting in the absence of full agent integration?
*   What mechanisms are in place to audit, trace, and analyze all MVP actions and state transitions for debugging and compliance?
*   How will the MVP engine and its interfaces be evolved or refactored as new requirements and agent capabilities are introduced in later phases?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*


