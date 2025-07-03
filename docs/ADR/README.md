# Architecture Decision Records (ADR) Index

This directory contains all Architecture Decision Records for the Hybrid AI Operating System (HAiOS). ADRs document important architectural decisions, their context, rationale, and consequences.

## Quick Navigation

### 🏗️ **Core Concepts & Data Models (Foundation)**
- [**ADR-OS-001**](ADR-OS-001.md) - **Core Operational Loop & Phasing** - The five-phase state machine: ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE.
- [**ADR-OS-002**](ADR-OS-002.md) - **Hierarchical Planning Model** - Multi-tiered planning from `Request` → `Analysis` → `Initiative Plan` → `Execution Plan`.
- [**ADR-OS-003**](ADR-OS-003.md) - **Artifact Annotation Strategy** - Mandates the `EmbeddedAnnotationBlock` for self-describing artifacts.
- [**ADR-OS-004**](ADR-OS-004.md) - **Global Event Tracking & Versioning** - `g` counter for total event ordering and `v` versioning for optimistic locking.
- [**ADR-OS-005**](ADR-OS-005.md) - **Directory Structure & File Naming** - Configuration-driven project layout via `haios.config.json`.
- [**ADR-OS-009**](ADR-OS-009.md) - **Issue Management & Summarization** - Structured, tiered issue tracking from individual files to global summaries.

### ⚙️ **Operational Patterns & Execution**
- [**ADR-OS-006**](ADR-OS-006.md) - **Scaffolding Process** - Automated artifact creation using `Scaffold Definition` files and templates.
- [**ADR-OS-010**](ADR-OS-010.md) - **Constraint Management & Locking Strategy** - Using `_locked` fields to enforce architectural integrity and prevent agent drift.
- [**ADR-OS-011**](ADR-OS-011.md) - **Task Failure Handling & Remediation** - "Log, Isolate, and Remediate" strategy for robust error handling.
- [**ADR-OS-013**](ADR-OS-013.md) - **Pre-Execution Readiness Checks** - Mandates verification of task prerequisites to prevent guaranteed failures.
- [**ADR-OS-015**](ADR-OS-015.md) - **Precision Context Loading** - Efficient, targeted context loading for LLM agents using line/pattern slicing.
- [**ADR-OS-016**](ADR-OS-016.md) - **Live Execution Status Tracking** - Separating immutable plans from mutable status files (`exec_status_*.txt`).
- [**ADR-OS-018**](ADR-OS-018.md) - **Execution Status Persistence & Recovery** - *(Note: Content is about foundational security controls, not persistence. Needs review.)*
- [**ADR-OS-022**](ADR-OS-022.md) - **Mechanical Inventory Buffer** - Prevents redundant work by staging reusable resources in a crash-safe buffer.

### 🤖 **Agent & Tool Management**
- [**ADR-OS-012**](ADR-OS-012.md) - **Dynamic Agent Management** - Runtime agent registration and configuration via an agent registry and "Agent Cards".
- [**ADR-OS-030**](ADR-OS-030.md) - **Archetypal Agent Roles & Protocols** - Defines a fixed set of agent roles (Supervisor, Manager, etc.) with strict permissions and escalation paths.
- [**ADR-OS-033**](ADR-OS-033.md) - **Cookbook & Recipe Management System** - ⚠️ **PROPOSED** - Formal system for capturing, validating, and reusing implementation patterns across HAiOS projects.
- [**ADR-OS-034**](ADR-OS-034.md) - **Orchestration Layer & Session Management** - ⚠️ **PROPOSED** - Unified coordination of multi-agent workflows with persistent session state and Cockpit interface.
- [**ADR-OS-035**](ADR-OS-035.md) - **The Crystallization Protocol & Gatekeeper Agent** - ⚠️ **PROPOSED** - Formal two-space system for validating exploratory work before canonization.

### 🔍 **Quality, Governance & Meta-Architecture**
- [**ADR-OS-007**](ADR-OS-007.md) - **Integrated Testing Lifecycle** - Evidence-based testing with a strict separation of duties between agents.
- [**ADR-OS-008**](ADR-OS-008.md) - **OS-Generated Reporting Strategy** - Mandates `Analysis`, `Validation`, and `Progress` reports for human oversight.
- [**ADR-OS-014**](ADR-OS-014.md) - **Project Guidelines Artifact** - A durable, version-controlled home for project standards, conventions, and checklists.
- [**ADR-OS-021**](ADR-OS-021.md) - **Explicit Assumption Surfacing** - Mandates that all ADRs surface assumptions, confidence levels, and self-critiques.
- [**ADR-OS-031**](ADR-OS-031.md) - **Pre-Initiative Source Artifact Standards** - Defines the required set of upstream documents (PRD, TRD, etc.) for any new initiative.
- [**ADR-OS-032**](ADR-OS-032.md) - **Canonical Models and Frameworks Registry & Enforcement** - A registry of best practices (KISS, DRY, ToC) that artifacts must explicitly reference and prove compliance with.

### 🌐 **Distributed Systems & Cross-Cutting Policies**
- [**ADR-OS-019**](ADR-OS-019.md) - **Observability & Budget Governance** - Defines Prometheus metrics, cost tracking, and budget enforcement.
- [**ADR-OS-020**](ADR-OS-020.md) - **Runtime Modes & Developer Experience** - Defines `STRICT` and `DEV_FAST` modes to balance safety and velocity.
- [**ADR-OS-023**](ADR-OS-023.md) - **Universal Idempotency & Retry Policy** - A cross-cutting policy for safe retries with exponential backoff and circuit breakers.
- [**ADR-OS-024**](ADR-OS-024.md) - **Asynchronous and Eventual Consistency Patterns** - Standardizes on event-driven communication, sagas, and eventual consistency.
- [**ADR-OS-025**](ADR-OS-025.md) - **Zero-Trust Internal Security Baseline** - Mandates mTLS and token-based auth for all internal service communication.
- [**ADR-OS-026**](ADR-OS-026.md) - **Dynamic Topology, Health Checking, and Failure Propagation** - Defines service discovery, heartbeats, and status propagation.
- [**ADR-OS-027**](ADR-OS-027.md) - **Global and Vector Clock Event Ordering** - Specifies the use of logical clocks to preserve causality in distributed workflows.
- [**ADR-OS-028**](ADR-OS-028.md) - **Partition Tolerance and Split-Brain Protocol** - Defines explicit CAP trade-offs and reconciliation strategies for network partitions.
- [**ADR-OS-029**](ADR-OS-029.md) - **Universal Observability and Trace Propagation** - Mandates end-to-end distributed tracing via universal `trace_id` propagation.

### 🚀 **Implementation & Phasing**
- [**ADR-OS-017**](ADR-OS-017.md) - **Phase 1 - MVP Engine & Tooling** - Defines the scope and deliverables for the initial implementation phase.

---

## Contributing to ADRs

When proposing a new ADR:
1. Use the next available ADR-OS-XXX number.
2. Follow the established template format defined in `adr_os_template.md` and mandated by `ADR-OS-021`.
3. Update this index with the new ADR.
4. Ensure the ADR includes a valid `EmbeddedAnnotationBlock`.
5. Ensure the ADR complies with the governance standards in `ADR-OS-031` and `ADR-OS-032`. 