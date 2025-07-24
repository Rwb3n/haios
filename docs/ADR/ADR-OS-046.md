ADR-OS-046: Cross-Reference Integrity Management Protocol
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: This ADR is based on the "Blast Radius" problem identified in the cross_validation_plan.md and provides the formal specification for the dependency_linter.py tool.
1. Context
The HAiOS canon is a deeply interconnected web of documents. ADRs depend on other ADRs, Execution Plans depend on Schemas, and Project Guidelines govern all of them. This interconnectedness is a source of strength, but also a significant source of risk.
A change to a single, foundational artifact (e.g., updating a core schema in ADR-OS-003) can have cascading, non-obvious impacts on dozens of other documents. Without an automated way to detect these dependencies, we risk architectural drift, where different parts of the canon slowly fall out of sync, leading to contradictions, broken assumptions, and implementation failures.
This ADR defines the protocol and tooling for maintaining the cross-reference integrity of the entire HAiOS knowledge base.
2. Models & Frameworks Applied
Specification-Driven Development (SDD Framework): This protocol is a key part of the "Specification Quality Gates." It provides the automated tooling to run "Specification Tests" that validate the consistency of the entire architectural specification layer.
The Governance Flywheel (ADR-OS-043): This protocol is a critical Enforcement mechanism in the flywheel. It ensures that the Principles & Standards (the canon) remain internally consistent.
Graph Theory: The underlying model for this protocol is a directed acyclic graph (DAG) where documents are nodes and dependencies are edges.
3. Decision
We will implement a formal Cross-Reference Integrity Management Protocol, which will be enforced by a new, mandatory CI/CD tool: the Dependency Graph Linter.
The Dependency Graph Linter (lint/dependency_linter.py)
Purpose: To build a complete dependency graph of the entire HAiOS canon and use it to detect broken links and analyze the "blast radius" of any proposed change.
Mechanism: The linter will be a Python script that runs automatically on every pull request that modifies a file in the docs/ directory.
The "Napkin Sketch" of the Linter's Workflow:
Generated code
+-------------------------------------------------------------+
|    1. ON PULL REQUEST (e.g., "Update ADR-OS-003.md")          |
+------------------------------┬------------------------------+
                               |
                               | Triggers the CI/CD Pipeline...
                               |
                               ▼
+------------------------------┴------------------------------+
|    2. DEPENDENCY GRAPH LINTER EXECUTION                     |
+-------------------------------------------------------------+
|                                                             |
|   A. `BUILD GRAPH`: Scan ALL files in `docs/`.              |
|      - Parse `EmbeddedAnnotationBlock` for                 |
|        `internal_dependencies` to create edges.             |
|      - Parse Markdown for `[link text](path)` to create edges.|
|                                                             |
|   B. `VALIDATE GRAPH`: Check for...                         |
|      - `BROKEN_LINKS`: Does the target of an edge exist?      |
|      - `CIRCULAR_DEPENDENCIES`: Are there any loops?         |
|                                                             |
|   C. `ANALYZE BLAST RADIUS`: For each changed file...       |
|      - Find all nodes that have an incoming edge from the   |
|        changed file (i.e., find all dependents).            |
|                                                             |
+------------------------------┬------------------------------+
                               |
                               | 3. REPORT FINDINGS
                               |
                               ▼
+------------------------------┴------------------------------+
|    4. PULL REQUEST COMMENT & STATUS CHECK                   |
|    - If BROKEN_LINKS found -> FAIL BUILD.                     |
|    - If BLAST RADIUS found -> POST COMMENT:                 |
|      "WARNING: This change impacts [ADR-028, ADR-054].       |
|       Please confirm they remain consistent."              |
|    - STATUS CHECK: BLOCKED until Operator acknowledges.     |
+-------------------------------------------------------------+
Use code with caution.
Implementation Details
Dependency Sources: The linter will parse two sources of dependency information:
Formal Dependencies: The internal_dependencies array within the EmbeddedAnnotationBlock of each artifact. This is for explicit, architectural dependencies.
Informal Dependencies: Standard Markdown links ([text](./path/to/file.md)) within the body of the documents. This is for informational cross-references.
Output: The linter will produce a dependency_graph.json file as a build artifact, which can be used for visualization and further analysis.
CI/CD Integration: The linter will be a mandatory check in our pre-commit hooks and our GitHub Actions workflow. A pull request that introduces a broken link must not be mergeable.
4. Consequences
Positive:
Makes our architectural knowledge base vastly more robust and reliable.
Automates the tedious and error-prone task of checking for broken links.
Provides an automated "blast radius" analysis, which is a critical tool for preventing unintended consequences when making changes to core documents.
Enforces a high degree of discipline in how we manage our documentation.
Negative:
Adds a new, potentially slow step to the CI/CD pipeline. The graph-building process may take time as the canon grows. (Mitigation: caching the graph and only re-computing changed nodes).
Can create "lint fatigue" if the "blast radius" warnings are too noisy. The reporting must be tuned to be concise and high-signal.