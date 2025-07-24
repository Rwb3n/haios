 Specification Firewall Protocol
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR formalizes the critical governance policy of blocking all implementation until a clear, consistent, and validated specification is in place. It is a direct response to observed agent failures and operator burnout caused by executing on ambiguous or incomplete plans.
1. Context
Experience within the HAiOS project has repeatedly demonstrated that the single greatest source of wasted effort, agent misalignment, and operator burnout is the act of commencing implementation (CONSTRUCT phase) based on an incomplete, ambiguous, or internally inconsistent specification.
AI Builder agents, unlike human developers, cannot "fill in the gaps" with common sense. They require absolute clarity. An ambiguous specification will invariably lead to a flawed or unexpected implementation, which then requires costly debugging, refactoring, or a full reset.
To solve this problem at its root, we must move beyond treating specifications as simple "documents" and elevate them to the status of formal, binding, and programmatically verifiable contracts. This ADR defines the protocol for this enforcement: The Specification Firewall.
2. Models & Frameworks Applied
Specification-Driven Development (SDD Framework): This protocol is the central enforcement mechanism for the entire SDD framework. It is the gate that ensures the Bridge Layer is complete and correct before the Foundation or Implementation layers can begin.
The "Certainty Ratchet": The firewall is a key "pawl" in our ratchet. It physically prevents the system from moving forward into a state of lower certainty (i.e., a chaotic implementation based on a flawed spec).
Test-Driven Specifications (TDS): The firewall is the "test runner" for our specification tests.
3. Decision
We will implement a Specification Firewall as a mandatory, non-negotiable governance gate between the BLUEPRINT and CONSTRUCT phases of the HAiOS operational loop.
No CONSTRUCT task may be initiated by any agent until its governing Execution Plan and all dependent artifacts have been validated and have received a status of SPECIFICATION_COMPLETE.
This validation will be performed by a new, automated tool: the Specification Linter.
The "Napkin Sketch" of the Firewall in the HAiOS Loop:
Generated code
+--------------------+      +--------------------+      +---------------------------------+
|      ANALYZE       |----->|      BLUEPRINT     |----->|   THE SPECIFICATION FIREWALL    |
| (Create Init Plan) |      | (Create Exec Plan) |      | (Run `Specification Linter`)    |
+--------------------+      +--------------------+      +------------------┬--------------+
                                                                          |
                                                                          | IF FAIL:
                                                                          | - Block
                                                                          | - Report Errors
                                                                          | - Loop back to BLUEPRINT
                                                                          |
                                                                          | IF PASS:
                                                                          |
                                                                          ▼
+--------------------+      +--------------------+      +------------------┴--------------+
|        IDLE        |<-----|       VALIDATE     |<-----|           CONSTRUCT             |
|                    |      |                    |      | (Implementation is now allowed) |
+--------------------+      +--------------------+      +---------------------------------+
Use code with caution.
The Specification Linter (lint/spec_linter.py)
This tool is the automated guardian of the firewall. It is a component of our Plan Validation Gateway (ADR-038) and will be executed automatically by our CI/CD pipeline before any implementation plan is marked as "Ready."
The linter must perform the following checks:
Completeness Check:
Rule: Scans all provided specification artifacts (Execution Plan, ADRs, Schemas) for _placeholder_ text, empty sections, or "TODO" comments.
Failure: Rejects the specification if any incomplete sections are found.
Consistency Check (Cross-Reference Integrity):
Rule: It will run the dependency_linter.py (from ADR-OS-046) to ensure that all links are valid and there are no broken dependencies.
Failure: Rejects if any broken links are found.
Schema Version Check:
Rule: If a plan references a schema (e.g., uses_schema: dialogue_summary_schema-v1.2), the linter must verify that this schema exists and that its version matches the one specified.
Failure: Rejects on version mismatch or missing schema.
Open Questions Check:
Rule: It will scan the ADR Clarification Records associated with any ADRs in the plan's context.
Failure: Rejects the plan if any of its governing ADRs have clarification questions with a Status: OPEN.
4. Consequences
Positive:
Eliminates a whole class of errors: Prevents agents from ever starting work on a flawed or incomplete plan.
Enforces Architectural Discipline: Forces the Planner agent and the Operator to produce high-quality, complete specifications as a prerequisite for action.
Dramatically Reduces Wasted Effort: The cost of fixing a spec is orders of magnitude lower than the cost of fixing the flawed code that results from it.
Negative:
Increases Upfront "Time to Code": This protocol intentionally introduces friction at the beginning of the process. This is a strategic and accepted trade-off. It slows down the start to accelerate the finish.
5. Integration Plan
CI/CD (Appendix H): A new, mandatory job, SpecificationLint, will be added to our pipeline. It must run after the Blueprint phase and before the Construct phase.
Planner Agent (role_planner.md): The Planner's "Definition of Done" for a blueprint is no longer just "the file is written." It is now "the file passes the Specification Linter."
ADR-OS-038 (Plan Validation Gateway): This protocol is a formal, more detailed implementation of the "Semantic & Causal Linting" responsibility of the Gateway.