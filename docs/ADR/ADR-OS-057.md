ADR-OS-057: The 2A Dialogue System Architecture
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR formally documents the architecture of the successful v1.3 implementation of the "2A System" (2a_orchestrator), our first machine-orchestrated agentic workflow for architectural validation.
1. Context
The HAiOS Clarification & Canonization Protocol (ADR-OS-040) requires a robust mechanism for performing the "Adversarial Dialogue" between Architect-1 (Proposer) and Architect-2 (Adversarial Synthesizer). Initial attempts to manage this dialogue manually proved to be a major bottleneck, source of operator burnout, and were prone to "Contextual Amnesia."
To solve this, we initiated a CONSTRUCT phase to build an automated orchestrator. This process went through several iterations, culminating in a stable, robust v1.3 implementation. This ADR canonizes the final, successful architecture of that system.
2. Models & Frameworks Applied
This system is a practical, ground-truth implementation of several core HAiOS principles:
PocketFlow (EXEC_PLAN_REFACTOR_ATOMIC_NODES): The entire system is architected as a declarative PocketFlow graph, using modular, single-responsibility "Atomic Nodes."
File-Based State Machine (ADR-OS-053): The orchestrator is stateless. The complete state of the dialogue is durably persisted in a dialogue.json file, which the agents read from and write to.
HAiOS Agent Instruction Protocol (HAIP) (ADR-OS-055): The orchestrator follows the strict HAIP standard, creating "skeleton" entries in the state file and commanding agents with simple, file-based instructions, ensuring the agent only ever modifies the content field.
The "Certainty Ratchet": The entire purpose of the 2A system is to act as the engine for the "Certainty Ratchet," transforming low-certainty questions into high-certainty, canon-compliant specifications.
3. Decision
The official architecture for the 2A Dialogue System is a PocketFlow-based, stateless orchestrator that directs Claude Code agents to manipulate a durable, file-based state machine according to the HAIP standard.
The "Napkin Sketch" of the v1.3 Architecture:
Generated code
+-------------------------------------------------------------+
|          main_clean.py (The Stateless Orchestrator)           |
|  - Creates the PocketFlow `AsyncFlow` object.                 |
|  - Initializes the `shared` state dictionary with file paths.|
|  - Calls `flow.run_async(shared)`.                           |
+-------------------------------------------------------------+
                           |
                           | Manages the execution of...
                           ▼
+-------------------------------------------------------------+
|             flow_clean.py (The Declarative Graph)             |
|                                                             |
|  ConsensusCheck -> Summarizer -> ReadPrompt(A1) -> Update(A1) |
|                                                       |     |
|                                                       ▼     |
|                              ReadPrompt(A2) -> Update(A2) --+ (loops back to ConsensusCheck)
|                                                             |
+-------------------------------------------------------------+
                           |
                           | The Nodes in the graph operate on...
                           ▼
+-------------------------------------------------------------+
|            output_2A/session_XYZ/ (The State Files)           |
|  - dialogue.json (The ground truth, appended to by agents)  |
|  - summary.md (The context memory, written by Scribe agent) |
+-------------------------------------------------------------+
Use code with caution.
Core Components:
Orchestrator (main_clean.py): The entry point. Its only job is to set up the initial files and the shared state object, and then execute the PocketFlow graph.
Flow Definition (flow_clean.py): A declarative, readable definition of the dialogue process. It defines the connections and conditional logic (e.g., "continue" vs. "consensus").
Atomic Nodes (nodes/ directory): A collection of modular, single-responsibility AsyncNode classes.
ConsensusCheckNode: Reads dialogue.json to see if the loop should terminate.
SummarizerNode: Creates the context memory by writing to summary.md.
ReadPromptNode: A reusable node that reads a persona's prompt file.
UpdateDialogueNode: A reusable, HAIP-compliant node that first creates a skeleton entry in dialogue.json and then commands an agent to fill in the content.
Durable State (dialogue.json, summary.md): The complete state of the conversation, stored as traceable, on-disk artifacts.
4. Consequences
Positive:
This architecture is robust and resilient. A crash in the orchestrator does not destroy the state of the conversation.
It is highly maintainable and extensible. To change the dialogue flow, we only need to edit the simple graph definition in flow_clean.py. To change an agent's behavior, we only need to edit its specific Node class.
It is secure and governable. The use of HAIP and persona-based tool restrictions provides strong guardrails against agent misalignment.
It works. It has been successfully used to automate the generation of architectural dialogues.
Negative:
The file-based approach introduces I/O latency. For this specific, low-frequency use case, this is an acceptable trade-off.