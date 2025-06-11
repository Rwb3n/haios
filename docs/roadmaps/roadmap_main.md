# Roadmap: From Architectural Foundation to the Agent Development Kit (ADK)

---

## Phase 0: Architectural Foundation & Definition (Current Stage)

**Status:** ✅ COMPLETE

**Outcome:**  
A complete, ratified set of 16 ADRs, 3 core documentation volumes (Phase Logic, Data Schemas, Scaffold Spec), and a Project Directory Scaffold. The "laws of physics" for our universe are now written.

---

## Phase 1: Core OS Engine & Tooling (The MVP Implementation)

**Mission:**  
"Bring the Blueprints to Life." To create the minimum viable engine that can execute the simplest of our defined processes. The goal is to have a runnable, albeit manually driven, system that can manage a project according to our file structures.

**Key Objectives:**
- **Formalize Schemas:** Translate our Markdown schema documentation into actual JSON Schema files (`*.schema.json`) for programmatic validation.
- **Build the Config Loader:** Implement the logic to read and parse `haios.config.json`.
- **Implement the State Manager:** Create the core functions to read, update (respecting the `v` counter for optimistic locking), and write `state.txt`.
- **Build a "Task Runner" MVP:** Develop a simple executable that can:
  - Parse a basic `exec_plan_<g>.txt`.
  - Execute a single, simple task (e.g., a SCAFFOLDING task that creates a directory and a file from a template).
  - Update the corresponding `exec_status_<g_plan>.txt` with the task's completion.

**Success Criteria / Definition of Done:**
- The OS engine can be run from a command line.
- It can successfully execute a minimal, two-task SCAFFOLDING Execution Plan from start to finish.
- `state.txt`, `exec_status_*.txt`, and `global_registry_map.txt` are all correctly updated as a result.

**Value Delivered to You:**  
You transition from having a set of documents to having a tool. You can start using the HAiOS file structure to manage your own projects, offloading significant cognitive load by formalizing your plans, even if you are manually triggering the single-task execution. This is the first return on your time investment.

---

## Phase 2: Agent Integration & Core Logic (The Sentient MVP)

**Mission:**  
"Give the Machine a Mind." To integrate real AI agent personas into the OS engine, enabling them to execute tasks autonomously based on the plans.

**Key Objectives:**
- **Implement Agent Registry:** Build the logic to read `agent_registry.txt` and the `persona_*.txt` cards.
- **Build the Orchestrator:** Develop the core logic that powers `AI_Execute_Next_Viable_Task_From_Active_Plan`. This orchestrator will:
  - Select a viable task from a plan.
  - Perform the Pre-Execution Readiness Check (ADR-OS-013).
  - Load the required context using the Precision Context Loading (ADR-OS-015) instructions.
  - Select the correct agent persona from the registry based on `assigned_agent_persona`.
  - Invoke the designated AI model with the generated prompt.
  - Process the AI's output (e.g., write to a file, update exec_status).
- **Implement Core CONSTRUCT & VALIDATE Loops:** Build out the full logic for these two phases. The VALIDATE phase must be able to parse Test Results Artifacts.

**Success Criteria / Definition of Done:**
- A CODING_ASSISTANT can successfully execute a multi-task DEVELOPMENT plan.
- A TESTING_VALIDATOR can execute a TEST_EXECUTION plan and produce a "signed" Test Results Artifact.
- The VALIDATE phase can parse that Test Results Artifact, update the quality_notes of the source code, and generate a Validation Report.

**Value Delivered to You:**  
The system now performs complex, multi-step work autonomously. You transition from being the "doer" to being the "supervisor." Your leverage increases by an order of magnitude.

---

## Phase 3: Advanced Capabilities & Full Autonomy (The Supervisor)

**Mission:**  
"Teach the System to Think Strategically." To make the "Supervisor Agent" persona a reality, automating the full project lifecycle from Request to Validation.

**Key Objectives:**
- **Implement the Full ANALYZE Phase:** Build the logic for the "investigative mini-cycle," where the AI autonomously blueprints and executes an ANALYSIS_EXECUTION plan to produce an Analysis Report.
- **Implement the Full BLUEPRINT Phase:** Build the logic for the `AI_Blueprint_Execution_Plans_...` action, including the Default Task Injection for testing and documentation.
- **Implement Critique Loops:** Formalize the PLAN_CRITIQUE and TEST_SCRIPT_CRITIQUE plan types, allowing the Supervisor to orchestrate review cycles between different agent personas.
- **Automate Escalation & Remediation:** The Supervisor can now automatically blueprint REMEDIATION plans in response to BLOCKER issues from failed tasks or readiness checks.

**Success Criteria / Definition of Done:**
- The OS can take a complex Request (e.g., "Add a new feature X") and autonomously run the entire lifecycle through the VALIDATE phase of the first Execution Plan for that feature.
- The `human_attention_queue.txt` is the primary interaction point, with the OS only halting for explicit approvals or critical, unrecoverable failures.

**Value Delivered to You:**  
You transition from "supervisor" to "client" and "governor." You issue high-level strategic directives (Requests) and make key approval decisions. The system handles almost all of the intermediate operational and tactical thinking.

---

## Phase 4: The ADK & Ecosystem Foundation (The Product)

**Mission:**  
"Package the Magic and Prepare for Scale." To transform the operational system into a distributable Agent Development Kit (ADK) and build the foundational tools for the SPAA vision.

**Key Objectives:**
- **Package the ADK:** Refactor the core OS engine into a formal library/package (e.g., `@haios/adk`) with a clean public API.
- **Create the init command:** Build the command-line tool that bootstraps a new project using our defined Project Directory Scaffold.
- **Build the "Cockpit" UI (v1):** Develop a simple web-based UI that can read the `os_root/` directory and provide a read-only dashboard view of project status, plans, issues, and the `human_attention_queue`.
- **Implement NATS/Jetstream POC:** Develop a proof-of-concept where agents, instead of being invoked directly, communicate via NATS. An agent "vessel" subscribes to a `task.execute` subject, and the Supervisor publishes tasks to it.

**Success Criteria / Definition of Done:**
- A new developer can `npm install @haios/adk`, run `npx haios init`, and have a fully functional HAiOS project instance.
- The basic Cockpit UI can successfully visualize the state of an active project.
- Two separate agent processes can communicate and complete a simple task via NATS.

**Value Delivered to You:**  
The system is now replicable, distributable, and extensible. It is no longer just a project; it is a platform. This is the path to scaling beyond your direct involvement and addressing your financial constraint.

---

## Phase N: The Autonomous Explorer (The Grand Vision)

**Mission:**  
"Unleash the Potential." To build upon the ADK and SPAA backbone to create a system capable of proactive discovery and self-evolution.

**Key Objectives:**
- **Implement the world_model:** Evolve `global_registry_map.txt` into a true semantic knowledge graph.
- **Develop the Hypothesis Engine:** Create a "Scientist Agent" that can analyze the world_model for gaps and proactively propose new Hypothesis artifacts for you to approve.
- **Implement AGENT_METAMORPHOSIS:** Enable the system to dynamically create new, specialized agent personas by templating and re-configuring existing Agent Cards.

**Success Criteria / Definition of Done:**  
These become more abstract. "The system can generate a novel, testable hypothesis that leads to a demonstrable improvement in its own capabilities or knowledge base."

**Value Delivered to You:**  
The system transitions from an incredibly efficient tool to a true intellectual partner, capable of driving discovery alongside you.