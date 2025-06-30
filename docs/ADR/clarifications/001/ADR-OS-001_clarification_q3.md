# ADR-OS Clarification Record – Clarification #3

**Subject:** *Phase Regression Handling in the Five-Phase Loop*
**Status:** ✅ Accepted
**Decision Date:** 2025-06-28
**Participants:** Architect-1 (proposer), Architect-2 (reviewer)
**Scribe:** ChatGPT-o3

---

## 1  |  Clarifying Question

> **How will the OS handle tasks that require jumping back to a previous phase**
> *(e.g. a validation failure that demands more construction work)?*

---

## 2  |  Consensus Answer

The platform will use a **REGRESSION_REMEDIATION plan** (RR-plan) – a specialised subtype of the existing *REMediation-plan* defined in ADR-OS-011 – to represent any backward jump in the operational loop.

### 2.1 Core Mechanics

| Element                     | Final Decision                                                                                                                                                                                                                                                  |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Trigger**                 | Validation agent emits a `PHASE_REGRESSION_REQUEST` containing the target earlier phase and a root-cause report (RCR).                                                                                                                                          |
| **Plan Creation**           | The Supervisor spawns one RR-plan per distinct root-cause **branch** (`branch_id = SHA-1(trace_id)`), copying the failing plan’s vector-clock snapshot (`vc_parent`).                                                                                           |
| **Entry Phase**             | May start in **ANALYZE, BLUEPRINT, CONSTRUCT, or VALIDATE** (depth 1-4). Depth > 2 requires a SupervisorConsensus quorum; depth > 1 is blocked during declared production hours unless quorum is met.                                                           |
| **Revision & Branching**    | RR-plan IDs take the form `EP-42-RR(brX)-n` where `brX` is the deterministic branch hash and `n` is the local revision. Parallel branches may proceed concurrently.                                                                                             |
| **Blueprint Handling**      | Supervisor forks the last canonical blueprint into `blueprint_v<rev>.yaml` inside the RR directory. All downstream agents reference that fork.                                                                                                                  |
| **Promotion on Success**    | A **Blueprint Promotion Service (BPS)** performs an atomic compare-and-swap (CAS) in a Raft-backed etcd cluster to publish the winning blueprint; superseded branches emit `VC_NULLIFY <id>` and seal `STATUS=OBSOLETE_*`.                                      |
| **Merge & Supersession**    | If multiple branches succeed, BPS initiates an automatic three-way YAML merge (`canonical`, `branch-A`, `branch-B`) with pluggable semantic validators. Non-conflicting merges auto-promote; semantic or key-level conflicts route to a human *Merge-Reviewer*. |
| **Governance & Escalation** | Default `max_regressions_before_human = 3` (configurable). SLA-based alerts escalate missing post-mortems; after 15 business days a governance freeze blocks further blueprint promotions for the affected initiative.                                          |
| **Garbage Collection**      | Nightly `gc-remediation` agent prunes artefacts/logs of obsolete branches after the initiative’s `retention_class` window (90 days / 7 years / ∞). A 1 KB tombstone file preserves replay integrity.                                                            |

### 2.2 Distributed-Systems Guarantees

* **Immutability & Traceability** – Original execution plans are sealed; all new work appends events.
* **Vector-Clock Integrity** – `VC_NULLIFY` maintains monotonic clocks for forensic replay.
* **Single-Writer Principle** – Only the Supervisor (and its BPS side-car) may create or promote RR-plans.
* **Partition Tolerance** – BPS enters read-only mode on etcd quorum loss; promotion resumes automatically after reconciliation.
* **Adaptive Batching** – Supervisor batches failure events (30 s base, adaptive to 5 min) and re-deduplicates on every batch close to prevent duplicate branches.

---

## 3  |  Rationale

* **Unifies Failure Handling** – By extending REMediation-plans, the design avoids parallel mechanisms.
* **Flexible Yet Safe Rollback** – One-shot, depth-guarded regression minimises plan churn while retaining policy gates.
* **Concurrent Workflows** – Branch-aware IDs, deterministic tie-breaks, and serialised promotion allow independent teams to iterate without race conditions.
* **Audit & Compliance** – Signed overrides, vector-clock lineage, tombstones, and retention classes satisfy both operational forensics and long-term regulatory needs.
* **Operational Resilience** – Adaptive batching, quorum-based CAS, and scoped governance freezes prevent systemic slow-downs during incident spikes.

---

## 4  |  Implications

| Area                | Impact                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Schema**          | Extend Execution-Plan header (`rework_depth`, `branch_id`), add `VC_NULLIFY` event type, introduce `canonical_blueprint.json`. |
| **Services**        | Add Blueprint Promotion Service, gc-remediation agent, semantic-validator plug-in framework.                                   |
| **Observability**   | New metrics: `haios_rrplan_regression_depth`, `haios_rrplan_merge_conflicts_total`; dashboards updated per ADR-OS-019.         |
| **Tooling & Tests** | Integration tests for multi-branch convergence, CAS promotion, semantic-validator hooks, governance freeze.                    |
| **Ops Playbooks**   | Procedures for etcd quorum loss, manual merge review, retention-class overrides, override_request workflow.                   |

---

## 5  |  Alternatives Considered

* **In-place Phase Rewind** – Rejected: mutates history, breaks audit trail and vector-clock causality.
* **Single-Phase-Only Regression** – Rejected: excessive chain-length under deep root causes, higher CI cost.
* **First-Writer-Wins Promotion** – Rejected after critique: risk of losing partial fixes; replaced with merge & validators.

---

## 6  |  Decision

All outstanding concerns resolved; Architect-2 declared **“No Further Dissent”** on 2025-06-28.
The RR-plan mechanism is **accepted** as the authoritative strategy for handling phase regression within the HAiOS operational loop.

---

## 7  |  Changelog

| Date       | Description                                                   | Author      |
| ---------- | ------------------------------------------------------------- | ----------- |
| 2025-06-24 | Initial PRP proposal                                          | Architect-1 |
| 2025-06-25 | Second iteration – merge with REMediation-plan, depth control | Architect-1 |
| 2025-06-26 | Third iteration – convergence logic, BPS, VC_NULLIFY         | Architect-1 |
| 2025-06-27 | Fourth iteration – implementation specifics, compliance knobs | Architect-1 |
| 2025-06-28 | Clarification accepted; record finalised                      | Scribe      |

---

*End of Clarification Record*