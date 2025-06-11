# ADR-OS-005: Directory Structure & File Naming Conventions

*   **Status:** Accepted (was Proposed)
*   **Date:** 2025-06-07
*   **Context:**
    A predictable and well-organized file system structure is essential for the Hybrid_AI_OS and any human collaborators. The OS needs a reliable way to locate its operational files, user-provided materials, and the project workspace. Hardcoding paths would make the system brittle and difficult to adapt or package as a distributable tool.

*   **Decision:**
    We will adopt a **configuration-driven directory structure**. All key paths required for OS operation will be defined in a central project configuration file named **`haios.config.json`**, located at the project root.

    The OS, upon initialization in a project, **MUST** read this `haios.config.json` file to determine the paths for its operational root, the project workspace, templates, and other key locations. A standardized default directory structure will be provided as a "best practice" scaffold, but the config file is the single source of truth for paths.

    Furthermore, all key OS Control File artifacts will continue to follow a strict naming convention that incorporates their type and creation `g` value for uniqueness and chronological context.

*   **Rationale:**
    *   **Flexibility & Configurability:** Defining paths in a config file makes the OS adaptable to different project layouts or user preferences. It is a core principle for creating a distributable "Agent Development Kit (ADK)".
    *   **Explicitness:** `haios.config.json` makes the entire directory layout explicit and self-documenting. There is no "magic" in where the OS looks for its files.
    *   **Separation of Concerns:** The structure cleanly separates the OS's internal data (defined by `paths.os_root`), the project being built (defined by `paths.project_workspace`), and the materials used for building (defined by `paths.project_templates` and `paths.initial_source_materials`).
    *   **Containment & Scalability:** The `os_root/initiatives/initiative_<g>/` structure (whose parent `initiatives` path is defined in the config) remains the mechanism for containing all operational artifacts for a specific strategic initiative.

*   **`haios.config.json` and Default Directory Structure Specification:**

    The OS will expect a `haios.config.json` file at the project root. A default project scaffold will generate this file and the corresponding directories:

    **Default `haios.config.json` `paths` object:**
    ```json
    "paths": {
      "os_root": "./os_root",
      "project_workspace": "./project_workspace",
      "project_templates": "./project_templates",
      "initial_source_materials": "./initial_source_materials",
      "scaffold_definitions": "./os_root/scaffold_definitions"
    }
    ```

    **Default Directory Layout corresponding to the config:**
    ```
    [PROJECT_NAME]/
    ├── haios.config.json
    ├── os_root/
    │   ├── state.txt
    │   ├── global_issues_summary.txt
    │   ├── global_registry_map.txt
    │   ├── ... (other global files & dirs)
    │   └── initiatives/
    │       └── initiative_<g_init>/
    │           └── ...
    ├── project_workspace/
    ├── project_templates/
    └── initial_source_materials/
    ```

*   **File Naming Conventions (Unchanged):**

    The decision to use `g`-based, unique, and descriptive filenames for OS Control Files and OS-generated artifacts remains unchanged.
    *   `request_<g>.txt`, `init_plan_<g>.txt`, `exec_plan_<g>.txt`, `issue_<g>.txt`
    *   `analysis_report_..._g<report_g>.md`, `validation_report_..._g<report_g>.md`
    *   `Scaffold Definition` definitions will use semantic names (e.g., `react_module_v1.json`).

*   **Consequences:**
    *   **Pros:**
        *   System is no longer tied to hardcoded paths, making it more robust and portable.
        *   Provides a single, clear configuration entry point for a project.
        *   Aligns with standard practices for modern development tooling.
    *   **Cons:**
        *   Adds one level of indirection: the OS must always read the config file first to know where to operate. This is a negligible and worthwhile trade-off.
        *   A missing or malformed `haios.config.json` is now a fatal startup error for the OS.

*   **Alternatives Considered:**
    *   **Hardcoded Paths:** The previous approach. Rejected as too rigid and less aligned with a distributable package model.
    *   **Environment Variables for Paths:** Using environment variables to define paths. Rejected as it makes project configuration less portable and self-contained compared to a config file within the project directory itself.