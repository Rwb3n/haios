# II. DATA ECOSYSTEM OVERVIEW

The Hybrid_AI_OS operates on a well-defined ecosystem of structured data files. These files are the durable memory, plans, and state of the system. They are separated into three distinct categories: **OS Control Files**, **Project Artifacts**, and **Definition & Template Files**.

All key directory paths are defined in the project's central **`haios.config.json`** file (ADR-005), making the structure configurable. The default paths are referenced below.

For the complete, normative JSON schemas for each file type, refer to **Document 2: Hybrid AI OS - Data Schemas**.

## A. OS Control Files

These files are the internal "nervous system" of the OS, located within the `os_root/` directory structure. They are typically JSON-formatted, stored with a `.txt` extension, and follow the modular header/payload format.

#### Core State & Configuration
*   **`state.txt`**: The central, ephemeral state of the OS, tracking the current phase, status, and active plan/task. Includes the global event counter `g` (ADR-004).
*   **`haios.config.json`**: The foundational, user-provided static configuration file for the OS instance, defining paths, project-wide constants, and core constraints.

#### Planning & Execution Hierarchy (ADR-002)
*   **`request_<g>.txt`**: An individual, atomic directive that triggers new work.
*   **`init_plan_<g>.txt`**: The high-level, strategic plan for a major work initiative.
*   **`exec_plan_<g>.txt`**: A detailed, typed, tactical plan containing the specific tasks to be executed by agents.

#### Registries & Summaries
*   **`global_registry_map.txt`**: The global index of all Project Artifacts, their locations, and history.
*   **`agent_registry.txt`** & **`agents/persona_*.txt`**: The dynamic registry and detailed "cards" for all available AI agent personas (ADR-012).
*   **`issue_<g>.txt`**, **`initiative_issues_summary_<g_init>.txt`**, & **`global_issues_summary.txt`**: The three-tiered system for tracking individual issues and their aggregated statuses (ADR-009).

#### Queues & State Capture
*   **`human_attention_queue.txt`**: An explicit queue of items requiring human review or intervention.
*   **`snapshot_<g>.json`**: A point-in-time JSON bundle that captures the current versions of key OS Control Files (e.g., `state.txt`, active plans) to provide immutable restore points.

#### Supplementary Logs (Future Use)
*   This category includes potential future log files for highly verbose tracking, such as `task_retry_log_<task_id>.txt` for tasks with excessive retries.

## B. Project Artifacts

These are the tangible outputs of the project work, residing in the `project_workspace/`. All text-editable artifacts managed by the OS **MUST** contain an `EmbeddedAnnotationBlock` (ADR-003).

*   **Core Project Outputs:** Source Code (`.ts`, `.py`), Configuration Files (`package.json`), and User-Facing Documentation (`README.md`).
*   **OS-Generated Reports & Evidence (ADR-008):**
    *   **`Analysis Report` (.md):** The documented output of the `ANALYZE` phase.
    *   **`Validation Report` (.md):** The documented output of the `VALIDATE` phase.
    *   **`Progress Review` (.md):** A higher-level synthesis of project progress.
    *   **`Test Results` (.json, etc.):** The raw, machine-readable evidence from test execution (ADR-007).
    *   **`Readiness Assessment` (.md):** An optional report from a pre-execution readiness check (ADR-013), typically stored alongside its originating `exec_plan_<g>.txt`.
*   **Governance & Guideline Artifacts:**
    *   **`Guideline Artifacts` (.md):** A collection of documents (e.g., `testing_guidelines.md`) defining project-wide standards (ADR-014). The default path is `project_workspace/docs/guidelines/`, but this is configurable.
    *   **`Architecture Decision Records (ADRs)` (.md):** Formal documentation of key architectural decisions.
    *   **(Future Use) `license_manifest.json` / `data_classification.md`**: Placeholders for future security and data governance specifications.

## C. Definition & Template Files

These are user-provided files that act as inputs or templates for OS processes.

*   **`Scaffold Definition` (.json) (ADR-006):**
    *   **Location:** `os_root/scaffold_definitions/`
    *   **Purpose:** Provides the set of instructions for the `SCAFFOLDING` process.
*   **`Template Files` (various extensions):**
    *   **Location:** `project_templates/`
    *   **Purpose:** Raw boilerplate content (source code, configs) referenced by `Scaffold Definitions`.

All artifacts are uniquely identifiable via their `artifact_id`, versioned, and have their lifecycle tracked in the `global_registry_map.txt`. The strict, verbose, and schema-compliant nature of these artifacts is the bedrock of the OS's traceability and automation capabilities.

### C. Distributed Systems Compliance

To ensure robustness in modern, potentially distributed environments, all OS Control Files and the operations upon them MUST adhere to the following cross-cutting principles, which are formally defined in ADRs 023 through 029:

*   **Observability:** All significant state changes are accompanied by a `trace_id` to allow for end-to-end debugging and performance monitoring.
*   **Idempotency:** Operations that mutate state are designed to be safely retried, often through the use of an `idempotency_key`.
*   **Event Ordering:** The global counter `g` provides a total order of events, supplemented by vector clocks where necessary for distributed causality.
*   **Security:** A Zero-Trust model is enforced via agent archetypes and access control policies defined within the schemas.
*   **Consistency & Partition Tolerance:** Schemas for stateful components include fields like `consistency_mode` and `partition_status` to explicitly manage behavior during network partitions or asynchronous operations.