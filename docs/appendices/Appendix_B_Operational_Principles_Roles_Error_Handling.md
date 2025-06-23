# Appendix B: Operational Principles, Roles & Error Handling

<!-- EmbeddedAnnotationBlock v1.0 START -->
```json
{
  "artifact_id": "appendix_b_operational_principles_roles_error_handling_g26",
  "g_created": 26,
  "version": 1,
  "source_documents": [
    "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md"
  ],
  "frameworks_models_applied": [
    "Separation of Concerns v1.0",
    "Fail-Safe Design v1.0",
    "Traceability v1.0"
  ],
  "trace_id": "g26_b_ops",
  "commit_digest": null
}
```
<!-- EmbeddedAnnotationBlock v1.0 END -->

---

## Purpose
This appendix consolidates all operational doctrines: phase intents, agent roles, escalation protocols, and continuity strategies.

> NOTE: Portions of these documents were originally distributed across multiple markdown files. They are now centralized for easier reference and auditability.

### 1. Phase Intents & Core AI Actions

*(Migrated from IV-PHASE_INTENTS_CORE_AI_ACTIONS)*

#### ANALYZE
- Goal: Investigate a Request and draft an Analysis Report
- Key Action: `AI_Initiate_Analysis_And_Draft_Report`

#### BLUEPRINT
- Goal: Derive detailed Execution Plans from initiative stage goals
- Key Action: `AI_Blueprint_Execution_Plans_For_Initiative_Stage`

#### CONSTRUCT
- Goal: Execute tasks in an active `exec_plan` via authorized agents
- Key Action: `AI_Execute_Next_Viable_Task_From_Active_Plan`

#### VALIDATE
- Goal: Audit outcomes, verify evidence, and generate Validation Report
- Key Action: `AI_Validate_Completed_Execution_Plan`

#### IDLE
- Goal: Await new work or human input; handle blocking conditions
- Key Action: `AI_Manage_Idle_State_And_Await_Input`

## 2. Continuity, Error Handling & State Management

*(Migrated from V-CONTINUITY_ERROR_HANDLING_STATE_MANAGEMENT)*

### 2.1 Task Failure & Remediation (ADR-OS-011)

1. **Log** – error recorded in `exec_status_<g>.txt`.
2. **Isolate** – set task `status: FAILED`; create linked `BLOCKER` Issue; halt plan.
3. **Remediate** – supervisor approves a new `REMEDIATION` Execution Plan.

Policies applied: Idempotency (ADR-023), Failure Propagation (ADR-026), distributed tracing (ADR-029).

### 2.2 Constraint Violation Handling (ADR-OS-010)

When a `_locked*` constraint blocks work:
1. Mark task `BLOCKED`.
2. Log `BLOCKER` Issue.
3. Push item to `human_attention_queue.txt` requesting override.

### 2.3 State Integrity & Optimistic Locking (ADR-OS-004)

All mutable control files carry `v_file_instance`. Agents follow read-check-write; mismatched `v` aborts write and retries.

### 2.4 Snapshot Strategy

Snapshots (`snapshot_<g>.json`) capture key control files for audit only; never auto-replayed. Triggered after major validations or explicit Requests.

<!-- Begin migrated content snippet -->