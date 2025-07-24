ADR-OS-056: The Hook-Based Builder/Validator Protocol
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of a Claude Code session log (Cody_Report_0019) where a Consistency Enforcer (Builder) agent's changes broke tests, this ADR formalizes the use of Claude Code hooks to create an automated, adversarial validation loop.
1. Context
The HAiOS Builder/Validator pattern is a cornerstone of our "Certainty Ratchet." However, our initial implementation relied on a manual, sequential process: a Builder agent would complete its task, and then a human Operator would have to manually trigger a Validator agent to check the work. This is slow, error-prone, and creates a significant bottleneck.
The discovery that a Validator agent's task is a perfect PostToolUse hook provides the key to automating this entire loop. We can now create a system where the very act of a Builder agent completing its work automatically triggers an adversarial review from a Validator agent.
This ADR defines the architecture for this tightly-coupled, automated, and adversarial development loop.
2. Models & Frameworks Applied
The Governance Flywheel (ADR-OS-043): This protocol is the engine of the flywheel's Enforcement -> Feedback cycle. It provides the mechanism to get immediate, automated feedback on every single Execution step.
Separation of Duties: This protocol creates a perfectly balanced adversarial relationship between the Builder (incentivized to complete its task) and the Validator (incentivized to find flaws).
Test-Driven Specifications (TDS): The Validator agent, triggered by the hook, is the automated executor of the Test_Specification.yml for a given initiative.
3. Decision
We will adopt the Hook-Based Builder/Validator Protocol as the canonical model for all CONSTRUCT phase operations that involve code or configuration modification.
This will be implemented by creating a formal PostToolUse hook script that is configured to run after any Edit or Write operation by a Builder agent. This hook will act as an automated Task Dispatcher, immediately commissioning a Validator agent to review the change.
The "Napkin Sketch" of the Hook-Based Validation Loop:
Generated code
+-------------------------------------------------------------+
|    1. BUILDER AGENT (e.g., Consistency Enforcer)            |
|    - Executes an `Edit` or `Write` command on a file.         |
+------------------------------┬------------------------------+
                               |
                               | 2. Claude Code executes the file change.
                               |    Then, it triggers the hook...
                               |
                               ▼
+------------------------------┴------------------------------+
|    3. THE HOOK (`hooks/post_build_validator.py`)              |
|       (Our Automated "Quality Control Officer")             |
+-------------------------------------------------------------+
|                                                             |
|   A. `IDENTIFY CONTEXT`: The hook receives the path of the  |
|      changed file from Claude Code. It uses this to find    |
|      the relevant `Test_Specification.yml` for the initiative.|
|                                                             |
|   B. `DISPATCH VALIDATOR`: The hook uses the `2A Orchestrator`|
|      (or a similar tool) to programmatically invoke the     |
|      `Testing Strategist` (`Validator`) agent.              |
|                                                             |
|   C. `PROVIDE TASK`: The task assignment for the Validator  |
|      is: "Execute all checks defined in Test_Specification.yml|
|      against the recently modified file and produce a       |
|      ValidationReport.md."                                  |
|                                                             |
+------------------------------┬------------------------------+
                               |
                               | 4. The hook waits for the Validator to
                               |    complete and produce its report.
                               |
                               ▼
+------------------------------┴------------------------------+
|    5. THE VALIDATION REPORT (`ValidationReport.md`)         |
|    - Contains `Status: PASS` or `Status: FAIL`.             |
+------------------------------┬------------------------------+
                               |
                               | 6. The hook reads the report status and
                               |    returns the appropriate exit code to
                               |    the original Builder agent.
                               |
                               ▼
+------------------------------┴------------------------------+
|    7. BUILDER AGENT (Receives feedback)                     |
|    - If PASS -> proceeds to its next task.                  |
|    - If FAIL -> receives the `ValidationReport.md` as       |
|      context and is instructed to "Fix the reported issues."|
+-------------------------------------------------------------+
Use code with caution.
4. Consequences
Positive:
Creates a "Self-Healing" Development Loop: Bugs and regressions introduced by a Builder agent are detected and assigned for fixing within seconds, often in the very next turn of the agent's thought process.
Fully Automates the Inner Loop: This automates the most critical feedback loop in software development (Write Code -> Run Tests -> Get Feedback).
Massively Increases Certainty: No code change can be considered "done" until it has passed validation from a separate, specialized agent, all orchestrated automatically.
Negative:
Increased Latency per Step: Each Edit or Write action by a Builder will now be slightly slower, as it must wait for the hook and the Validator to complete. This is an accepted trade-off for the massive increase in reliability.
Requires Robust Tooling: This protocol is entirely dependent on a reliable 2A Orchestrator (to run the Validator) and a well-defined Test_Specification.yml.
5. Integration Plan
ADR-OS-054 (Specification Firewall): The firewall ensures a good Test_Specification.yml exists before this hook is ever allowed to run. They are two parts of the same quality system.
hooks/pattern_linter.py: Our existing plan for a PreToolUse linter will handle static architectural checks. This new PostToolUse hook will handle dynamic functional checks (i.e., running tests). Together they form a complete "lint -> build -> test" cycle for every agent action.
CI/CD: This hook-based system becomes our "inner CI/CD loop," providing continuous integration at the level of a single file edit, long before a formal git commit is ever made.