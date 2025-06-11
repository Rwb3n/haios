# Schema: `issue_<g>.txt`

- **Location:** `os_root/initiatives/<g_init>/issues/issue_<g_creation>.txt`
- **Purpose:** Defines the structure for an Issue artifact, capturing bugs, enhancements, blockers, and other project issues, with full traceability and locking support.

---

## 1. Schema Structure

The `issue_<g>.txt` file is a JSON object with a modular header and a payload.

```json
{
  // --- Modular Header Block for OS File ---
  "os_file_header": {
    "file_id": "str", // e.g., "issue_130" (matches g_creation from filename)
    "entity_type": "ISSUE",
    "schema_definition_id_ref": "HybridAI_OS_Issue_Payload_v5.1",
    "g_file_created": "int", // Same as g_reported in payload
    "g_file_last_modified": "int", // Same as g_status_updated in payload
    "v_file_instance": "int"
  },
  // --- Payload Specific to Issue ---
  "payload": {
    "g_reported": "int", // Immutable fact
    "g_status_updated": "int", // Changes with status
    "g_resolved": "int|null",  // Populated on resolution

    "title": "str", // Can be edited for clarity, so not locked by default
    "_title_locked": "true|false",

    "description": "str", // Can be edited for clarity
    "_description_locked": "true|false",

    "type": "BUG|ENHANCEMENT|TASK|LINT_ERROR|RUNTIME_ERROR|DESIGN_FLAW|ANNOTATION_DEFECT|BLOCKER|SCHEMA_VIOLATION|USER_FEEDBACK|SECURITY_VULNERABILITY|PERFORMANCE_CONCERN|DOCUMENTATION_GAP",
    "_type_locked": "true|false", // The fundamental type of issue might be locked after initial triage

    "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFORMATIONAL",
    // Severity can be re-evaluated, so not locked by default.

    "status": "OPEN|IN_PROGRESS|ON_HOLD|RESOLVED|CLOSED|WONT_FIX|NEEDS_CLARIFICATION",
    // Status is the primary mutable field.

    "reported_by": "str",
    "_reported_by_locked": true, // Immutable fact

    "assigned_to": "str|null", // Can change

    // --- Linking & Context ---
    "init_plan_id_ref": "str|null",
    "_init_plan_id_ref_locked": true, // Context is usually fixed

    "exec_plan_id_ref": "str|null",
    "_exec_plan_id_ref_locked": true, // Context is usually fixed

    "task_id_ref": "str|null",
    "_task_id_ref_locked": true, // Context is usually fixed

    "artifact_id_ref": "str|null",
    "_artifact_id_ref_locked": true, // Context is usually fixed

    "artifact_filepath_at_reporting": "str|null", // Immutable historical context
    "_artifact_filepath_at_reporting_locked": true,

    // --- Resolution & Discussion ---
    "resolution_details": {
      "resolving_init_plan_id": "str|null",
      "resolving_exec_plan_id": "str|null",
      "resolving_task_id": "str|null",
      "resolving_artifact_ids_and_versions": [
        { "artifact_id": "str", "version_tag_at_resolution": "str", "g_modified_for_fix": "int" }
      ],
      "summary_of_fix": "str"
    }|null, // This entire object is populated upon resolution.

    "comments": [ // A log; entries are append-only and immutable once added.
      {
        "_locked_entry": true,
        "g_comment": "int",
        "author": "str",
        "comment_text": "str"
      }
    ],

    "tags": ["str"] // List of tags can be modified.
  }
}
```

---

## 2. Field Descriptions

### 2.1. `os_file_header`

- `file_id` (string): e.g., `"issue_130"` (matches `g_creation` from filename)
- `entity_type` (string): Constant `"ISSUE"`
- `schema_definition_id_ref` (string): Schema version reference
- `g_file_created` (int): Same as `g_reported` in payload
- `g_file_last_modified` (int): Same as `g_status_updated` in payload
- `v_file_instance` (int): Version for optimistic locking

### 2.2. `payload`

- `g_reported` (int): When the issue was reported (immutable)
- `g_status_updated` (int): Last status update
- `g_resolved` (int|null): When resolved, else null

#### Core Fields

- `title` (string): Editable; `_title_locked` (bool) if locked
- `description` (string): Editable; `_description_locked` (bool) if locked
- `type` (enum): See schema; `_type_locked` (bool) if locked
- `severity` (enum): CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
- `status` (enum): OPEN, IN_PROGRESS, ON_HOLD, RESOLVED, CLOSED, WONT_FIX, NEEDS_CLARIFICATION
- `reported_by` (string): Reporter; `_reported_by_locked` (bool, always true)
- `assigned_to` (string|null): Current assignee

#### Linking & Context

- `init_plan_id_ref`, `exec_plan_id_ref`, `task_id_ref`, `artifact_id_ref` (string|null): Contextual links; each has a corresponding `_locked` boolean
- `artifact_filepath_at_reporting` (string|null): Filepath at report time; `_artifact_filepath_at_reporting_locked` (bool, always true)

#### Resolution & Discussion

- `resolution_details` (object|null): Populated on resolution; includes references to resolving plans/tasks/artifacts and a summary of the fix
- `comments` (array): Append-only log; each entry has `_locked_entry`, `g_comment`, `author`, `comment_text`
- `tags` (array of string): Modifiable list of tags