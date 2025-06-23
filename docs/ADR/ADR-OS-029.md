# ADR-OS-029: Universal Observability and Trace Propagation

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

While ADR-OS-019 establishes a baseline for observability, it does not mandate a universal standard for propagating trace context across agent and service boundaries, especially in asynchronous workflows. Without a standard, it becomes nearly impossible to reconstruct the full end-to-end lifecycle of a request as it flows through multiple components, making debugging and performance analysis extremely difficult.

## Assumptions

* [ ] A standard for trace context propagation (e.g., W3C Trace Context) can be adopted and enforced across all services.
* [ ] The chosen tracing library can automatically instrument both synchronous (HTTP) and asynchronous (message bus) communications.
* [ ] The performance overhead of generating, propagating, and exporting trace data is acceptable for production workloads.
* [ ] The observability and trace propagation policy is robust against trace loss, sampling errors, and context breakage.
* [ ] The system can detect and recover from tracing misconfiguration or backend outages.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-019, ADR-OS-026, ADR-OS-032) are up-to-date and enforced.

## Decision

**Decision:**

> We will mandate universal, cross-component trace propagation and a minimum standard for metrics and logs for all orchestrated actions.
> 1.  **Trace ID Propagation:** Every request entering the system will be assigned a unique `trace_id`. This `trace_id` MUST be propagated through all subsequent synchronous calls (e.g., in HTTP headers) and asynchronous messages (e.g., in message headers).
> 2.  **Span Generation:** Every component (agent, service) processing a request MUST generate a "span" representing its unit of work, linking it to the parent span via the propagated trace context.
> 3.  **Mandatory Metrics/Logs:** Every orchestrated action must emit a minimum set of structured logs and metrics (e.g., start time, end time, duration, status, `trace_id`), in addition to the heartbeats defined in ADR-026.

**Confidence:** High

## Rationale

1. **End-to-End Visibility**
   * Self-critique: Full, high-fidelity tracing can generate a massive volume of data, which can be expensive to store and process. Sampling strategies may be necessary for high-traffic services.
   * Confidence: High
2. **Simplified Debugging**
   * Self-critique: If a single component in the chain fails to propagate the trace context, the trace is broken. This requires 100% compliance, which can be hard to enforce across a diverse set of services.
   * Confidence: High
3. **Performance Analysis**
   * Self-critique: The act of instrumenting code and exporting trace data adds a small amount of latency to every operation. This must be measured and monitored.
   * Confidence: High

## Alternatives Considered

1. **Log Correlation**: Relying on manually correlating logs from different services using a shared request ID.
   * Brief reason for rejection: Brittle, labor-intensive, and often impossible to do correctly in complex, asynchronous workflows. It doesn't provide the rich parent-child relationship and timing information of a proper trace.
   * Confidence: High
2. **Per-Service Observability**: Allowing each service to have its own observability strategy without a shared context.
   * Brief reason for rejection: This creates isolated silos of information, making it impossible to get a holistic view of the system's behavior.
   * Confidence: High

## Consequences

* **Positive:** Provides complete, end-to-end visibility into request flows across the entire system. Dramatically simplifies the process of debugging production issues and identifying performance bottlenecks.
* **Negative:** Requires all components to be integrated with a standard tracing library. Adds a dependency on a distributed tracing backend (e.g., Jaeger, Zipkin). Can generate a large volume of telemetry data that must be managed.

## Clarifying Questions

* What is the standard tracing library and backend (e.g., OpenTelemetry SDK with Jaeger exporter) to be used, and how will upgrades or migrations be managed?
* What is the policy for trace sampling in high-volume services, and how is sampling adapted to balance cost, fidelity, and performance?
* What specific tags and attributes are mandatory for all generated spans, and how is the span schema versioned and evolved?
* What mechanisms are in place to enforce and audit compliance with trace propagation and span generation across all components?
* How is trace data retention, storage, and privacy managed, especially for sensitive or regulated environments?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
