ADR-OS-036: Multi-Agent LLM (MAL) Protocol
Status: SUPERSEDED
Date: 2025-06-25
Deciders: Architecture Team
Superseded By: ADR-OS-037 (Adaptive Task Execution Protocol) and ADR-OS-038 (Plan Validation & Governance Gateway)
Context
This ADR was an early attempt to formalize multi-agent interaction. The core problem identified was that a single, monolithic LLM agent struggles with complex tasks that require both broad planning and deep, focused execution. The initial hypothesis was that a specialized "Multi-Agent LLM" (MAL) protocol was needed, where different LLM "instances" with different prompts would collaborate on a single task.
The proposed system consisted of:
A "Planner" LLM: Responsible for decomposing a high-level task into a sequence of smaller sub-tasks.
An "Executor" LLM: Responsible for taking a single, well-defined sub-task and executing it.
A "Critique" LLM: Responsible for reviewing the output of the Executor and providing feedback for revision.
This was conceptualized as a "society of models" working in concert.
Decision (Original)
The original decision was to mandate a "MAL-compliant" task runner. Any complex task would be routed to the Planner LLM first, which would generate a dynamic checklist. The runner would then loop through the checklist, passing each item to the Executor and then its output to the Critique, creating a micro-feedback loop for each sub-task.
Rationale for Supersession
This ADR was correct in its identification of the problem but flawed in its proposed solution. It was superseded because subsequent architectural innovations provided a much more robust and elegant solution to the same problem, rendering this approach obsolete.
Conflation of Concerns: The MAL protocol mixed up two distinct problems: how to plan and how to execute. It put the planning logic (decomposition) inside the task execution loop.
Superior Solution: ADR-OS-038 (The Plan Validation & Governance Gateway) correctly moves all planning, decomposition, and validation logic into a dedicated pre-flight stage. The BLUEPRINT agent is the "Planner," and the Plan Linter is the "Critique." This happens before execution even begins, which is far more efficient.
Lack of Adaptability: The MAL protocol assumed a single, fixed pattern of "Plan -> Execute -> Critique" for all tasks. It did not account for the fact that different foundation models have different capabilities.
Superior Solution: ADR-OS-037 (Adaptive Task Execution Protocol) solves this by introducing the concept of execution_paradigm. It recognizes that a powerful "holistic" model doesn't need this complex decomposition, while a "literal" model does. It adapts the execution strategy to the agent, rather than forcing all agents through the same rigid protocol.
Architectural Bloat: This protocol would have created a complex, nested loop inside the main CONSTRUCT phase, making the system harder to reason about and debug.
Superior Solution: The combination of ADR-037 and ADR-OS-038 provides a cleaner Separation of Concerns. The Plan Gateway handles the quality of the plan, and the Adaptive Executor handles the method of execution. This is a more modular, maintainable, and governable architecture.
Conclusion
ADR-OS-036 was a valuable stepping stone in our architectural thinking. It correctly identified the limitations of a single-agent model. However, its proposed implementation has been fully superseded by a more mature and effective set of protocols. It is preserved in an "Archived" state to provide a historical record of our design evolution, demonstrating the Certainty Ratchet in action.