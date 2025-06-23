# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_013_md",
        "g_annotation_created": 13,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 13, "identifier": "Hybrid_AI_OS" },
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

# ADR-OS-013: Pre-Execution Readiness Checks

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

Executing a task within an `Execution Plan` can be computationally expensive and may have side effects. Attempting to execute a task when its environmental prerequisites (e.g., required tools, configuration files, dependencies, input artifacts) are missing or invalid leads to guaranteed failure, wasted resources, and potentially corrupted state. A proactive mechanism is needed to verify that a task is ready to be executed *before* its primary work commences.

## Assumptions

*   [ ] The executing agent has the necessary permissions to check for all required prerequisites on the filesystem.
*   [ ] The cost of performing the readiness check is significantly lower than the cost of a failed task execution.
*   [ ] The information in `global_registry_map.txt` is up-to-date and accurate.
*   [ ] The readiness check logic is robust against transient and distributed environment changes.
*   [ ] The system can detect and recover from partial or failed readiness checks.
*   [ ] The readiness check process is idempotent and auditable.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Fail-Fast Principle v1.0
- **Compliance Proof:** Readiness Check as mandatory first step prevents expensive task failures by catching environmental issues early.
- **Self-Critique:** For simple, low-risk tasks, formal check overhead might slightly outweigh benefit.

### KISS (Keep It Simple, Stupid) v1.0
- **Compliance Proof:** Simple pass/fail readiness check with clear BLOCKED status and issue creation for failures.
- **Self-Critique:** Readiness agent itself might require significant context, shifting complexity rather than eliminating it.

### Distributed Systems Principles v1.0
- **Compliance Proof:** "Distributed Systems Implications" section addresses idempotency and observability for readiness checks.
- **Self-Critique:** Missing explicit handling of network dependencies and service availability checks.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about agent permissions, check costs, and registry accuracy.
- **Self-Critique:** Only three assumptions listed; readiness checking likely has more implicit assumptions about environment stability.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between environmental verification (readiness) and task execution (primary work).
- **Self-Critique:** Quality of BLOCKER issue depends on quality of checking logic; poor check could lead to misleading issue.

## Decision

**Decision:**

> We will mandate that a **"Readiness Check"** is the first step in the execution of any task within the `CONSTRUCT` phase.
>
> This check is a formal, non-negotiable procedure where the executing agent verifies the existence, accessibility, and basic validity of all environmental prerequisites for the task. The prerequisites are determined by analyzing the task's `inputs` and, crucially, its `context_loading_instructions`.
>
> If the Readiness Check fails:
> 1.  The agent **MUST NOT** proceed with the main execution of the task.
> 2.  The agent **MUST** set the task's `status` to `BLOCKED`.
> 3.  The agent **MUST** log a new `Issue` of type `BLOCKER`, detailing precisely which prerequisites are missing or invalid.
> 4.  The agent's work on the task ceases, and the OS waits for a `REMEDIATION` plan to fix the environment before the original task can be retried.
>
> The output of a successful Readiness Check can be a simple internal "pass" or, for complex tasks like test execution, it can be a formal **`Readiness Assessment`** artifact (.md) detailing the status of all components.
>
> ### Implementation within the `CONSTRUCT` Phase
>
> The `AI_Execute_Next_Viable_Task_...` core action will be updated to include this logic:
>
> ```
> 1. Select viable task.
> 2. Update state.ct_id to this task.
> 3. --> **PERFORM READINESS CHECK for the task:**
>        a. Parse task.inputs and task.context_loading_instructions.
>        b. Verify existence of all referenced artifact IDs in `global_registry_map.txt`.
>        c. Verify existence of required files/tools on the file system (e.g., `.env.local`, `k6` binary if needed).
>        d. Verify project dependencies are installed (e.g., `node_modules` exists if `package.json` is a context).
>        e. **IF CHECK FAILS:**
>           i.   Update task status to `BLOCKED`.
>           ii.  Create a `BLOCKER` issue with details.
>           iii. Update state.st to `BLOCK_INPUT` (awaiting remediation plan).
>           iv.  Cease processing this task.
>        f. **IF CHECK PASSES (and is complex enough to warrant it):**
>           i.   Optionally generate a `readiness_assessment_gX.md` artifact.
> 4. --> **EXECUTE PRIMARY TASK WORK (only if Readiness Check passed).**
> 5. ... (Continue with normal task completion logic).
> ```
>
> ### Distributed Systems Implications
>
> The Readiness Check procedure must be designed for a distributed environment.
>
> *   **Idempotency (ADR-OS-023):** The entire Readiness Check process MUST be idempotent. Running the check multiple times on an unchanged environment must yield the same result without causing side effects. This is critical for retrying a `BLOCKED` task after a remediation plan has run.
> *   **Observability (ADR-OS-029):** The start, pass, and fail outcomes of every Readiness Check MUST be recorded as distinct events within the task's distributed trace. A failed check's event must contain structured data about which specific prerequisite failed, enabling automated analysis of systemic environmental issues.

**Confidence:** High

## Rationale

1.  **Fail-Fast Principle**
    *   Self-critique: For some very simple, low-risk tasks, the overhead of a formal check might slightly outweigh the benefit.
    *   Confidence: High
2.  **Reduces "Context Overwhelm"**
    *   Self-critique: The "readiness" agent itself might require significant context to perform its checks correctly, shifting complexity rather than eliminating it.
    *   Confidence: Medium
3.  **Explicit Error Reporting**
    *   Self-critique: The quality of the `BLOCKER` issue is dependent on the quality of the checking logic; a poor check could lead to a misleading issue.
    *   Confidence: High
4.  **Improved System Stability**
    *   Self-critique: This doesn't prevent logical errors within the task itself, only environmental ones. The system can still enter an inconsistent state due to flawed task logic.
    *   Confidence: High

## Alternatives Considered

1.  **No Explicit Check (Reactive Failure)**: Letting tasks fail mid-execution and then trying to parse the error logs. Rejected as messy, unreliable, and provides poor-quality error reporting.
    *   Confidence: High
2.  **A Single Validation Phase for Environment**: Having one big check at the beginning of an `Execution Plan`. Rejected because different tasks within the same plan may have different environmental needs, making a single upfront check insufficient or overly broad. A per-task check is more precise.
    *   Confidence: High

## Consequences

*   **Positive:** Dramatically increases the reliability and robustness of task execution. Makes debugging environmental setup issues straightforward via the generated `BLOCKER` issues. Fits perfectly with the "separation of concerns" principle for agent actions.
*   **Negative:** Adds a small amount of overhead at the beginning of every task for the verification step. This is a highly worthwhile trade-off for the increased reliability.

## Clarifying Questions

* How are complex dependencies (e.g., service availability over a network) handled by this check, and how is this coordinated with ADR-OS-026 and ADR-OS-028?
* What is the retry policy for a task that fails its readiness check, and how are repeated failures escalated or audited?
* How is readiness state and prerequisite verification kept consistent and up-to-date in distributed or rapidly changing environments?
* What mechanisms are in place to audit, trace, and analyze readiness check failures for systemic issues?
* How is the readiness check logic versioned and evolved as new types of prerequisites or environmental requirements are identified?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*