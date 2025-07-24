ADR-OS-045: The Self-Improvement Protocol & Modification Boundaries
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR is a direct successor to ADR-OS-044 (The Three Learning Loops). It defines the governance framework that allows the system to act upon its own learnings safely.
1. Context
ADR-OS-044 provides the architecture for HAiOS to learn and generate insights about its own performance. However, insight without action is useless. For the system to become truly autonomous and self-improving, it needs a protocol for translating those insights into modifications of its own core logic, architecture, and behavior.
This capability is profoundly powerful and equally dangerous. An unconstrained self-modification protocol could lead to catastrophic failures, security vulnerabilities, or a complete deviation from the Operator's intent.
This ADR defines the Self-Improvement Protocol: a set of strict boundaries, permissions, and validation gates that govern how, when, and what parts of the HAiOS canon the system is allowed to modify autonomously.
2. Models & Frameworks Applied
The Three Learning Loops (ADR-OS-044): This protocol is the "actuator" for the learning loops. The loops provide the "why"; this protocol provides the "how."
Specification-Driven Development (SDD Framework): The protocol mandates that any proposed self-improvement must first be rendered as a formal Specification Artifact (e.g., a proposed change to an ADR) before it can be implemented.
The "Hook Firewall" (from Builder/Validator pattern): The validation of any self-modification will be performed by automated, hook-based linters and tests, ensuring changes do not violate core principles.
3. Decision
We will adopt a formal Self-Improvement Protocol based on a tiered system of Modification Boundaries. Different parts of the HAiOS canon will have different levels of protection, requiring different levels of authorization for an autonomous agent to modify them.
The "Napkin Sketch" of Modification Boundaries:
Generated code
+-------------------------------------------------------------+
|    TIER 3: THE KERNEL (Operator-Only, Immutable by AI)        |
|    - The Genesis Architect Notes, The SDD Framework          |
|    - The Core Philosophy & Prime Directive                   |
+-------------------------------------------------------------+
              ^
              | Requires explicit Operator command
              | to modify.
+-------------|-----------------------------------------------+
|    TIER 2: THE GOVERNANCE LAYER (Supervisor Approval Required)|
|    - ADRs, The Anti-Patterns Registry, Security Guidelines   |
|    - The schemas for core artifacts (`dialogue.json`, etc.)  |
+-------------|-----------------------------------------------+
              ^
              | Requires a formal proposal that passes
              | the Plan Validation Gateway AND is signed
              | off by a Supervisor-level agent.
+-------------|-----------------------------------------------+
|    TIER 1: THE OPERATIONAL LAYER (Autonomous with Validation)|
|    - Cookbook Recipes, Linter Rules, Test Specifications     |
|    - Agent Personas, n8n/PocketFlow Workflows              |
+-------------------------------------------------------------+
Use code with caution.
Tier 1: The Operational Layer (Autonomous with Validation)
Scope: Artifacts that define how work is done, but not the fundamental rules of the system. This includes Cookbook recipes, PocketFlow graphs, agent persona prompts, and the rules for our linters.
Modification Protocol:
The Daedalus Loop (Planner agent) identifies a potential improvement (e.g., "The PocketFlow graph for the 2A System could be made more efficient by adding a caching node.").
It generates a formal REFACTORING_EXECUTION_PLAN, including a proposed diff of the change.
This plan is submitted to the Plan Validation Gateway. The Gateway runs a battery of automated checks: Does the new PocketFlow graph still pass our pattern_linter? Do the changes pass all regression tests in a sandboxed environment?
If validation passes, the change is automatically approved and merged.
Agent Authority: The Planner agent has the authority to propose and execute changes at this tier, subject to automated validation.
Tier 2: The Governance Layer (Supervisor Approval Required)
Scope: Core architectural and governance artifacts, including most ADRs, Schemas, and Security Guidelines. These define the rules of the game.
Modification Protocol:
The Daedalus Loop identifies a potential improvement (e.g., "Our analysis shows that ADR-OS-042 is missing a key security consideration for data residency.").
It generates a proposed new version of the ADR as a diff or a new file.
This proposed change is submitted to the Plan Validation Gateway for a full battery of consistency and dependency checks.
If the Gateway approves the change as "safe and consistent," it is then placed in a human_attention_queue.txt for a Supervisor (initially, you, the Operator) to review.
The change is only merged after a formal, signed approval from the Supervisor.
Agent Authority: The Planner can propose changes, but cannot commit them. Authority is delegated to the Supervisor.
Tier 3: The Kernel (Immutable by AI)
Scope: The foundational, philosophical documents that define the system's core purpose and identity. This includes the Genesis_Architect_Notes, ADR-OS-000 (SDD Adoption), and any document that defines the prime directive (e.g., "Achieve Operator Sustainability").
Modification Protocol:
No autonomous modification is permitted under any circumstances.
The Planner agent can propose changes to these documents, but they are flagged as KERNEL_MODIFICATION_REQUEST and require your direct, manual intervention and git commit.
Agent Authority: None. This layer is the source of the agent's authority and thus cannot be changed by it.
4. Consequences
Positive:
Provides a clear, safe, and auditable path for the system to autonomously improve itself.
Protects the core integrity and intent of the system while allowing for operational flexibility and optimization.
The tiered structure ensures that the risk of a proposed change is proportional to the level of authorization required.
Negative:
This is a highly sophisticated protocol that will require significant work to implement, especially the automated validation gates.
It places a high degree of trust in the Plan Validation Gateway. The quality of our automated checks becomes paramount.