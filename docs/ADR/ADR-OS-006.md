# ADR-OS-006: Scaffolding Process & `Scaffold Definition` Usage

*   **Status:** Proposed
*   **Date:** 2024-06-06
*   **Context:**
    To ensure consistency, reduce boilerplate, and accelerate the setup of new projects or components, a standardized and automated scaffolding process is required. 
    This process must create not only the file and directory structure but also embed foundational metadata (`EmbeddedAnnotationBlock`), content placeholders, and initial testing considerations directly into the newly created artifacts. 
    This provides durable context for all subsequent development work.

*   **Decision:**
    We will adopt a two-part scaffolding system:

    1.  **`Scaffold Definition` Definitions:** Un-annotated JSON files (located in `os_root/scaffold_definitions/` with semantic names like `react_module_v1.json`) will serve as the master instructions for scaffolding. These schemas define directory structures, file creation instructions, references to boilerplate source files, placeholder definitions, initial annotation hints, and test considerations.
    2.  **Boilerplate Template Assets:** Reusable source files (e.g., `.tsx.template`, `tsconfig.json.template`) will be stored in the `project_templates/` directory. The `Scaffold Definition` definitions will reference these assets.

    The OS will execute scaffolding via a dedicated **`SCAFFOLDING` type `Execution Plan`**. This plan's tasks will be blueprinted based on a `Scaffold Definition` and initiative-specific `customization_parameters` defined in the `Initiative Plan`.

*   **Rationale:**
    *   **Consistency & Best Practices:** Ensures all new components or projects start from a pre-defined, best-practice structure, preventing inconsistencies.
    *   **Durable Context from Inception:** By creating files with fully populated `EmbeddedAnnotationBlock`s (including `scaffold_info` and `test_plan_notes_from_scaffold`) from the very beginning, we establish a rich, durable context that persists throughout the artifact's lifecycle, reducing AI "drift" or "forgetting."
    *   **Separation of Instruction and Content:** Separating the `Scaffold Definition` (the "how-to" instructions) from the `project_templates/` (the "what-to-use" boilerplate content) makes both easier to manage, version, and reuse.
    *   **Dynamic Customization:** The use of `customization_parameters` in the `Initiative Plan` allows a generic `Scaffold Definition` to be adapted for specific contexts (e.g., different module or entity names) without altering the master template, making the system flexible.
    *   **Structured Process:** Using a dedicated `SCAFFOLDING` Execution Plan makes the entire scaffolding process traceable, verifiable, and manageable like any other unit of work in the system.

*   **Scaffolding Workflow:**

    1.  **Directive:** An `Initiative Plan`'s lifecycle stage specifies `expected_exec_plan_types: ["SCAFFOLDING"]` and provides `scaffolding_directives` (including the `master_scaffold_schema_id_ref` and any `customization_parameters`).
    2.  **`BLUEPRINT` Phase:** The OS generates a new `Execution Plan` of `plan_type: "SCAFFOLDING"`. The tasks in this plan are derived from the `Scaffold Definition`'s `directories` and `files` arrays, adapted with the initiative's `customization_parameters`. The plan will include tasks for directory creation, file creation (from templates), and a final task for verifying inter-artifact linking.
    3.  **`CONSTRUCT` Phase:** The OS executes the `SCAFFOLDING` plan. For each file creation task:
        a.  The corresponding template file from `project_templates/` is read.
        b.  Any defined `template_processing_instructions` (e.g., JSON merges, placeholder replacements) are applied.
        c.  The resulting content (including placeholder markers like `// <<PLACEHOLDER_ID: Description>>` in the body) is written to the target path in `project_workspace/`.
        d.  A complete `EmbeddedAnnotationBlock` is generated and injected into the new file's designated annotation area. This block is populated using hints and definitions from the `Scaffold Definition`.
        e.  The new artifact is registered in `global_registry_map.txt`.
    4.  **Final Linking Task:** The last task in the `SCAFFOLDING` plan iterates over the newly created artifacts to ensure their `dependents` fields are correctly populated, establishing bi-directional linkage.

*   **Consequences:**
    *   **Pros:**
        *   Highly automated and reliable project/component bootstrapping.
        *   Creates "intelligent" artifacts from day one.
        *   Enforces project structure and coding conventions from the start.
        *   The process is fully auditable via the `SCAFFOLDING` Execution Plan.
    *   **Cons:**
        *   Requires well-structured `Scaffold Definition` definitions and `project_templates/`, which represents an upfront investment.
        *   The logic for the AI to correctly interpret and execute `template_processing_instructions` can be complex.

*   **Alternatives Considered:**
    *   **Manual Scaffolding:** Relying on a human to set up all initial files. Rejected as it is slow, error-prone, and fails to establish the initial `EmbeddedAnnotationBlock` metadata required for autonomous operation.
    *   **Simple File Copy:** A simpler mechanism that just copies files without annotation or placeholder processing. Rejected because it misses the primary benefit of creating intelligent, context-aware artifacts from inception.