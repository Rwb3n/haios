# ADR-OS-033: Cookbook & Recipe Management System

* **Status**: Proposed
* **Date**: 2025-01-28
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

HAiOS agents repeatedly implement similar patterns across different projects and contexts - API client configurations, error handling strategies, testing frameworks, deployment patterns, and architectural components. Currently, these patterns are either:

1. **Reimplemented from scratch** each time, leading to inconsistency and wasted effort
2. **Copied informally** without validation or standardization
3. **Lost** when projects end, creating institutional knowledge gaps

This violates core architectural principles (DRY, KISS) and creates quality inconsistencies across the HAiOS ecosystem. Additionally, the system lacks a formal mechanism for capturing, validating, and evolving proven implementation patterns, leading to repeated architectural decisions and potential regression of quality standards.

The current `docs/cookbook/` directory exists but lacks formal structure, validation processes, or integration with the broader HAiOS governance model.

## Assumptions

* [ ] Implementation patterns can be abstracted into reusable templates without losing essential context or becoming overly generic.
* [ ] The Recipe validation process can distinguish between high-quality, proven patterns and experimental or context-specific implementations.
* [ ] Agents can be trained/configured to consistently discover and apply relevant Recipes during implementation tasks.
* [ ] The Recipe format can capture sufficient metadata (prerequisites, constraints, alternatives) to enable safe reuse across different contexts.
* [ ] Recipe versioning and evolution can be managed without breaking existing implementations that depend on older Recipe versions.
* [ ] The Cookbook system can integrate with existing HAiOS governance (ADR compliance, testing requirements) without creating excessive overhead.
* [ ] Recipe discovery and selection can be made efficient enough to not slow down implementation tasks.
* [ ] The system can handle Recipe conflicts when multiple Recipes could apply to the same implementation scenario.

_This section was expanded to surface implicit assumptions about pattern abstraction, validation sophistication, agent training, and system integration complexity._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Recipe system explicitly captures and reuses proven implementation patterns, eliminating redundant implementation work across projects.
- **Self-Critique:** Risk of over-abstraction leading to Recipes that are too generic to be useful or too specific to be reusable.

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** Recipe format focuses on essential implementation details with clear, minimal structure for maximum usability.
- **Self-Critique:** Balancing simplicity with comprehensive metadata requirements may create tension between usability and completeness.

### Single Source of Truth v1.0
- **Compliance Proof:** Cookbook serves as the authoritative source for all validated implementation patterns, preventing conflicting or outdated pattern usage.
- **Self-Critique:** Recipe versioning complexity could undermine single source of truth if multiple versions create confusion about which is authoritative.

### Quality Assurance v1.0
- **Compliance Proof:** Recipe validation process ensures only proven, tested patterns enter the Cookbook, maintaining consistent quality standards.
- **Self-Critique:** Validation process must be rigorous enough to catch quality issues while not being so strict as to reject innovative but valid patterns.

### Evidence-Based Development v1.0
- **Compliance Proof:** All Recipes must include evidence of successful implementation and testing before canonization.
- **Self-Critique:** Evidence requirements must be comprehensive; insufficient evidence validation could allow unproven patterns to be treated as authoritative.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between Recipe definition (what), Recipe application (how), and Recipe validation (quality assurance).
- **Self-Critique:** Integration points between Recipe system and existing HAiOS components may blur separation boundaries.

### Audit Trail v1.0
- **Compliance Proof:** Complete lineage tracking from pattern discovery through validation to Recipe creation and usage across projects.
- **Self-Critique:** Comprehensive audit trails may become voluminous and require sophisticated tooling for effective navigation and analysis.

### Assumption Surfacing v1.0
- **Compliance Proof:** Eight explicit assumptions about pattern abstraction, validation processes, agent integration, and system complexity.
- **Self-Critique:** Recipe system likely has additional implicit assumptions about pattern categorization and cross-project applicability.

## Decision

**Decision:**

> We will implement a **Cookbook & Recipe Management System** that formalizes the capture, validation, and reuse of proven implementation patterns across all HAiOS projects. This system will enforce DRY principles while maintaining quality standards through a structured validation process.

### Recipe Structure & Format

**Recipe Definition Schema:**
```json
{
  "recipe_header": {
    "recipe_id": "recipe_[category]_[name]",
    "title": "Human-readable recipe name",
    "category": "api_client|error_handling|testing|deployment|architecture",
    "version": "semantic version (1.0.0)",
    "status": "VALIDATED|EXPERIMENTAL|DEPRECATED",
    "created_g": "global event counter",
    "last_validated_g": "most recent validation event"
  },
  "applicability": {
    "tech_stack": ["nodejs", "python", "react"],
    "project_types": ["service", "library", "ui_component"],
    "prerequisites": ["dependency1", "dependency2"],
    "constraints": ["memory < 512MB", "latency < 100ms"]
  },
  "implementation": {
    "description": "Clear problem statement and solution approach",
    "code_template": "Parameterized code template with {{variables}}",
    "configuration_example": "Complete working example",
    "testing_strategy": "How to validate the implementation"
  },
  "validation_evidence": {
    "successful_implementations": ["project_id_1", "project_id_2"],
    "test_results": "Evidence of successful testing",
    "performance_metrics": "Benchmarks or performance characteristics",
    "alternatives_considered": "Why this approach over alternatives"
  },
  "maintenance": {
    "known_issues": ["issue1", "issue2"],
    "evolution_path": "How this Recipe might evolve",
    "deprecation_strategy": "Migration path if Recipe becomes obsolete"
  }
}
```

### Recipe Lifecycle Management

1. **Pattern Discovery**: Agents identify recurring implementation patterns during project work
2. **Recipe Proposal**: Create experimental Recipe in `/proposals/recipes/` with initial evidence
3. **Validation Process**: Recipe undergoes validation by designated Recipe Validator agent:
   - Code quality assessment
   - Evidence verification (minimum 2 successful implementations)
   - Framework compliance check (DRY, KISS, etc.)
   - Integration testing with existing Recipes
4. **Canonization**: Validated Recipes move to `docs/cookbook/recipes/` with VALIDATED status
5. **Usage Tracking**: Monitor Recipe application across projects for effectiveness metrics
6. **Evolution**: Regular review process for Recipe updates, deprecation, and replacement

### Recipe Categories & Organization

**Directory Structure:**
```
docs/cookbook/
├── recipes/
│   ├── api_client/
│   ├── error_handling/
│   ├── testing/
│   ├── deployment/
│   └── architecture/
├── recipe_index.md
└── validation_criteria.md
```

### Integration with HAiOS Governance

**ADR Compliance**: All Recipes must demonstrate compliance with relevant ADRs (testing standards, security controls, etc.)

**Framework Integration**: Recipes must explicitly reference and comply with canonical frameworks from ADR-OS-032

**Event Tracking**: Recipe creation, validation, and usage tracked via global event counter `g`

**Distributed Systems Implications**: Recipe system MUST adhere to cross-cutting policies:
- **Idempotency (ADR-OS-023):** Recipe application produces consistent results regardless of retry attempts
- **Event Ordering (ADR-OS-027):** All Recipe lifecycle events properly timestamped and ordered
- **Observability (ADR-OS-029):** Recipe usage and effectiveness captured in distributed traces
- **Zero Trust (ADR-OS-025):** Recipe validation operates under zero-trust principles

**Confidence:** High

## Rationale

1. **DRY Principle Enforcement**
   * Self-critique: Systematic capture and reuse of proven patterns eliminates redundant implementation work and ensures consistency.
   * Confidence: High

2. **Quality Standardization**
   * Self-critique: Validation process ensures only proven, tested patterns become canonical, raising overall implementation quality.
   * Confidence: High

3. **Knowledge Preservation**
   * Self-critique: Formal Recipe system prevents loss of institutional knowledge when projects end or team members change.
   * Confidence: High

4. **Implementation Velocity**
   * Self-critique: Reusable Recipes accelerate development by providing proven starting points for common implementation challenges.
   * Confidence: Medium

5. **Architectural Consistency**
   * Self-critique: Standardized patterns ensure consistent architectural approaches across all HAiOS projects.
   * Confidence: High

## Alternatives Considered

1. **Informal Pattern Sharing**: Continue current ad-hoc pattern sharing without formal structure.
   * Brief reason for rejection: Leads to inconsistency, quality variations, and knowledge loss. Violates DRY principles.
   * Confidence: High

2. **External Pattern Libraries**: Use existing pattern libraries (e.g., design patterns, architectural templates).
   * Brief reason for rejection: External libraries lack HAiOS-specific context and governance integration. May not align with HAiOS principles.
   * Confidence: Medium

3. **Code Generation Tools**: Implement automated code generation instead of reusable patterns.
   * Brief reason for rejection: Less flexible than Recipe system and doesn't capture contextual knowledge or decision rationale.
   * Confidence: Medium

4. **Wiki-Based Documentation**: Use informal wiki or documentation for pattern sharing.
   * Brief reason for rejection: Lacks validation processes, versioning, and integration with HAiOS governance model.
   * Confidence: High

## Consequences

* **Positive:**
  - Eliminates redundant implementation work across projects
  - Ensures consistent quality and architectural approaches
  - Preserves institutional knowledge in formal, searchable format
  - Accelerates development velocity through proven starting points
  - Enables systematic improvement of implementation patterns over time
  - Integrates with existing HAiOS governance and quality assurance processes

* **Negative:**
  - Adds overhead for Recipe creation and validation processes
  - Risk of over-abstraction making Recipes too generic or too specific
  - Requires agent training for effective Recipe discovery and application
  - Recipe versioning and evolution complexity
  - Potential Recipe conflicts requiring resolution processes

## Clarifying Questions

* What specific validation criteria should be applied to ensure Recipe quality while not being overly restrictive to innovation?
* How should Recipe versioning be managed to balance stability for existing implementations with evolution for improved patterns?
* What metrics should be tracked to measure Recipe effectiveness and identify candidates for deprecation or improvement?
* How should Recipe conflicts be resolved when multiple Recipes could apply to the same implementation scenario?
* What is the governance process for Recipe evolution, including who has authority to update or deprecate existing Recipes?
* How should Recipe discovery be optimized to ensure agents can quickly find relevant patterns without being overwhelmed by choices?
* What is the migration strategy for existing informal patterns in the current `docs/cookbook/` directory?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 