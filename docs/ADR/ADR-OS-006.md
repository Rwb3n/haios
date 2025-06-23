# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_006_md",
        "g_annotation_created": 12,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 12, "identifier": "Hybrid_AI_OS" },
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

# ADR-OS-006: Scaffolding Process & `Scaffold Definition` Usage

* **Status**: Proposed
* **Date**: 2024-06-06
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

To ensure consistency, reduce boilerplate, and accelerate the setup of new projects or components, a standardized and automated scaffolding process is required. This process must create not only the file and directory structure but also embed foundational metadata (`EmbeddedAnnotationBlock`), content placeholders, and initial testing considerations directly into the newly created artifacts.

## Assumptions

* [ ] `Scaffold Definition` definitions are well-formed, valid JSON.
* [ ] Boilerplate assets referenced in a `Scaffold Definition` exist at the specified paths within `project_templates/`.
* [ ] The OS has write permissions to the target `project_workspace/` directory.
* [ ] The template processing logic can handle all supported file types and placeholder patterns.
* [ ] The scaffolding process is idempotent and can recover from partial failures.
* [ ] All scaffolded artifacts receive a valid and complete EmbeddedAnnotationBlock at creation.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### AAA (Arrange, Act, Assert) v1.0
- **Compliance Proof:** Scaffolding process follows AAA pattern: Arrange (prepare templates), Act (execute scaffold), Assert (validate created artifacts with annotations).
- **Self-Critique:** Initial annotation might become stale if not updated during development, giving false sense of context.

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Template-based approach eliminates code duplication by reusing boilerplate assets from project_templates/ for multiple component creation.
- **Self-Critique:** Managing the link between Scaffold Definition and its many template assets could become complex.

### Explicit Diagramming v1.0
- **Compliance Proof:** Scaffolding process and template structure are described textually.
- **Self-Critique:** **NON-COMPLIANCE:** Actual diagram showing scaffolding workflow and template relationships is missing.
- **Mitigation:** Future revision will include explicit scaffolding process diagram.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between scaffold instructions (Scaffold Definition), template content (project_templates/), and target artifacts (project_workspace/).
- **Self-Critique:** Template processing logic could become complex subsystem to maintain.

### Self-Describing Systems v1.0
- **Compliance Proof:** Every scaffolded artifact receives complete EmbeddedAnnotationBlock from inception, making it immediately self-describing.
- **Self-Critique:** Poorly designed Scaffold Definition could enforce bad practices across many components.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation about JSON validity, template existence, and write permissions.
- **Self-Critique:** Only three assumptions listed; scaffolding process likely has more implicit assumptions about template structure and processing capabilities.

### Best Practices Enforcement v1.0
- **Compliance Proof:** Scaffolding system enforces consistent project structure and coding conventions through standardized templates.
- **Self-Critique:** Requires upfront investment in creating well-structured Scaffold Definitions and templates.

## Decision

**Decision:**

> We will implement a scaffolding system driven by **`Scaffold Definition`** JSON files that instruct a dedicated **`SCAFFOLDING`-type `Execution Plan`**. This plan will use boilerplate assets from `/project_templates` to create new artifacts in the `/project_workspace`, injecting a complete `EmbeddedAnnotationBlock` into each file upon creation.

**Confidence:** High

## Rationale

1. **Consistency & Best Practices**
   * Self-critique: A poorly designed `Scaffold Definition` could enforce bad practices across many components.
   * Confidence: High
2. **Durable Context from Inception**
   * Self-critique: The initial annotation might become stale if not updated during development, giving a false sense of context.
   * Confidence: High
3. **Separation of Instruction and Content**
   * Self-critique: Managing the link between a `Scaffold Definition` and its many template assets could become complex.
   * Confidence: Medium
4. **Dynamic Customization**
   * Self-critique: The logic for placeholder replacement and customization could become a complex subsystem to maintain.
   * Confidence: Medium

## Alternatives Considered

1. **Manual Scaffolding**: Rejected as it is slow, error-prone, and fails to establish the initial `EmbeddedAnnotationBlock` required for autonomous operation.
   * Confidence: High
2. **Simple File Copy**: Rejected because it misses the primary benefit of creating intelligent, context-aware artifacts from inception.
   * Confidence: High

## Consequences

* **Positive:** Highly automated and reliable project bootstrapping. Creates "intelligent" artifacts from day one. Enforces project structure and coding conventions. The process is fully auditable.
* **Negative:** Requires an upfront investment in creating well-structured `Scaffold Definition` definitions and templates. The template processing logic can be complex.

## Clarifying Questions

* How will versioning and backward compatibility of `Scaffold Definition` files and templates be managed as requirements evolve?
* What is the process for updating or migrating existing components that were created from an older scaffold version?
* How does the system validate the integrity and completeness of scaffolded artifacts, especially their `EmbeddedAnnotationBlock`?
* What are the error recovery and rollback procedures if the scaffolding process fails partway through execution?
* How are customizations and overrides handled for components that deviate from the standard scaffold?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
