# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_019_md",
        "g_annotation_created": 19,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Refactored to align with the standardized ADR template as per ADR-OS-021. Moved embedded annotation to the header.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To define the unified Observability & Budget Framework for the HAiOS runtime.",
        "authors_and_contributors": [
            { "g_contribution": 19, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 231, "identifier": "platform-observability-wg" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "core_atomic_io_py_g222",
            "utils_cost_meter_py_g226",
            "engine_py_g120"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-019: Observability & Budget Governance

*   **Status**: Proposed
*   **Date**: 2025-06-11
*   **Deciders**: platform-observability-wg
*   **Reviewed By**: \[List of reviewers]

---

## Context

Phase-1 introduces live execution on a single node. To keep the "titanium" promise we need **continuous visibility** (metrics, logs, traces) and **cost guard-rails** (CPU, memory, disk, tokens, USD). Existing ADRs focus on artefact-level auditability but lack runtime telemetry and budget enforcement.

## Assumptions

*   [ ] The performance impact of the Prometheus and OpenTelemetry clients is acceptable.
*   [ ] The chosen metric taxonomy is comprehensive enough for initial monitoring and alerting needs.
*   [ ] Self-hosted Prometheus and Grafana are suitable for the Phase-1 deployment model.
*   [ ] The observability and budget framework is robust against event loss, metric spikes, and storage failures.
*   [ ] The system can detect and recover from misconfigured or missing observability endpoints.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-029, ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** Event-driven architecture addresses distributed system communication patterns; asynchronous processing prevents blocking.
- **Self-Critique:** Missing explicit handling of event ordering and potential message loss in distributed environments.

### Event Ordering v1.0
- **Compliance Proof:** Event sequencing and timestamp management ensure consistent event processing across distributed components.
- **Self-Critique:** Clock synchronization challenges in distributed systems could affect event ordering accuracy.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about event delivery reliability, processing latency, and storage durability.
- **Self-Critique:** Only three assumptions listed; event-driven systems likely have more implicit assumptions about network reliability and processing capacity.

### Separation of Concerns v1.0
- **Compliance Proof:** Clear separation between event generation, routing, processing, and storage responsibilities.
- **Self-Critique:** Event schema evolution and backward compatibility might blur separation boundaries over time.

### Scalability v1.0
- **Compliance Proof:** Event-driven architecture enables horizontal scaling of event processors and consumers.
- **Self-Critique:** Event volume spikes could overwhelm processing capacity; needs careful capacity planning and backpressure handling.

### Traceability v1.0
- **Compliance Proof:** Event logs provide complete audit trail of system state changes and decision points.
- **Self-Critique:** High event volumes might make trace analysis challenging; requires efficient indexing and querying capabilities.

## Decision

**Decision:**

> Implement a unified **Observability & Budget Framework** with the following mandatory controls.
>
> | ID | Control | Mandatory artefacts / endpoints | Enforcement / alert path |
> | :--- | :--- | :--- | :--- |
> | **19-O1** | *Prometheus metrics endpoint* | HTTP `/metrics` started by engine bootstrap (`port=8000` default). | Exposes Counters, Gauges, Histograms defined below; missing endpoint â†’ hard fail on readiness check. |
> | **19-O2** | *Metric taxonomy* | Prefix `haios_â€¦`; required series:<br>â€¢ `haios_task_total{type, result}`<br>â€¢ `haios_task_duration_seconds{type}` (Histogram)<br>â€¢ `haios_registry_lock_wait_seconds` (Histogram)<br>â€¢ `haios_tokens_total{agent}`<br>â€¢ `haios_usd_spend_total` | PlanRunner & atomic\_io increment metrics; CI test asserts presence of all required series. |
> | **19-O3** | *CostMeter integration* | Each task writes `cost_record` block (CPU sec, disk bytes, tokens, usd) into its entry in `exec_status_<g>.txt`. | CostMeter also updates Prometheus counters. |
> | **19-O4** | *Config-driven budgets* | `haios.config.json.budgets` keys:<br>â€¢ `cpu_seconds`<br>â€¢ `mem_bytes`<br>â€¢ `disk_bytes`<br>â€¢ `tokens`<br>â€¢ `usd` | CostMeter compares running totals; on >100% triggers `BUDGET_EXCEEDED` â†’ soft-kill; on >90% raises Prometheus `budget_warning` alert. |
> | **19-O5** | *Weekly cost snapshot* | Plan template `COST_REPORT` emits `cost_report_g###.md` summarising last 7 days (auto-generated). | Snapshot stored & registered; failing to produce report raises `COST_REPORT_MISSED` Issue. |
> | **19-O6** | *Grafana dashboards & alerts*| JSON dashboards under `docs/observability/grafana/`; Alertmanager rules yaml in repo. | CI lints dashboard JSON & alert rules. |
> | **19-O7** | *Trace context* | OpenTelemetry spans: `plan`, `task`, `file_write`. Trace id embedded in annotation block (`trace_id`). | Jaeger exporter required in strict mode; DEV\_FAST may skip. |

### Relationship to ADR-OS-029 (Universal Observability)

The controls in this ADR provide the specific implementation details (Prometheus metrics, Grafana dashboards) for the principles mandated in **ADR-OS-029**. Control **19-O7** (Trace context) is the direct, practical application of the universal trace propagation policy.

ADR-OS-029 elevates this from a single control to a core, system-wide requirement:
*   The `trace_id` is not just an embedded field; it is a fundamental propagation context that MUST be passed to every function, service, and agent interaction.
*   This ensures that even if a specific metric is not captured for a subsystem, its actions can still be causally linked within a distributed trace.

In essence, this ADR provides the "how" (OpenTelemetry, Prometheus), while ADR-OS-029 provides the non-negotiable "what" and "where" (universal propagation).

**Confidence:** High

## Rationale

1.  **Run-time truths > post-mortem guesses**
    *   Self-critique: Live metrics catch drift before it hurts.
    *   Confidence: High
2.  **Budgets as config, not tribal knowledge**
    *   Self-critique: The same locked config file drives enforcement and alerts.
    *   Confidence: High
3.  **Artefact â†” metric correlation**
    *   Self-critique: `g_counter`, `plan_id`, `trace_id` tie Prometheus, logs, and snapshots together for seamless audit.
    *   Confidence: High

## Alternatives Considered

1.  **Push metrics to external SaaS (Datadog)**
    *   Brief reason for rejection: heavier footprint, licence friction. Self-hosted Prom+Grafana keeps Phase-1 lightweight and audit-friendly.
    *   Confidence: High

## Consequences

*   **Positive:** Adds `prometheus_client`, `opentelemetry-sdk` deps (~3 MB). Engine must open one extra port (can be auth-gated by reverse proxy). Developers need Docker Compose with Grafana/Prom for local fuzzing (template provided).
*   **Negative:** Increased complexity in the local development setup. Requires maintaining dashboard and alert configurations as code.

## Clarifying Questions

* How is the USD cost per token calculated and configured in the CostMeter?
* What is the retention policy for metrics and traces?
* How are metric and trace data validated for accuracy and completeness, and what is the process for handling gaps or anomalies?
* What mechanisms are in place to detect and recover from misconfigured or missing observability endpoints?
* How is access to sensitive observability and budget data controlled and audited?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*

