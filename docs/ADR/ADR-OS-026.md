# ADR-OS-026: Dynamic Topology, Health Checking, and Failure Propagation

* **Status**: Proposed
* **Date**: YYYY-MM-DD
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

ADR-OS-012 defines a registry for dynamic agents, but it relies on agents polling for changes. The system lacks a proactive mechanism for service discovery, standardized health checks, and propagating status changes (e.g., an agent becoming unhealthy) to dependent components. This ADR establishes a formal protocol for managing the lifecycle and health of agents and services within the OS.

## Assumptions

* [ ] All agents and services can expose a standardized HTTP `/health` endpoint.
* [ ] The central agent registry can handle the write load of frequent heartbeat updates from all active agents.
* [ ] The underlying network supports a lightweight subscription model (e.g., WebSockets, gRPC streams) for propagating status changes.
* [ ] The health checking and failure propagation protocol is robust against registry outages, network partitions, and heartbeat loss.
* [ ] The system can detect and recover from registry/health monitor misconfiguration or overload.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-012, ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision

**Decision:**

> We will implement a standardized protocol for dynamic topology, health checking, and status propagation.
> 1.  **Service Discovery:** The `agent_registry.txt` (from ADR-OS-012) will be the single source of truth for available services. Agents will register themselves upon startup.
> 2.  **Health Checking:** Every agent/service MUST expose a `/health` endpoint that returns its operational status (`UP`, `DEGRADED`, `DOWN`). A central health monitor will periodically poll these endpoints.
> 3.  **Heartbeating:** Every active agent MUST send a regular heartbeat to the agent registry to signal its liveness. Failure to receive a heartbeat within a configured interval will mark the agent as `UNHEALTHY`.
> 4.  **Failure Propagation:** The agent registry will expose a subscription-based stream of status changes. Supervisor agents and other interested components MUST subscribe to this stream to be immediately notified when a dependency's status changes.

**Confidence:** High

## Rationale

1. **Proactive Failure Detection**
   * Self-critique: Centralized health checking can be a bottleneck and a single point of failure. A decentralized, peer-to-peer gossip protocol could be more resilient but is significantly more complex to implement.
   * Confidence: High
2. **Dynamic System Topology**
   * Self-critique: Relying on a single registry for discovery couples all services to it. If the registry is down, no new connections can be made.
   * Confidence: Medium
3. **Reduces Stale State**
   * Self-critique: The "correct" interval for health checks and heartbeats is a difficult tuning problem. Too frequent, and it creates excess network traffic; too infrequent, and the system is slow to react to failures.
   * Confidence: High

## Alternatives Considered

1. **DNS-based Discovery**: Using DNS SRV records for service discovery.
   * Brief reason for rejection: DNS can have high propagation delays (due to caching), making it slow to react to changes in topology. It doesn't include a built-in health checking or status propagation mechanism.
   * Confidence: High
2. **Manual Configuration**: Hardcoding agent addresses in configuration files.
   * Brief reason for rejection: Extremely brittle and static. Does not support dynamic scaling or failover. This is the problem ADR-OS-012 was created to solve.
   * Confidence: High

## Consequences

* **Positive:** Creates a robust and self-healing system that can react quickly to component failures. Enables dynamic scaling of agents without manual reconfiguration. Provides a clear, centralized view of the health of the entire system.
* **Negative:** Adds network traffic due to health checks and heartbeats. Requires a highly available agent registry and health monitoring service. Increases the complexity of the agent lifecycle.

## Clarifying Questions

* What is the standard schema and versioning strategy for the `/health` endpoint response, and how are custom health signals supported?
* What is the protocol, failover, and security model for the status update subscription stream (e.g., gRPC, WebSockets), and how are missed updates handled?
* How do we prevent a "thundering herd" problem when a critical service comes back online and all subscribers try to connect at once?
* What mechanisms are in place to ensure high availability, failover, and recovery for the agent registry and health monitoring service?
* How are health check and heartbeat intervals tuned, monitored, and adapted to balance responsiveness and network overhead in different deployment scenarios?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.* 
