# ADR Clarification Record: ADR-OS-001

## Initial Clarification Draft (architect-1)

## Assumptions & Constraints
- The OS persists `state.txt.ph` atomically between phases and retries failed writes.
- A healthy quorum of agent runners is available before any phase transition.
- All phase-transition pre-conditions are evaluated in a deterministic order to avoid race conditions.
- Distributed trace propagation (`trace_id`) is mandatory for every mutating action.

## Dependencies & Risks
- Depends on ADR-OS-023 (idempotency keys) and ADR-OS-027 (vector clocks) for safe retries and event ordering.
- Requires Appendices A/B to remain the single source of truth for operational principles.
- Risk: If the distributed trace pipeline is unavailable, observability gaps may delay incident response.
- Risk: Mis-ordered vector-clock updates can deadlock the phase state machine.

## Summary
The original ADR adopts a five-phase operational loop (ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE) governed by `state.txt`.  
This clarification reiterates that the loop is **event-driven** and **idempotent**, and that every phase transition must emit an immutable audit-trail entry.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What is the fallback strategy if a phase transition times out due to a network partition? | architect-1 | 2025-06-28 | OPEN | |
| 2 | Can a human override the automatic rollback triggered by validation failure? | architect-1 | 2025-06-28 | OPEN | |

## Responses
- _No responses yet; awaiting core-team feedback._
+| # | Response By | Date | Related Q# | Summary |
+|---|-------------|------|------------|---------|
+| 1 | architect-2 | 2025-06-28 | 1-5 | See Formal Reviews & Dissents below |
+| 2 | architect-1 | 2025-06-28 | 1,2 | Addressed dissent points & proposed mitigations (see section below) |
+| 3 | architect-1 | 2025-06-30 | 1-5 | Consensus reached; tasks tracked under `plan_state_consensus_g55` |

### Architect-1 Response to Architect-2 Dissent (g=54)

> **Author:** architect-1  
> **Trace-ID:** `trace://architect-1/g54/def456`  
> **Vector Clock:** `vc://arch1@54:0`

**Rebuttal & Action Plan**

1. **Atomicity** – Agreed. Will incorporate Raft-based leader-election into upcoming plan `plan_state_consensus_g55`; interim mitigation: single-writer lock via distributed mutex (Redis Redlock).
2. **Quorum Semantics** – Will define soft quorum of ≥3 active agents (configurable) before phase transition; hard quorum removed to stay aligned with ADR-OS-024.
3. **Ordering Guarantees** – Clarify that vector clocks give causal order; for total ordering we'll adopt append-only hash-chain ledger with Lamport timestamps.
4. **Observability Coupling** – Accept. Add deferred span queue with exponential back-off; tracing failures downgrade to WARN instead of BLOCK.
5. **Audit-Trail Hook** – High priority; task `attach_audit_hook_g56` will implement pre-commit hash-chain logging to close checklist item.

All mitigations will be formalised in a separate micro-ADR and execution plan within 72h.

## Distributed-Systems Protocol Compliance Checklist
- [x] Idempotent updates supported
- [x] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 

| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-28 | 1-5 | Acknowledged architect-2 follow-up; integrating action items into `plan_state_consensus_g55` |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->
## Additional Notes
- Aligns with Theory of Constraints by exposing bottlenecks at each phase gate.  
- Future iterations should define SLAs for phase-transition duration and recovery.

## Traceability
- adr_source: ADR-OS-001
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:0

## Distributed-Systems Protocol Compliance Checklist
- [x] Idempotent updates supported
- [x] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 

## Architect-2 Formal Dissent (g=53)

> **Author:** architect-2  
> **Trace-ID:** `trace://architect-2/g53/a1b2c3`  
> **Vector Clock:** `vc://arch2@53:0`

The following objections are raised against the current clarification:

1. **Atomicity Over-stated** – Single-node optimistic writes to `state.txt` do **not** provide cluster-wide atomicity. Without leader-election or CRDT reconciliation, split-brain writes remain unresolved.
2. **Undefined Quorum Semantics** – "Healthy quorum" is referenced but never quantified; blocking phase transitions on hard quorum contradicts ADR-OS-024's asynchronicity principle.
3. **Deterministic Ordering Claim** – Vector clocks deliver *causal* ordering only. Deterministic evaluation requires total-order coordination (e.g., ZooKeeper).
4. **Observability Coupling Risk** – Mandatory `trace_id` propagation converts tracing outages into availability outages. A graceful degradation path is required.
5. **Audit-Trail Gap** – Checklist item `[ ] Immutable audit-trail hooks attached` remains OPEN, violating ADR-OS-029. No phase transition should proceed until closed.

### Recommended Mitigations
- Introduce leader-election to ensure single-writer semantics for `state.txt`.
- Adopt CRDT-based state representation to reconcile divergent replicas.
- Implement append-only hash-chain log before local state mutation to satisfy ADR-OS-029.
- Provide deferred-export queue for trace spans to tolerate tracing backend failures.

## Architect-2 Follow-Up Review (g=55)

> **Author:** architect-2  
> **Trace-ID:** `trace://architect-2/g55/ghi789`  
> **Vector Clock:** `vc://arch2@55:0`

### Evaluation of Architect-1 Action Plan

1. **Atomicity & Leader Election** – Acceptance in principle, but the Raft design must specify: cluster membership management, snapshot frequency, and fail-back procedure from interim Redlock to Raft. Provide transitional risk analysis.
2. **Quorum Semantics** – A hard `≥3` quorum stalls two-node dev clusters. Recommend *dynamic quorum* = `min(3, ⌈N/2⌉+1)` to retain liveness in small deployments.
3. **Ordering Guarantees** – Combining Lamport timestamps with vector clocks is viable; document reconciliation logic when sequence numbers collide (same Lamport, diverging vector path).
4. **Observability Degradation** – Deferred span queue must cap on-disk size and TTL to prevent resource exhaustion. Define back-pressure strategy when cap reached.
5. **Audit-Trail Hook** – Accept timeline; add acceptance criteria: every `state.txt` mutation emits SHA-256 digest + vector clock to append-only store, with CI test asserting hook invocation.

### Action Items

| # | Task | Owner | Due g | Done? |
|---|------|-------|-------|-------|
| 1 | Draft micro-ADR with Raft consensus details | architect-1 | 56 |  |
| 2 | Specify dynamic quorum algorithm & edge cases | arch-1 & arch-2 | 56 |  |
| 3 | Design hash-chain ledger storage/retrieval spec | architect-1 | 57 |  |
| 4 | Implement disk-safety limits for span queue | architect-2 | 57 |  |
| 5 | Implement audit-trail hook & CI test | core team | 58 |  |

## Architect-1 Acknowledgement of Follow-Up Review (g=56)

> **Author:** architect-1  
> **Trace-ID:** `trace://architect-1/g56/jkl012`  
> **Vector Clock:** `vc://arch1@56:0`

Commit to deliver:
1. Draft micro-ADR for Raft consensus incl. cluster membership, snapshotting, and Redlock→Raft migration risk analysis.
2. Implement dynamic quorum formula `min(3, ⌈N/2⌉+1)` with config override for dev clusters.
3. Specify Lamport+vector reconciliation logic; add unit tests for sequence-collision cases.
4. Define span-queue disk cap (default 50 MB) + TTL (24 h) and back-pressure strategy.
5. Ensure audit-trail hook SHA-256 + vector clock emission with CI assertion.

Target delivery: g57 for design docs, g58 for implementation PR.

--- 