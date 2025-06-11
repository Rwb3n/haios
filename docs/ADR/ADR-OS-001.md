# ADR-OS-001: Core Operational Loop & Phasing

*   **Status:** Proposed
*   **Date:** 2025-06-06
*   **Context:**
    The Hybrid_AI_OS requires a predictable, structured, and traceable process for managing complex projects from user request to completion. 
    An ad-hoc or purely reactive model would lead to inconsistencies, poor traceability, and difficulty in coordinating autonomous agents. 
    We need a defined operational lifecycle that provides clear states, transitions, and objectives for the OS and its agents at every step.

*   **Decision:**
    We will adopt a five-phase, event-driven operational loop: **ANALYZE, BLUEPRINT, CONSTRUCT, VALIDATE, and IDLE**. 
    The OS will transition between these phases based on the completion of prior phase objectives, the state of planning artifacts, and explicit user directives. 
    This loop provides the foundational state machine for all OS operations. The current phase is tracked in `state.txt.ph`.

*   **Rationale:**
    *   **Clarity & Predictability:** A defined set of phases makes the system's current state and next likely actions predictable for both human supervisors and other AI agents.
    *   **Separation of Concerns:** Each phase has a distinct purpose (strategic analysis vs. tactical planning vs. execution vs. verification), which allows for the potential use of specialized agents for each phase and prevents a single monolithic "do everything" process.
    *   **Quality Gates:** The transition between phases acts as a natural quality gate. For example, work cannot move from `CONSTRUCT` to the next major initiative stage without passing through `VALIDATE`.
    *   **Alignment with Software Development:** The phases loosely mirror established software development lifecycle stages (Requirements Analysis, Design, Implementation, QA/Testing), making the process intuitive.
    *   **Supports Theory of Constraints:** The loop allows for identifying and managing bottlenecks. For instance, if work piles up waiting for the `VALIDATE` phase, it becomes clear that validation is a system constraint that needs to be addressed.

*   **Phase Definitions & Transitions:**

    1.  **ANALYZE:**
        *   **Goal:** To process a `Request` and produce a comprehensive, human-readable `Analysis Report`. This report details the understanding of the request, identifies risks/dependencies, and proposes a strategic `Initiative Plan`.
        *   **Process:** This phase internally orchestrates a mini-cycle (`ANALYSIS_EXECUTION` plan) to investigate the request and populate the `Analysis Report` artifact. The final step of the `ANALYZE` goal is to use this completed report to formulate or update the main `Initiative Plan`.
        *   **Trigger:** A new `Request` detected while in the `IDLE` phase.
        *   **Transitions To:** `BLUEPRINT` (to begin work on the first stage of the newly formulated `Initiative Plan`).

    2.  **BLUEPRINT:**
        *   **Goal:** To translate the strategic goals of a specific `initiative_lifecycle_stage` into one or more detailed, tactical, and typed `Execution Plans`.
        *   **Process:** Based on the `expected_exec_plan_types` for the current initiative stage (e.g., SCAFFOLDING, DEVELOPMENT, TEST_EXECUTION), the OS generates detailed tasks, inputs, outputs, and checklists. For `SCAFFOLDING` plans, it consumes `Scaffold Definition` definitions.
        *   **Trigger:** The completion of the `ANALYZE` phase, or the completion and validation of the previous `initiative_lifecycle_stage`.
        *   **Transitions To:** `CONSTRUCT` (once an `Execution Plan` is ready to be worked on).

    3.  **CONSTRUCT:**
        *   **Goal:** To execute the tasks defined in an active `Execution Plan`.
        *   **Process:** The OS's "Coding Agent" (or other specialized agent) works through tasks, creating/modifying Project Artifacts, embedding/updating comprehensive `EmbeddedAnnotationBlock`s, generating `Test Results` artifacts, or authoring reports as defined by the plan type. It updates the `registry_map.txt` and task statuses as it proceeds.
        *   **Trigger:** An `Execution Plan` being ready for execution after the `BLUEPRINT` phase.
        *   **Transitions To:** `VALIDATE` (once an `Execution Plan` is fully executed and marked as `COMPLETED_SUCCESS` or `COMPLETED_PARTIAL`).

    4.  **VALIDATE:**
        *   **Goal:** To rigorously verify the outputs of a completed `Execution Plan` against its goals and quality standards.
        *   **Process:** The OS checks artifact integrity, schema compliance of annotations, parses `Test Results` artifacts to update the `quality_notes` of tested code, logs any new `Issues`, and generates a formal `Validation Report` artifact summarizing all findings.
        *   **Trigger:** An `Execution Plan` completing its `CONSTRUCT` phase.
        *   **Transitions To:** `IDLE` (if the initiative is complete or awaiting further direction), or back to `BLUEPRINT` (if remediation plans are needed), or signals readiness for the next `initiative_lifecycle_stage`.

    5.  **IDLE:**
        *   **Goal:** The default resting state, awaiting new directives or the resolution of blocking conditions.
        *   **Process:** The OS monitors for new `Requests` or handles `BLOCK_INPUT` states, where it awaits human clarification or approval.
        *   **Trigger:** Completion of all active work (e.g., after `VALIDATE` finds no immediate next step) or when a process is explicitly blocked.
        *   **Transitions To:** `ANALYZE` (upon detecting a new `User Request`).

*   **Consequences:**
    *   **Pros:**
        *   Provides a highly structured and auditable workflow.
        *   Enforces a "plan before doing" and "verify after doing" discipline.
        *   Creates clear points for potential human intervention or review.
        *   Modular design supports specialized AI agents for each phase.
    *   **Cons:**
        *   Can introduce overhead for very small, simple tasks compared to a purely conversational approach.
        *   The effectiveness of the loop relies heavily on the quality of the artifacts generated in each phase (e.g., a poor `Analysis Report` leads to a poor `Initiative Plan`).

*   **Alternatives Considered:**
    *   **Monolithic "Do Task" Model:** A single phase where the AI takes a request and tries to do everything (analyze, plan, code, test) in one go. Rejected due to lack of traceability, scalability, and control for complex tasks.
    *   **Purely Agile/Kanban Model:** A board of "tasks" without the strategic `Initiative Plan` layer. Rejected as it lacks the high-level strategic planning and lifecycle stage management needed for long-term, multi-stage projects. Our model incorporates Kanban/TOC principles *within* the structured phases.