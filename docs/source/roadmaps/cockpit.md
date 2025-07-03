# Roadmap: "Cockpit" UI Reverse Engineering Analysis

* **Status:** Complete
* **Owner(s):** [System Architect]
* **Created:** [g_event_cockpit_analysis]
* **Context Source:** Analysis of a hypothetical "CodePilot Studio" UI.
* **Trace ID:** [trace_id_cockpit_analysis_v1]

---

## 1. **Mission / North Star**

- To analyze a hypothetical high-level UI ("Cockpit") to understand how its features would map to the existing HAiOS schemas and to identify potential gaps or improvements in the OS design needed to support such a control panel.

## 2. **Key Objectives**

- Decompose the UI into its primary screens (Overview, Git, Agents, Architect, Sessions, Terminal).
- Map UI elements and actions on each screen to corresponding HAiOS control files and operational phases.
- Identify new schema requirements or architectural layers implied by the UI's functionality.
- Synthesize findings into a set of actionable improvements for the HAiOS project.

## 3. **Scope Boundaries & Out-of-Scope**

- **In Scope:** Analysis of the UI's logical components and their mapping to the HAiOS backend concepts.
- **Out-of-Scope:** Actual implementation of the UI; detailed front-end technology choices.

## 4. **Assumptions & Constraints**

- [x] *Assumption:* "The hypothetical UI represents a desirable and plausible end-state for interacting with the HAiOS." (**Confidence:** High; **Self-critique:** "This is one of many possible UI paradigms. The core findings about the backend should be adaptable.")
- [x] *Constraint:* "The analysis must map to existing HAiOS schemas and ADRs where possible, only proposing new structures when a clear gap is identified." (**Confidence:** High)

## 5. **Dependencies & Risks**

- [x] *Dependency:* "A solid understanding of the current HAiOS schemas and operational loop is required to perform the mapping." (**Mitigation:** This analysis was performed by the core architect.)
- [x] *Risk:* "The UI implies an 'Agent Orchestrator' layer that is not yet formally designed." (**Mitigation:** The analysis focuses on how the OS *serves* this layer, not on designing the orchestrator itself, deferring that complexity.)

## 6. **Distributed System Protocol Compliance**

- [x] *Observability (ADR-028):* "The UI's ability to display agent status, session history, and git history tied to intent relies heavily on comprehensive, traceable logging via `trace_id`."
- [x] *Zero Trust (ADR-025):* "The 'Agents' screen, which allows for deploying agents, implies a secure registration and deployment mechanism, aligning with the need for a formal Agent Registry and a zero-trust interaction model."

## 7. **Agent/Role Protocol**

- **Implied Roles:** The UI surfaces the need for distinct roles: a `User/Architect` who defines goals, and `Agents` (like Code Assistant, Test Runner) who execute them. This reinforces the need for explicit agent personas in plans.
- **Escalation:** The UI dashboard could surface items from the `human_attention_queue.txt`, providing a clear escalation point for when the system requires human input.

## 8. **Milestones & Timeline**

- This is an analysis document, not a project plan with a timeline. The "milestones" are the key insights derived.
  - **Insight 1:** Confirmed need for an "Agent Orchestrator" layer above the core OS file system.
  - **Insight 2:** Confirmed need for an `agent_registry.txt` or similar mechanism to define available agent personas and capabilities.
  - **Insight 3:** Confirmed the utility of the `human_attention_queue.txt` as a primary interaction point for a UI.
  - **Insight 4:** Identified that UI "Sessions" or "Goals" map well to the existing `init_plan` concept.
  - **Insight 5:** Revealed the potential for an "interactive" CONSTRUCT phase, where a user can converse with an agent during task execution.

## 9. **Fallbacks & Escalation Paths**

- N/A for an analysis document.

## 10. **Clarifying Questions**

- [ ] "Should the findings from this analysis be formalized into a new set of ADRs for the Agent Orchestrator and Registry?"
- [ ] "How should the 'interactive CONSTRUCT' concept be reconciled with the current, non-interactive `AI_Execute_Next_Viable_Task` model?"

---

*Appendix (optional):*
- The original line-by-line decomposition of the UI screens is preserved as the source data for this analysis.
