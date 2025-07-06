# ADR-OS-015: Precision Context Loading

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

Modern Large Language Model (LLM) agents operate within a finite context window. Loading entire documents or artifacts as context for a task is highly inefficient and often counterproductive. It floods the context with irrelevant information, increases operational costs (token usage), and can lead to "context overwhelm" or "prompt contamination," where the agent is distracted or confused by non-essential data.

## Assumptions

*   [ ] The OS's orchestrator can be equipped with reliable logic to parse and slice artifacts based on lines or patterns.
*   [ ] The structure of artifacts is consistent enough for pattern-based slicing to be effective.
*   [ ] The agent creating the `Execution Plan` is capable of identifying the precise sections of context needed for a task.
*   [ ] The system can detect and recover from pattern or line-based slicing failures.
*   [ ] The context loading process is auditable and versioned for traceability.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Performance Optimization v1.0
- **Compliance Proof:** Precision context loading maximizes context window value and reduces operational costs by loading only relevant data.
- **Self-Critique:** Pattern parsing overhead might introduce small delays; incorrectly specified patterns could cause silent failures.

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** Simple line-based and pattern-based slicing mechanisms provide straightforward, understandable context loading.
- **Self-Critique:** Adding source_location_details increases complexity for plan creators; requires sophisticated planning agents.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about OS parsing capabilities, artifact structure consistency, and agent planning sophistication.
- **Self-Critique:** Only three assumptions listed; precision loading likely has more implicit assumptions about pattern stability and artifact formats.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between context identification (planning phase) and context loading (orchestrator execution).
- **Self-Critique:** Planning agent must understand both task requirements and artifact structure, potentially coupling concerns.

### Fail-Safe Design v1.0
- **Compliance Proof:** Fallback behavior needed for missing patterns; system should gracefully handle slicing failures.
- **Self-Critique:** Current design doesn't specify fallback behavior for pattern matching failures, potential for silent context loss.

### Cost-Effectiveness v1.0
- **Compliance Proof:** Precision loading directly reduces token usage and operational costs by eliminating irrelevant context.
- **Self-Critique:** Compute overhead for pattern matching might offset some token savings for very small contexts.

## Decision

**Decision:**

> We will implement a **Precision Context Loading** mechanism. The `context_loading_instructions` array within each `Task` object in an `Execution Plan` will be enhanced to support granular, targeted data retrieval.
>
> This will be achieved by adding an optional `source_location_details` object to each context loading instruction. This object will allow the specification of:
> 1.  **Line-based slicing:** Using `start_line` and `end_line` numbers to extract a specific portion of a text-based artifact.
> 2.  **Pattern-based slicing:** Using `start_pattern` and `end_pattern` (string or regex) to dynamically locate and extract a specific, named section of a document (e.g., a specific chapter in a Markdown file).
>
> The OS's orchestrator, when preparing a prompt for an agent, **MUST** process these instructions to construct a minimal, highly-relevant context payload.
>
> ### Implementation Details
>
> *   The `Task Object` schema within `exec_plan_schema.md` will be updated to include the `source_location_details` sub-object in its `context_loading_instructions`.
> *   The agent orchestrator component of the OS engine will be responsible for implementing the file-reading and slicing logic based on these instructions before assembling the final prompt for an AI agent.
> *   An `Execution Plan` task for "onboarding" a new agent can now be a series of context-loading steps that walk the agent through key sections of project documentation, one chunk at a time.
>
> ### Example Use Case
>
> To instruct an agent to write a test based on a specific ADR section, the `context_loading_instructions` would not load the entire ADR. Instead, it would specify:
> ```json
> {
>   "description": "Load only the 'Decision' section of ADR-007.",
>   "source_reference": { "type": "ARTIFACT_ID", "value": "adr_007_testing_lifecycle_gX" },
>   "source_location_details": {
>     "start_pattern": "## Decision",
>     "end_pattern": "## Rationale"
>   }
> }
> ```

**Confidence:** High

## Rationale

1.  **Maximizes Context Window Value**
    *   Self-critique: Incorrectly specified patterns or line numbers could lead to loading the wrong context or no context at all, causing silent failures.
    *   Confidence: High
2.  **Reduces Operational Costs**
    *   Self-critique: The logic for slicing might add a small amount of compute overhead before the main LLM call.
    *   Confidence: High
3.  **Prevents "Context Overwhelm"**
    *   Self-critique: An agent might still be overwhelmed if the *precisely loaded* context is itself extremely dense or complex.
    *   Confidence: High
4.  **Enhances Security & Data Hygiene**
    *   Self-critique: This relies on the planning agent correctly identifying what is and isn't sensitive. A flawed plan could still load sensitive data.
    *   Confidence: Medium
5.  **Robustness to Change**
    *   Self-critique: Pattern-based slicing is more robust but can still break if key headings or structural elements are changed without updating the corresponding execution plans.
    *   Confidence: Medium

## Alternatives Considered

1.  **Whole-File Loading**: The default, simple approach. Rejected as inefficient and unscalable for any non-trivial project with documentation.
    *   Confidence: High
2.  **Automated Summarization/RAG**: Using an intermediate AI call to summarize a document before adding it to context. Rejected as it adds latency, cost, and a potential layer of information loss or misinterpretation. Direct, precise slicing is more reliable.
    *   Confidence: High

## Consequences

*   **Positive:** Drastically improves the efficiency and effectiveness of agent context. Lowers operational costs. Improves agent focus and output quality.
*   **Negative:** Adds complexity to the context-loading logic within the OS orchestrator. The `BLUEPRINT` phase agent must be sophisticated enough to correctly identify and specify these precise sections when creating `Execution Plans`.

## Clarifying Questions

*   What is the fallback behavior if a `start_pattern` or `end_pattern` is not found in the source artifact?
*   How will this mechanism handle non-text or binary artifacts?
*   How are context loading failures detected, logged, and surfaced to the user or orchestrator?
*   What validation or testing is in place to ensure that context slices are accurate and do not omit critical information?
*   How does the system handle updates to artifact structure that may invalidate existing pattern-based context loading instructions?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
