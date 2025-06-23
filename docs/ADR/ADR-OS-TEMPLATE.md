# ADR-OS-XXX: \[Short Decision Title]

* **Status**: {Proposed | Accepted | Deprecated}
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

Describe the background and motivation for this decision. Explain what problem or requirement the architecture must address.

## Assumptions

List the key assumptions underlying this decision. Each entry should include a checkbox and concise statement.

* [ ] {Assumption 1}
* [ ] {Assumption 2}
* [ ] {Assumption 3}

## Models/Frameworks Applied

List all governing models, frameworks, and design/engineering heuristics that inform or constrain this decision (e.g., Distributed Systems Principles, Theory of Constraints, KISS, DRY, AAA, JTBD, Self-Critique, etc.). For each, demonstrate compliance, note exceptions, and reference registry entry/version.

- **[Model/Framework Name] (Registry vX.Y):**
  - *Proof:* {How is this model/framework enforced or demonstrated here? (e.g., explicit buffer for ToC, retry logic for DS, diagram for protocol)}
  - *Self-critique:* {Weaknesses, plausible violations, or partial compliance?}
  - *Exceptions/Justifications:* {If not fully compliant, why?}
- …

*Example:*
- **Distributed Systems Principles (Registry v1.0):**
  - *Proof:* Inventory and retry logic for network failures; event ordering via `g`.
  - *Self-critique:* Partition handling may require human override; not all flows are fully async.
  - *Exceptions:* None.

- **KISS (Registry v1.0):**
  - *Proof:* Single responsibility per agent archetype; protocol minimized.
  - *Self-critique:* Some artifact chains are verbose by necessity.
  - *Exceptions:* None.


## Decision

State the decision clearly. Provide enough detail so that the chosen approach and its implications are understandable.

**Decision:**

> {Describe the decision.}

**Confidence:** {High | Medium | Low}

## Rationale

Explain why this decision was made. For each major point, include a self-critique and confidence annotation.

1. **{Rationale Point A}**

   * Self-critique: {What could go wrong?}
   * Confidence: {High | Medium | Low}
2. **{Rationale Point B}**

   * Self-critique: {Potential weak spot}
   * Confidence: {High | Medium | Low}

## Alternatives Considered

Briefly describe other options that were considered and why they were not chosen. Include confidence or critique where relevant.

1. **{Alternative A}**: {Brief reason for rejection}

   * Confidence: {High | Medium | Low}
2. **{Alternative B}**: {Brief reason for rejection}

   * Confidence: {High | Medium | Low}

## Consequences

Describe the positive and negative consequences of the decision.

* **Positive:** {Benefit or positive outcome}
* **Negative:** {Cost or drawback}

## Clarifying Questions

List any unresolved questions or areas requiring further investigation.

* {Clarifying question 1}
* {Clarifying question 2}
* {Clarifying question 3}

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
