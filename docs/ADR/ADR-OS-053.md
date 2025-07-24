ADR-OS-053: File-Based State Machine Orchestration
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR canonizes the successful, emergent architectural pattern discovered during the development of the 2a_orchestrator_working.py (v1.0) prototype.
1. Context
Early prototypes for multi-step agentic workflows (like the 2A System) assumed a stateful orchestrator that would manage the dialogue history and context in-memory, passing data between steps. This approach, while logical, introduced significant complexity:
State Management: The orchestrator script itself became a complex, stateful application, making it hard to debug and reason about.
** brittleness:** If the orchestrator script crashed mid-process, the entire conversational state was lost.
Agent Interface Complexity: Agents needed to be designed to accept large, complex data payloads as input and return them as output, leading to complex prompt engineering.
The successful v1.0 implementation of the 2A Orchestrator revealed a superior, simpler, and more resilient pattern: treating the filesystem as the state machine.
2. Models & Frameworks Applied
Durable, Co-located Context (HAiOS Pillar): This pattern is the ultimate expression of this principle. The entire state of the workflow is a durable, co-located artifact.
Separation of Concerns: This pattern creates a perfect separation between the Orchestrator (a stateless script) and the State (a durable file).
KISS (Keep It Simple, Stupid): This approach radically simplifies the orchestrator, removing the need for complex in-memory state management.
3. Decision
For all MVP-stage, single-machine agentic workflows, we will adopt the File-Based State Machine pattern as the canonical orchestration model.
The "Napkin Sketch" of the File-Based State Machine:
Generated code
+-----------------------------------+
|   ORCHESTRATOR.PY (Stateless)     |
| - A simple, stateless script.     |
| - Its only job is to command agents.|
+-----------------┬-----------------+
                  |
                  | 1. Command: "Agent A, read
                  |    state.json and append your
                  |    response to it."
                  |
                  ▼
+-----------------┴-----------------+
|   AGENT A (e.g., Claude Code)     |
| - Uses `Read` and `Edit` tools.   |
+-----------------┬-----------------+
                  |
                  | 2. Modifies the file directly.
                  |
                  ▼
+-----------------┴-----------------+
|      STATE.JSON (The State)       |
| - A durable, on-disk file.        |
| - The single source of truth for  |
|   the workflow's state.           |
| - Can be inspected at any time.   |
+-----------------┬-----------------+
                  |
                  | 3. Orchestrator can now
                  |    command Agent B to operate
                  |    on the updated file.
                  |
                  ▼
+-----------------┴-----------------+
|   AGENT B                         |
+-----------------------------------+
Use code with caution.
Core Principles of the Pattern:
The State is the File: A dedicated, structured file (e.g., dialogue.json) is the single source of truth for the workflow's state.
The Orchestrator is Stateless: The main orchestration script (main.py, flow.py) holds no in-memory state related to the workflow's progress. Its job is to read the state file, decide which agent to command next, and issue the command.
Agents are File Manipulators: Agents are commanded with simple, file-based instructions ("Read file X," "Edit file X"). They interact with the durable state artifact directly using their tools.
4. Consequences
Positive:
Extreme Robustness: If the orchestrator script crashes, no state is lost. It can be restarted, read the state file, and resume exactly where it left off.
High Observability: The state of the workflow is always visible and inspectable by simply opening a file. This makes debugging incredibly easy.
Simplified Agent Design: Agents do not need complex inputs/outputs. They just need to know how to read and edit files, which is a core capability of tools like Claude Code.
Perfect for HAIP: This pattern is the perfect implementation of the HAiOS Agent Instruction Protocol (ADR-OS-055), as it forces all context and data to live in files.
Negative:
Performance: This pattern is not suitable for high-frequency, low-latency operations, as it relies on disk I/O. (Accepted trade-off for simplicity and robustness in our current use cases).
Concurrency: This simple model does not handle multiple agents trying to edit the same file at the same time. (Accepted trade-off for single-machine workflows. Distributed workflows will require a more advanced state management system, as described in future ADRs).
5. Integration Plan
2A System: The v1.2 implementation is now the reference implementation for this pattern.
Rhiza Agent: The blueprint for the Rhiza agent must be refactored to use this pattern. Instead of n8n passing data in memory, it will now orchestrate a series of claude-code calls that operate on a central research_session.json file.
Cookbook: This pattern will be added to the Cookbook as recipe_file_based_state_machine.md.