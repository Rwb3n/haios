ADR-OS-055: The HAiOS Agent Instruction Protocol (HAIP)
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR canonizes a critical, emergent security and governance pattern discovered during the validation of the 2A_Orchestrator v1.2 prototype.
1. Context
Initial designs for HAiOS agent orchestration involved constructing complex prompts that embedded large amounts of data and context directly into the prompt string. For example, a Summarizer agent's prompt might contain the entire raw JSON of the dialogue it needed to summarize.
This approach has been proven to be flawed and dangerous. It suffers from several critical vulnerabilities:
Context Window Limitations: It is not scalable. As the context grows, it quickly exceeds the agent's context window.
Risk of "Prompt Injection": If the embedded data contains text that looks like an instruction, it can confuse the agent and cause it to deviate from its primary task. This is a vector for the "Lethal Trifecta."
Lack of Traceability: The context provided to the agent is ephemeral. It exists only for the duration of a single API call, leaving no durable audit trail of what information the agent was actually working with.
Agent Hallucination of Structure: It allows the agent to control the structure of its output (e.g., deciding what role name to use in a JSON object), which can lead to inconsistencies and data corruption.
The successful v1.2 implementation of the 2A Orchestrator revealed a far superior pattern based on a strict separation of duties between the orchestrator and the agent. This ADR formalizes this pattern.
2. Models & Frameworks Applied
Separation of Duties: This protocol creates the ultimate separation of duties. The Orchestrator is responsible for structure and metadata. The Agent is responsible only for content.
Durable, Co-located Context (HAiOS Pillar): This protocol is the purest implementation of this principle. It mandates that all context must exist as a durable, on-disk artifact before an agent is called.
"Lethal Trifecta" Mitigation: This protocol is a primary defense against the trifecta. By preventing the agent from controlling its output structure and metadata, we architecturally sever the link that could allow it to perform a malicious write or data exfiltration in a structured field.
3. Decision
We will adopt the HAiOS Agent Instruction Protocol (HAIP) as the mandatory, non-negotiable standard for how all HAiOS Orchestrator components command Builder agents (like Claude Code).
The protocol is defined by three core principles.
The "Napkin Sketch" of the HAIP Flow:
Generated code
+------------------------------------------+
|      ORCHESTRATOR (e.g., PocketFlow Node)  |
+--------------------┬---------------------+
                     |
                     | 1. The Orchestrator prepares the "canvas."
                     |    It writes a "skeleton" entry to the
                     |    state file (`dialogue.json`), filling in
                     |    all metadata (`role`, `timestamp`, etc.).
                     |    The `content` field is left empty.
                     |
                     ▼
+--------------------┴---------------------+
|      STATE FILE (`dialogue.json`)        |
| - { "role": "Architect-1", "content": "" } |
+--------------------┬---------------------+
                     |
                     | 2. The Orchestrator issues a simple,
                     |    file-based command to the agent.
                     |    NO data is embedded in the prompt.
                     |
                     ▼
+--------------------┴---------------------+
|      AGENT (e.g., Claude Code)           |
|  - Receives prompt: "Read dialogue.json   |
|    and use the Edit tool to fill the      |
|    'content' of the last entry."          |
+--------------------┬---------------------+
                     |
                     | 3. The Agent uses its tools to read the
                     |    state file and then performs a targeted
                     |    edit on ONLY the 'content' field.
                     |
                     ▼
+--------------------┴---------------------+
|      STATE FILE (`dialogue.json`)        |
| - { "role": "Architect-1", "content": "..." } |
+------------------------------------------+
Use code with caution.
HAIP Core Principles:
NO CONTENT EMBEDDING IN PROMPTS: An agent's prompt must not contain the data it is supposed to process. The prompt must only contain the instructions and pointers to the file(s) where the data resides.
ORCHESTRATOR CONTROLS METADATA: The trusted, deterministic Orchestrator code (e.g., our PocketFlow nodes) is solely responsible for creating and managing the structure and metadata of all artifacts. Before calling an agent to contribute to a file, the orchestrator must first create the "skeleton" of the entry, populating all fields (role, round, timestamp, etc.) except for the content itself.
AGENT CONTROLS CONTENT ONLY: The LLM agent's permission, both via the prompt and via its allowed_tools, must be restricted to modifying only the content field of a pre-existing data structure. It is never allowed to define its own role, alter timestamps, or change the schema of the artifact.
4. Consequences
Positive:
Drastically Improved Security: Prevents a wide class of prompt injection and data corruption attacks by architecturally limiting the agent's "blast radius."
Enhanced Reliability: Ensures that all generated artifacts have a consistent, predictable structure, as the structure is controlled by deterministic code, not a stochastic LLM.
Perfect Auditability: The "skeleton" entry created by the orchestrator serves as a perfect, immutable record of the intent of an agent call, even before the agent has responded.
Scales to Infinite Context: This pattern completely solves the context window problem. The agent's context is the entire filesystem, accessible via its Read tool.
Negative:
Increased I/O: This pattern is more "chatty" with the filesystem. An agent must first Read a file and then Edit it, whereas the old pattern was a single API call. This is an accepted trade-off for security and reliability.
