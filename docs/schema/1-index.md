# Hybrid_AI_OS - Data Schema Documentation (v5.1)

## 1. Introduction

This documentation provides the definitive specification for all data structures used by the Hybrid_AI_OS. These schemas serve as the "data contracts" that all OS agents and processes must strictly adhere to.

The schemas are divided into three main categories:
- **OS Control Files:** JSON structures, stored in `.txt` files, that manage the OS's state, plans, and tracking.

- **Project Artifacts:** Files that constitute the actual project output (e.g., source code, reports). This section details the schema for the `EmbeddedAnnotationBlock` found within them.

- **Schema/Definition Files:** JSON files that provide templates and definitions used by the OS, such as `Scaffold Definitions`.

A key architectural principle is the use of a **Modular Header Block** for OS Control Files and `EmbeddedAnnotationBlock`s to ensure consistency and explicit schema versioning. Additionally, a **Constraint Locking Mechanism** (`_locked*` flags) is defined within the schemas to allow for the protection of critical, immutable data from unintended modification by AI agents.

## 2. OS Control Files

These files constitute the internal state and operational plans of the OS. They all follow a standard structure containing an `os_file_header` and a `payload`.

*   [**`state.txt`**](./state_schema.md) - The global state of the OS, including the master event counter (`g`).
*   [**`request_<g>.txt`**](./request_schema.md) - An individual directive from a user or another agent that initiates work.
*   [**`request_summary.txt`**](./request_summary_schema.md) - A global summary and index of all `Request` files.
*   [**`init_plan_<g>.txt`**](./init_plan_schema.md) - The high-level, strategic plan for a major initiative.
*   [**`exec_plan_<g>.txt`**](./exec_plan_schema.md) - The detailed, tactical plan for a specific stage of an initiative.
*   [**`issue_<g>.txt`**](./issue_schema.md) - A detailed report of a single issue (bug, enhancement, etc.).
*   [**`initiative_issues_summary_<g>.txt`**](./initiative_issues_summary_schema.md) - A summary of all issues related to a single initiative.
*   [**`global_issues_summary.txt`**](./global_issues_summary_schema.md) - A global index of all issue summaries.
*   [**`global_registry_map.txt`**](./global_registry_map_schema.md) - The global index of all Project Artifacts, their locations, and history.
*   [**`global_project_summary.txt`**](./global_project_summary_schema.md) - A high-level, mutable summary of the overall project's status.
*   [**`snapshot_<g>.json`**](./snapshot_schema.md) - A point-in-time capture of key OS state data.
*   [**`haios.config.json`**](./haios_config_schema.md) - The central, project-wide configuration file for the OS instance.

## 3. Project Artifact Metadata

This section defines the schemas for metadata embedded within the project files built by the OS.

*   [**`EmbeddedAnnotationBlock`**](./embedded_annotation_block_schema.md) - The comprehensive JSON metadata block embedded in all OS-managed text-editable Project Artifacts. This is the primary mechanism for durable context, dependency tracking, and quality assurance.
*   [**OS-Generated Reports (Markdown)**](./os_generated_reports_schema.md) - Describes the structured outlines and `EmbeddedAnnotationBlock` usage for AI-generated artifacts like `Analysis Reports`, `Validation Reports`, and `Progress Reviews`.
*   [**`Test Results` Artifacts**](./test_results_artifact_schema.md) - Describes the structure and annotation for artifacts that store the output of test executions.

## 4. Schema/Definition Files

This section defines the schemas for files that are used as *input definitions* for the OS.

*   [**`Scaffold Definition` Definition**](./scaffold_schema_definition.md) - The schema for `.json` files that define how to scaffold new project components, referencing boilerplate from `project_templates/`.