# ADR-OS-012: Dynamic Agent Management

*   **Status:** Proposed
*   **Date:** 2024-05-31 (g value of this session)
*   **Context:**
    For the Hybrid_AI_OS to evolve into a truly autonomous and adaptable system, especially one supporting multiple specialized AI agents ("vessels"), the management of these agents cannot be a static, hardcoded configuration. The system requires a dynamic way to register, configure, and monitor the agent personas available for executing tasks. This mechanism needs to be robust, transparent, and controllable via OS-level operations, aligning with the potential for a "cockpit" UI for human supervision.

*   **Decision:**
    We will implement a dynamic, file-based agent management system using the established **"Index + Individual File"** pattern. This system will consist of two new types of OS Control Files:

    1.  **`os_root/agent_registry.txt` (The Index):** A single, top-level file that serves as an index of all known and available agent personas. It will map `persona_id`s to the file path of their detailed "Agent Card" and mirror key status information for quick lookups.
    2.  **`os_root/agents/persona_<id>.txt` (The Agent Card):** Individual, detailed files for each agent persona. Each "Agent Card" will contain the complete configuration for that role, including its capabilities, currently assigned AI model, model-specific parameters, operational status, and a history log.

    Adding, removing, or modifying an agent persona will be an OS-level action (triggered by a `Request`), which modifies the relevant `Agent Card` file and updates the `agent_registry.txt` index. This functionality will be managed by a high-level "Supervisor" or "Manager" agent persona.

*   **Rationale:**
    *   **Scalability & Performance:** Separating the index from the detailed cards ensures that the main registry file remains small and fast to parse for the OS or a UI, even if there are many agents with detailed configurations and long histories.
    *   **Dynamic & Controllable:** This approach treats the agent roster as part of the OS's dynamic state, not a static project configuration. It allows for adding, disabling, or reconfiguring agents at runtime through formal OS `Requests`, which is essential for a long-running, autonomous system.
    *   **Consistency with OS Design Patterns:** This solution reuses the successful "Index + Individual File" pattern already established for `Requests` and `Issues`, leading to a more coherent and predictable overall OS architecture.
    *   **Rich, Granular Configuration:** The individual `Agent Card` file provides a dedicated, structured place for rich details about each persona, including model parameters, capabilities mapping to `plan_type`s, and operational history, without cluttering a single monolithic file.
    *   **Supports UI "Cockpit":** This structure is ideal for powering a UI. The registry populates a list of agent "cards," and clicking a card loads the detailed information from its specific file.

*   **Workflow Integration:**

    1.  **Orchestration:** When the OS needs to assign a task from an `Execution Plan`, the orchestrating agent (e.g., Supervisor) will consult the `agent_registry.txt` to find an available agent with the required capability (matching the task's `assigned_agent_persona`).
    2.  **Configuration Loading:** The orchestrator will then load the detailed `Agent Card` (`persona_*.txt`) for the chosen persona to retrieve its specific `model_configuration` (model ID, parameters) to use when invoking that agent "vessel."
    3.  **Updating:** Actions like swapping an agent's model or disabling it are handled via a `Request` that triggers an OS action to update the `Agent Card` file and the `agent_registry.txt` index.

*   **Consequences:**
    *   **Pros:**
        *   Provides a flexible and scalable system for managing a fleet of diverse AI agents.
        *   Enables runtime configuration of agents without restarting the OS or manually editing project configuration files.
        *   Keeps the core `haios.config.json` clean and focused on static, foundational project settings.
        *   Creates a clear, auditable trail for changes to agent configurations via updates to these OS Control Files.
    *   **Cons:**
        *   Introduces two new OS Control File schemas that need to be defined and managed.
        *   Requires the OS to have a privileged "manager" capability to modify the agent registry and cards.

*   **Alternatives Considered:**
    *   **Static Configuration (`haios.config.json`):** Placing the agent roster in the main config file. Rejected as too rigid, not suitable for dynamic runtime changes, and less scalable for detailed agent configurations.
    *   **Single Monolithic Registry File:** A single file containing all details for all agents. Rejected because it could become very large and unwieldy to parse and update, violating the principle of isolating detailed records.