# ADR-OS-015: Precision Context Loading

*   **Status:** Proposed
*   **Date:** 2024-05-31 (g value of this session)
*   **Context:**
    Modern Large Language Model (LLM) agents operate within a finite context window. Loading entire documents or artifacts as context for a task is highly inefficient and often counterproductive. It floods the context with irrelevant information, increases operational costs (token usage), and can lead to "context overwhelm" or "prompt contamination," where the agent is distracted or confused by non-essential data.

*   **Decision:**
    We will implement a **Precision Context Loading** mechanism. The `context_loading_instructions` array within each `Task` object in an `Execution Plan` will be enhanced to support granular, targeted data retrieval.

    This will be achieved by adding an optional `source_location_details` object to each context loading instruction. This object will allow the specification of:
    1.  **Line-based slicing:** Using `start_line` and `end_line` numbers to extract a specific portion of a text-based artifact.
    2.  **Pattern-based slicing:** Using `start_pattern` and `end_pattern` (string or regex) to dynamically locate and extract a specific, named section of a document (e.g., a specific chapter in a Markdown file).

    The OS's orchestrator, when preparing a prompt for an agent, **MUST** process these instructions to construct a minimal, highly-relevant context payload.

*   **Rationale:**
    *   **Maximizes Context Window Value:** Ensures that every token included in an agent's prompt is highly relevant to the task at hand, dramatically improving the signal-to-noise ratio.
    *   **Reduces Operational Costs:** Minimizes the number of tokens sent to the LLM API, directly reducing the cost of each task execution.
    *   **Prevents "Context Overwhelm":** Protects the agent from being distracted by irrelevant sections of large documents, improving its focus and the quality of its output.
    *   **Enhances Security & Data Hygiene:** Prevents the accidental inclusion of sensitive information from other parts of a document into a prompt where it is not needed.
    *   **Robustness to Change:** Pattern-based slicing is more resilient to minor document edits (where line numbers might change) than simple line-based slicing.

*   **Implementation Details:**
    *   The `Task Object` schema within `exec_plan_schema.md` will be updated to include the `source_location_details` sub-object in its `context_loading_instructions`.
    *   The agent orchestrator component of the OS engine will be responsible for implementing the file-reading and slicing logic based on these instructions before assembling the final prompt for an AI agent.
    *   An `Execution Plan` task for "onboarding" a new agent can now be a series of context-loading steps that walk the agent through key sections of project documentation, one chunk at a time.

*   **Example Use Case:**
    To instruct an agent to write a test based on a specific ADR section, the `context_loading_instructions` would not load the entire ADR. Instead, it would specify:
    ```json
    {
      "description": "Load only the 'Decision' section of ADR-007.",
      "source_reference": { "type": "ARTIFACT_ID", "value": "adr_007_testing_lifecycle_gX" },
      "source_location_details": {
        "start_pattern": "## Decision",
        "end_pattern": "## Rationale"
      }
    }
    ```

*   **Consequences:**
    *   **Pros:**
        *   Drastically improves the efficiency and effectiveness of agent context.
        *   Lowers operational costs.
        *   Improves agent focus and output quality.
    *   **Cons:**
        *   Adds complexity to the context-loading logic within the OS orchestrator.
        *   The `BLUEPRINT` phase agent must be sophisticated enough to correctly identify and specify these precise sections when creating `Execution Plans`.

*   **Alternatives Considered:**
    *   **Whole-File Loading:** The default, simple approach. Rejected as inefficient and unscalable for any non-trivial project with documentation.
    *   **Automated Summarization/RAG:** Using an intermediate AI call to summarize a document before adding it to context. Rejected as it adds latency, cost, and a potential layer of information loss or misinterpretation. Direct, precise slicing is more reliable.