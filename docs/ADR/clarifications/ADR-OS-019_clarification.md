# ADR Clarification Record: ADR-OS-019

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Prometheus endpoint bound to 127.0.0.1 unless `haios.config.json.observability.public` set true.
- Metric cardinality guidelines restrict label combinations to <10k series.
- CostMeter converts OpenAI tokens to USD via configurable `usd_per_token` fetched daily.
- Grafana dashboards stored in JSON; editing via UI exports committed by CI helper script.
- Budget thresholds configurable per environment (dev/stage/prod) via config overlay.

## Dependencies & Risks
- **Metric Explosion:** Uncontrolled labels could overload Prometheus; enforced regex lint.
- **Token Cost Drift:** API price changes may skew budgets; daily cron updates exchange rate.
- **Port Exposure:** /metrics endpoint may leak info; reverse proxy restricts.
- **Alert Fatigue:** Too many budget alerts reduce signal; thresholds tuned via SLO review.
- **Storage Retention:** Long-term traces consume disk; Loki/tempo integration backlog.

## Summary
ADR-OS-019 introduces a unified Observability & Budget Framework using Prometheus metrics, OpenTelemetry traces, Grafana dashboards, and CostMeter budget enforcement to provide real-time visibility and guard-rails for resource usage.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What default retention period will Prometheus use for metrics in dev vs prod? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | How are secrets (e.g., API keys) scrubbed from traces and logs before export? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | Will budget enforcement support per-task overrides for resource-intensive migrations? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | Which alert channels (Slack, email) are integrated for budget and health alerts? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | How is metric taxonomy versioned to avoid breaking dashboards when labels change? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->


## Additional Notes
- Appendix H Observability policy references control IDs 19-O1‒O7.
- Grafana dashboard JSON validated by `grafana-dashboard-linter` in CI.

## Traceability
- adr_source: ADR-OS-019
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 