# ADR-OS-014: Project Guidelines Artifact

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

To ensure consistency and quality, and to combat AI "drift" or "forgetting" of critical project standards, there is a need for a durable, central repository of project-wide rules, conventions, and procedures. These guidelines must be easily accessible and referenceable by all AI agents during planning and execution phases.

## Assumptions

*   [ ] Agents can reliably parse and adhere to instructions provided in Markdown guideline files.
*   [ ] The `global_registry_map.txt` provides a stable way to reference and retrieve guideline artifacts.
*   [ ] The overhead of managing and versioning guideline artifacts is less than the cost of inconsistent agent behavior.
*   [ ] The guidelines management process is robust against outdated or conflicting rules.
*   [ ] The system can detect and recover from missing or corrupted guideline artifacts.
*   [ ] All guideline artifacts are versioned and auditable for changes.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Central repository eliminates duplication of project standards across multiple locations; single source of truth for guidelines.
- **Self-Critique:** Guidelines becoming outdated could enforce incorrect behavior; requires regular review and maintenance process.

### Single Source of Truth v1.0
- **Compliance Proof:** Project Guidelines artifact store serves as canonical source for all project-wide rules, conventions, and procedures.
- **Self-Critique:** Malicious or poorly designed plan could intentionally omit guideline context, bypassing the control.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about agent parsing capabilities, registry stability, and overhead/benefit trade-offs.
- **Self-Critique:** Only three assumptions listed; guidelines management likely has more implicit assumptions about agent compliance and maintenance processes.

### Traceability v1.0
- **Compliance Proof:** Guidelines are version-controlled Project Artifacts with EmbeddedAnnotationBlocks providing complete audit trail.
- **Self-Critique:** Audit trail only proves guideline was loaded, not that agent perfectly adhered to it; validation steps still critical.

### Human-Centered Design v1.0
- **Compliance Proof:** Guidelines designed to combat AI drift and provide human-readable standards for project oversight.
- **Self-Critique:** Different underlying LLMs might interpret same natural language guidelines differently, leading to subtle inconsistencies.

### First-Class Citizen Principle v1.0
- **Compliance Proof:** Guidelines treated as first-class Project Artifacts with full lifecycle support, versioning, and registry integration.
- **Self-Critique:** As more guidelines are added, managing dependencies and ensuring they don't contradict each other becomes more complex.

## Decision

**Decision:**

> We will establish the concept of a **`Project Guidelines` artifact store**, which will be a designated collection of Markdown documents within the project workspace (e.g., located at `project_workspace/docs/guidelines/`). These are version-controlled Project Artifacts, complete with `EmbeddedAnnotationBlock`s.
>
> Key guideline artifacts will be created to house specific types of standards. A crucial initial example is the **`testing_guidelines.md`** artifact, which will contain procedural checklists, such as the **"Bias Prevention Checklist"** for validating test results.
>
> All relevant `Execution Plan` tasks (e.g., development, testing, validation, critique) **MUST** include a `context_loading_instructions` entry that explicitly loads the appropriate guideline artifacts. The AI agent executing the task is then required to adhere to and/or apply the procedures outlined in the loaded guidelines.
>
> ### Implementation Example
>
> 1.  A `testing_guidelines.md` artifact is created in `project_workspace/docs/guidelines/` and registered in `global_registry_map.txt`. Its content includes the `Bias Prevention Checklist`.
> 2.  An `Execution Plan` of type `CRITICAL_ASSESSMENT` is blueprinted.
> 3.  A task within this plan will have the following `context_loading_instructions`:
>     ```json
>     {
>       "context_id": "ctx_bias_checklist",
>       "description": "Load the mandatory Bias Prevention Checklist to guide the critical assessment of test results.",
>       "load_type": "ARTIFACT_CONTENT",
>       "source_reference": { "type": "ARTIFACT_ID", "value": "testing_guidelines_md_artifact_id" },
>       "priority": "CRITICAL",
>       "is_input_for_prompt": true
>     }
>     ```
> 4.  The agent executing the task receives the content of the checklist as part of its prompt and must structure its response and actions according to the checklist's items.

**Confidence:** High

## Rationale

1.  **Durable Memory**
    *   Self-critique: If guidelines become outdated, they could enforce incorrect behavior. This requires a process for regular review and maintenance.
    *   Confidence: High
2.  **Explicit Instruction**
    *   Self-critique: A malicious or poorly designed plan could intentionally omit the guideline context, bypassing the control. This relies on robust plan validation.
    *   Confidence: High
3.  **Consistency**
    *   Self-critique: Different underlying LLMs might interpret the same natural language guidelines differently, leading to subtle inconsistencies.
    *   Confidence: Medium
4.  **Auditable Procedures**
    *   Self-critique: The audit trail only proves the guideline was loaded, not that the agent perfectly adhered to it. Validation steps are still critical.
    *   Confidence: High
5.  **Evolvability**
    *   Self-critique: As more guidelines are added, managing their dependencies and ensuring they don't contradict each other becomes more complex.
    *   Confidence: Medium

## Alternatives Considered

1.  **Embedding all rules in system prompts**: Rejected as it's not version-controlled, not easily auditable per-project, and can quickly bloat the base system prompt.
    *   Confidence: High
2.  **Relying on AI's general knowledge**: Rejected as it leads to inconsistent application of standards and "AI drift."
    *   Confidence: High

## Consequences

*   **Positive:** Significantly improves the reliability and consistency of AI agent actions. Creates a formal feedback loop where operational learning can be captured and standardized. Makes the AI's adherence to standards explicit and verifiable.
*   **Negative:** Adds an extra layer of artifacts to manage. Requires discipline in the `BLUEPRINT` phase to ensure tasks correctly reference the guideline artifacts.

## Clarifying Questions

*   What is the process for proposing and ratifying a new project guideline?
*   How are conflicting rules between different guideline documents resolved?
*   How is guideline versioning managed, and what is the process for deprecating or updating outdated guidelines?
*   What mechanisms are in place to ensure agents consistently load and apply the correct guidelines for each task?
*   How are guideline artifacts audited for compliance, and what is the escalation process for detected violations?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*


