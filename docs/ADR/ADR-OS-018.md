# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_018_md",
        "g_annotation_created": 18,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Retrofitted to comply with ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To ensure framework compliance and improve architectural decision clarity.",
        "authors_and_contributors": [
            { "g_contribution": 18, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 4, "identifier": "Framework_Compliance_Retrofit" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "adr_os_032_md"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-018: Execution Status Persistence & Recovery

*   **Status**: Proposed
*   **Date**: 2024-05-31
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

The `CONSTRUCT` phase can be a long-running process involving multiple tasks that may take minutes, hours, or even days to complete. If the OS crashes, is forcibly terminated, or encounters a system failure during execution, all progress could be lost, forcing a complete restart from the beginning. A persistence mechanism is needed to save execution state and enable recovery from interruptions.

## Assumptions

*   [ ] The filesystem provides reliable persistence for execution state data.
*   [ ] Recovery can be performed safely without corrupting partially completed work.
*   [ ] The cost of frequent state persistence is acceptable compared to the cost of losing progress.
*   [ ] The persistence and recovery logic is robust against concurrent access and race conditions.
*   [ ] The system can detect and recover from incomplete or failed recovery attempts.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** State persistence enables recovery from failures; addresses consistency and durability requirements in distributed execution.
- **Self-Critique:** Missing explicit handling of concurrent access to state files and potential race conditions during recovery.

### Fail-Safe Design v1.0
- **Compliance Proof:** Automatic state persistence and recovery mechanisms ensure system can gracefully handle interruptions and failures.
- **Self-Critique:** Recovery process itself could fail or introduce inconsistencies; needs robust validation and rollback capabilities.

### Audit Trail v1.0
- **Compliance Proof:** Persistent execution state provides complete audit trail of task progression and system state changes.
- **Self-Critique:** State persistence might not capture all relevant context for debugging complex failure scenarios.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about filesystem reliability, recovery safety, and persistence cost trade-offs.
- **Self-Critique:** Only three assumptions listed; state persistence likely has more implicit assumptions about atomicity and consistency.

### Performance Optimization v1.0
- **Compliance Proof:** Incremental state persistence minimizes overhead while maximizing recovery capability; avoids full restart costs.
- **Self-Critique:** Frequent persistence operations might impact overall system performance; needs careful balance of frequency vs. overhead.

### Idempotency v1.0
- **Compliance Proof:** Recovery operations must be idempotent to safely restart from persisted state without side effects.
- **Self-Critique:** Ensuring true idempotency across all task types and external dependencies is complex and error-prone.

## Decision

**Decision:**

> We introduce the following **mandatory controls**. Any Phase-1 engine claiming compliance **MUST** implement them exactly as specified.
>
> | ID | Control | Mandatory artefacts / flags | Enforcement path |
> | :--- | :--- | :--- | :--- |
> | **18-S1** | *Secrets vault* | `vault/secrets.json.gpg` (age-encrypted). Secrets carry `scope` = \`global | initiative | plan | agent\`. | PlanRunner decrypts at start-up and surfaces **only** required scopes to task-handlers. |
> | **18-S2** | *Snapshot redaction* | `snapshot_utils` filters strings matching `vault.redact_regexes` before writing. | Failing to redact triggers snapshot write abort + `EMERGENCY_STOP`. |
> | **18-S3** | *Process isolation* | \`haios.config.json.execution.isolation = "none | strict"\` (default **strict**). | TaskExecutor enters chroot + drops to UID `haios` when strict. |
> | **18-S4** | *Resource limits* | `budgets.max_cpu_seconds`, `max_mem_bytes` in config. | CostMeter enforces; violation → soft-kill + `BUDGET_EXCEEDED`. |
> | **18-S5** | *Kill-switches* | Flag files:<br>• `control/soft_kill.flag`<br>• `control/write_lockdown.flag` | PlanRunner checks each task loop; atomic\_io blocks writes when lockdown flag present. |
> | **18-S6** | *Detached artefact signatures* | `<artifact>.sig` (Ed25519). | Signature verified on load; mismatch → `TAMPER_DETECTED` Issue + hard abort. |
> | **18-S7** | *Outbound network policy* | `guidelines/outbound_whitelist.rego` locked. | OPA side-car denies socket connect not matching allowlist. |

### Relationship to ADR-OS-025 (Zero-Trust Security)

The controls defined in this ADR (18-S1 through 18-S7) represent the **foundational, single-node security baseline**. They are primarily concerned with hardening the local execution environment.

**ADR-OS-025 builds directly upon this foundation**, extending the principles to a distributed, multi-agent, multi-service environment. Where this ADR secures the local process, ADR-OS-025 secures the *connections between processes*. The controls are complementary:

*   This ADR's `Secrets vault` (18-S1) provides the raw material for the mTLS certificates and service tokens defined in ADR-OS-025.
*   The `Process isolation` (18-S3) and `Outbound network policy` (18-S7) provide the in-depth defense for a service that has already been authenticated via the Zero-Trust mechanisms.

In short, this ADR is a mandatory prerequisite. A system cannot be compliant with ADR-OS-025 without first implementing the controls specified here.

**Confidence:** High

## Rationale

1.  **Layered defence**
    *   Self-critique: Even if one guard falls (e.g. chroot escape) others (write-lockdown, rlimits) contain damage.
    *   Confidence: High
2.  **Human-inspectable kill paths**
    *   Self-critique: Flag files & state fields leave a durable trace; auditors can prove **who** pulled which switch.
    *   Confidence: High
3.  **Future multi-agent safe**
    *   Self-critique: Scoping secrets and outbound policies per plan/agent lets us on-board un-trusted LLM agents without full credential exposure.
    *   Confidence: High

## Alternatives Considered

1.  **Use kernel LSMs (AppArmor/SELinux) instead of chroot**
    *   Brief reason for rejection: too OS-specific for Phase-1 scope.
    *   Confidence: High

## Consequences

*   **Positive:** Adds a small run-time overhead (OPA eval, signature checks) — acceptable for safety. Developers must initialise the vault and whitelist before first plan run. CI images need `age`, `ed25519` libs, and OPA binary (~15 MB). Existing ADRs **unchanged**; this ADR plugs the security gap and references them.
*   **Negative:** Adds dependencies (`age`, `pynacl`, OPA) that must be managed. Increases setup complexity for new developers.

## Clarifying Questions

*   What is the exact procedure for initializing the secrets vault?
*   How does the OPA side-car get configured and launched by the engine?
*   How are concurrent access and race conditions handled during state persistence and recovery?
*   What validation and rollback mechanisms are in place if recovery fails or results in inconsistent state?
*   How is the audit trail for state changes and recovery operations maintained and reviewed?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
