# ADR-OS-009: Issue Management & Summarization

* **Status**: Proposed
* **Date**: 2025-06-09
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

A robust system requires a formal mechanism for tracking, managing, and resolving issues. A simple, unstructured log is insufficient. We need a system that treats issues as first-class entities, linked to their context (plans, artifacts), and summarized at different levels for effective project oversight.

## Assumptions

* [ ] A file-based, hierarchical issue management system is sufficient for the OS's internal needs.
* [ ] The overhead of maintaining summary files is acceptable for the performance gains in retrieving issue overviews.
* [ ] Issues can be adequately represented as structured JSON data.
* [ ] The file system can handle the volume and concurrency requirements of issue management.
* [ ] The system can detect and recover from synchronization bugs across issue, summary, and global files.
* [ ] The issue schema is extensible to capture all necessary nuances and cross-initiative dependencies.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Theory of Constraints (ToC) v1.0
- **Compliance Proof:** Two-tiered issue management system identifies bottlenecks at initiative and global levels, enabling systematic constraint resolution.
- **Self-Critique:** Maintaining consistency across three files for every issue update could become a source of synchronization bugs.

### First-Class Citizen Principle v1.0
- **Compliance Proof:** Issues are treated as first-class entities with dedicated file structure (issue_<g>.txt) rather than simple log entries.
- **Self-Critique:** File-based approach assumes sufficient for OS needs; may not scale to enterprise-level issue volumes.

### Hierarchical Organization v1.0
- **Compliance Proof:** Three-tier structure (individual issues -> initiative summaries -> global summary) provides scalable organization.
- **Self-Critique:** Bi-directional linking between issues, plans, and artifacts adds complexity to update logic.

### Traceability v1.0
- **Compliance Proof:** Issues linked to their context (plans, artifacts) providing complete audit trail and relationship mapping.
- **Self-Critique:** If issue schema is too rigid, may not capture all necessary nuances of problems.

### Performance Optimization v1.0
- **Compliance Proof:** Summary files provide performance gains for retrieving issue overviews without parsing all individual issue files.
- **Self-Critique:** Structure assumes UI will be primary consumer; less convenient for command-line inspection.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation about file-based sufficiency, overhead acceptance, and JSON representation.
- **Self-Critique:** Only three assumptions listed; issue management likely has more implicit assumptions about file system performance and concurrency.

### Scalability v1.0
- **Compliance Proof:** Hierarchical summarization prevents single monolithic issue file that would become contention point and slow to parse.
- **Self-Critique:** Three-file consistency requirement increases logical complexity for every issue update.

## Decision

**Decision:**

> We will implement a two-tiered, file-based issue management system. Each issue will be a distinct **`issue_<g>.txt`** file. These will be indexed by an **`initiative_issues_summary_*.txt`** at the initiative level, and all initiative summaries will be indexed by a single **`global_issues_summary.txt`** at the root.

**Confidence:** High

## Rationale

1. **Atomicity & Traceability**
   * Self-critique: The bi-directional linking between issues, plans, and artifacts adds complexity to the update logic.
   * Confidence: High
2. **Rich Context**
   * Self-critique: If the issue schema is too rigid, it may not capture all necessary nuances of a problem.
   * Confidence: Medium
3. **Scalability & Performance**
   * Self-critique: Maintaining consistency across three files for every issue update could be a source of synchronization bugs.
   * Confidence: High
4. **Supports Supervisor/Cockpit UI**
   * Self-critique: This structure assumes a UI will be the primary consumer; it might be less convenient for simple command-line inspection.
   * Confidence: High

## Alternatives Considered

1. **External Issue Tracker (e.g., GitHub Issues)**: Rejected for the core OS to maintain self-containment and a unified data model, though an external synchronization agent could be a future feature.
   * Confidence: High
2. **Single Monolithic Issue File**: Rejected as it would become a massive point of contention and would be slow to parse and update as the project grows.
   * Confidence: High

## Consequences

* **Positive:** Provides a highly structured and robust system for tracking project issues. Clear separation of detailed records from high-level summaries. Deeply integrates issue tracking with the development lifecycle.
* **Negative:** Requires the OS to maintain data consistency across three levels of files (individual, initiative summary, global summary) for every issue update, increasing logical complexity.

## Clarifying Questions

* What is the precise schema for `issue_<g>.txt`, and how is it versioned and evolved as requirements change?
* What is the trigger and mechanism for synchronizing the summary files? Is it immediate, batched, or event-driven, and how are failures detected and recovered?
* How are cross-initiative dependencies between issues tracked, visualized, and resolved?
* What audit and recovery mechanisms exist for desynchronization or corruption between individual, initiative, and global summaries?
* How does the system scale and maintain performance as the number of issues grows to enterprise levels?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
