# ADR-OS-037: Adaptive Task Execution Protocol

*   **Status**: Proposed
*   **Date**: 2025-06-26
*   **Deciders**: Architecture Team
*   **Reviewed By**: \[TBD]

---

## Context

Foundation models possess different intrinsic execution capabilities. A "holistic" model may succeed at a complex, single-shot task, while a "literal" model requires explicit, sequential sub-tasking to avoid failure. A rigid Task Executor that attempts all tasks in the same way is inefficient and brittle, failing to leverage the unique strengths of each available model. This ADR formally separates the definition of a task from the strategy used to execute it.

## Assumptions

*   \[ ] Foundation models have predictable and classifiable execution paradigms (e.g., "holistic" vs. "literal").
*   \[ ] The `aiconfig.json` file is the reliable and definitive source for model capability profiles.
*   \[ ] The cost of the internal BLUEPRINT call for task decomposition is less than the cost of a failed or low-quality single-shot execution.
*   \[ ] The system can reliably determine the active persona model and access its profile at runtime.
*   \[ ] The defined execution strategies (Direct and Iterative) cover the majority of required execution paradigms.

## Models/Frameworks Applied

*   **Separation of Duties (Registry v1.0):**
    *   *Proof:* The decision explicitly separates the `what` (the task in the Execution Plan) from the `how` (the execution strategy chosen by the Task Executor). The BLUEPRINT agent defines the former, while the Task Executor dynamically determines the latter.
    *   *Self-critique:* This introduces a new dependency where the Task Executor must have out-of-band knowledge of model capabilities, which could become a point of failure if not maintained.
    *   *Exceptions:* None.
*   **Strategy Pattern (Design Pattern):**
    *   *Proof:* The Task Executor is refactored to act as a dispatcher that selects a specific execution strategy (`DirectExecutionStrategy`, `IterativeDecompositionStrategy`) based on runtime conditions (the model's `execution_paradigm`).
    *   *Self-critique:* Over-engineering is a risk if only two strategies exist. However, it provides a clear extension point for future, more nuanced execution methods.
    *   *Exceptions:* None.

## Decision

Mandate an Adaptive Task Execution Protocol. The Task Executor agent will be a strategy-based dispatcher that dynamically selects the appropriate execution method based on the active foundation model's profile.

**Core Components:**

1.  **Schema Enhancement (`aiconfig.json`):** The `model_profiles` object must contain a `capabilities` object for each model. This object must include the key:
    *   `execution_paradigm`: (Enum: `single_shot_holistic`, `iterative_decomposition_required`)
2.  **Core Logic Refactor (Task Executor):** The Task Executor will implement the Strategy Pattern.
    *   **Flow:**
        1.  Receive Task object.
        2.  Read the `active_persona_model` from `aiconfig.json`.
        3.  Look up the model's `execution_paradigm` in its profile.
        4.  Dispatch to the corresponding execution strategy module.
3.  **Execution Strategies Defined:**
    *   **DirectExecutionStrategy:** Triggered by `single_shot_holistic`. Executes the task as a single, atomic action.
    *   **IterativeDecompositionStrategy:** Triggered by `iterative_decomposition_required`. Initiates a nested loop:
        *   **A (Nested Blueprint):** Make an internal call to the BLUEPRINT agent to decompose the high-level task into sub-tasks.
        *   **B (Sub-Task Loop):** Execute the resulting sub-tasks sequentially.
        *   **C (Finalization):** Mark the parent task as complete only after the sub-task sequence is finished.

**Confidence:** High

## Rationale

1.  **Maximizes Agent Effectiveness:**
    *   Allows the system to leverage the unique strengths of each model by choosing the optimal execution mode.
    *   *Self-critique:* The manual classification of models is subjective and may not capture the full nuance of a model's capabilities.
    *   *Confidence:* High
2.  **Increases Runtime Robustness:**
    *   Proactively avoids errors by selecting a safer, more granular execution path for models known to struggle with complex, single-shot tasks.
    *   *Self-critique:* The nested decomposition loop introduces its own failure modes (e.g., failure in the sub-task planning step).
    *   *Confidence:* Medium
3.  **Decouples Planning from Execution:**
    *   Keeps the primary Execution Plan clean and high-level. The implementation details of task decomposition are abstracted away from the main plan.
    *   *Self-critique:* This abstraction can make debugging more difficult, as the true execution path is not visible in the primary plan artifact.
    *   *Confidence:* High

## Alternatives Considered

1.  **Monolithic Executor:** Continue with a single, rigid execution method.
    *   *Reason for rejection:* Inefficient and brittle, as it fails to adapt to different model capabilities, leading to higher failure rates.
2.  **Bake Decomposition into All Plans:** Require the BLUEPRINT agent to always decompose complex tasks, regardless of the target model.
    *   *Reason for rejection:* Unnecessarily inflates plan complexity and execution time for powerful, holistic models that do not require it.

## Consequences

*   **Positive:**
    *   Improved performance and reliability by matching tasks to the most suitable execution strategy.
    *   Cleaner, more abstract Execution Plans.
    *   Creates actionable data (`strategy_used`) for future automated performance tuning.
*   **Negative:**
    *   Increases the complexity of the Task Executor.
    *   Introduces a new maintenance burden: keeping model capability profiles in `aiconfig.json` accurate and up-to-date.

## Clarifying Questions

*   How will the system handle a model whose `execution_paradigm` is not defined in its profile? Should it default to the safest strategy (iterative)?
*   What is the mechanism for updating model capability profiles as new models are added or existing ones are fine-tuned?
*   Should the `IterativeDecompositionStrategy` have a depth limit to prevent infinite recursion?
*   How are sub-task failures handled within the nested loop? Does a single sub-task failure cause the entire parent task to fail?

---
*This ADR is now compliant with the standards set in ADR-OS-021 and ADR-OS-032.*