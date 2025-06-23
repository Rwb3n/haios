# Changelog: 2025-06-25 - Schema Retrofit for Distributed Systems

## Summary

This update represents a foundational hardening of the entire OS data model to support robust, observable, and secure distributed operations. Following the policies outlined in `docs/schema/ADR-RETROFIT-POLICIES`, all core OS Control File schemas have been retrofitted to align with the new distributed systems ADRs (023-029).

---

## 1. Core Policy Integration

The following cross-cutting concerns have been systematically integrated into the schema definitions:

*   **Observability (ADR-029):** `trace_id` fields have been added to nearly every event, log, history entry, and status update across all schemas. This provides a universal mechanism for tracking causality in a distributed environment.
*   **Event Ordering (ADR-027):** `vector_clock` fields were added where appropriate (e.g., `state.txt`, `snapshot_schema`) to ensure a clear causal ordering of events, supplementing the global `g` counter.
*   **Idempotency (ADR-023):** `idempotency_key` fields were added to schemas for mutable operations, such as `request_schema`, `issue_schema`, and plan status files, to prevent unintended side effects from retried operations.
*   **Partition Tolerance (ADR-028):** `partition_status` fields were introduced in key stateful files (`state.txt`, `init_plan_schema`, `exec_status_schema`) to explicitly track and manage the system's state during network partitions.
*   **Zero-Trust Security (ADR-025):** `access_control`, `authorized_agent_archetypes`, and `last_updated_by_archetype` fields were added to enforce security policies and track agent actions at a granular level.
*   **Dynamic Topology (ADR-026):** `escalation_policy` fields were added to schemas like `human_attention_queue_schema` to handle failures and timeouts in a distributed agent environment.

---

## 2. Affected Schema Artifacts

The following schema definition files in `docs/schema/` were updated:

*   `global_registry_map_schema.md`
*   `haios_config_schema.md`
*   `human_attention_queue_schema.md`
*   `init_issues_summary_schema.md`
*   `init_plan_schema.md`
*   `issue_schema.md`
*   `request_schema.md`
*   `request_summary_schema.md`
*   `snapshot_schema.md`
*   `state_schema.md`
*   `embedded_annotation_block_schema.md`
*   `exec_plan_schema.md`
*   `exec_status_schema.md`
*   `global_issues_summary_schema.md`
*   `global_project_summary_schema.md`

This comprehensive update ensures that all future development and OS operations are built upon a foundation that is explicitly designed for the complexities of a distributed environment. 