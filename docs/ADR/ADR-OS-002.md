# ADR-OS-002: Hierarchical Planning Model

*   **Status:** Proposed
*   **Date:** 2025-06-06
*   **Context:**
    Complex projects require more than a simple, flat list of tasks. 
    To ensure strategic alignment, provide context to agents, and manage large scopes, a multi-layered planning approach is necessary. 
    We need a structure that connects high-level strategic intent to the granular, tactical work performed by coding agents.

*   **Decision:**
    We will adopt a multi-tiered, hierarchical planning model that flows from a high-level `Request` down to specific `Execution Plans`. The primary artifacts in this hierarchy are: **`Request` -> `Analysis Report` -> `Initiative Plan` -> `Execution Plan`**. This structure ensures that all work is traceable back to a strategic objective and an originating request.

*   **Rationale:**
    *   **Traceability:** Provides a clear "golden thread" from the lowest-level task in an `Execution Plan` all the way up to the strategic `Initiative Plan` goal and the initial `Request` that prompted it. This is critical for auditing, debugging, and understanding purpose.
    *   **Context Scoping:** The `Initiative Plan` provides high-level strategic context, while the `Execution Plan` provides focused, tactical context. This allows specialized agents to operate with the appropriate level of detail without needing the entire project history in their immediate context window.
    *   **Separation of Strategic and Tactical Concerns:** The Supervisor Agent (or human) can focus on the strategic "what" and "why" at the `Initiative Plan` level, while the Coding Agent can focus on the tactical "how" at the `Execution Plan` level.
    *   **Enables Phased Rollout:** The `Initiative Plan`'s `initiative_lifecycle_stages` allow for breaking down a large project into manageable, sequential phases, preventing the system from planning too far ahead in excessive detail.

*   **Hierarchy Components & Flow:**

    1.  **`Request` (`request_<g>.txt`):**
        *   **Role:** The trigger for all new work. It is the raw, unprocessed directive from an external source (human user, another agent, system alert).
        *   **Flow:** A new `Request` initiates the `ANALYZE` phase.

    2.  **`Analysis Report` (`analysis_report_*.md`):**
        *   **Role:** The formal, documented output of the `ANALYZE` phase. It serves as the bridge between a raw `Request` and a structured `Initiative Plan`. It contains the interpretation, risk assessment, and detailed strategic proposal.
        *   **Flow:** Consumes a `Request`, is produced via an `ANALYSIS_EXECUTION` plan, and serves as the primary input for creating or updating an `Initiative Plan`.

    3.  **`Initiative Plan` (`init_plan_<g>.txt`):**
        *   **Role:** The strategic layer. It defines a major project or work campaign. It holds the `overall_goal`, `quality_acceptance_criteria`, a `decision_log`, and a roadmap of `initiative_lifecycle_stages`. It is the central "charter" for a significant body of work. It does **not** contain specific coding tasks.
        *   **Flow:** Consumes an `Analysis Report`. Its active `initiative_lifecycle_stage` is the input to the `BLUEPRINT` phase.

    4.  **`Execution Plan` (`exec_plan_<g>.txt`):**
        *   **Role:** The tactical layer. It is a detailed, actionable plan of a specific `plan_type` (e.g., SCAFFOLDING, DEVELOPMENT) designed to fulfill the objective of a single `initiative_lifecycle_stage`. It contains the granular list of `tasks` to be performed.
        *   **Flow:** Is produced by the `BLUEPRINT` phase. It is the direct input for the `CONSTRUCT` phase, where its `tasks` are executed.

*   **Consequences:**
    *   **Pros:**
        *   Creates a highly structured and organized project management system.
        *   Enforces strategic alignment for all tactical work.
        *   Provides appropriate levels of abstraction for different agents or human roles.
        *   The structured artifacts at each level serve as durable, long-term memory for the project.
    *   **Cons:**
        *   Introduces overhead; creating all these planning artifacts for a very trivial one-off task might feel heavyweight. (This can be mitigated by having a `GENERIC_TASK_LIST` `Execution Plan` type for simple initiatives).
        *   Requires a sophisticated "Supervisor Agent" to manage the transitions and relationships between these planning layers.

*   **Alternatives Considered:**
    *   **Flat Task List:** A single global list of tasks or issues. Rejected because it lacks strategic context, makes prioritization difficult for large projects, and offers poor traceability for the "why" behind a task.
    *   **Two-Tiered (Plan -> Tasks):** A simpler model with just plans and tasks. Rejected because it merges strategic ("what is the overall goal of this 6-month project?") and tactical ("what specific files do I change today?") planning into a single artifact, which becomes unwieldy and lacks the phased lifecycle management provided by the `Initiative Plan` layer.