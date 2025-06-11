# ADR-OS-017: Phase 1 - MVP Engine & Tooling

*   **Status:** Proposed
*   **Date:** 2024-05-31 (g value of this session)
*   **Context:**
    The architectural foundation of the Hybrid AI Operating System (HAiOS) is now fully specified across a comprehensive set of ADRs (001-016) and supporting documentation. The next logical step is to transition from architectural definition to implementation. A minimal, viable implementation is required to validate the core concepts in practice and provide a foundational toolset for both human operators and future agent development.

*   **Decision:**
    We will formally initiate **Phase 1: Core OS Engine & Tooling**. The singular goal of this phase is to build the **Minimum Viable Product (MVP)** of the HAiOS orchestrator.

    This MVP will be a command-line executable (the "engine") capable of performing a single, complete, end-to-end `SCAFFOLDING` Execution Plan. It must be able to read and write all necessary OS Control Files according to their ratified schemas, demonstrating the core operational loop in its simplest form.

*   **Rationale:**
    *   **De-risking Core Concepts:** An end-to-end "thin slice" through the system will prove that the core architectural concepts (modular headers, file-based state, plan execution, status tracking) are sound and practical to implement.
    *   **Delivering Immediate Utility:** Even a simple scaffolding engine provides immediate value by automating project setup, enforcing best practices from day one, and creating the structured environment required for subsequent agent-driven development.
    *   **Foundation for Agent Integration:** This MVP engine will serve as the stable foundation upon which Phase 2 (Agent Integration) will be built. The interfaces for reading plans and writing status will be established.
    *   **Focus on the "Happy Path":** This phase intentionally focuses on the successful execution of a straightforward plan, deferring complex error handling, advanced agent orchestration, and UI development to later phases.

*   **Scope & Key Deliverables:**

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

*   **Exclusions (Out of Scope for Phase 1):**
    *   Integration with actual LLM-based AI agents. The MVP engine will be a deterministic script runner that *simulates* an agent's actions.
    *   The full `ANALYZE` or `BLUEPRINT` phases. The `init_plan` and `exec_plan` files for the MVP test case will be created manually.
    *   The full `VALIDATE` phase. The MVP will stop after `CONSTRUCT`.
    *   Advanced error handling, remediation planning, and critique loops.
    *   The "Cockpit" UI.

*   **Success Criteria ("Definition of Done" for Phase 1):**
    *   The OS engine executable can be successfully run against a project initialized with our standard directory scaffold.
    *   Given a manually created `SCAFFOLDING` `Execution Plan`, the engine correctly creates all specified directories and files in the `project_workspace`.
    *   All newly created artifacts contain a valid, fully populated `EmbeddedAnnotationBlock`.
    *   `global_registry_map.txt` and `exec_status_*.txt` are accurately created and updated.
    *   The final `state.txt` correctly reflects the completion of the process.

*   **Consequences:**
    *   This provides a tangible, testable product at the end of the phase.
    *   It creates the core modules (ConfigLoader, StateManager, TaskRunner) that will be the building blocks for the more complex, agent-driven system in Phase 2.
    *   It forces us to confront any practical implementation challenges with our file-based approach early on.