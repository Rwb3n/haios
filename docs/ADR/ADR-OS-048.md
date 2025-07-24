ADR-OS-048: The Configurable Persona System
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Supersedes: ADR-OS-030: Archetypal Agent Roles and Protocols
Context: Based on the analysis of the Roo Code system from the Task Master repository, this ADR refactors our agent management from a hardcoded set of archetypes to a flexible, file-based persona configuration system.
1. Context
The original ADR-OS-030 defined a small, fixed set of agent "archetypes" (Supervisor, Builder, etc.). While this provided initial structure, it is too rigid for a mature, multi-agent system. This static approach suffers from several flaws:
Inflexibility: Creating a new, specialized agent role (e.g., a "Security Auditor" or a "Database Refactoring Specialist") would require a formal ADR to amend the core canon.
Implicit Behavior: The specific goals, constraints, and behaviors of each archetype were defined in narrative text within the ADR, which is not easily machine-readable or verifiable.
Poor Maintainability: Modifying an agent's core prompt or ruleset was a manual, error-prone process.
The Task Master project demonstrated a superior pattern: treating Agent Personas as first-class Configuration Artifacts. This ADR adopts that pattern, transforming our agent management into a dynamic, transparent, and governable system.
2. Models & Frameworks Applied
Specification-Driven Development (SDD Framework): This is a Foundation Layer architecture. It defines the system for creating the "minds" of the Implementation Layer agents. The persona files themselves are Bridge Layer specifications.
Infrastructure as Code (IaC): Agent personas are no longer abstract concepts; they are version-controlled, auditable files in the repository.
Principle of Least Privilege: The new tool_access_policy schema allows us to define fine-grained permissions for each persona, a critical security enhancement.
3. Decision
We will deprecate the static "Archetype" system of ADR-OS-030 and adopt a new, file-based Configurable Persona System.
The New Persona Directory Structure
All persona definitions will now live in a new canonical directory: os_root/personas/. Each persona is defined by its own subdirectory.
Generated code
os_root/
└── personas/
    ├── planner/
    │   ├── persona.json
    │   ├── system_prompt.md
    │   └── rules/
    │       └── always_use_ooda.md
    │
    ├── builder_python/
    │   ├── persona.json
    │   ├── system_prompt.md
    │   └── rules/
    │       └── follow_pep8.md
    │
    └── validator_testing/
        ├── persona.json
        ├── system_prompt.md
        └── rules/
            └── check_test_coverage.md```

#### **The Persona Artifacts**

1.  **`persona.json` (The "ID Card"):**
    *   **Purpose:** A machine-readable file defining the persona's identity and permissions.
    *   **Schema:**
        ```json
        {
          "persona_id": "planner-v1",
          "name": "Planner Agent",
          "description": "Orchestrates development by creating plans and tasks.",
          "version": "1.0.0",
          "tool_access_policy": {
            "allow": ["Read", "Write", "LS", "Glob", "Task"],
            "deny": ["Bash"]
          }
        }
        ```

2.  **`system_prompt.md` (The "Soul"):**
    *   **Purpose:** The core system prompt that defines the persona's goals, mindset, constraints, and operational protocols.
    *   **Content:** This file will contain the detailed, high-quality prompts we have been developing (e.g., `role_planner.md`). It can use a templating syntax to import rules.
    *   **Example (`system_prompt.md` for the Planner):**
        ```markdown
        You are the Planner Agent for HAiOS.
        {{import:rules/always_use_ooda.md}}
        Your core responsibilities are...
        ```

3.  **`rules/` (The "Library of Maxims"):**
    *   **Purpose:** A directory of reusable, single-responsibility rule snippets in Markdown.
    *   **Example (`rules/always_use_ooda.md`):** `## MANDATORY OPERATIONAL PROCEDURES\n\nEVERY AGENT ACTION FOLLOWS THE OODA LOOP...`
    *   **Rationale:** This allows us to apply the DRY principle to our prompt engineering. Common constraints can be defined once and imported by multiple personas.

#### **Integration with the HAiOS**

*   **`Agent Card` Refactoring:** The `agent_card.json` schema (ADR-OS-012) is updated. The `archetype` field is replaced with `persona_id`, which must point to a valid persona directory in `os_root/personas/`.
*   **Orchestrator Refactoring:** The `Task Executor` and `2A Orchestrator` must now, before running an agent, load its `persona.json` and `system_prompt.md`.
    1.  It constructs the full system prompt by resolving any `{{import}}` statements.
    2.  It configures the `ClaudeCodeOptions` (or equivalent) with the loaded system prompt and the `allowed_tools` / `disallowed_tools` from the `tool_access_policy`.

## **4. Consequences**

*   **Positive:**
    *   **Extreme Flexibility:** We can now create, modify, and version new agent personas as easily as we edit text files, without changing core architectural code.
    *   **Explicit & Auditable Behavior:** An agent's entire "mind" is now stored in version-controlled artifacts, making its behavior transparent and auditable.
    *   **Enhanced Security:** The `tool_access_policy` provides a robust, per-persona mechanism for enforcing the Principle of Least Privilege.
    *   **Prompt Reusability (DRY):** The `rules/` directory allows us to build a library of proven prompt components, improving consistency and reducing duplication.
*   **Negative:**
    *   Requires a refactoring of our existing `Task Executor` and `Agent Card` systems.
    *   Introduces a new build step: the "prompt construction" phase where rule imports are resolved.