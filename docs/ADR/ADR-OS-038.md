# ADR-OS-038: The Plan Validation & Governance Gateway

*   **Status**: Proposed
*   **Date**: 2025-06-26
*   **Deciders**: Architecture Team
*   **Reviewed By**: \[TBD]

---

## Context

An Execution Plan can be syntactically correct and schema-compliant but still be strategically flawed, economically inefficient, or behaviorally mismatched for its assigned agent. Approving such a plan leads to wasted resources, runtime failures, and low-quality outcomes. This ADR introduces a formal, automated "peer review" for the BLUEPRINT agent's work to prevent such failures.

## Assumptions

*   \[ ] The logic, cost, and behavioral characteristics of a plan can be reliably linted and validated before execution.
*   \[ ] The governing artifacts (`planning_guidelines.md`, `aiconfig.json`) are accurate and available to the linter.
*   \[ ] The benefits of pre-execution validation outweigh the computational cost of running the Plan Linter.
*   \[ ] The Plan Linter is capable of constructing an accurate causal graph of tasks to detect logical errors.
*   \[ ] A sufficiently accurate cost model exists to make economic linting meaningful.

## Models/Frameworks Applied

*   **Evidence-Based Development (Registry v1.0):**
    *   *Proof:* The decision mandates an automated, evidence-based gateway that requires every Execution Plan to pass explicit checks (semantic, economic, behavioral) before it can be approved. The plan itself becomes the evidence to be validated.
    *   *Self-critique:* The linter's checks are only as good as their governing artifacts. An outdated cost model or incomplete planning guideline could provide a false sense of security.
    *   *Exceptions:* None.
*   **Separation of Duties (Registry v1.0):**
    *   *Proof:* It establishes a formal separation between the BLUEPRINT agent (the creator of the plan) and the Plan Linter (the automated reviewer of the plan). This enforces an impartial, automated quality gate.
    *   *Self-critique:* This adds a potential bottleneck. If the linter is slow or overly strict, it could impede development velocity.
    *   *Exceptions:* None.

## Decision

Mandate a new, non-negotiable **Plan Validation Gateway** stage in the HAiOS lifecycle. This gateway consists of a **Plan Linter** that executes a series of automated checks after the BLUEPRINT phase and before the CONSTRUCT phase.

**Core Component: The Plan Linter**

This component will execute three categories of checks:

1.  **Semantic & Causal Linting:**
    *   **Function:** Validates the logical integrity of the plan.
    *   **Checks:** Constructs a causal graph to detect orphan resources, temporal logic errors, and TDD sequence violations.
    *   **Governing Artifact:** `planning_guidelines.md`
2.  **Economic Linting:**
    *   **Function:** Validates the resource efficiency of the plan.
    *   **Checks:** Estimates the plan's cost (tokens, time) against the initiative's budget and recommends more efficient Cookbook recipes.
    *   **Governing Artifact:** `cost_model` section in `aiconfig.json`
3.  **Behavioral Linting:**
    *   **Function:** Validates the plan's suitability for the assigned agent.
    *   **Checks:** Compares task complexity against the target model's capabilities (from `model_profiles` in `aiconfig.json`) and raises a `MODEL_MISMATCH_WARNING` if misaligned.
    *   **Governing Artifact:** `model_profiles` section in `aiconfig.json`

**Confidence:** High

## Rationale

1.  **Shifts Quality Control "Left":**
    *   Moves validation from the expensive, reactive VALIDATE phase to a cheap, proactive linting phase before work begins, saving time and resources.
    *   *Self-critique:* The linter cannot catch all possible strategic flaws, only those that can be programmatically defined.
    *   *Confidence:* High
2.  **Formalizes "Architectural Review":**
    *   Automates the expert checks a senior architect would perform for logic, efficiency, and feasibility, ensuring consistency and rigor.
    *   *Self-critique:* Automation may lack the nuanced judgment of a human reviewer, potentially allowing through plans that are technically correct but strategically unwise.
    *   *Confidence:* Medium
3.  **Harnesses Stochasticity Proactively:**
    *   Acts as a crucial filter that shapes the creative but potentially chaotic output of the BLUEPRINT agent into a plan that is guaranteed to be logical, economical, and executable.
    *   *Self-critique:* An overly aggressive linter could stifle innovative or unconventional plans that might otherwise be successful.
    *   *Confidence:* Medium

## Alternatives Considered

1.  **Manual Peer Review Only:** Rely solely on human engineers to review every plan.
    *   *Reason for rejection:* Slow, expensive, and prone to human error and inconsistency. Not scalable for a highly autonomous system.
2.  **Post-Execution Validation Only:** Catch errors only in the VALIDATE phase.
    *   *Reason for rejection:* Inefficient and wasteful, as it allows flawed plans to consume significant resources before being caught.

## Consequences

*   **Positive:**
    *   Prevents a significant class of errors before they consume resources.
    *   Enforces architectural and economic best practices automatically.
    *   Improves the overall quality and reliability of Execution Plans.
*   **Negative:**
    *   Introduces a new component (the Plan Linter) that must be developed and maintained.
    *   Adds a step to the workflow, which could slightly increase the time from planning to execution.

## Clarifying Questions

*   How will the Plan Linter be implemented and integrated into the CI/CD pipeline?
*   What happens when a plan fails validation? Is there an automated feedback loop to the BLUEPRINT agent for correction?
*   How are the linting rules in the governing artifacts versioned and updated?
*   Should there be a mechanism to manually override the linter for exceptional cases, and if so, how is that governed?

---
*This ADR is now compliant with the standards set in ADR-OS-021 and ADR-OS-032.*