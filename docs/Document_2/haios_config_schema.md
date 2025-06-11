# Schema: `haios.config.json`

- **ADR References:** ADR-005, ADR-012, ADR-014
- **Location:** `[PROJECT_NAME]/haios.config.json` (Project Root)
- **Purpose:** To serve as the single, foundational configuration file for a specific Hybrid_AI_OS project instance. It contains user-defined, largely static settings that govern the OS's operational environment, core constraints, and default behaviors. It is the first file the OS reads upon initialization.

---

## 1. Schema Structure

The `haios.config.json` file is a JSON object. Unlike OS Control Files, it does **not** use the modular header/payload structure, as it is a pure configuration file provided by the user, not a dynamic state file managed by the OS.

```json
{
  "os_config_version": "1.0",
  "project_name": "Agent Browse SDK",
  "paths": {
    "_locked_object_definition": true,
    "os_root": "./os_root",
    "project_workspace": "./project_workspace",
    "project_templates": "./project_templates",
    "initial_source_materials": "./initial_source_materials",
    "scaffold_definitions": "./os_root/scaffold_definitions",
    "guidelines": "./project_workspace/docs/guidelines"
  },
  "os_settings": {
    "max_task_retries_before_escalation": 3,
    "default_ai_model_preference": "gpt-4-turbo-preview",
    "status_update_poll_interval_sec": 60,
    "wip_limits": {
      "max_active_execution_plans": 2,
      "max_plans_awaiting_validation": 3
    }
  },
  "project_constraints": [
    {
      "_locked_entry_definition": true,
      "constraint_id": "tech_001",
      "description": "Primary UI Component Library",
      "value": "shadcn/ui",
      "notes": "All new UI development must use shadcn/ui components where applicable."
    },
    {
      "_locked_entry_definition": true,
      "constraint_id": "tech_002",
      "description": "Primary Language",
      "value": "TypeScript",
      "version_preference": "5.x"
    }
  ],
  "default_scaffolds": {
    "_locked_object_definition": true,
    "react_component": "react_component_shadcn_v1",
    "nodejs_service": "nodejs_service_express_v1"
  }
}
```

---

## 2. Field Descriptions

- `os_config_version` (string): The version of this configuration schema itself. Allows the OS to handle future changes to the config file structure.
- `project_name` (string): The human-readable name of the project, used in prompts, reports, etc.
- `paths` (object): **CRITICAL.** Defines the directory layout for this project instance. All path values are relative to the project root.
  - `_locked_object_definition` (boolean): Should always be true. The core directory structure is not intended to be changed at runtime by the AI.
  - `os_root` (string): Path to the directory containing all OS-internal state and plans.
  - `project_workspace` (string): Path to the directory where the AI will build the actual project artifacts.
  - `project_templates` (string): Path to the directory containing user-provided boilerplate source files.
  - `initial_source_materials` (string): Path to the directory containing initial input documents for analysis.
  - `scaffold_definitions` (string): Path to the directory containing user-provided Scaffold Definition files.
  - `guidelines` (string): Path to the directory containing Project Guidelines artifacts.
- `os_settings` (object): Defines operational parameters for the OS and its agents.
  - `max_task_retries_before_escalation` (integer): The default number of times an agent should retry a failing task before logging a BLOCKER issue and escalating.
  - `default_ai_model_preference` (string): The default AI model to be used by agent personas if not specified in their Agent Card.
  - `status_update_poll_interval_sec` (integer, optional): For a Supervisor agent, how often to check exec_status files for progress.
  - `wip_limits` (object, optional): Work-In-Progress limits inspired by Theory of Constraints to prevent system overload.
    - `max_active_execution_plans` (integer): The maximum number of exec_plans that can be in the ACTIVE state at once.
    - `max_plans_awaiting_validation` (integer): The maximum number of completed plans that can be in the queue for the VALIDATE phase.
- `project_constraints` (object[]): An array defining high-level, deterministic project constraints that all agents must adhere to.
  - `_locked_entry_definition` (boolean): true for foundational constraints.
  - `constraint_id`, `description`, `value`, `notes`: Define a specific, non-negotiable rule (e.g., programming language, core library).
- `default_scaffolds` (object): A map that links an abstract component type to a specific scaffold_definition_id. This allows an agent to be told "create a new React component" and it knows which scaffold definition to use by default.
  - `_locked_object_definition` (boolean): true.