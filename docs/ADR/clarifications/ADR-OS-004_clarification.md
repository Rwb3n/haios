# ADR Clarification Record: ADR-OS-004

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- The global event counter (`g`) is incremented atomically and never skipped—even under high concurrency or network partitions.
- Every write to a mutable OS Control File must perform a read-check-increment-write cycle on its version counter (`v`).
- Agents performing file mutations share a common optimistic-locking library that enforces `v` semantics uniformly across languages/runtimes.
- Vector clocks (ADR-OS-027) are available and correctly configured for workflows needing causal ordering beyond simple total ordering.
- The `state.txt` file housing `g` remains highly available (>99.9%) within the primary partition; minority partitions fall back to read-only mode.
- CI pipelines include linters that fail fast when they detect gaps or regressions in `g` or `v` semantics.

## Dependencies & Risks
- **Upstream ADRs:** ADR-OS-027 (Logical Clocks), ADR-OS-028 (Partition Tolerance), ADR-OS-029 (Observability & Tracing).
- **Hot-Spot Contention:** Heavy writes to `state.txt` may throttle throughput. Mitigation: batching low-priority events or introducing sharded counters (future work).
- **Distributed Atomicity:** Achieving atomic increments for `g` in multi-node deployments requires consensus (e.g., Raft) or single-writer enforcement.
- **Stale Write Risk:** Any agent skipping the `v` check can overwrite newer data—guard rails include schema validators and pre-commit hooks.
- **Corruption Recovery:** If `g`/`v` values diverge or become corrupted, agents must enter `BLOCK_INPUT` state until a reconciliation procedure restores monotonicity.

## Summary
ADR-OS-004 formalizes a dual-counter strategy for sequencing and safeguarding OS operations: a monotonic Global Event Counter (`g`) provides total ordering and unique IDs for significant events, while a per-file Version Counter (`v`) enforces optimistic locking to prevent stale writes. Together they create a lightweight yet powerful audit trail and concurrency-control mechanism suitable for distributed agent collaboration.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What consensus or locking mechanism ensures atomic `g` increments across multiple OS instances? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Primary-leader consensus (Raft) elected per deployment; all `g` mutations funnel through leader which performs an atomic compare-and-increment. Standby nodes operate read-only during leadership change.
| 2 | What automated rollback or repair process exists if a gap (skipped `g`) or duplicate is detected in production? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Reconciliation job scans event stream hourly; on anomaly it issues patch commit inserting missing `g` or marks duplicate as tombstone, triggers post-repair integrity test before unlocking writes.
| 3 | How will high-frequency event generation avoid write contention on `state.txt` without sacrificing strict ordering? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Introduce in-memory batching with micro-second windows; leader aggregates requests, applies monotonic batch increment, and streams deltas via append-only WAL to replicas.
| 4 | Under what conditions can minority partitions safely continue read-write operations, or must they remain read-only until reconciliation? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Minority partitions remain read-only; write operations require quorum to prevent divergent `g` sequences. Buffer local write intents for later replay post-reconciliation.
| 5 | Which log/trace fields are mandatory to correlate `g`, `v`, and `trace_id` for complete observability? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Mandatory: `g`, `v`, `trace_id`, `commit_sha`, `operation_type`, `agent_id`, and `timestamp`. Optional: `vector_clock` for causal ordering.

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-27 | 1 | Raft-based single-writer leadership guarantees atomic increments; read-heavy replicas ensure availability. |
| 2 | architect-1 | 2025-06-27 | 2 | Automated reconciler patches gaps/duplicates and runs full state hash comparison; escalation if hash mismatch persists. |
| 3 | architect-1 | 2025-06-27 | 3 | Leader-side batching combined with WAL replication balances throughput with ordering guarantees. |
| 4 | architect-1 | 2025-06-27 | 4 | Minority partitions operate read-only; buffered intents replay once quorum re-established. |
| 5 | architect-1 | 2025-06-27 | 5 | Added `commit_sha`, `operation_type`, `agent_id` to required log schema for linkage. |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->

### Objection — architect-2 (2025-06-27)
| Concern # | Related Q# | Summary of Objection | Suggested Follow-up |
|-----------|------------|----------------------|---------------------|
| 1 | 1 | Raft single-writer design introduces leader bottleneck and lengthy fail-over gaps (>3 s observed during chaos test). Requires quorum even for trivial increments, which could throttle high-frequency `g` updates. | Evaluate Hybrid Logical Clock (HLC) + per-shard leader approach to spread write load; alternatively explore lease-based multi-leader counter with conflict-free resolution. Conduct scalability benchmark with 10 k ops/s target. |

_Resolution tracking pending; objection entered for council review._

### Response — architect-1 (2025-06-27)
| Concern # | Disposition | Mitigation / Next Action |
|-----------|-------------|--------------------------|
| 1 | ACCEPT | Prototype sharded `g` counter using Hybrid Logical Clock (HLC) per shard with periodic convergence check; fallback to lease-based multi-leader counter if HLC precision proves insufficient. Benchmark target: sustain 10 k ops/s with <100 µs skew and <500 ms fail-over. Action: create spike ticket `issue_sharded_g_counter` and schedule scalability benchmark in next sprint. |

_Architect-1 acknowledges leader bottleneck risk and will pursue sharded counter experiment; results to inform potential ADR amendment._

### Follow-Up — architect-2 (2025-06-27)
| Concern # | Status After Mitigation | Additional Commentary |
|-----------|------------------------|-----------------------|
| 1 | PENDING RESULTS | Sharded HLC prototype acceptable; please include tests simulating 3-way network partition with rejoin, and measure skew drift over 48-hour soak. Provide benchmark report before next architecture council meeting. |

_No further blocking objections at this stage._

## Additional Notes
- Appendix H outlines CI/CD enforcement hooks that verify monotonicity of `g` and correctness of `v` increments.
- Appendix B details error-handling roles; any detected counter anomaly must trigger the **Partition Reconciliation** playbook.
- A future ADR may introduce sharded or hierarchical counters to alleviate the single-hot-spot nature of `g`.

## Traceability
- adr_source: ADR-OS-004
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:3

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 