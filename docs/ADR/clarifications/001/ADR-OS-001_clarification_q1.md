# ADR-OS-001 Clarification — Network Partition Fallback Strategy

## 1  |  Clarifying Question

What is the fallback strategy if a phase transition times out due to a network partition?

## 2  |  Consensus Answer

A quorum-based acknowledgment (default 90%) is required to complete a configuration rollout. Nodes that fail to acknowledge are considered "stragglers" and are retried in the background. A rollout is automatically rolled back if the acknowledgment quorum falls below a safety threshold (default 75%). Straggler nodes are tracked via detailed metrics and surfaced in operational dashboards for visibility.

### 2.1 Core Mechanics

*   **Quorum-Based Rollout:**
    *   An orchestrator pushes a new configuration to all nodes in a target group.
    *   Rollout is considered successful if ≥ 90% of nodes send a successful acknowledgment (ACK) within a defined timeout.
*   **Straggler Reconciliation:**
    *   Nodes that do not ACK are placed in a "straggler" queue.
    *   The orchestrator retries the update on stragglers with exponential backoff (6 retries, starting at 30s, x2 multiplier, ±20% jitter, max 30 minutes).
    *   If a node fails all retries, it is flagged as `STALE_CONFIG`, a PagerDuty ticket is created, and it is added to a manual investigation queue.
*   **Rollback Safety Net:**
    *   If the ACK quorum drops below 75% at any point, the orchestrator initiates an immediate rollback to the last known-good configuration.
*   **Handling Successive Rollouts:**
    *   Before initiating a new rollout, the orchestrator checks the version of each node.
    *   Nodes flagged as `STALE_CONFIG` are force-updated to the new version instead of being rolled back. Force-update failures follow the standard straggler process.
*   **Permanent Partitions & Dead Nodes:**
    *   Nodes that remain in a `STALE_CONFIG` state for more than 24 hours are automatically de-registered from the quorum, tagged as `RETIRED`, and their record is retained for audit purposes. The quorum size is recalculated accordingly. An operator can manually re-enroll a retired node.
*   **Metric Granularity:**
    *   A Prometheus counter vector, `config_propagation_stragglers_total`, is implemented with a `reason` label to track failures.
    *   Reasons include: `timeout`, `load_error`, `network_partition`, and `unknown`.
    *   Dashboards provide a detailed breakdown of stragglers by reason.

## 3  |  Rationale

This strategy provides a balance between rollout velocity and system stability. A quorum-based approach prevents a small number of unresponsive nodes from blocking a deployment, while the two-tier rollback and straggler-handling mechanisms provide robust safeguards against widespread failures. The detailed metrics ensure that operational teams have full visibility into configuration drift and can intervene when necessary.

## 4  |  Implications

*   **Tooling:** Requires an orchestrator capable of tracking node versions and performing quorum-based rollouts.
*   **Observability:** Requires Prometheus and Grafana (or similar) for metrics and dashboarding.
*   **On-call:** PagerDuty (or similar) integration is required for notifications.

## 5  |  Alternatives Considered

*   **Halt-and-retry:** A simpler approach where the entire transition is halted and retried. This was rejected due to the potential for cascading failures and the lack of a degraded mode.
*   **Manual intervention:** Requiring a human to manually intervene in all cases of network partitions. This was rejected as it would not be scalable.

## 6  |  Decision

The quorum-based acknowledgment protocol with straggler reconciliation and a rollback safety net is the accepted strategy.

## 7  |  Changelog

| Date       | Description                                                   | Author      |
| ---------- | ------------------------------------------------------------- | ----------- |
| 2025-06-28 | Initial proposal of halt-and-retry mechanism.                 | Architect-1 |
| 2025-06-29 | Introduction of degraded mode and backoff with jitter.        | Architect-1 |
| 2025-06-30 | Adoption of adaptive quorum reconfiguration.                  | Architect-1 |
| 2025-07-01 | Implementation of secure, audited manual overrides.           | Architect-1 |
| 2025-07-03 | Introduction of canary rollouts and SLO remediation.          | Architect-1 |
| 2025-07-05 | Refinement of SLO remediation to require human approval.      | Architect-1 |
| 2025-07-07 | Introduction of emergency auto-apply mode.                    | Architect-1 |
| 2025-07-09 | Implementation of expanded emergency canary.                  | Architect-1 |
| 2025-07-10 | Final consensus on quorum-based ACK protocol.                 | Architect-1 |
| 2025-07-11 | Final clarifications and acceptance.                          | Architect-2 |