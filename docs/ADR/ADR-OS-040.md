ADR-OS-040: Clarification & Canonization Protocol
Status: Proposed
Date: 2025-07-11
Deciders: Founding Operator, Genesis Architect
Reviewed By: Self-reviewed via this process
Context
As the HAiOS architecture grows, the number of ADRs and their interdependencies increase. The initial ADRs often leave open "clarifying questions" that must be resolved to ensure a robust implementation. A simple, unstructured Q&A process risks creating knowledge silos, context drift, and non-auditable decisions.
The system requires a formal, repeatable, and auditable protocol for resolving these open questions and integrating the resulting consensus back into the core architectural canon. This process must embody the core HAiOS principles of evidence, traceability, and structured governance. It is the practical application of the "Certainty Ratchet" to the architecture itself.
Assumptions
A purely conversational or ad-hoc process for resolving architectural ambiguity is insufficient and risky.
The "Adversarial Dialogue" between two distinct architectural personas (a "Proposer" and a "Synthesizer") is an effective method for pressure-testing ideas and forging a high-certainty consensus.
The output of this process must be a durable, version-controlled artifact (ADR Clarification Record).
The new knowledge gained from a clarification is only truly "canonized" when it is verifiably integrated back into the affected core architectural documents (ADRs, Schemas, Appendices).
This entire process can be governed by a formal template and a defined workflow.
Models/Frameworks Applied
Certainty Ratchet (Custom Model):
Proof: The entire protocol is designed as a mechanism that takes low-certainty open questions and, through a structured, adversarial process, transforms them into high-certainty, canonized architectural decisions. There is no path for ambiguity to increase.
Separation of Duties (ADR-OS-030):
Proof: The protocol mandates distinct roles: Architect-1 (Proposer), whose job is to create solutions; Architect-2 (Adversarial Synthesizer), whose job is to critique and test them; and the Scribe, whose job is to record and synthesize the final consensus. This prevents flawed self-validation.
Evidence-Based Development (Genesis Architect Notes):
Proof: The final consensus is not based on a simple declaration of agreement. It is based on the evidence of the full, turn-by-turn dialogue, which is preserved in its entirety as an auditable record.
Assumption Surfacing (ADR-OS-021):
Proof: The protocol's official artifact template mandates the explicit enumeration of the final agreed-upon assumptions, dependencies, risks, and mitigations that underpin the consensus decision.
Decision
We will adopt a formal Clarification & Canonization Protocol for resolving all open questions related to existing ADRs. The protocol consists of two primary components: a standardized artifact template and a defined workflow.
1. The ADR Clarification Record Artifact
This is the standard artifact produced by the protocol, defined in docs/templates/ADR_Clarification_Template.md. Its key sections are:
Header: Captures formal metadata (Subject, Status, Decision Date, Participants).
Final Consensus Summary: A human-readable synthesis of the final decision.
Final Context & Assumptions: The agreed-upon assumptions, dependencies, risks, and mitigations for the solution.
Full Dialogue Record: The complete, turn-by-turn, verbatim transcript of the dialogue between Architect-1 and Architect-2.
Canonization & Integration Directives: The critical "commit" section, which includes:
Synthesis of Final Consensus: A technical summary of the outcome.
Architectural Artifacts to be Modified: A checklist of specific files to be created or updated. This serves as the input for a subsequent REMEDIATION plan.
New Terminology for Global Glossary: A list of new terms defined during the dialogue.
2. The Three-Phase Workflow
Phase 1: Adversarial Dialogue
The process is initiated with a new ADR Clarification Record artifact.
Architect-1 proposes a solution.
Architect-2 critiques and dissents.
The dialogue continues turn-by-turn until Architect-2 declares "No Further Dissent."
Phase 2: Scribe Synthesis
The Scribe (the human operator or a designated agent) analyzes the completed dialogue.
The Scribe populates the top-level summary sections (Final Consensus Summary, Final Context & Assumptions) and the critical Canonization & Integration Directives section at the bottom.
Phase 3: Integration & Verification
The completed ADR Clarification Record is committed as a canonical, immutable artifact.
A new REMEDIATION Execution Plan is created, using the "Architectural Artifacts to be Modified" table as its task list.
This plan is executed to bring the entire HAiOS canon (ADRs, schemas, etc.) into alignment with the new consensus. The VALIDATE phase of this plan confirms that all required changes have been made.
Consequences
Positive:
Creates a highly structured, repeatable, and auditable process for evolving the architecture.
Turns ambiguous open questions into robust, pressure-tested solutions.
Ensures that new architectural knowledge is not just documented but actively and verifiably integrated back into the core system artifacts.
Provides an explicit "Definition of Done" for architectural decisions.
Negative:
Introduces significant procedural overhead compared to an informal Q&A. This is an accepted trade-off in the pursuit of high certainty and auditability.
The quality of the outcome is dependent on the quality of the adversarial dialogue.
Clarifying Questions
How will the system track the Status of each clarification record (e.g., DRAFT, PENDING_REVIEW, ACCEPTED)?
Should the final REMEDIATION plan be automatically generated from the Canonization & Integration Directives table?
What is the process for superseding or amending a previously ACCEPTED clarification record?