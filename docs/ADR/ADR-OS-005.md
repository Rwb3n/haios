# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_005_md",
        "g_annotation_created": 10,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 10, "identifier": "Hybrid_AI_OS" },
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

# ADR-OS-005: Directory Structure & File Naming Conventions

* **Status**: Accepted
* **Date**: 2025-06-07
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

A predictable and well-organized file system structure is essential for the Hybrid_AI_OS and any human collaborators. The OS needs a reliable way to locate its operational files, user-provided materials, and the project workspace. Hardcoding paths would make the system brittle and difficult to adapt or package as a distributable tool.

## Assumptions

* [ ] A `haios.config.json` file will always be present at the project root where the OS is initialized.
* [ ] The OS has read permissions for the `haios.config.json` file at startup.
* [ ] The paths defined within `haios.config.json` are valid and accessible to the OS.
* [ ] The file system supports the directory structure and naming conventions defined in the config.
* [ ] The OS can detect and handle missing or malformed config files gracefully.
* [ ] The configuration-driven approach is compatible with distributed and multi-agent deployments.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** Directory structure uses simple, predictable naming conventions with clear separation of concerns (os_root, project_workspace, etc.).
- **Self-Critique:** Configuration-driven approach adds startup complexity requiring config file parsing before any operations.

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Single configuration file eliminates hardcoded path duplication throughout the system; all paths defined once in haios.config.json.
- **Self-Critique:** Reliance on single config file might be less suitable for highly complex, multi-repository projects.

### Separation of Concerns v1.0
- **Compliance Proof:** Clean separation between OS internal data (os_root), project being built (project_workspace), and build materials (templates, source materials).
- **Self-Critique:** Users might misconfigure paths, leading to unexpected behavior and concern boundary violations.

### Configuration-Driven Design v1.0
- **Compliance Proof:** All operational paths defined in central haios.config.json file, making system adaptable and portable.
- **Self-Critique:** Corrupted or invalid config file becomes single point of failure for OS initialization.

### Explicit Diagramming v1.0
- **Compliance Proof:** Directory structure diagram is provided showing default layout and path relationships.
- **Self-Critique:** **PARTIAL COMPLIANCE:** Diagram is textual; visual directory tree diagram would improve clarity.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation about config file presence, permissions, and path validity.
- **Self-Critique:** Only three assumptions listed; directory structure likely has more implicit assumptions about file system capabilities.

### Portability v1.0
- **Compliance Proof:** Configuration-driven approach eliminates hardcoded paths, making system distributable and adaptable to different environments.
- **Self-Critique:** Environment variables approach rejected in favor of self-contained config file for better portability.

## Decision

**Decision:**

> We will adopt a **configuration-driven directory structure**. All key paths required for OS operation will be defined in a central project configuration file named **`haios.config.json`**, located at the project root. The OS **MUST** read this file on initialization to determine all operational paths. The OS Control Files will maintain their `g`-based naming convention.

**Confidence:** High

## Rationale

1. **Flexibility & Configurability**
   * Self-critique: Increased startup complexity as the OS must first parse the config file before it can access any other file.
   * Confidence: High
2. **Explicitness**
   * Self-critique: A corrupted or invalid `haios.config.json` becomes a single point of failure for OS initialization.
   * Confidence: High
3. **Separation of Concerns**
   * Self-critique: Users might misconfigure paths, leading to unexpected behavior.
   * Confidence: Medium
4. **Containment & Scalability**
   * Self-critique: The reliance on a single config file might be less suitable for highly complex, multi-repository projects in the future.
   * Confidence: Medium

## Alternatives Considered

1. **Hardcoded Paths**: The previous approach. Rejected as too rigid and not suitable for a distributable tool.
   * Confidence: High
2. **Environment Variables for Paths**: Rejected as it makes project configuration less portable and self-contained compared to a config file committed to the project repository.
   * Confidence: High

## Consequences

* **Positive:** System is no longer tied to hardcoded paths, making it robust and portable. Provides a single, clear configuration entry point. Aligns with standard practices for modern development tooling.
* **Negative:** A missing or malformed `haios.config.json` is a fatal startup error. Adds a minor, but acceptable, level of indirection to all file access.

## Clarifying Questions

* What is the defined validation schema for `haios.config.json`, and how is it versioned and evolved?
* How does the OS behave if a configured path points to a non-existent or inaccessible directory, and what are the recovery or notification mechanisms?
* How will this configuration approach be extended to support multi-agent, distributed, or multi-repository deployments?
* What is the migration or upgrade process if the directory structure or config schema changes in future versions?
* How are configuration errors, overrides, and environment-specific customizations tracked and audited?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*

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
     haios.config.json
     os_root/
        state.txt
        global_issues_summary.txt
        global_registry_map.txt
        ... (other global files & dirs)
        initiatives/
            initiative_<g_init>/
                ...
     project_workspace/
     project_templates/
     initial_source_materials/
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
