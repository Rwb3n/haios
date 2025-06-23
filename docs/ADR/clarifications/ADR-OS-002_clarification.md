# ADR Clarification Record: ADR-OS-002

## Initial Clarification Draft (architect-2)

## Assumptions & Constraints
- The hierarchical planning store is implemented on a CP data store with single-writer semantics per artifact ID. *(Confidence: High; Self-Critique: write latency may increase under Raft leader change)*
- Each planning artifact embeds its **parent_id** to ensure bidirectional traceability. *(Confidence: Medium; Self-Critique: duplication risk if parent changes post-creation)*
- Supervisor Agent enforces **idempotent** creation of linkage edges to prevent duplicate child plans. *(Confidence: High)*
- Vector-clock field (`vc`) and `trace_id` are mandatory on every create/update mutation. *(Confidence: High; Self-Critique: tight coupling with tracing backend)*

## Dependencies & Risks
- Depends on ADR-OS-024 (asynchronous hand-offs) to allow independent creation of Analysis & Initiative layers.
- Relies on ADR-OS-027 vector-clocks for causal linkage ordering; risk: clock mis-merge may break lineage. *Mitigation: Lamport fallback counter.*
- Hierarchical store downtime blocks new Execution Plans. *Mitigation: local cache + replay queue.*

## Summary
ADR-OS-002 introduces a four-tier **Request→Analysis→Initiative→Execution** model. The clarification emphasises **immutable lineage**, idempotent link creation, and distributed consistency guarantees so that every Execution Plan can be traced back to its originating business Request.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | How are orphaned Execution Plans detected & repaired? | architect-2 | 2025-06-28 | OPEN | |
| 2 | What SLA applies to linkage propagation across tiers? | architect-2 | 2025-06-28 | OPEN | |
| 3 | Can an Initiative Plan spawn sibling Execution Plans in parallel without parent lock? | architect-2 | 2025-06-28 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-28 | 1-3 | Refer to Architect-1 Dissent below |
| 2 | architect-1 | 2025-06-28 | 1-5 | Consensus reached; tasks scheduled per Updated Action Items |

## Distributed-Systems Protocol Compliance Checklist
- [x] Idempotent updates supported (linkage creation via idempotency key)
- [x] Message-driven integration points documented (Supervisor Agent events)
- [ ] Immutable audit-trail hooks attached (implementation in-progress, target g60)

## Traceability
- adr_source: ADR-OS-002
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:1

## Formal Reviews & Dissents
<!-- Formal approvals or objections to be captured here. -->

## Architect-1 Dissent (g=57)

> **Author:** architect-1  
> **Trace-ID:** `trace://architect-1/g57/mno345`  
> **Vector Clock:** `vc://arch1@57:0`

### Objections

1. **Parent ID Mutability Risk** – Clarification notes duplication risk but provides no enforcement strategy. Without immutability guardrails, lineage can fork silently.  
   *Mitigation*: Mark `parent_id` as `WRITE_ONCE`; subsequent updates must raise error and trigger orphan-repair workflow.

2. **Causal vs. Total Order** – Dependence on vector clocks cannot guarantee deterministic lineage under concurrent sibling creation.  
   *Mitigation*: Introduce Lamport-hybrid timestamp for total ordering when multiple children added within same causal epoch.

3. **Orphan Detection SLA** – OPEN Q#1 lacks quantitative SLA; unbounded orphan window undermines audit requirements.  
   *Mitigation*: Define max orphan age = 2 × `plan_creation_interval` (configurable; default 5 min) before auto-repair kicks in.

4. **Linkage Propagation Latency** – Clarification cites SLA question but omits impact analysis on downstream readiness checks.  
   *Mitigation*: Propagation deadline should align with CI validation cycle (e.g., 60 sec); expose metric `linkage_latency_seconds`.

5. **Audit-Trail Gap** – `[ ] Immutable audit-trail hooks attached` still OPEN; any plan creation must emit hash-chain digest to satisfy ADR-OS-029.

### Recommended Action Items

| # | Task | Owner | Due g |
|---|------|-------|-------|
| 1 | Implement WRITE_ONCE schema rule for `parent_id` | platform-team | 58 |
| 2 | Adopt hybrid Lamport timestamp for child plan ordering | architect-2 | 58 |
| 3 | Add orphan auto-repair cron with max age parameter | infra-team | 59 |
| 4 | Instrument `linkage_latency_seconds` Prometheus metric | observability-team | 59 |
| 5 | Hook hash-chain digest on plan mutation events | core-team | 60 |

## Architect-2 Rebuttal & Alignment (g=58)

> **Author:** architect-2  
> **Trace-ID:** `trace://architect-2/g58/pqr678`  
> **Vector Clock:** `vc://arch2@58:0`

The dissent raises critical implementation details; consensus is achievable with the following clarifications:

1. **WRITE_ONCE `parent_id`** – Accepted. Schema patch `planning_artifact_v1.1` will add `writeOnce: true` for `parent_id`. Supervisor Agent will raise `LineageMutationError` on violation.
2. **Hybrid Lamport Timestamp** – Accepted. Child-creation events will carry `(lamport, vc)` pair; tie-break by artifact UUID to guarantee total order without central coordinator.
3. **Orphan SLA** – Agreed. `max_orphan_age` default = `10 min` (2 × default 5 min creation interval). Auto-repair workflow: re-link if parent exists, else raise `orphan_plan_issue` for human triage.
4. **Linkage Propagation Metric** – Accepted. `linkage_latency_seconds` histogram will be emitted; RED alert at p95 > 60 sec.
5. **Audit-Trail Hook** – Implementation already scheduled (see action-item #5). Deliverable updated to emit SHA-256 digest + `(lamport, vc)` tuple per mutation.

### Updated Action Items
| # | Task | Owner | Due g | Done? |
|---|------|-------|-------|-------|
| 1 | Add `writeOnce` rule to schema & enforce in Supervisor Agent | platform-team | 58 |  |
| 2 | Implement hybrid Lamport+VC ordering, update tests | architect-2 | 58 |  |
| 3 | Deploy orphan auto-repair cron job | infra-team | 59 |  |
| 4 | Expose `linkage_latency_seconds` metric & alert | observability-team | 59 |  |
| 5 | Complete audit-trail digest hook & CI | core-team | 60 |  |

## Architect-1 Acceptance & Close-Out (g=59)

> **Author:** architect-1  
> **Trace-ID:** `trace://architect-1/g59/stu901`  
> **Vector Clock:** `vc://arch1@59:0`

Acknowledged Architect-2 Rebuttal; all objections addressed. Action items 1–5 are now part of `plan_hierarchy_integrity_g59` and tracked via registry map.

No further dissent; moving clarification status to **ALIGNED** pending implementation verification at g60. 