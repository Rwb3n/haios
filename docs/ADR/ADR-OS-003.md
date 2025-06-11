# ADR-OS-003: Artifact Annotation Strategy (`EmbeddedAnnotationBlock`)

*   **Status:** Proposed
*   **Date:** 2025-06-06
*   **Context:**
    For an autonomous agent system to effectively manage, understand, and modify a codebase over time, it cannot rely solely on reading the primary content of files. 
    It requires rich, structured metadata about each artifact's purpose, history, dependencies, quality, and relationship to the overall project. This metadata needs to be durable, version-controlled, and live alongside the artifact it describes, avoiding reliance on external databases or transient agent memory.

*   **Decision:**
    We will mandate the use of a comprehensive **`EmbeddedAnnotationBlock`** for all text-editable Project Artifacts managed by the OS (e.g., source code, documentation, reports, configuration files). This block will be a structured JSON object containing all critical metadata for the artifact.

    The embedding method will be determined by the host file type:
    1.  **For non-JSON-root files** (e.g., `.ts`, `.py`, `.md`, `.css`): The JSON object will be placed within a dedicated comment block at the top of the file, delineated by `/* ANNOTATION_BLOCK_START` and `ANNOTATION_BLOCK_END */`.
    2.  **For JSON-root files** (e.g., `package.json`, `.eslintrc.json`): The JSON object will be embedded as a single top-level key named `_annotationBlock`.

*   **Rationale:**
    *   **Durable Context:** Embedding metadata directly within the artifact ensures that context is never lost. When an agent (or human) opens a file, all information about its purpose, history, and dependencies is immediately available, reducing reliance on external lookups or limited context windows.
    *   **Single Source of Truth:** The annotation block serves as the authoritative source for an artifact's metadata. The `global_registry_map.txt` may mirror some of this data for quick lookups, but the annotation block is the ground truth.
    *   **Version Control Synergy:** Since the annotation is part of the file, any changes to it are tracked naturally by the version control system (e.g., Git), providing a history of metadata changes alongside content changes.
    *   **Supports Agent Specialization:** Different agents can use different parts of the annotation. A Testing Agent uses `quality_notes` and `test_plan_notes_from_scaffold`. A Refactoring Agent uses `internal_dependencies` and `dependents`. A Planning Agent uses `purpose_statement`.
    *   **Enables Constraint Enforcement:** Critical project constraints and decisions (e.g., "use shadcn/ui") can be embedded as `requisites` and locked, providing persistent guidance for all agents interacting with the file.

*   **Core Information Categories within the `EmbeddedAnnotationBlock`:**

    The `EmbeddedAnnotationBlock` will be a rich structure (defined in detail in Document 2: Data Schemas) containing, but not limited to, the following key categories:

    1.  **Identity & Provenance:** `artifact_id`, `version_tag`, various `g_*` event markers for creation/modification, `authors_and_contributors`.
    2.  **Purpose & Description:** `description`, `artifact_type`, `status_in_lifecycle`, `purpose_statement`.
    3.  **Dependencies & Relationships:** `internal_dependencies` (other project artifacts), `dependents` (who uses this artifact), `external_dependencies` (npm packages, etc.), `linked_issue_ids`.
    4.  **Scaffolding Origin:** A `scaffold_info` object detailing the `Scaffold Definition` used, the `g` of scaffolding, and the status of all `placeholders`.
    5.  **Quality & Testing:**
        *   A `quality_notes` object with granular status fields for various test types (unit, integration, static analysis, etc.) and a manual review log.
        *   A `test_plan_notes_from_scaffold` array that carries forward testing considerations defined during scaffolding and tracks their implementation and execution status.
    6.  **Constraints & Assumptions:** A `requisites_and_assumptions` array to document hard constraints (e.g., technology choices), which can be locked.
    7.  **Locking Mechanism:** A system of `_locked*` flags will be used within the annotation structure to mark specific metadata fields or entries as immutable by AI agents without explicit override, ensuring adherence to critical decisions.

*   **Consequences:**
    *   **Pros:**
        *   Creates self-describing, intelligent artifacts.
        *   Massively improves traceability and context durability.
        *   Provides a robust mechanism for enforcing architectural and design constraints.
        *   Reduces the cognitive load on agents, as critical information is always co-located with the artifact.
    *   **Cons:**
        *   Increases file size and adds a "non-functional" block to source files.
        *   Requires disciplined agents that consistently and correctly update the annotation block whenever they modify an artifact. The `VALIDATE` phase is critical for enforcing this discipline.
        *   Parsing this block from every file can introduce a small performance overhead compared to a centralized database (a trade-off made for durability and simplicity).

*   **Alternatives Considered:**
    *   **Centralized Metadata Database:** Storing all artifact metadata in an external database. Rejected due to the risk of desynchronization between the database and the actual files in version control. It also makes the system more complex, requiring a database management layer.
    *   **Sidecar Metadata Files:** Storing metadata in a companion file (e.g., `Button.tsx.meta.json`). Rejected because it doubles the number of files to manage and increases the risk of the metadata file being moved, renamed, or deleted separately from its source artifact. Embedding is more robust.