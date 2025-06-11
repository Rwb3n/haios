# ADR-OS-014: Project Guidelines Artifact

*   **Status:** Proposed
*   **Date:** 2024-05-31 (g value of this session)
*   **Context:**
    To ensure consistency and quality, and to combat AI "drift" or "forgetting" of critical project standards, there is a need for a durable, central repository of project-wide rules, conventions, and procedures. These guidelines must be easily accessible and referenceable by all AI agents during planning and execution phases.

*   **Decision:**
    We will establish the concept of a **`Project Guidelines` artifact store**, which will be a designated collection of Markdown documents within the project workspace (e.g., located at `project_workspace/docs/guidelines/`). These are version-controlled Project Artifacts, complete with `EmbeddedAnnotationBlock`s.

    Key guideline artifacts will be created to house specific types of standards. A crucial initial example is the **`testing_guidelines.md`** artifact, which will contain procedural checklists, such as the **"Bias Prevention Checklist"** for validating test results.

    All relevant `Execution Plan` tasks (e.g., development, testing, validation, critique) **MUST** include a `context_loading_instructions` entry that explicitly loads the appropriate guideline artifacts. The AI agent executing the task is then required to adhere to and/or apply the procedures outlined in the loaded guidelines.

*   **Rationale:**
    *   **Durable Memory:** It provides a persistent, version-controlled "memory" for project-specific rules, preventing reliance on the limited context window of an AI agent session.
    *   **Explicit Instruction:** By forcing tasks to explicitly load these guidelines as context, we make adherence an integral part of task execution, not an optional afterthought.
    *   **Consistency:** Ensures that all agents, regardless of their specialization or the underlying model, are operating from the same set of rules and best practices for the project.
    *   **Auditable Procedures:** The checklists within these guidelines (like the Bias Prevention Checklist) provide a clear, auditable framework for complex tasks like validation. Reports can reference the checklist and show how each item was addressed.
    *   **Evolvability:** As the project evolves and new best practices are discovered (like the agent's self-correction on biased testing), they can be codified into these guideline documents, making the entire system smarter over time.

*   **Implementation Example:**

    1.  A `testing_guidelines.md` artifact is created in `project_workspace/docs/guidelines/` and registered in `global_registry_map.txt`. Its content includes the `Bias Prevention Checklist`.
    2.  An `Execution Plan` of type `CRITICAL_ASSESSMENT` is blueprinted.
    3.  A task within this plan will have the following `context_loading_instructions`:
        ```json
        {
          "context_id": "ctx_bias_checklist",
          "description": "Load the mandatory Bias Prevention Checklist to guide the critical assessment of test results.",
          "load_type": "ARTIFACT_CONTENT",
          "source_reference": { "type": "ARTIFACT_ID", "value": "testing_guidelines_md_artifact_id" },
          "priority": "CRITICAL",
          "is_input_for_prompt": true
        }
        ```
    4.  The agent executing the task receives the content of the checklist as part of its prompt and must structure its response and actions according to the checklist's items.

*   **Consequences:**
    *   **Pros:**
        *   Significantly improves the reliability and consistency of AI agent actions.
        *   Creates a formal feedback loop where operational learning can be captured and standardized.
        *   Makes the AI's adherence to standards explicit and verifiable.
    *   **Cons:**
        *   Adds an extra layer of artifacts to manage.
        *   Requires discipline in the `BLUEPRINT` phase to ensure tasks correctly reference the guideline artifacts.

*   **Alternatives Considered:**
    *   **Embedding all rules in system prompts:** Rejected as it's not version-controlled, not easily auditable per-project, and can quickly bloat the base system prompt.
    *   **Relying on AI's general knowledge:** Rejected as it leads to inconsistent application of standards and "AI drift."