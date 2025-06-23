## E. Reporting & Reviews

To ensure transparency and support effective human-in-the-loop governance, the OS is responsible for generating a series of structured, human-readable reports. These reports are not simple logs; they are synthesized, analytical documents produced as version-controlled Project Artifacts, complete with their own `EmbeddedAnnotationBlock`. Report templates, defined as part of the project's standards, should include a header for license or data-sensitivity classification to support compliance requirements.

### Analysis Report (`.md`) (ADR-OS-008)
- **Example Filename:** `analysis_report_request_95_g100.md`
- **Purpose:** Provide a comprehensive and transparent record of the OS's reasoning when processing a new `Request`. Serves as the bridge between a high-level directive and a detailed strategic `init_plan`.
- **Generation:** Produced via a dedicated `ANALYSIS_EXECUTION` plan, triggered by the `ANALYZE` phase. The AI investigates the `Request` and populates a standard report template (defined in `project_templates/report_outlines/`) to ensure all critical aspects are covered.

### Validation Report (`.md`) (ADR-OS-008)
- **Example Filename:** `validation_report_exec_plan_125_g150.md`
- **Purpose:** Document the evidence-based verification of a completed `exec_plan`. It is the formal "sign-off" artifact that proves the work was done and its quality assessed.
- **Generation:** Produced as a primary output of the `VALIDATE` phase. The OS parses `Test Results` artifacts, checks for task completion, and synthesizes these findings. The `EmbeddedAnnotationBlock` of the report **must** include the `testing_agent_signature` (persona ID) to prove chain-of-custody for the validation evidence (ADR-OS-007).

### Progress Review (`.md`) (ADR-OS-008)
- **Example Filename:** `progress_review_g200.md`
- **Purpose:** Provide a high-level, cumulative summary of project progress, synthesizing information across multiple plans and initiatives. This is a key tool for stakeholder communication and strategic reviews.
- **Generation:** Created on-demand via a `REVIEW_EXECUTION` plan. This plan's tasks involve gathering and analyzing multiple artifacts, including `initiative_issues_summary_*.txt` and `global_issues_summary.txt` to surface active blockers (ADR-OS-009). The generation of a `Progress Review` may trigger the creation of a `snapshot_<g>.json` to ensure audit parity. Its annotation should link to any previous review it supersedes (via `supersedes_report_id_ref`) for easy comparison.

### Readiness Assessment (`.md`) (ADR-OS-013)
- **Example Filename:** `readiness_assessment_task_abc_g140.md`
- **Purpose:** An optional but recommended report produced by a pre-execution `Readiness Check` for complex tasks. It documents the status of all prerequisites (tools, artifacts, configs).
- **Generation:** Produced as an output of a `Readiness Check` step within the `CONSTRUCT` phase. It is typically stored alongside its originating `exec_plan_<g>.txt`.

---

### Structured Outlines & Critical Self-Assessment

All report types are generated based on predefined, structured outlines. Crucially, these outlines include sections that prompt the agent for **critical self-assessment** (ADR-OS-014), such as applying the `Bias Prevention Checklist` from `testing_guidelines.md`, forcing the AI to question its own results and report on the rigor of its process.

---

### Summary of Reporting Artifacts

| Report Type              | Triggering Phase / Plan Type         | Primary Inputs                                                        | Primary Consumers                |
|--------------------------|--------------------------------------|-----------------------------------------------------------------------|----------------------------------|
| **Analysis Report**      | `ANALYZE` / `ANALYSIS_EXECUTION`     | `request_<g>.txt`, Contextual Artifacts                               | Supervisor, Stakeholders         |
| **Validation Report**    | `VALIDATE`                           | `exec_plan_<g>.txt`, `exec_status_*.txt`, `Test Results` Artifacts    | Supervisor, Dev Team, QA         |
| **Progress Review**      | On-demand / `REVIEW_EXECUTION`       | Past Plans, Validation Reports, Issue Summaries                       | Stakeholders, Project Managers   |
| **Readiness Assessment** | `CONSTRUCT` (Pre-flight check)       | `exec_plan_<g>.txt` Task Definition (Inputs & Context)                | Supervisor, Dev Team             |

### Key Principles of Reporting

*   **Completeness:** It must summarize all relevant work within its scope (e.g., all tasks in a completed `Execution Plan`).
*   **Evidence-Based:** All claims and status updates must be backed by evidence, typically by linking to `Validation Report` artifacts or specific test results.
*   **Traceability:** It must provide clear links back to the `Initiative Plan`, `Execution Plan(s)`, and originating `Request` that it relates to. Furthermore, to comply with **ADR-029 (Observability)**, the report's own `trace_id` must be linked to the `trace_id`s of all significant input artifacts, creating an unbroken causal chain for auditing.