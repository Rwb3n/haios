# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_035_md",
        "g_annotation_created": 251,
        "version_tag_of_host_at_annotation": "1.0.0"
    },
    "payload": {
        "description": "Defines the Crystallization Protocol and Gatekeeper Agent for formal knowledge validation and canonization.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To establish a formal two-space system that safely isolates exploratory work from canonical system state while providing auditable knowledge integration.",
        "authors_and_contributors": [
            { "g_contribution": 251, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 250, "identifier": "Third_Party_Architectural_Review" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "adr_os_032_md",
            "adr_os_021_md",
            "3rdpartyeval-10.md"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-035: The Crystallization Protocol & Gatekeeper Agent

* **Status**: SUPERSEDED 
* **Date**: 2025-01-28
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

_ UPDATE: This was a good idea, but it's been replaced by a more powerful and integrated concept. The function of the "Canonizer-Agent" is now better understood as a part of the CI/CD pipeline's lint stage, not a standalone agent. _ 

---

## Context

The operator's creative, exploratory process (regenerating responses, refining inputs, iterative development) introduces beneficial chaos that drives innovation and discovery. However, this creative process risks polluting the canonical, stable state of the system with transient, unvalidated artifacts. The current system lacks a formal mechanism to distinguish between exploratory work and validated knowledge, creating potential for system corruption when experimental artifacts are inadvertently treated as authoritative.

Additionally, the system currently has no defined protocol for how human creativity and AI iteration are integrated into the formal architecture. This creates a critical gap between the creative process that generates new knowledge and the rigorous governance that maintains system integrity.

## Assumptions

* [ ] The file system supports creating and managing a parallel directory structure for exploratory work.
* [ ] The Gatekeeper Agent can be implemented with sufficient validation sophistication to prevent corrupted artifacts from entering canonical state.
* [ ] The validation process can be made deterministic and auditable while still allowing for creative exploration.
* [ ] Operators will adopt the discipline of working in the exploration space rather than directly modifying canonical artifacts.
* [ ] The two-space architecture can be maintained without creating excessive operational overhead.
* [ ] The validation criteria can be made comprehensive enough to catch all categories of potential corruption.
* [ ] The crystallization process can preserve the intent and context of exploratory work during canonization.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032, ADR-OS-021) are up-to-date and enforced.

_This section was expanded to surface implicit assumptions about validation sophistication, operator discipline, and process overhead._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Evidence-Based Development v1.0
- **Compliance Proof:** The Gatekeeper Agent performs formal validation checks with evidence requirements before allowing canonization, ensuring all canonical knowledge is evidence-based.
- **Self-Critique:** Validation criteria must be comprehensive; incomplete validation could allow corrupted artifacts to pass through.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between exploration space (creative chaos) and canonical state (validated truth) with distinct purposes and access patterns.
- **Self-Critique:** Maintaining separation requires operator discipline; accidental cross-contamination could compromise system integrity.

### Single Source of Truth v1.0
- **Compliance Proof:** Canonical state remains the single source of truth, with exploration space explicitly marked as non-authoritative.
- **Self-Critique:** Risk of confusion about which space contains the authoritative version of evolving artifacts.

### Quality Assurance v1.0
- **Compliance Proof:** Formal gatekeeping process ensures only validated, coherent artifacts become part of canonical system state.
- **Self-Critique:** Validation process could become a bottleneck if not properly streamlined and automated.

### Audit Trail v1.0
- **Compliance Proof:** Complete audit trail of crystallization decisions, validation results, and artifact lineage from exploration to canonization.
- **Self-Critique:** Detailed audit trails may become voluminous and difficult to navigate without proper tooling.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about validation sophistication, operator discipline, process overhead, and validation comprehensiveness.
- **Self-Critique:** Eight assumptions listed; crystallization protocol likely has additional implicit assumptions about tool integration and workflow adoption.

### Distributed Systems Principles v1.0
- **Compliance Proof:** Protocol addresses consistency (canonical vs. exploration state), availability (non-blocking exploration), and partition tolerance (independent workspaces).
- **Self-Critique:** Distributed implications of multi-operator exploration spaces not fully addressed in current design.

### Fail-Safe Design v1.0
- **Compliance Proof:** System defaults to rejecting artifacts that fail validation rather than allowing potentially corrupted knowledge into canonical state.
- **Self-Critique:** Overly strict validation could reject valid innovations; balance between safety and innovation acceptance is critical.

## Decision

**Decision:**

> We will implement the **Crystallization Protocol**, a formal two-space system enforced by a new agent persona, the **Gatekeeper Agent**. This protocol establishes a clear separation between exploratory and canonical work while providing an auditable mechanism for knowledge integration.

### Two-Space Architecture

**Exploration Space:**
- Location: `/proposals` directory (or configurable path in `haios.config.json`)
- Purpose: Dedicated, non-canonical directory where all interactive, exploratory artifacts are stored
- Status: These artifacts have no official status and are explicitly marked as experimental
- Permissions: Full read/write access for exploration and iteration

**Canonized State:**
- Location: Official `docs/` and `os_root/` directories
- Purpose: The single source of truth representing validated, official system knowledge  
- Status: All artifacts have passed formal validation and represent authoritative system state
- Permissions: Write access only through Crystallization Protocol

### Crystallization Protocol Workflow

1. **Exploration Phase**: Operator works freely in the exploration space, generating and refining artifacts without constraints
2. **Crystallization Request**: Operator signals desire to formalize a proposal from the exploration space
3. **Gatekeeper Invocation**: The Gatekeeper Agent is invoked to perform validation
4. **Validation Execution**: Agent performs comprehensive validation checks:
   - Schema conformance against established schemas
   - Consistency checks against existing canonized ADRs and artifacts
   - Link integrity verification
   - Framework compliance validation (per ADR-OS-032)
   - Assumption surfacing completeness (per ADR-OS-021)
5. **Validation Decision**: 
   - **Success**: Artifact is committed to canonical state with full audit trail
   - **Failure**: Process halts with detailed feedback; artifact remains in exploration space for refinement

### Distributed Systems Implications

The Crystallization Protocol MUST adhere to the following cross-cutting policies:

* **Idempotency (ADR-OS-023):** All crystallization operations MUST be idempotent. Retrying a crystallization request with the same exploration artifact produces the same validation result.
* **Event Ordering (ADR-OS-027):** All validation steps and crystallization events MUST be properly timestamped and ordered using the global event counter `g`.
* **Observability (ADR-OS-029):** Every crystallization attempt MUST be captured in a distributed trace with full validation details and decision rationale.
* **Zero Trust (ADR-OS-025):** The Gatekeeper Agent operates under zero-trust principles, validating all artifacts regardless of source or previous validation history.

**Confidence:** High

## Rationale

1. **System Integrity Protection**
   * Self-critique: The two-space architecture protects canonical state from experimental corruption while preserving creative freedom.
   * Confidence: High
   
2. **Formalized Human-AI Interface**
   * Self-critique: Creates a precise, auditable workflow for integrating human creativity with formal system governance.
   * Confidence: High
   
3. **Quality Ratchet Mechanism**
   * Self-critique: Ensures architectural quality and consistency can only increase over time through formal validation.
   * Confidence: High
   
4. **Innovation Enablement**
   * Self-critique: Provides safe space for experimentation without compromising system stability.
   * Confidence: Medium
   
5. **Audit Trail Completeness**
   * Self-critique: Creates complete lineage from creative exploration to canonical knowledge with validation evidence.
   * Confidence: High

## Alternatives Considered

1. **Direct Canonical Editing**: Continue allowing direct modification of canonical artifacts.
   * Brief reason for rejection: Risks system corruption from experimental changes and lacks validation discipline.
   * Confidence: High

2. **Version Control Branching**: Use git branches for exploration with merge reviews.
   * Brief reason for rejection: Git workflows don't provide the formal validation semantics and artifact-level governance required by HAiOS.
   * Confidence: High

3. **Manual Review Process**: Human-only review for canonization decisions.
   * Brief reason for rejection: Doesn't scale and lacks the systematic validation checks needed for complex architectural artifacts.
   * Confidence: Medium

## Consequences

* **Positive:** 
  - Protects system integrity while enabling creative exploration
  - Formalizes knowledge integration process with complete audit trails  
  - Creates a "quality ratchet" ensuring canonical knowledge quality only increases
  - Enables safe experimentation and iteration
  - Provides clear workflow for human-AI collaborative knowledge creation

* **Negative:** 
  - Adds process overhead for canonizing new knowledge
  - Requires operator discipline to work in exploration space
  - Gatekeeper Agent implementation complexity
  - Potential bottleneck if validation process is too slow or rigid

## Clarifying Questions

* What specific validation checks should the Gatekeeper Agent perform, and how comprehensive should schema and consistency validation be?
* How should the system handle partial crystallization (e.g., only some artifacts from an exploration session are ready for canonization)?
* What is the fallback procedure if the Gatekeeper Agent fails or produces inconsistent validation results?
* How should the exploration space be organized and managed to prevent it from becoming cluttered with obsolete experiments?
* What metrics and observability should be implemented to monitor the health and effectiveness of the crystallization process?
* How should the protocol handle multi-operator scenarios where multiple people are exploring related concepts simultaneously?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
