# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_003_md",
        "g_annotation_created": 7,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 7, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 4, "identifier": "Framework_Compliance_Retrofit" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "adr_os_032_md"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-003: Artifact Annotation Strategy (`EmbeddedAnnotationBlock`)

* **Status**: Proposed
* **Date**: 2025-06-06
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

For an autonomous agent system to effectively manage, understand, and modify a codebase over time, it cannot rely solely on reading the primary content of files. 
It requires rich, structured metadata about each artifact's purpose, history, dependencies, quality, and relationship to the overall project. This metadata needs to be durable, version-controlled, and live alongside the artifact it describes, avoiding reliance on external databases or transient agent memory.

## Assumptions

* [ ] The chosen embedding method (comment block vs. JSON key) will cover all relevant text-editable file types.
* [ ] The performance overhead of parsing JSON from comment blocks is acceptable.
* [ ] Agents can be reliably programmed to maintain the integrity of the annotation block.
* [ ] All supported file formats can accommodate the annotation block without breaking primary functionality.
* [ ] Annotation parsing and validation logic is robust against malformed or partially corrupted blocks.
* [ ] The annotation block schema is stable and versioned to prevent breaking changes for agents.
* [ ] Updates to annotation blocks and global_registry_map.txt are atomic or recoverable to prevent divergence.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Artifact metadata is stored once in the embedded annotation block, eliminating need to duplicate context in external systems or agent memory.
- **Self-Critique:** Risk of divergence between annotation block and mirrored data in global_registry_map.txt if updates fail mid-process.

### Single Source of Truth v1.0
- **Compliance Proof:** The embedded annotation block serves as the canonical source for all artifact metadata, avoiding multiple competing sources.
- **Self-Critique:** Requires disciplined agents and strong validation to maintain integrity of the single source.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation about embedding methods, performance, and agent reliability.
- **Self-Critique:** Only three assumptions listed; annotation strategy likely has more implicit assumptions about file formats and parsing capabilities.

### Distributed Systems Principles v1.0
- **Compliance Proof:** The "Distributed Systems Implications" section addresses idempotency and observability for annotation operations.
- **Self-Critique:** Missing explicit handling of partition tolerance and event ordering for annotation updates.

### Explicit Diagramming v1.0
- **Compliance Proof:** Annotation block structure and embedding patterns are described textually.
- **Self-Critique:** **NON-COMPLIANCE:** Actual diagram showing annotation block structure and embedding methods is missing.
- **Mitigation:** Future revision will include explicit annotation architecture diagram.

### Version Control Integration v1.0
- **Compliance Proof:** Annotations are embedded directly in files to leverage version control synergy and avoid external database dependencies.
- **Self-Critique:** Large, frequent annotation changes could bloat git history.

### Self-Describing Systems v1.0
- **Compliance Proof:** Every artifact becomes self-describing through embedded metadata, reducing cognitive load and improving agent understanding.
- **Self-Critique:** Increases file size and requires parsing overhead; balance between self-description and performance needs monitoring.

## Decision

**Decision:**

> We will mandate the use of a comprehensive **`EmbeddedAnnotationBlock`** for all text-editable Project Artifacts managed by the OS. This block will be a structured JSON object containing all critical metadata for the artifact. It will be embedded in a comment block for most files, and as a top-level `_annotationBlock` key in JSON-root files.
>
> ### Distributed Systems Implications
>
> The creation and maintenance of the `EmbeddedAnnotationBlock` must adhere to the following policies:
>
> *   **Idempotency (ADR-OS-023):** Any operation that creates or modifies an artifact and its annotation block MUST be idempotent. This prevents the creation of duplicate artifacts or corrupted annotations if the operation is retried.
> *   **Observability (ADR-OS-029):** Every modification to an annotation block MUST be captured in a distributed trace. The `trace_id` of the operation causing the change SHOULD be stored within the annotation's history to provide a perfect audit trail from effect back to cause.

**Confidence:** High

## Rationale

1. **Durable Context**
   * Self-critique: An agent could maliciously or accidentally corrupt the JSON within the annotation block, breaking subsequent parsing.
   * Confidence: High
2. **Single Source of Truth**
   * Self-critique: There is a risk of divergence between the annotation block and mirrored data in the `global_registry_map.txt` if an update fails mid-process.
   * Confidence: Medium
3. **Version Control Synergy**
   * Self-critique: Large, frequent changes to annotations (e.g., test results) could bloat the git history.
   * Confidence: High
4. **Supports Agent Specialization**
   * Self-critique: Requires a well-defined and stable schema for the annotation block to prevent breaking changes for specialized agents.
   * Confidence: High
5. **Enables Constraint Enforcement**
   * Self-critique: The locking mechanism for requisites could be too rigid, preventing necessary evolution of the system.
   * Confidence: Medium

## Alternatives Considered

1. **Centralized Metadata Database**: Storing all artifact metadata in an external database. Rejected due to the risk of desynchronization between the database and the actual files in version control and increased system complexity.
   * Confidence: High
2. **Sidecar Metadata Files**: Storing metadata in a companion file (e.g., `Button.tsx.meta.json`). Rejected because it doubles the number of files to manage and increases the risk of the metadata file being separated from its source artifact.
   * Confidence: High

## Consequences

* **Positive:** Creates self-describing, intelligent artifacts. Massively improves traceability and context durability. Provides a robust mechanism for enforcing architectural and design constraints. Reduces the cognitive load on agents.
* **Negative:** Increases file size. Requires disciplined agents and a strong `VALIDATE` phase to ensure integrity. Introduces minor performance overhead for parsing.

## Clarifying Questions

* What is the recovery and validation process if an `EmbeddedAnnotationBlock` becomes corrupted or is missing required fields?
* How are annotation updates coordinated in distributed or concurrent agent scenarios to prevent race conditions or partial updates?
* What is the fallback or handling strategy for binary or non-text-editable files that cannot contain embedded annotations?
* How is the annotation schema versioning managed to ensure backward compatibility and safe evolution?
* What are the audit and traceability requirements for changes to annotation blocks, and how are these enforced?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
