# ADR-OS-030: Archetypal Agent Roles and Protocols

* **Status:** Proposed
* **Date:** 2025-06-23
* **Deciders:** Architecture Team
* **Reviewed By:** \[TBD]

---

## Context

The Hybrid AI Orchestration System relies on agents (â€œpersonasâ€) with specific operational responsibilities. Until now, agent roles, access boundaries, and escalation protocols have been loosely defined, leading to role drift, privilege creep, and ad hoc recovery flows.

To achieve deterministic, auditable, and robust distributed operation, we must define a small, closed set of *archetypal agents* with locked behavioral contracts, access rights, escalation/fallback paths, and lifecycle protocols. This aligns with both distributed system best practices and Goldrattâ€™s â€œwork-centerâ€ specialization: every function and failure must have one, and only one, responsible agent type.

---

## Assumptions

* [ ] Only five core agent archetypes are required at present (Supervisor, Manager, Builder, Janitor, Auditor).
* [ ] Each agent archetype is protocol-defined (not just named), with explicit permissions and forbidden actions.
* [ ] No agent may cross its boundaries except via explicit, protocol-defined escalation or fallback.
* [ ] Extensions or hybrid roles must be proposed via a future ADR and pass architectural review.
* [ ] The agent role and protocol system is robust against privilege escalation, role drift, and protocol misconfiguration.
* [ ] The system can detect and recover from agent registry or protocol definition errors.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-012, ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

---

## Decision

**We hereby formalize the following archetypal agents, their protocols, and their access boundaries:**

### **1. Supervisor**

* **Role:** Final authority for orchestration, recovery, plan approval, and override.
* **Permissions:**

  * R/W all plans, inventories, agent states, and constraints.
  * Can unlock or forcibly recover any system state.
* **Forbidden:**

  * Cannot directly execute atomic Builder tasks.
* **Escalation/Fallback:**

  * All critical errors, deadlocks, and â€œunownedâ€ failures escalate to Supervisor.
* **Lifecycle:**

  * Must always be available (human or highly privileged AI).

### **2. Manager**

* **Role:** Task delegation, plan-level orchestration, inventory mutation, and agent assignment.
* **Permissions:**

  * R/W to plan artifacts and inventory.
  * Can assign and promote/demote Builder, Janitor, Auditor agents.
* **Forbidden:**

  * Cannot override locked constraints (must escalate to Supervisor).
  * Cannot GC/expire inventory (Janitor only).
* **Escalation/Fallback:**

  * Any denied inventory mutation escalates to Supervisor.

### **3. Builder**

* **Role:** Execute atomic tasks; does not mutate shared state except working artifacts.
* **Permissions:**

  * R to plans, tasks, inventory.
  * W to designated working artifact only.
* **Forbidden:**

  * Cannot mutate plan-level inventory, state, or promote/demote other agents.
* **Escalation/Fallback:**

  * If required resource is missing, must request via Manager.

### **4. Janitor**

* **Role:** Automated GC, buffer cleanup, health/heartbeat tasks.
* **Permissions:**

  * R to all state.
  * W only to expired/orphaned items (inventory, plans).
* **Forbidden:**

  * Cannot assign/execute Builder tasks or mutate active artifacts.
* **Escalation/Fallback:**

  * Reports GC errors to Manager.

### **5. Auditor**

* **Role:** System audit, log reading, trace/metrics analysis.
* **Permissions:**

  * R all logs, plans, state, events.
* **Forbidden:**

  * No mutation of any artifact or agent.
* **Escalation/Fallback:**

  * May recommend but not execute recovery.

---

## Rationale

* **Role purity:** Prevents privilege creep, confusion, and accidental state mutation.
* **Predictable escalation:** System failures and gaps are never â€œunownedâ€â€”every error escalates through a fixed path.
* **Access control:** Every plan, inventory, and annotation block operation is authorized only if the requesting agent matches protocol.
* **Extensible:** New archetypes only by explicit ADR.

---

## Protocol Diagrams

1. Access Control Matrix

| Agent      | Plan Artifact | Task Artifact | Inventory | Agent Registry | Logs/Events | GC/Orphans |
|------------|:------------:|:-------------:|:---------:|:-------------:|:-----------:|:----------:|
| Supervisor |   R / W      |   R / W       |   R / W   |     R / W     |    R / W    |   R / W    |
| Manager    |   R / W      |   R / W       |   R / W   |     R / W     |     R       |     R      |
| Builder    |     R        |   R / W       |     R     |      R        |     R       |     -      |
| Janitor    |     R        |     R         |   W (expired/orphaned only) | R |   W (GC events) |  W  |
| Auditor    |     R        |     R         |     R     |      R        |     R       |     R      |
R = Read, W = Write

Builder only writes to assigned task artifacts, never plan/inventory.
Janitor writes only to expired/orphaned items (via GC protocol).


2. Escalation & Fallback Flow

Agent Escalation Paths

flowchart TD
    B[Builder]
    M[Manager]
    J[Janitor]
    S[Supervisor]
    A[Auditor]

    B -- "Resource missing or forbidden" --> M
    M -- "Denied or locked action" --> S
    J -- "GC error or orphan unresolved" --> M
    M -- "Cannot resolve/approve" --> S
    A -- "Audit report/issue" --> M
    M -- "If unavailable" --> S
    J -- "If Manager unavailable" --> S

Explanation:
Builder escalates all forbidden actions or missing resources to Manager.
Manager escalates denied/locked actions to Supervisor.
Janitor reports GC issues to Manager (or Supervisor if Manager is unavailable).
Auditor can only recommend or report, not escalate state changes directly.


3. Agent-to-System Interaction Map

graph TD
    Supervisor -- R/W --> PlanArtifact
    Supervisor -- R/W --> Inventory
    Supervisor -- R/W --> AgentRegistry
    Supervisor -- R/W --> LogsEvents

    Manager -- R/W --> PlanArtifact
    Manager -- R/W --> Inventory
    Manager -- R/W --> AgentRegistry

    Builder -- R --> PlanArtifact
    Builder -- R/W --> TaskArtifact
    Builder -- R --> Inventory

    Janitor -- R --> PlanArtifact
    Janitor -- W (expired/orphaned) --> Inventory
    Janitor -- W --> LogsEvents

    Auditor -- R --> PlanArtifact
    Auditor -- R --> Inventory
    Auditor -- R --> AgentRegistry
    Auditor -- R --> LogsEvents


4. Minimal State Machine for Builder

stateDiagram-v2
    [*] --> Idle
    Idle --> RequestTask: Assigned task
    RequestTask --> Working: Starts execution
    Working --> Done: Completes execution
    Working --> NeedsHelp: Missing resource/forbidden
    NeedsHelp --> Waiting: Escalates to Manager
    Waiting --> Working: Receives help/resource
    Done --> Idle

---

## Example Schema Contracts

```jsonc
// Example: Builder agent_card excerpt
{
  "persona_id": "builder_XYZ",
  "archetype": "BUILDER",
  "allowed_actions": ["READ_PLAN", "EXECUTE_TASK", "READ_INVENTORY"],
  "forbidden_actions": ["MUTATE_PLAN", "MUTATE_INVENTORY", "PROMOTE_AGENT"],
  "escalation_path": "MANAGER",
  "access_scope": {
    "plan": "READ",
    "task": "READ/WRITE",
    "inventory": "READ"
  }
}
```

---

## Alternatives Considered

* **Loose, flexible personas:** Led to privilege creep and accidental cross-role mutations.
* **Code-only enforcement:** Lacked clarity for documentation, onboarding, and review.

---

## Consequences

* **Positive:** Tighter system safety, auditability, and onboarding clarity.
* **Negative:** Slight rigidityâ€”new workflows must justify new roles in future ADRs.

---

## Clarifying Questions

* Should archetype enforcement be implemented in code, config, or both?
* How are temporary hybrid roles handled during migration periods?
* Do escalation paths require explicit fallback (if Manager down, escalate to Supervisor, etc.)?

---

**This ADR will govern all future agent design, schema, and protocol work.**
**Any new agent type or capability requires explicit ADR review.**

