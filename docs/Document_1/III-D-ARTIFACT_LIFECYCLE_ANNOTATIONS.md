## III D. Artifact Lifecycle & Annotations

Project Artifacts are the primary, tangible outputs of the development process. The OS manages their entire lifecycle—from creation to deprecation—through a combination of the global artifact registry and rich, embedded metadata.

1.  **Creation (Scaffolding or Generation)**
    *   Artifacts are typically born during the `CONSTRUCT` phase, as an output of a task within an `Execution Plan`.
    *   If created via a `SCAFFOLDING` plan (ADR-006), the Artifact is generated from a `Template` file and is immediately imbued with a comprehensive `EmbeddedAnnotationBlock`. This includes `scaffold_info` (with placeholder tracking) and `test_plan_notes_from_scaffold`.
    *   Upon creation, the new Artifact is immediately registered in `global_registry_map.txt` with a unique `artifact_id` and its initial `history` log entry (e.g., `event_type: "SCAFFOLDED"`).

2.  **Modification & Versioning**
    *   When an agent modifies an Artifact's content as part of a task, it must also update the Artifact's `EmbeddedAnnotationBlock`.
    *   Key updates include:
        *   Incrementing or changing the `version_tag`.
        *   Updating both the `g_last_modified_content` and `g_last_modified_annotations` markers to the current `g` value as appropriate.
        *   Adding to the `authors_and_contributors` log.
        *   Updating `key_logic_points_or_summary` and `internal_dependencies`.
    *   The OS, after the modification, updates the Artifact's entry in `global_registry_map.txt`, mirroring key metadata and adding a new event to its `history` (e.g., `CONTENT_MODIFIED`, `RENAMED_MOVED`). When all scaffold placeholders are resolved, the OS logs a `PLACEHOLDERS_FILLED` event.

3.  **The `EmbeddedAnnotationBlock`: The Artifact's Passport (ADR-003)**
    *   This embedded JSON object is the single source of truth for an Artifact's metadata. Its presence is mandatory for all text-editable Artifacts managed by the OS.
    *   It provides durable, co-located context for any agent. Agents must consult the `EmbeddedAnnotationBlock` (via `context_loading_instructions`) to understand the rules and context governing the Artifact, especially any `_locked*` constraints (ADR-010).

4.  **Dependency & Relationship Tracking**
    *   The `internal_dependencies` array lists all project Artifacts this Artifact uses.
    *   The OS uses this information to maintain the `dependents` array in other Artifacts, creating a bi-directional dependency graph. This graph refresh typically occurs during a `VALIDATE` phase or a dedicated `ANNOTATION_MAINTENANCE` plan.

5.  **Quality & Governance**
    *   The `quality_notes` object serves as a live "quality dashboard." During the `VALIDATE` phase, the OS updates these fields based on hard evidence from `Test Results` Artifacts (ADR-007). If a pre-execution readiness check (ADR-013) produces a formal `readiness_assessment_<g>.md` artifact, its ID can be referenced here.
    *   The OS also tracks governance metadata such as `license` and `data_sensitivity_level` within the annotation for security and compliance purposes. Optionally, a `file_hash` may be stored for quick integrity checks.

6.  **Deprecation, Archival, & Deletion**
    *   The lifecycle is formally managed:
        1.  An `Execution Plan` task changes an Artifact's `status_in_lifecycle` in its annotation to `DEPRECATED`.
        2.  Another action can set the status to `ARCHIVED`, which functionally locks the Artifact against further edits without physical deletion.
        3.  A final task can physically delete the file. The `history` log in `global_registry_map.txt` is updated with a `DELETED` event, but the artifact's entry remains for a complete historical record.