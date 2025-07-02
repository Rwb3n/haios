# Schema: `global_registry_map.txt`

*   **ADR References:** ADR-005, ADR-010, ADR-027, ADR-028, ADR-029
*   **Location:** `os_root/global_registry_map.txt`
*   **Purpose:** To serve as the single, authoritative, global index of all Project Artifacts. It provides both a hierarchical, logical view and a flat, high-performance lookup map. It binds a globally unique `artifact_id` to its physical file path, key metadata, and a comprehensive change history.

---

## 1. Schema Structure

The `global_registry_map.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "global_registry_map",
    "entity_type": "REGISTRY_MAP",
    "schema_definition_id_ref": "HybridAI_OS_RegistryMap_Payload_v5.3",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "artifact_registry_tree": {
      // Contains nested JSON objects representing logical directories or groupings.
      // Leaf nodes within this tree have keys that are the globally unique `artifact_id`s.
      "[directory_name]": {
        "[artifact_id]": {
          "_locked_entry_definition": false, // boolean
          "primary_filepath": "str",
          "g_created_in_registry": "int",
          "g_last_updated_in_registry": "int",
          "mirrored_annotation_data": {
            "version_tag": "str",
            "artifact_type": "str",
            "status_in_lifecycle": "str"
          },
          "history": [
            {
              "_locked_entry_definition": true, // boolean
              "g_event": "int",
              "event_type": "CREATED|CONTENT_MODIFIED|ANNOTATION_MODIFIED|RENAMED_MOVED|DELETED|REVIEW_PASSED|TESTS_PASSED",
              "summary": "str",
              "responsible_execution_plan_id": "str|null",
              "responsible_task_id": "str|null",
              "trace_id": "str|null",
              "vector_clock": "str|null"
            }
          ]
        }
      },
      "flat_lookup_map": {
      // Flat map for O(1) lookups...
      "[artifact_id]": "str" // path
    },
    "partition_status": "CONSISTENT|PARTITIONED|RECONCILING"
    }
  }
}

2. Field Descriptions
2.1. os_file_header
A standard modular header block for OS Control Files.
2.2. payload
artifact_registry_tree (object):
The primary data store. A hierarchical object representing the logical project structure, where leaf nodes are the detailed artifact entries keyed by their artifact_id.
artifact_registry_tree.[...].[artifact_id] (object)
The leaf node object for a single registered artifact.
_locked_registration (boolean): If true, this artifact's registration is protected from being moved, renamed, or deleted by standard AI operations.
artifact_id (string): The unique ID of the artifact. This is stored here for redundancy and easy searching.
initiative_id_ref (string): The ID of the initiative this artifact primarily belongs to, for efficient filtering.
primary_filepath (string): The definitive, relative path to the physical artifact file.
path_origin_type (string): Enum indicating the root of the path. Values: PROJECT_WORKSPACE, OS_ROOT.
content_hash (string, optional): A hash (e.g., "sha256:...") of the artifact's content for quick integrity checks.
g_created_in_registry (int): The g value when this artifact was first registered.
g_last_updated_in_registry (int): The g value when this entry was last modified.
mirrored_annotation_data (object): A subset of data mirrored from the artifact's EmbeddedAnnotationBlock for fast lookups.
version_tag (string)
artifact_type (string)
status_in_lifecycle (string)
g_last_annotation_sync (int): The g value when this mirror was last synchronized with the source annotation block.
history (object[]): An append-only log of significant lifecycle events for this artifact.
_list_is_immutable (boolean): Always true, ensuring the historical order cannot be changed.
Each entry is an object:
_locked_entry_definition (boolean): Always true.
g_event (int): The g value of the event.
event_type (string): Enum including SCAFFOLDED, CREATED, CONTENT_MODIFIED, ANNOTATION_MODIFIED, PLACEHOLDERS_FILLED, RENAMED_MOVED, CONSTRAINT_LOCKED, CONSTRAINT_OVERRIDDEN, TESTS_PASSED, DEPRECATED, DELETED.
summary (string): Verbose summary of the event.
responsible_execution_plan_id (string, optional)
responsible_task_id (string, optional)
trace_id (string, optional): **(ADR-029)** The ID of the distributed trace this event belongs to.
vector_clock (string, optional): **(ADR-027)** The vector clock timestamp for causal ordering in a distributed environment.
flat_lookup_map (object):
A secondary, non-authoritative index for high-performance lookups. It is a simple map of artifact_id to primary_filepath.
This map can be regenerated from the artifact_registry_tree at any time and is not subject to versioning or locking itself.
partition_status (string, optional): **(ADR-028)** Current state of the registry partition. Defaults to `CONSISTENT`.
3. Future Scalability Considerations
For projects with an exceptionally large number of artifacts (>100,000), the single global_registry_map.txt file may become a performance bottleneck. A future version of the OS may introduce a sharding mechanism, where each initiative contains its own registry_shard.txt, and the global file becomes a lightweight index of these shards. This schema is designed to be forward-compatible with such a strategy.