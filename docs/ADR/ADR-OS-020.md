# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_020_md",
        "g_annotation_created": 20,
        "version_tag_of_host_at_annotation": "1.2.0"
    },
    "payload": {
        "description": "Refactored to align with the standardized ADR template as per ADR-OS-021. Moved embedded annotation to the header.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To define official runtime modes to balance safety and developer velocity.",
        "authors_and_contributors": [
            { "g_contribution": 20, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 232, "identifier": "dx-steering-committee" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "core_config_loader_py_g151",
            "engine_py_g120",
            "utils_cost_meter_py_g226"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-020: Runtime Modes & Developer Experience

*   **Status**: Proposed
*   **Date**: 2025-06-11
*   **Deciders**: dx-steering-committee
*   **Reviewed By**: \[List of reviewers]

---

## Context

Phase-1 aims for *titanium-grade* safety, but everyday contributors need a faster inner loop. Every run currently executes full readiness checks, writes snapshots, and enforces hard budgetsâ€”great for CI, heavy for day-to-day coding. We need an **official switchboard** so devs can trade off rigour for velocity *without* bypassing audit expectations.

## Assumptions

*   [ ] A command-line flag is a sufficient and conventional way for developers to switch modes.
*   [ ] The two defined modes, `STRICT` and `DEV_FAST`, cover the vast majority of use cases for Phase-1.
*   [ ] The risks of skipping certain checks in `DEV_FAST` mode are acceptable for local development environments.
*   [ ] The system can detect and prevent the use of DEV_FAST artifacts as dependencies in STRICT mode.
*   [ ] The runtime mode switching logic is robust against misconfiguration and race conditions.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Human-Centered Design v1.0
- **Compliance Proof:** Agent card design prioritizes human oversight capabilities and clear status communication for effective human-AI collaboration.
- **Self-Critique:** Card format might not accommodate all relevant agent context; could lead to oversimplified representation of complex agent states.

### Self-Describing Systems v1.0
- **Compliance Proof:** Agent cards provide self-contained descriptions of agent capabilities, status, and current context.
- **Self-Critique:** Self-description accuracy depends on agent's ability to accurately assess its own state; potential for self-reporting bias.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about human oversight needs, card format effectiveness, and agent self-awareness capabilities.
- **Self-Critique:** Only three assumptions listed; agent management likely has more implicit assumptions about human availability and intervention capabilities.

### Traceability v1.0
- **Compliance Proof:** Agent cards provide traceable record of agent activities and decision points for audit and debugging.
- **Self-Critique:** Card updates might not capture all relevant context changes; granularity balance between completeness and usability.

### Standardization v1.0
- **Compliance Proof:** Consistent agent card format enables systematic comparison and management across multiple agents.
- **Self-Critique:** Rigid standardization might not accommodate diverse agent types and specialized requirements.

### Transparency v1.0
- **Compliance Proof:** Agent cards expose internal agent state and reasoning to human operators for better oversight.
- **Self-Critique:** Too much transparency might overwhelm human operators; needs careful balance of detail and clarity.

## Decision

**Decision:**

> Introduce a **`runtime.mode`** field in `haios.config.json` (override-able by CLI flag `--mode`). Exactly two modes are recognised for Phase-1:
>
> | Mode | Purpose | Behaviour deltas from STRICT | Artefact labelling |
> | :--- | :--- | :--- | :--- |
> | `STRICT` *(default)* | CI, prod runs, releases | â€¢ Full readiness checks<br>â€¢ Snapshots required<br>â€¢ Budgets enforced at 100%<br>â€¢ Detached signatures verified<br>â€¢ Kill-switch escalation on first violation<br>â€¢ **Full trace export required** | No suffix (e.g. `snapshot_g230.txt`) |
> | `DEV_FAST` | Local dev & spike branches | â€¢ Readiness failures â†’ *warning* only<br>â€¢ Snapshots **skipped** unless task type explicitly `CREATE_SNAPSHOT`<br>â€¢ Budgets enforced at 150% (soft-kill beyond)<br>â€¢ Detached signature **validation skipped**, signing still happens<br>â€¢ Prometheus metrics still emit<br>â€¢ **Traces are still generated and propagated, but export MAY be skipped (ADR-OS-029)** | Artefacts gain `devfast` suffix: `exec_status_g231_devfast.txt` & registry entry flag `"dev_mode": true` |
>
> ### Config schema changes
>
> ```jsonc
> "runtime": {
>   "mode": "STRICT",      // enum STRICT | DEV_FAST
>   "cli_override": true     // allows --mode flag
> }
> ```
>
> ### Execution-time enforcement
>
> *   `engine.py` resolves mode: CLI flag > config > default.
> *   `PlanRunner` branches on mode for:
>     *   snapshot scheduling,
>     *   readiness severity, and
>     *   budget threshold multiplier.
> *   `atomic_io` and `CostMeter` remain unchangedâ€”safety rails still active.

**Confidence:** High

## Rationale

1.  **Make the common case fast**
    *   Self-critique: Skipping snapshots & downgrading early errors makes iterative coding seconds, not minutes.
    *   Confidence: High
2.  **Still audit everything**
    *   Self-critique: Artefact suffix + registry flag ensure dev runs are distinguishable and ignorable during formal reviews.
    *   Confidence: High
3.  **Zero hidden branches in prod**
    *   Self-critique: Only two modes; dev mode must be explicitly configured or flagged.
    *   Confidence: High

## Alternatives Considered

1.  **Full continuum of tuning knobs**
    *   Brief reason for rejection: more granular but explodes test matrix. Two modes keep reasoning tractable while solving 90% of pain.
    *   Confidence: High

## Consequences

*   **Positive:** Provides a clear, auditable distinction between development and production runs. Improves developer velocity for iterative tasks.
*   **Negative:** CI images MUST hard-set `runtime.mode=STRICT`; otherwise PRs fail policy check. Any artefact produced in DEV_FAST is *disallowed* as a dependency for STRICT plansâ€”Validator will raise `INPUT_NOT_STRICT` error. Documentation and scaffold generator must include mode flag examples.

## Clarifying Questions

* How does the validator check for `INPUT_NOT_STRICT`? Does it inspect the registry entry flag?
* Will there be a visual indicator in logs or UI "cockpit" to show which mode is active?
* How are mode transitions (STRICT <-> DEV_FAST) tracked, audited, and protected against accidental or unauthorized changes?
* What safeguards are in place to prevent DEV_FAST artifacts from being used in production or CI environments?
* How does the system handle mode-specific configuration drift or misconfiguration across distributed agents?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

