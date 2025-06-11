# Schema: `EmbeddedAnnotationBlock`

*   **ADR References:** ADR-003, ADR-007, ADR-010, ADR-012, ADR-013, ADR-014
*   **Location:** Embedded within all text-editable Project Artifacts managed by the OS.
*   **Purpose:** To provide a comprehensive, structured, and durable set of metadata co-located with the artifact it describes. It is the primary mechanism for durable context, dependency tracking, quality assurance, constraint enforcement, and traceability throughout the artifact's lifecycle.

---

## 1. Embedding Rules

*   **For non-JSON-root files** (e.g., `.ts`, `.md`): The JSON object MUST be placed within a comment block delineated by `/* ANNOTATION_BLOCK_START` and `ANNOTATION_BLOCK_END */`.
*   **For JSON-root files** (e.g., `package.json`): The JSON object MUST be embedded as a single top-level key named `_annotationBlock`.

---

## 2. Schema Structure

The `EmbeddedAnnotationBlock` is a JSON object with a modular header (`artifact_annotation_header`) and a `payload`.

```json
# Schema: `EmbeddedAnnotationBlock` (v5.2)

*   **ADR References:** ADR-003, ADR-007, ADR-010, ADR-012, ADR-013, ADR-014
*   **Location:** Embedded within all text-editable Project Artifacts managed by the OS.
*   **Purpose:** To provide a comprehensive, structured, and durable set of metadata co-located with the artifact it describes. It is the primary mechanism for durable context, dependency tracking, quality assurance, constraint enforcement, and traceability.

---

## 1. Embedding Rules

The embedding method is determined by the host file type to ensure syntactic validity.

*   **C-style/JavaScript-like (e.g., `.ts`, `.js`, `.css`, `.java`):**
    ```javascript
    /* ANNOTATION_BLOCK_START
    { ... JSON object ... }
    ANNOTATION_BLOCK_END */
    ```
*   **Python (e.g., `.py`):**
    ```python
    """
    ANNOTATION_BLOCK_START
    { ... JSON object ... }
    ANNOTATION_BLOCK_END
    """
    ```
*   **Markdown (e.g., `.md`):**
    ```markdown
    <!-- ANNOTATION_BLOCK_START
    { ... JSON object ... }
    ANNOTATION_BLOCK_END -->
    ```
*   **JSON-root files (e.g., `package.json`):**
    ```json
    {
      "_annotationBlock": { ... JSON object ... },
      "other_json_keys": "..."
    }
    ```
*   **Shell/YAML/etc. (using `#`):**
    ```bash
    # ANNOTATION_BLOCK_START
    # { ... JSON object, each line prefixed with '#' ... }
    # ANNOTATION_BLOCK_END
    ```

---

## 2. Schema Structure

The `EmbeddedAnnotationBlock` is a JSON object with a modular header and a payload.

```json
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "str",
    "entity_type": "EMBEDDED_ANNOTATION_BLOCK",
    "schema_definition_id_ref": "HybridAI_OS_EmbeddedAnnotation_Payload_v5.3",
    "g_annotation_created": "int",
    "g_annotation_last_modified": "int",
    "version_tag_of_host_at_annotation": "str"
  },
  "payload": {
    // --- Definitional & Lifecycle ---
    "description": "str",
    "artifact_type": "str",
    "_artifact_type_locked": false,
    "status_in_lifecycle": "str",
    "purpose_statement": "str",
    "_purpose_statement_locked": false,
    "license": "str|null",
    "data_sensitivity_level": "PUBLIC|INTERNAL|CONFIDENTIAL|SECRET|null",

    // --- Governance ---
    "governing_guideline_artifact_ids": ["str"], // List of artifact_ids for relevant guidelines

    // --- History & Contribution ---
    "authors_and_contributors": [
      {
        "_locked_entry_definition": true, // boolean
        "g_contribution": "int",
        "identifier": "str",
        "contribution_summary": "str"
      }
    ],

    // --- Structural & Functional ---
    "key_logic_points_or_summary": ["str"],
    "interfaces_provided": [
      {
        "_locked_entry_definition": false, // boolean
        "name": "str",
        "interface_type": "FUNCTION|API_ENDPOINT|UI_ELEMENT|DATA_CONTRACT",
        "details_or_schema": "str_or_object"
      }
    ],

    // --- Dependencies & Constraints ---
    "requisites_and_assumptions": [
      {
        "_locked_entry_definition": false, // boolean
        "description": "str",
        "type": "ENVIRONMENT_DEPENDENCY|DATA_ASSUMPTION|SCHEMA_DEPENDENCY|TECHNOLOGY_STACK_CONSTRAINT|EXTERNAL_SERVICE_AVAILABILITY"
      }
    ],
    "external_dependencies": [
      {
        "_locked_entry_definition": false, // boolean
        "name": "str",
        "version_constraint": "str",
        "reason_or_usage": "str"
      }
    ],
    "internal_dependencies": ["str"],
    "_internal_dependencies_list_immutable": false, // boolean
    "dependents": ["str"],

    // --- Scaffolding & Generation ---
    "scaffold_info": {
      "_object_is_immutable": true, // boolean
      "scaffold_definition_id": "str",
      "g_scaffolded": "int",
      "placeholders_status": [
        {
          "id": "str",
          "_id_locked": true, // boolean
          "description_from_scaffold": "str",
          "_description_locked": true, // boolean
          "status": "PENDING_IMPLEMENTATION|IMPLEMENTATION_IN_PROGRESS|IMPLEMENTED|DEFERRED|REMOVED",
          "g_status_updated": "int",
          "implementing_task_id": "str|null"
        }
      ]
    }|null,

    // --- Quality & Testing ---
    "quality_notes": {
      "overall_quality_assessment": "EXCELLENT|GOOD|NEEDS_IMPROVEMENT|FAILING|NOT_ASSESSED|null",
      "last_readiness_check_g": "int|null",
      "last_test_run_evidence": {
        "test_results_artifact_id_ref": "str",
        "testing_agent_signature": "str" // The persona_id of the trusted testing agent
      }|null,
      
      "static_analysis": {
        "status": "PENDING|PASS|FAIL_WITH_ISSUES|NOT_APPLICABLE",
        "g_last_run": "int|null"
      },
      "unit_tests": {
        "status": "PENDING_DEFINITION|DEFINED_AWAITING_IMPLEMENTATION|IMPLEMENTATION_IN_PROGRESS|IMPLEMENTED_AWAITING_EXECUTION|EXECUTION_PASS|EXECUTION_FAIL|DEFERRED|NOT_APPLICABLE",
        "coverage": { "percentage": "float|null", "summary_text": "str|null" },
        "g_last_run": "int|null"
      },
      "integration_tests": {
        "status": "PENDING_DEFINITION|DEFINED_AWAITING_IMPLEMENTATION|IMPLEMENTATION_IN_PROGRESS|IMPLEMENTED_AWAITING_EXECUTION|EXECUTION_PASS|EXECUTION_FAIL|DEFERRED|NOT_APPLICABLE",
        "g_last_run": "int|null"
      },
      "manual_review_log": [
        {
          "_locked_entry_definition": true, // boolean
          "g_review": "int",
          "reviewer": "str",
          "comment": "str",
          "status_outcome": "APPROVED|NEEDS_REWORK|REJECTED"
        }
      ]
    },
    "test_plan_notes_from_scaffold": [
      {
        "_locked_entry_definition": false, // boolean
        "g_originated_from_scaffold": "int",
        "test_type": "UNIT|INTEGRATION|E2E|PERFORMANCE|SECURITY|API_CONTRACT|USABILITY|ACCESSIBILITY",
        "focus_area_or_scenario": "str",
        "initial_guidance_from_scaffold": "str",
        "current_status": "PENDING_DEFINITION|DEFINED_AWAITING_IMPLEMENTATION|IMPLEMENTATION_IN_PROGRESS|IMPLEMENTED_AWAITING_EXECUTION|EXECUTION_PASS|EXECUTION_FAIL|DEFERRED|NOT_APPLICABLE",
        "g_status_updated": "int",
        "linked_test_script_artifact_ids": ["str"],
        "linked_test_results_artifact_ids": ["str"],
        "linked_issue_ids_found": ["str"]
      }
    ],

    // --- Linkage & Miscellaneous ---
    "linked_issue_ids": ["str"],
    "custom_metadata": {}
  }
}

```

3. Key Field Descriptions (payload section)
Definitional & Lifecycle:
description: Verbose summary of the artifact's content and role.
artifact_type: A specific enum (e.g., UI_COMPONENT_REACT, VALIDATION_REPORT, SCAFFOLD_SCHEMA_DEFINITION). Can be locked to prevent fundamental re-purposing.

status_in_lifecycle: The current state of the artifact (e.g., SCAFFOLDED, UNDER_DEVELOPMENT, STABLE, DEPRECATED).
purpose_statement: A clear, narrative sentence explaining why this artifact exists. Can be locked after initial design.
History & Contribution:
authors_and_contributors: An append-only log of which agents/users worked on this artifact, when, and what they did. Entries are immutable facts.
Structural & Functional:
key_logic_points_or_summary: Bullet points summarizing the core logic or content.
interfaces_provided: Defines the "public API" of this artifact (functions, UI props, REST endpoints). Definitions of established interfaces can be locked.
Dependencies & Constraints:
requisites_and_assumptions: Critical preconditions for this artifact to function. This is where locked constraints like "MUST use shadcn/ui" are stored.
external_dependencies: List of non-project libraries/services (e.g., npm packages). Key dependencies can be locked.
internal_dependencies: List of artifact_ids within this project that this artifact uses. The list can be locked if the core architecture is stable.
dependents: List of artifact_ids that use this artifact (usually auto-populated by the OS).
Scaffolding & Generation:
scaffold_info: If generated from a Scaffold Definition, this object contains immutable information about its origin (scaffold_definition_id, g_scaffolded) and a mutable list of placeholders_status which tracks the implementation of defined placeholders.
Quality & Testing:
quality_notes: A dashboard of the artifact's current quality status, updated by the VALIDATE phase based on evidence from Test Results artifacts. The manual_review_log is an immutable record of reviews.
test_plan_notes_from_scaffold: The list of tests that should be performed on this artifact, originating from the Scaffold Definition. The plan for each test can be locked, but its current_status changes as it's implemented and executed.
Linkage & Miscellaneous:
linked_issue_ids: A running list of issues related to this artifact.
custom_metadata: An escape hatch for any project-specific metadata not covered by the standard schema.

This schema is the culmination of all our discussions about durable context, traceability, testing, and constraint management. It's dense, but every part has a clear purpose designed to support a sophisticated autonomous agent system.
