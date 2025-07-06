# ADR-OS-010: Constraint Management & Locking Strategy

* **Status**: Proposed
* **Date**: 2025-06-09
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

Autonomous AI agents can "drift" or "forget" critical project-level constraints over time. To ensure long-term project integrity, a mechanism is needed to make these constraints durable and explicitly non-mutable by standard agent operations.

## Assumptions

* [ ] AI "drift" is a real and significant risk to long-term project stability.
* [ ] A data-centric locking mechanism is an effective way to mitigate this risk.
* [ ] The OS and its agents can be reliably programmed to respect these lock fields.
* [ ] The semantics and enforcement of all `_locked*` fields are clearly defined and versioned.
* [ ] The system can detect and recover from failed or partial lock/unlock operations.
* [ ] The override and audit trail process is robust and tamper-evident.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-028) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** "Distributed Systems Implications" section addresses idempotency and partition tolerance for lock operations.
- **Self-Critique:** Lock checking in distributed environment needs more comprehensive failure mode analysis.

### Data-Centric Security v1.0
- **Compliance Proof:** Locking mechanism places constraints directly on data rather than relying on agent-level access control.
- **Self-Critique:** Over-locking could lead to excessive rigidity requiring frequent human intervention.

### Fail-Safe Design v1.0
- **Compliance Proof:** Agents MUST halt and log BLOCKER issue when encountering locked constraints, preventing unauthorized modifications.
- **Self-Critique:** Override process requiring new Request could become bottleneck if not managed efficiently.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section about AI drift risk, locking effectiveness, and agent compliance reliability.
- **Self-Critique:** Only three assumptions listed; constraint management likely has more implicit assumptions about lock semantics.

### Architectural Integrity v1.0
- **Compliance Proof:** Granular boolean lock fields protect foundational decisions from inadvertent agent changes.
- **Self-Critique:** Meaning of different lock types adds cognitive load for developers and agents.

### Audit Trail v1.0
- **Compliance Proof:** Override process creates formal, auditable trail for high-stakes constraint changes.
- **Self-Critique:** Audit trail quality depends on proper logging of override decisions and rationale.

### Proximity Principle v1.0
- **Compliance Proof:** Lock fields placed directly within schemas near the data they protect for contextual awareness.
- **Self-Critique:** Decoupled constraints in global file would be harder for agents to discover contextually.

## Decision

**Decision:**

> We will implement a granular, data-centric locking strategy using specific boolean fields (e.g., `_fieldname_locked`, `_locked_entry_definition`) directly within the schemas of OS Control Files and `EmbeddedAnnotationBlock`s. An agent encountering a `true` lock on an item it must modify **MUST** halt, log a `BLOCKER` issue, and set its task to `BLOCKED`.
>
> ### Distributed Systems Implications
>
> Operations that set or check these locks must be robust in a distributed environment.
>
> *   **Idempotency (ADR-OS-023):** Any OS action that sets or removes a lock (`_locked*` flag) MUST be idempotent. A second attempt to apply the same lock should result in success, not an error.
> *   **Partition Tolerance (ADR-OS-028):** Checking a lock is a read operation and can proceed in any partition. However, changing a lock is a write operation. Since OS Control Files are CP systems, an attempt to change a lock in a minority partition will fail until the partition heals, preventing inconsistent lock states across the system.

**Confidence:** High

## Rationale

1. **Enforces Architectural Integrity**
   * Self-critique: Over-locking could lead to excessive rigidity and require frequent human intervention for minor, legitimate changes.
   * Confidence: High
2. **Durable, Proximate Constraints**
   * Self-critique: The meaning of different lock types (e.g., `_list_immutable` vs. `_locked_entry_definition`) adds cognitive load for developers and agents.
   * Confidence: High
3. **Clear Override Path**
   * Self-critique: The override process, requiring a new `Request` and explicit authorization, could become a bottleneck if not managed efficiently.
   * Confidence: Medium

## Alternatives Considered

1. **Role-Based Access Control (RBAC)**: Considered complementary, not mutually exclusive. RBAC is agent-centric; this is data-centric. Combining them could be a future enhancement.
   * Confidence: High
2. **Constraints in a Single Global File**: Rejected because it decouples the constraint from the data it protects, making it harder for an agent to be contextually aware of the lock.
   * Confidence: High

## Consequences

* **Positive:** Provides strong guardrails for autonomous agents. Makes project constraints explicit and machine-readable. Creates a formal, auditable process for high-stakes changes.
* **Negative:** Adds complexity to schemas and agent logic, as they must always check for locks. Could introduce rigidity if locks are not applied judiciously.

## Clarifying Questions

* What is the definitive list of all `_locked*` field types and their precise meanings, and how is this list versioned and maintained?
* What is the process for a supervisor to review, approve, and audit a lock override request, and how is this process made tamper-evident?
* How does this locking mechanism apply to binary or non-text-based artifacts, and what are the limitations?
* How are distributed lock state, partition healing, and lock conflict resolution handled in multi-agent or partitioned environments?
* What is the process for evolving the lock schema or semantics as new constraint types are identified?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
