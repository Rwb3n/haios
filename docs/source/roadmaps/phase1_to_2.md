# Roadmap: Phase 1 to Phase 2 Contract Definition

* **Status:** Complete
* **Owner(s):** [System Architect]
* **Created:** [g_event_phase1_to_2_contract]
* **Context Source:** `docs/source/roadmaps/roadmap_main.md`
* **Trace ID:** [trace_id_phase1_to_2_contract_v1]

---

## 1. **Mission / North Star**

- To define a stable, deterministic contract surface between the completed Phase 1 "black-box" engine and the future Phase 2 multi-agent orchestration layer. This ensures Phase 2 can be developed and scaled independently without modifying or compromising the proven guarantees of the core engine.

## 2. **Key Objectives**

- **Artefact Schemas:** Solidify the immutable structure of all OS Control Files (`exec_plan`, `state`, `registry_map`, etc.) as the primary interaction medium.
- **CLI / API:** Define a minimal, stable command-line interface as the sole entry point for triggering engine actions.
- **Observability Contract:** Specify the exact Prometheus metrics the engine will expose for Phase 2 monitoring.
- **Security Contract:** Detail the non-negotiable security interfaces (kill-switches, Vault scopes, artefact signing) that Phase 2 must adhere to.
- **Economic Contract:** Formalize the cost and budget reporting mechanisms that any Phase 2 agent must comply with.

## 3. **Scope Boundaries & Out-of-Scope**

- **In Scope:** Defining the immutable *interface* of the Phase 1 engine.
- **Out-of-Scope:** Defining the *implementation* of the Phase 2 orchestrator or its agents.

## 4. **Assumptions & Constraints**

- [x] *Assumption:* "The Phase 1 engine can and should be treated as a deterministic, stateless black box whose behavior is entirely dictated by the contents of `os_root`." (**Confidence:** High)
- [x] *Constraint:* "Phase 2 components (orchestrators, remote agents) are forbidden from interacting with the engine through any mechanism other than the defined contract surface." (**Confidence:** High)
- [x] *Constraint:* "The contract, once defined, can only be changed via a new, superseding ADR." (**Confidence:** High)

## 5. **Dependencies & Risks**

- [x] *Dependency:* "ADRs 018, 019, and 020, which define the security, observability, and runtime mode contracts, must be in a locked, `APPROVED` state." (**Mitigation:** This was confirmed before the contract was finalized.)
- [x] *Risk:* "A future requirement in Phase 2 might necessitate a breaking change to the Phase 1 contract." (**Mitigation:** The high bar for changing the contract (a new ADR) forces careful consideration of alternatives before attempting to change the stable core.)

## 6. **Distributed System Protocol Compliance**

- This contract is the critical bridge that enables the Phase 2 system to be compliant with DS protocols, using the Phase 1 engine as a compliant component.
  - [x] *Idempotency (ADR-023):* The contract is stateless. It is the responsibility of the Phase 2 client to ensure its calls (e.g., plan creation) are idempotent.
  - [x] *Zero Trust (ADR-025):* The mandatory artefact signing and scoped Vault secrets are the core security primitives that the Phase 2 orchestrator will use to enforce a Zero Trust model for its remote agents.
  - [x] *Observability (ADR-028):* The Prometheus metrics contract is the exclusive channel through which a Phase 2 orchestrator can observe the internal state and health of the engine instances it manages.

## 7. **Agent/Role Protocol**

- **`Phase 1 Engine` (The Sovereign Executor):** Its role is to execute valid plans according to the contract. It is unaware of Phase 2.
- **`Phase 2 Orchestrator` (The Client):** Its role is to generate plans, submit them to the engine via the CLI, and monitor their execution via Prometheus metrics and by reading artefact statuses.
- **`Phase 2 Remote Agent` (The Worker):** Its role is to perform work requested by the engine, sign its resulting artefacts, and report its costs, adhering strictly to the contract.

## 8. **Milestones & Timeline**

- This is a contract definition, not a project with a timeline. The key contract points are:
  1. **Artefact Schemas:** Finalized and versioned.
  2. **CLI / API:** `haios run` and `haios state` commands are the only entry points.
  3. **Prometheus Metrics:** `/metrics` endpoint is stable.
  4. **Security Interfaces:** Kill-switch flags, Vault scopes, and detached signatures are mandatory.
  5. **Economic Interfaces:** `cost_record` reporting is mandatory.

## 9. **Fallbacks & Escalation Paths**

- **Contract Violation:** "The Phase 1 engine MUST reject any input that violates the contract (e.g., invalid schema, missing signature). It is the responsibility of the Phase 2 client to handle this rejection."
- **Contract Change:** "Any proposed change to this contract requires a new ADR."

## 10. **Clarifying Questions**

- All questions were resolved prior to the finalization of ADRs 018-020.

---

*Appendix (optional):*
- The original contract table and sequence diagram are preserved as the source data for this document.
