# ADR-OS-009: Issue Management & Summarization

*   **Status:** Proposed
*   **Date:** 2025-06-09
*   **Context:**
    A robust system requires a formal mechanism for tracking, managing, and resolving issues such as bugs, necessary enhancements, design flaws, or blocking conditions. A simple, unstructured log is insufficient. We need a system that allows issues to be treated as first-class entities, linked to their context (plans, artifacts), and summarized at different levels for effective project oversight.

*   **Decision:**
    We will implement a two-tiered, file-based issue management system that uses the "Index + Individual File" pattern.

    1.  **Individual Issue Files (`issue_<g>.txt`):** Each issue will be captured in its own dedicated, detailed OS Control File. This file will contain all information about the issue, including its description, type, severity, status, contextual links to plans and artifacts, comments, and resolution details. These files will be stored within the directory of the `Initiative` they pertain to (`os_root/initiatives/<g_init>/issues/`).
    2.  **Tiered Summaries:**
        *   **Initiative-Scoped Summary (`initiative_issues_summary_<g_init>.txt`):** Located within each initiative's directory, this file will provide a summary map of all issues specifically related to that initiative.
        *   **Global Summary (`global_issues_summary.txt`):** A single file at the top-level of `os_root/`, this will serve as an index to all `initiative_issues_summary_*.txt` files, providing a high-level, cross-initiative view of issue counts and statuses.

*   **Rationale:**
    *   **Atomicity & Traceability:** Treating each issue as a distinct, linkable file makes it a first-class entity. It can be referenced directly by plans, tasks, and `EmbeddedAnnotationBlock`s, creating a clear and traceable relationship between work, artifacts, and problems.
    *   **Rich Context:** The dedicated `issue_<g>.txt` schema allows for capturing rich, structured detail about an issue, including its resolution path, which is invaluable for auditing and knowledge sharing.
    *   **Scalability & Performance:** The two-tiered summary system ensures that getting an overview of issues (either for one initiative or globally) is fast, as it only requires parsing smaller summary files. The detailed, potentially large issue descriptions and comment threads are kept isolated in their own files until needed.
    *   **Supports Supervisor/Cockpit UI:** This structure is ideal for a UI. The global summary can power a top-level dashboard widget. Clicking into an initiative would load the initiative-scoped summary, and clicking an issue in that list would load the full `issue_<g>.txt` file for display.

*   **Workflow Integration:**
    *   **Creation:** New issues are created by the OS/agents during any phase (e.g., during `VALIDATE` when a test fails, during `ANALYZE` if an ambiguity is found, or during `CONSTRUCT` when a task is `BLOCKED`).
    *   **Management:** The status of an `issue_<g>.txt` file is updated as work is done to address it. `REMEDIATION` type `Execution Plans` are created specifically to resolve issues.
    *   **Summarization:** The OS is responsible for keeping the `initiative_issues_summary_*.txt` and `global_issues_summary.txt` files synchronized with the state of the individual issue files.

*   **Consequences:**
    *   **Pros:**
        *   Provides a highly structured and robust system for tracking all project issues.
        *   Clear separation of detailed records from high-level summaries.
        *   Deeply integrates issue tracking with the planning and execution lifecycle.
    *   **Cons:**
        *   Requires the OS to maintain consistency across three levels of files (individual issue, initiative summary, global summary) for every issue update.

*   **Alternatives Considered:**
    *   **External Issue Tracker (e.g., GitHub Issues, Jira):** Integrating with an external system. Rejected for the core OS to maintain self-containment, simplicity, and a unified data model. The OS could, however, have an agent that *synchronizes* its internal issues with an external tracker as a separate feature.
    *   **Single Monolithic Issue File:** A single JSON file containing all issues. Rejected as it would become a massive point of contention and would be slow to parse and update as the project grows.