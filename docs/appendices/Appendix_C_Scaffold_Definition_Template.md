# Appendix C: Scaffold Definition Template

<!-- EmbeddedAnnotationBlock v1.0 START -->
```json
{
  "artifact_id": "appendix_c_scaffold_definition_template_g27",
  "g_created": 27,
  "version": 1,
  "source_documents": [
    "docs/appendices/Appendix_C_Scaffold_Definition_Template.md"
  ],
  "frameworks_models_applied": [
    "Single Source of Truth v1.0",
    "Explicit Diagramming v1.0",
    "Traceability v1.0"
  ],
  "trace_id": "g27_c_scaffold",
  "commit_digest": null
}
```
<!-- EmbeddedAnnotationBlock v1.0 END -->

---

## Purpose
This appendix preserves the authoritative scaffold specification used to bootstrap new initiatives, execution plans, or codebases.

> NOTE: The full template from the source document is reproduced below for convenience. Any updates MUST be reflected here and version-bumped.

<!-- Begin migrated content snippet -->
+
### 1. Overview & Principles

A `Scaffold Definition` is a user-provided **JSON** blueprint consumed during the BLUEPRINT phase to generate a `SCAFFOLDING` execution plan.  Its responsibilities:

1. Declare the directories to create.
2. Reference boilerplate *Template* files located in `project_templates/`.
3. Provide ordered **Template Processing Instructions** (e.g., copy, placeholder replacement).
4. Supply initial `EmbeddedAnnotationBlock` hints for every artifact.

This enables automated, idempotent, and traceable project scaffolding that aligns with ADR-006.

### 2. File Format & Location

| Field | Value |
|-------|-------|
| **Format** | Single JSON object |
| **Default Path** | `os_root/scaffold_definitions/` |
| **Filename Pattern** | `<name>_v<semver>.json` (version in filename **must** match internal `version`) |

### 3. Top-Level Schema (excerpt)

```json
{
  "scaffold_definition_id": "react_feature_module_v1.2.0",
  "version": "1.2.0",
  "description": "Defines a standard feature module for a React/TypeScript application.",
  "g_created_or_imported": 15,
  "trace_id": "trace_xyz_123",
  "idempotency_key": "user_session_abc_456",
  "consistency_mode": "STRONG",
  "comment_syntax_for_placeholders": {
    "line_comment_prefix": "//",
    "block_comment_start": "/*",
    "block_comment_end": "*/"
  },
  "directories": [
    {
      "path": "project_workspace/src/features/<<MODULE_NAME>>/components",
      "description": "Directory for the feature's React components."
    }
  ],
  "files": []
}
```

*See the source specification for complete field descriptions, including the `files[]` sub-schema and error-handling rules.*

### 4. `files[]` Object Sub-Schema (excerpt)

Each entry in the `files` array defines a single file to be created by the scaffold plan.

```json
{
  "path_in_project_workspace": "project_workspace/src/features/<<MODULE_NAME>>/components/MyComponent.tsx",
  "template_source_path": "project_templates/react_components/MyComponent.tsx.template",
  "template_content_hash": "<sha256>",
  "is_json_root": false,
  "authorized_agent_archetypes": ["BUILDER", "REFACTORING_SPECIALIST"],
  "template_processing_instructions": [
    {
      "instruction_id": "step_1_copy",
      "action_type": "COPY_TEMPLATE_TO_WORKSPACE",
      "parameters": {}
    },
    {
      "instruction_id": "step_2_replace",
      "action_type": "REPLACE_PLACEHOLDERS",
      "parameters": {
        "MODULE_NAME": "UserProfile"
      }
    }
  ],
  "initial_annotation_hints": {
    "description": "React component for user profile display.",
    "artifact_type": "UI_COMPONENT",
    "license": "MIT",
    "data_sensitivity_level": "PUBLIC",
    "governing_guideline_artifact_ids": ["appendix_f_testing_guidelines_g27"],
    "requisites_and_assumptions": {
      "_list_immutable": false,
      "items": [
        {"description": "API endpoint /user/{id} exists", "type": "DEPENDENCY", "_locked_entry_definition": true}
      ]
    }
  },
  "placeholders": [
    {"id": "MODULE_NAME", "description": "PascalCase name of the feature module."}
  ],
  "test_considerations_on_scaffold": [
    {"test_type": "UNIT", "focus_area_or_scenario": "renders correctly with default props", "initial_guidance": "ensure snapshot stability"}
  ],
  "initial_internal_dependencies": []
}
```

*See the source document for complete field descriptions and additional examples.*

## 5. Error Handling

A missing or invalid `template_source_path` during the CONSTRUCT phase is a **fatal error** for the scaffolding task. The OS must:

1. Fail the readiness check, marking the task `BLOCKED_READINESS`.
2. Log a `BLOCKER`‐severity Issue detailing the missing or invalid template file path.
3. Halt further tasks in the plan and await a remediation Execution Plan.

Retries are **not** attempted automatically because supplying the correct template path generally requires human input or configuration fixes.

---

*End of Scaffold Definition Specification migration.*