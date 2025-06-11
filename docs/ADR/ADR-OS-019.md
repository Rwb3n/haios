# ADR-OS-019 — Observability & Budget Governance

*Status*: **PROPOSED**
*Deciders*: platform-observability-wg
*Date*: 2025-06-11

## 1  Context

Phase‑1 introduces live execution on a single node.  To keep the “titanium” promise we need **continuous visibility** (metrics, logs, traces) and **cost guard‑rails** (CPU, memory, disk, tokens, USD).  Existing ADRs focus on artefact‑level auditability but lack runtime telemetry and budget enforcement.

## 2  Decision

Implement a unified **Observability & Budget Framework** with the following mandatory controls.

| ID        | Control                       | Mandatory artefacts / endpoints                                                                                                                                                                                                                 | Enforcement / alert path                                                                                                                |
| --------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **19-O1** | *Prometheus metrics endpoint* | HTTP `/metrics` started by engine bootstrap (`port=8000` default).                                                                                                                                                                              | Exposes Counters, Gauges, Histograms defined below; missing endpoint → hard fail on readiness check.                                    |
| **19-O2** | *Metric taxonomy*             | Prefix `haios_…`; required series:<br>• `haios_task_total{type, result}`<br>• `haios_task_duration_seconds{type}` (Histogram)<br>• `haios_registry_lock_wait_seconds` (Histogram)<br>• `haios_tokens_total{agent}`<br>• `haios_usd_spend_total` | PlanRunner & atomic\_io increment metrics; CI test asserts presence of all required series.                                             |
| **19-O3** | *CostMeter integration*       | Each task writes `cost_record` block (CPU sec, disk bytes, tokens, usd) into its entry in `exec_status_<g>.txt`.                                                                                                                                | CostMeter also updates Prometheus counters.                                                                                             |
| **19-O4** | *Config‑driven budgets*       | `haios.config.json.budgets` keys:<br>• `cpu_seconds`<br>• `mem_bytes`<br>• `disk_bytes`<br>• `tokens`<br>• `usd`                                                                                                                                | CostMeter compares running totals; on >100 % triggers `BUDGET_EXCEEDED` → soft‑kill; on >90 % raises Prometheus `budget_warning` alert. |
| **19-O5** | *Weekly cost snapshot*        | Plan template `COST_REPORT` emits `cost_report_g###.md` summarising last 7 days (auto‑generated).                                                                                                                                               | Snapshot stored & registered; failing to produce report raises `COST_REPORT_MISSED` Issue.                                              |
| **19-O6** | *Grafana dashboards & alerts* | JSON dashboards under `docs/observability/grafana/`; Alertmanager rules yaml in repo.                                                                                                                                                           | CI lints dashboard JSON & alert rules.                                                                                                  |
| **19-O7** | *Trace context*               | OpenTelemetry spans: `plan`, `task`, `file_write`. Trace id embedded in annotation block (`trace_id`).                                                                                                                                          | Jaeger exporter required in strict mode; DEV\_FAST may skip.                                                                            |

## 3  Rationale

* **Run‑time truths > post‑mortem guesses** – live metrics catch drift before it hurts.
* **Budgets as config, not tribal knowledge** – same locked config file drives enforcement and alerts.
* **Artefact ↔ metric correlation** – `g_counter`, `plan_id`, `trace_id` tie Prometheus, logs, and snapshots together for seamless audit.

## 4  Consequences

* Adds `prometheus_client`, `opentelemetry-sdk` deps (\~3 MB).
* Engine must open one extra port (can be auth‑gated by reverse proxy).
* Developers need Docker Compose with Grafana/Prom for local fuzzing (template provided).

## 5  Alternatives considered

*Push metrics to external SaaS (Datadog)* – heavier footprint, licence friction.  Self‑hosted Prom+Grafana keeps Phase‑1 lightweight and audit‑friendly.

---

```jsonc
/* EmbeddedAnnotationBlock */
{
  "artifact_id_of_host": "adr_os_019_md_g231",
  "version_tag": "v1.0",
  "g_created": 231,
  "g_last_modified": 231,
  "authors_and_contributors": ["platform-observability-wg"],
  "external_dependencies": [
    {"name": "prometheus_client", "version_constraint": ">=0.18,<1.0"},
    {"name": "opentelemetry-sdk", "version_constraint": ">=1.6,<2.0"}
  ],
  "internal_dependencies": [
    "core_atomic_io_py_g222",
    "utils_cost_meter_py_g226",
    "engine_py_g120"
  ],
  "quality_notes": {
    "unit_tests": {"status": "N/A", "notes": "Policy document"},
    "overall_quality_assessment": "PASS"
  }
}
```
