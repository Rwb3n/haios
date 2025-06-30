# ADR-OS-039: The Argus Protocol (Continuous Runtime Auditing)

*   **Status**: Proposed
*   **Date**: 2025-06-26
*   **Deciders**: Architecture Team
*   **Reviewed By**: \[TBD]

---

## Context

Governance and validation in the current architecture are primarily "pre-flight" checks (Plan Validation Gateway) or "post-mortem" reviews (VALIDATE phase). This creates a gap during the CONSTRUCT phase where emergent, unexpected behavior (due to model drift, dependency changes, or runtime anomalies) can go undetected until after significant resources have been wasted or a flawed artifact has been produced. The system lacks a real-time, active auditor.

## Assumptions

*   \[ ] A stream of system events can be reliably ingested and processed in near real-time.
*   \[ ] A statistical model of "normal" operational behavior can be accurately built and maintained.
*   \[ ] Deviations from the normal operational baseline are reliable indicators of meaningful anomalies.
*   \[ ] The Auditor-Agent has the necessary permissions to access the event bus and the kill-switch flags.
*   \[ ] Granting a system agent autonomous authority to halt the entire OS is an acceptable and necessary safety feature.

## Models/Frameworks Applied

*   **Evidence-Based Development (Registry v1.0):**
    *   *Proof:* The protocol makes the runtime process itself the evidence to be validated. The Auditor-Agent continuously compares real-time event streams (the evidence) against a model of expected behavior.
    *   *Self-critique:* The anomaly detection model is a potential single point of failure. If it is poorly trained or becomes outdated, it could lead to false positives (unnecessary shutdowns) or false negatives (missed anomalies).
    *   *Exceptions:* None.
*   **Separation of Duties (Registry v1.0):**
    *   *Proof:* It establishes a new, distinct duty—active, real-time process auditing—and assigns it to a dedicated agent persona (the Auditor-Agent), which operates independently of the core execution agents.
    *   *Self-critique:* The Auditor-Agent has significant power (kill-switch authority). A bug or compromise in this single agent could have system-wide consequences.
    *   *Exceptions:* None.

## Decision

Mandate the **Argus Protocol**, a system for continuous, real-time runtime auditing, executed by a dedicated **Auditor-Agent** persona.

**Core Components:**

1.  **Agent Persona Update (ADR-OS-030):**
    *   The **Auditor-Agent** is an active, persistent process monitor that runs concurrently with all other operations.
2.  **Core Logic (Auditor-Agent):**
    *   **A) Real-Time Event Ingestion:** The agent subscribes to the primary system event bus to consume all significant events (e.g., `task_started`, `file_written`, `token_cost_logged`).
    *   **B) Anomaly Detection Engine:** The agent maintains a real-time statistical model of the system's normal operational behavior to detect deviations in:
        *   **Economic Anomalies:** Spikes in cost or duration.
        *   **Behavioral Drift:** Changes in model success/failure rates or strategy needs.
        *   **Causal Integrity Faults:** Events occurring out of logical sequence.
3.  **New Governance Mechanism (Kill-Switch Authority):**
    *   The Auditor-Agent is granted write-access to the kill-switch flags defined in ADR-OS-018.
    *   **On Critical Anomaly:** The agent writes to `control/hard_kill.flag` to halt the OS and logs a P0 issue.
    *   **On Warning Anomaly:** The agent writes to `control/write_lockdown.flag` to pause new actions and logs a P1 issue for review.

**Confidence:** Medium

## Rationale

1.  **Completes the Governance Loop:**
    *   The system gains governance at all three stages: Pre-flight (ADR-OS-038), In-flight (this ADR), and Post-flight (VALIDATE phase), providing comprehensive oversight.
    *   *Self-critique:* This adds significant complexity to the overall system architecture.
    *   *Confidence:* High
2.  **Proactive Failure Prevention:**
    *   Moves beyond preventing *planned* errors to detecting and halting *emergent*, unplanned errors in real time.
    *   *Self-critique:* The effectiveness is entirely dependent on the quality of the anomaly detection model.
    *   *Confidence:* Medium
3.  **Enables True Self-Awareness:**
    *   The data collected by the Auditor-Agent is the necessary input for future systems that can perform automated performance tuning and self-correction.
    *   *Self-critique:* This is a long-term vision; the immediate implementation will be a simpler version of this goal.
    *   *Confidence:* Medium

## Alternatives Considered

1.  **Log Analysis Only:** Rely on post-mortem analysis of logs to find anomalies.
    *   *Reason for rejection:* This is a reactive approach that cannot prevent damage from in-progress failures.
2.  **Embedded Checks in Core Agents:** Have each agent be responsible for its own runtime monitoring.
    *   *Reason for rejection:* Violates Separation of Duties and leads to duplicated, inconsistent monitoring logic across the system.

## Consequences

*   **Positive:**
    *   Provides a critical safety net against emergent, real-time failures.
    *   Completes the system's governance and validation framework.
    *   Lays the foundation for future self-tuning capabilities.
*   **Negative:**
    *   Introduces a highly complex new component (the Auditor-Agent and its anomaly detection engine).
    *   Grants a single agent the authority to halt the entire system, which is a significant risk.
    *   The system will incur a constant, low-level resource cost from the auditing process.

## Clarifying Questions

*   What specific event bus technology will be used?
*   What initial algorithms will be used for the anomaly detection engine, and how will it be trained?
*   What are the precise criteria for a "Critical Anomaly" vs. a "Warning Anomaly"?
*   Is there a manual override to prevent or reverse a kill-switch action taken by the Auditor-Agent?

---
*This ADR is now compliant with the standards set in ADR-OS-021 and ADR-OS-032.*