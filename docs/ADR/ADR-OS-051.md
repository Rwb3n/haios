ADR-OS-051: The "Committee of Experts" Pattern
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of the OWL stock-analysis agent and the ElizaOS Action-Provider-Evaluator cycle, this ADR canonizes a powerful, reusable pattern for complex problem-solving.
1. Context
Many complex tasks cannot be solved effectively by a single, monolithic AI agent. Problems such as "analyze this company's stock" or "perform a deep architectural review" are not singular tasks; they are multi-faceted problems requiring different types of expertise, reasoning, and even conflicting viewpoints to arrive at a robust conclusion.
A single agent attempting such a task is prone to bias, shallow analysis, and a failure to see the problem from multiple perspectives. Our analysis of mature, external agentic frameworks (OWL, ElizaOS) and our own 2A System has shown that a superior pattern exists: decomposing the problem into a "society" of specialized agents who collaborate.
This ADR formalizes this pattern, which we will call the "Committee of Experts," and establishes it as a canonical Cookbook recipe for all HAiOS Planner agents.
2. Models & Frameworks Applied
Separation of Duties (ADR-OS-030 / 048): This pattern is a direct, high-level application of this principle. Instead of just separating Builder from Validator, we are separating different types of analytical and creative duties.
Adversarial Dialogue (2A System): The pattern explicitly includes an adversarial step, which is crucial for the "Certainty Ratchet" to function.
GenAI Processors (ADR-OS-052): The genai-processors library, with its processor.chain (+) operator, is the ideal runtime framework for implementing this pattern as a linear pipeline.
3. Decision
We will adopt the "Committee of Experts" as a canonical, high-level architectural pattern for solving any complex analysis, synthesis, or strategic planning task within HAiOS.
The Planner agent, when faced with such a task, must decompose its Execution Plan into a PocketFlow or genai-processors graph that follows this six-stage pipeline.
The "Napkin Sketch" of the Committee Pipeline:
Generated code
+-------------------------------------------------------------+
|    INPUT: A complex, ambiguous question                     |
|    (e.g., "Is this a good stock to invest in?")              |
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 1: DATA INGESTION (The "Interns")                  |
|    - A team of simple, parallel agents.                     |
|    - Each fetches one type of raw data (market data, news, etc).|
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 2: SPECIALIZED ANALYSIS (The "Analysts")           |
|    - A team of specialist agents.                           |
|    - Each analyzes the data from a single viewpoint         |
|      (Technical, Fundamental, etc.).                        |
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 3: ADVERSARIAL REVIEW (The "Bull" vs. "The Bear")  |
|    - Two agents are tasked with taking opposite sides.      |
|    - Each constructs the strongest possible argument for its case.|
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 4: SYNTHESIS (The "Debate Moderator")              |
|    - A single agent receives the bull and bear cases.       |
|    - Its job is to synthesize a single, balanced verdict.   |
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 5: GOVERNANCE (The "Risk Manager")                 |
|    - A specialist agent checks the verdict against a set of |
|      formal rules or constraints (e.g., risk policies).     |
+------------------------------┬------------------------------+
                               |
                               ▼
+------------------------------┴------------------------------+
|    STAGE 6: DECISION (The "Portfolio Manager")              |
|    - A final agent takes the governed synthesis and makes   |
|      a single, actionable decision (e.g., "BUY/SELL/HOLD"). |
+-------------------------------------------------------------+
Use code with caution.
4. Consequences
Positive:
High-Quality, Robust Outputs: This pattern forces a multi-perspective analysis, reducing bias and shallow conclusions. The adversarial step is critical for uncovering hidden risks.
Traceability and Auditability: The output of each stage is a distinct, durable artifact. This creates a perfect "Evidence Chain" showing how a final decision was reached.
Agent Specialization: It allows us to use smaller, simpler, and more reliable specialist agents instead of relying on one massive, monolithic "super-agent."
Parallelism: The Ingestion and Analysis stages can often be run in parallel, improving performance.
Negative:
Increased Orchestration Complexity: This is a multi-step workflow that requires a more sophisticated orchestration graph (PocketFlow or genai-processors).
Higher Token Cost: Running a half-dozen specialized agents will consume more tokens than a single agent call. This is an accepted trade-off for higher quality and certainty.
5. Integration into HAiOS
Cookbook: A new, high-priority recipe named recipe_committee_of_experts.md will be created, documenting this pattern and providing a template PocketFlow graph.
Planner Agent: The Planner's core prompt (role_planner.md) will be updated to include this pattern. When it detects a complex analysis task, its OODA loop will now guide it to DECIDE on using this specific pipeline.
2A System: Our own 2A System is a simplified, two-node version of this pattern (Architect-1 is the Analyst, Architect-2 is the Adversarial Reviewer). This ADR provides the blueprint for expanding it with more sophisticated stages in the future.