ADR-OS-044: The Three Learning Loops Architecture
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on third-party evaluation feedback and the observed emergent behavior of the Planner agent commissioning its own tools.
1. Context
The HAiOS is designed as a learning system, but the mechanisms for "learning" have so far been implicit in the Governance Flywheel. As the system's complexity and autonomy increase, we require a more formal, explicit architecture for how the system learns and improves.
The third-party evaluation identified the need for "foundational learning loops." The Planner's emergent behavior of commissioning its own tooling demonstrates a practical need for this capability. This ADR defines a formal architecture for three distinct, interacting learning loops, each corresponding to a different level of abstraction and a different agent archetype.
2. Models & Frameworks Applied
The Governance Flywheel (ADR-OS-043): This architecture is the implementation layer for the flywheel. The learning loops are the "engine" that drives the "Improvement" phase of the flywheel.
Systems Thinking (Ackoff): This architecture directly maps to Ackoff's philosophy. The loops represent the mechanisms by which the system analyzes its parts, synthesizes their role in the whole, and improves its overall function.
OODA Loop: Each of the three learning loops is a specialized, long-running OODA loop.
3. Decision
We will adopt a formal "Three Learning Loops" architecture as the canonical model for machine learning and self-improvement within HAiOS. These loops are distinct but interconnected, forming a hierarchy of learning.
The "Napkin Sketch" of the Three Loops:
Generated code
+-------------------------------------------------------------+
|    LOOP 3: THE ORACLE LOOP (Supervision & Anomaly Detection)    |
|    - Learns: "What does 'normal' look like?"                  |
|    - Actor: `Auditor` Agent / `Argus Protocol`                  |
|    - Timescale: Real-time to Hours                             |
+------------------------------------┬--------------------------+
                                     |
                                     | Anomaly alerts trigger...
                                     |
+------------------------------------▼--------------------------+
|    LOOP 2: THE DAEDALUS LOOP (Planning & Causal Reasoning)    |
|    - Learns: "What plan is most likely to succeed?"           |
|    - Actor: `Planner` Agent                                 |
|    - Timescale: Days to Weeks                                 |
+------------------------------------┬--------------------------+
                                     |
                                     | Successful plans generate data for...
                                     |
+------------------------------------▼--------------------------+
|    LOOP 1: THE HEPHAESTUS LOOP (Execution & Policy Learning)  |
|    - Learns: "What is the best way to execute this specific task?" |
|    - Actor: `Builder` Agents (e.g., Claude Code)              |
|    - Timescale: Minutes                                       |
+-------------------------------------------------------------+
Use code with caution.
Loop 1: The Hephaestus Loop (Policy Learning for Execution)
Purpose: To optimize the execution of a single, well-defined task.
Mechanism: Reinforcement Learning from Tool Use and Human Feedback.
Example:
The Planner assigns the task: "Refactor nodes.py to use the Atomic Node pattern."
The Builder agent (Claude Code) tries to perform the refactoring. Its initial attempt fails the Pattern Integrity Linter hook. This is negative feedback.
The agent receives the linter's error message. It tries a different approach, breaking the classes into separate files. This passes the hook and subsequent tests. This is positive feedback.
Over time, the agent learns a "policy" that "refactoring tasks of this type are more successful when files are split." This learned policy can be stored as a Cookbook recipe.
Implementation: This loop is primarily implemented via our Hook-Based Validation system and the feedback mechanism of the Claude Code agent itself.
Loop 2: The Daedalus Loop (Causal Learning for Planning)
Purpose: To improve the strategic planning of entire Execution Plans.
Mechanism: Causal inference from historical project data.
Example:
The HAiOS has a history of 50 completed Initiative Plans.
The Planner agent is tasked with creating a new plan.
It first queries the historical data (the global_registry_map and Validation Reports): "What is the historical correlation between Initiatives that had a Test_Specification.yml and those that were completed on time and under budget?"
The agent finds a strong positive correlation.
It learns a causal rule: "Plans with explicit, upfront Test Specifications are more likely to succeed."
Therefore, for its new plan, it will create a high-priority task to "Draft the Test_Specification.yml" during the Bridge layer.
Implementation: This requires the Planner to have read-access to our historical database (NocoDB) and the ability to perform statistical analysis. The emergent behavior you observed (commissioning its own tracking tools) is a primitive form of this loop.
Loop 3: The Oracle Loop (Anomaly Detection for Supervision)
Purpose: To monitor the entire system for behavior that deviates from the established "normal" and to alert the Supervisor (human or AI).
Mechanism: Unsupervised learning (anomaly detection) on system-wide observability data.
Example:
The Auditor agent (implementing the Argus Protocol) ingests all system metrics from Prometheus (ADR-OS-019).
It builds a statistical model of "normal" behavior (e.g., "A typical CONSTRUCT phase for a Python script uses 2,000-5,000 tokens and takes 3-5 minutes.").
A new Execution Plan starts. The Builder agent enters a loop and consumes 500,000 tokens.
The Oracle Loop detects this massive deviation from the norm. It doesn't know why it's happening, only that it is anomalous.
It triggers an alert to the Supervisor: "ANOMALY DETECTED: Token usage in plan EXEC-123 is 100x above the historical average. Manual review required."
Implementation: This is the direct implementation plan for the Argus Protocol (ADR-OS-039).
4. Consequences
Positive:
Provides a clear, formal architecture for how HAiOS will learn and self-improve at every level of abstraction.
Gives each agent archetype (Builder, Planner, Auditor) a specific learning mandate.
Creates a virtuous cycle: better execution data from the Hephaestus Loop improves the planning data for the Daedalus Loop, which in turn creates better-defined norms for the Oracle Loop to monitor.
Negative:
This is a highly ambitious, long-term vision. Implementing all three loops will be a major engineering effort.
