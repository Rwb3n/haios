# Document 3: Scaffold Definition Specification (v3.3)

- **ADR References:** ADR-003, ADR-005, ADR-006, ADR-010, ADR-014
- **Purpose:** To define the structure and content of a `Scaffold Definition` file. This file serves as the master set of instructions for the OS's `SCAFFOLDING` process, enabling the automated and consistent creation of new project structures and components.

---

## 1. Overview & Principles

A `Scaffold Definition` is a user-provided, un-annotated JSON file that acts as a blueprint. It orchestrates the scaffolding process by:

1. Defining the **directory structure** to be created.
2. Pointing to **Boilerplate `Template` files** (located in `project_templates/`) to use as source content.
3. Specifying **`Template Processing Instructions`** for adapting the boilerplate.
4. Providing **initial hints** for the `EmbeddedAnnotationBlock` of each new artifact.

The `BLUEPRINT` phase consumes this definition to create a `SCAFFOLDING` type `Execution Plan`. This plan will include all specified scaffolding tasks, as well as an **auto-injected final task** to verify the bi-directional linking of all newly created artifacts.

---

## 2. File Format & Location

- **Format:** A single JSON object.
- **Location:** Reside in the directory specified by `haios.config.json.paths.scaffold_definitions` (default: `os_root/scaffold_definitions/`).
- **Naming Convention:** Use semantic, versioned names (e.g., `react_component_v1.2.0.json`). The version in the filename **must** match the `version` field inside the JSON content.

---

## 3. Top-Level Schema Structure

```json
{
  "scaffold_definition_id": "react_feature_module_v1.2.0",
  "g_created_or_imported": 15,
  "description": "Defines a standard feature module for a React/TypeScript application.",
  "version": "1.2.0",
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
  "files": [
    // Array of File Objects, see detailed schema below
  ]
}
```

---

## 4. `files[]` Object Sub-Schema

Each object in the files array defines a single file to be created.

```json
{
  "path_in_project_workspace": "str",
  "template_source_path": "str",
  "template_content_hash": "str|null",
  "is_json_root": false,
  "template_processing_instructions": [
    {
      "instruction_id": "str",
      "action_type": "COPY_TEMPLATE_TO_WORKSPACE|REPLACE_PLACEHOLDERS|JSON_MERGE|...",
      "parameters": {}
    }
  ],
  "initial_annotation_hints": {
    "description": "str",
    "artifact_type": "str",
    "license": "str|null",
    "data_sensitivity_level": "PUBLIC|INTERNAL|CONFIDENTIAL|SECRET|null",
    "governing_guideline_artifact_ids": ["str"],
    "requisites_and_assumptions": {
      "_list_immutable": false,
      "items": [ { "description": "str", "type": "str", "_locked_entry_definition": true } ]
    }
  },
  "placeholders": [
    { "id": "str", "description": "str" }
  ],
  "test_considerations_on_scaffold": [
    { "test_type": "str", "focus_area_or_scenario": "str", "initial_guidance": "str" }
  ],
  "initial_internal_dependencies": ["str"]
}
```

### 4.1. `files[]` Field Descriptions

- `path_in_project_workspace`: The final destination path for the new artifact. May contain placeholders (e.g., `<<MODULE_NAME>>`).
- `template_source_path`: The path to the boilerplate Template file within `project_templates/`.
- `template_content_hash`: (Optional) A hash (e.g., SHA256) of the template file's content at the time this definition was created. The OS can use this to verify the template has not changed unexpectedly.
- `template_processing_instructions`: An ordered list of actions for the AI to perform. The `action_type` enum can include `COPY_DIRECTORY` for complex components, but the primary action is file-based.
- `initial_annotation_hints`: Provides initial values for the `EmbeddedAnnotationBlock`. Includes license, data_sensitivity_level, governing_guideline_artifact_ids, and a structured requisites_and_assumptions object with its own locking flags.
- (Other fields as previously defined).

---

## 5. Error Handling

A missing or invalid `template_source_path` during the CONSTRUCT phase is a fatal error for the scaffolding task. The OS must fail the readiness check, set the task's status to BLOCKED, and log a BLOCKER Issue detailing the missing template file.