# Roadmap: From Architectural Foundation to the Agent Development Kit (ADK)

* **Status:** Active
* **Owner(s):** [System Architect / Lead Maintainer]
* **Created:** [Initial Project Conception]
* **Context Source:** `docs/source/Cody_Reports/Genesis_Architect_Notes.md`
* **Trace ID:** [trace_id_roadmap_main_v1]

---

## 1. **Mission / North Star**

- To evolve HAiOS from a set of architectural documents into a fully autonomous, distributable, and self-improving platform (the Agent Development Kit), capable of acting as a true intellectual partner in software development.

## 2. **Key Objectives**

- **Phase 0:** Establish the "laws of physics" for the OS through ratified ADRs and core documentation. ( COMPLETE)
- **Phase 1:** Build a runnable MVP engine that can execute simple, manual tasks.
- **Phase 2:** Integrate AI agent personas to execute complex plans autonomously.
- **Phase 3:** Implement strategic thinking in a "Supervisor" agent to manage the full project lifecycle.
- **Phase 4:** Package the core engine into a distributable ADK and build foundational ecosystem tools (UI, messaging).
- **Phase N:** Evolve the system into a proactive, self-improving "Autonomous Explorer."

## 3. **Scope Boundaries & Out-of-Scope**

- **In Scope:** Core OS engine development, agent integration, lifecycle automation, packaging, and foundational UI/messaging for a single-node instance.
- **Out-of-Scope (for initial phases):** Multi-node distributed consensus, enterprise-grade security features beyond the baseline, public cloud service offerings.

## 4. **Assumptions & Constraints**

- [x] *Assumption:* "A single, monolithic state file (`state.txt`) is sufficient for initial phases." (**Confidence:** High for Phases 1-2; **Self-critique:** "This becomes a bottleneck. Phase 3+ will require a move to a distributed log or event store.")
- [x] *Assumption:* "The defined agent personas (e.g., `CODING_ASSISTANT`, `TESTING_VALIDATOR`) are the correct initial archetypes." (**Confidence:** Medium; **Self-critique:** "Real-world use may reveal the need for more specialized or different roles.")
- [x] *Constraint:* "All development must adhere strictly to the defined ADRs, especially the new Distributed Systems protocols (ADR-023-029)." (**Confidence:** High)

## 5. **Dependencies & Risks**

- [x] *Dependency:* "Underlying AI models (e.g., GPT-series) provide sufficient instruction-following capabilities." (**Mitigation:** Isolate model interaction behind an adapter to allow for swapping models if needed.)
- [x] *Risk:* "The 'Supervisor' logic in Phase 3 may be significantly more complex than anticipated." (**Mitigation:** Break down Supervisor capabilities into smaller, incremental features. Prioritize core lifecycle management over advanced remediation logic initially.)
- [ ] *Risk:* "The transition to a message-based architecture (NATS) in Phase 4 introduces significant new failure modes." (**Mitigation:** Start with a synchronous POC before refactoring the entire core engine.)

## 6. **Distributed System Protocol Compliance**

- [x] *Idempotency (ADR-023):* "All phase transitions and task executions must be designed to be idempotent to support retries and message-based execution."
- [x] *Event Ordering (ADR-026):* "Vector clocks and `g_event` counters will be used to ensure strict event ordering, especially for state and plan updates."
- [x] *Zero Trust (ADR-025):* "Agent communication will eventually move to a message bus (Phase 4), enforcing a zero-trust model where agents only subscribe to authorized topics."
- [x] *Observability (ADR-028):* "All significant actions must be logged with a `trace_id` to provide a complete, traceable audit trail across all phases and agents."

## 7. **Agent/Role Protocol**

- **Roadmap Updates:** "Only a `Lead Maintainer` role may update this core roadmap. Changes must be proposed via a PR and require review."
- **Plan Execution:** "In Phases 1-2, plan execution is invoked manually. In Phase 3+, the `Supervisor` agent is the primary owner of plan execution."
- **Escalation:** "Any deviation from this roadmap must be documented in a new ADR, which must be ratified before implementation begins."

## 8. **Milestones & Timeline**

- **Phase 0: Architectural Foundation:**  COMPLETE
- **Phase 1: Core OS Engine (MVP):**
  - *Definition of Done:* A minimal, two-task SCAFFOLDING plan can be executed from the CLI, correctly updating all state and registry files.
- **Phase 2: Agent Integration (Sentient MVP):**
  - *Definition of Done:* A `CODING_ASSISTANT` can execute a development plan, and a `TESTING_VALIDATOR` can execute a test plan and produce a signed result.
- **Phase 3: Advanced Capabilities (Supervisor):**
  - *Definition of Done:* The system can autonomously run the full ANALYZE -> BLUEPRINT -> CONSTRUCT -> VALIDATE lifecycle for a simple feature request.
- **Phase 4: ADK & Ecosystem (The Product):**
  - *Definition of Done:* A developer can `npm install` the ADK, `init` a new project, and view its status in a basic web UI.
- **Phase N: Autonomous Explorer (Vision):**
  - *Definition of Done:* The system can generate and test a novel hypothesis that improves its own capabilities.

## 9. **Fallbacks & Escalation Paths**

- **Failed Milestone:** "If a phase's success criteria are not met, a `REMEDIATION` plan must be blueprinted and executed before proceeding to the next phase."
- **ADR Conflict:** "If a proposed change conflicts with an existing ADR, the conflict must be resolved by creating a new, superseding ADR."

## 10. **Clarifying Questions**

- [ ] "Is NATS the definitive choice for the message bus, or should other options (e.g., RabbitMQ, Kafka) be evaluated in a formal trade study?"
- [ ] "What is the specific feature set required for the 'Cockpit' UI v1?"

---

*Appendix (optional):*
- The detailed phase descriptions from the original document are preserved as the core rationale for the milestones listed above.
