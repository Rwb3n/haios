# ADR-OS-007: Integrated Testing Lifecycle & Artifacts

*   **Status:** Proposed
*   **Date:** 2025-06-08 
*   **Context:**
    An autonomous development system can inadvertently produce flawed code or "hallucinate" test success. To ensure project quality and reliability, a rigorous, evidence-based testing lifecycle must be an explicit and non-negotiable part of the development process. Claims of success must be backed by verifiable proof.

*   **Decision:**
    We will implement a closed-loop, evidence-based testing lifecycle built on three core principles:
    1.  **Dedicated Testing Plans & Artifacts:** The acts of defining tests, executing tests, and recording results will be handled by dedicated, typed `Execution Plans` that produce specific, machine-parsable `Test Script` and `Test Results` artifacts.
    2.  **Separation of Duties:** The agent persona responsible for development (`Coding Agent` executing `DEVELOPMENT` plans) is explicitly prohibited from generating the official `Test Results Artifact`. This artifact may only be produced by a trusted `Testing Agent` executing a `TEST_EXECUTION` plan.
    3.  **Validation of Evidence:** The `VALIDATE` phase acts as an auditor. It does not trust claims of success; it programmatically parses the `Test Results Artifact` (the evidence) to verify outcomes and update the quality status of the artifacts that were tested.

*   **Rationale:**
    *   **Prevents "Fox Guarding the Hennhouse":** Separating the duties of coding and test result generation ensures that the agent writing the code cannot fake its own test outcomes. This is a fundamental trust and security principle.
    *   **Evidence over Declaration:** The system's state of quality is based on verifiable, machine-readable `Test Results Artifacts`, not on an agent's declarative statement of completion. This makes the entire process auditable and reliable.
    *   **Makes Testing a First-Class Citizen:** By dedicating plan types (`VALIDATION_STRATEGY_DEFINITION`, `TEST_EXECUTION`) and artifact types (`Test Script`, `Test Results`) to testing, it is treated as a core part of the development process, not an afterthought.
    *   **Enables Quality Gates:** The verified test outcomes, recorded in `EmbeddedAnnotationBlock.quality_notes`, serve as the basis for automated quality gates defined in `Initiative Plan` exit criteria.

*   **Testing Lifecycle & Artifact Flow:**

    1.  **Scaffolding (`SCAFFOLDING` Plan):** `test_plan_notes_from_scaffold` are embedded in new artifacts, creating an initial test plan. `Test Script` stubs are generated.
    2.  **Test Definition (`VALIDATION_STRATEGY_DEFINITION` Plan):** A `Coding Agent` populates the `Test Script` stubs with actual test logic. The output is a complete `Test Script Artifact`.
    3.  **Test Execution (`TEST_EXECUTION` Plan):**
        *   A trusted **`Testing Agent`** executes this plan.
        *   The agent runs the `Test Script Artifact(s)`.
        *   Its sole write-output is the official **`Test Results Artifact`** (e.g., a JSON log from the test runner). The `EmbeddedAnnotationBlock` of this artifact is effectively "signed" by the Testing Agent's identifier in the `authors_and_contributors` field.
    4.  **Validation (`VALIDATE` Phase):**
        *   A **`Validation Agent`** (or Supervisor) loads the `Test Results Artifact`.
        *   It verifies the artifact was authored by the trusted `Testing Agent`.
        *   It parses the results (passes, fails, coverage).
        *   It updates the `quality_notes` in the `EmbeddedAnnotationBlock` of the *source artifacts that were tested*.
        *   It logs new `Issues` for any test failures.
        *   It documents these actions in its `Validation Report`.

*   **Consequences:**
    *   **Pros:**
        *   Creates a high-trust, verifiable quality assurance process.
        *   The system becomes inherently self-auditing regarding test outcomes.
        *   Dramatically reduces the risk of AI shortcuts or errors going undetected.
    *   **Cons:**
        *   More overhead than a simpler model. It requires more `Execution Plans` and a more sophisticated orchestration between different agent roles/permissions.
        *   Requires a trusted, isolated process/agent for test execution.

*   **Alternatives Considered:**
    *   **Trust-Based Model:** Allowing the `CONSTRUCT` agent to run tests and self-report success. Rejected as it is fundamentally unverifiable and insecure.
    *   **Validation Phase Runs Tests:** Having the `VALIDATE` phase run the tests itself instead of a `TEST_EXECUTION` plan. Rejected because it conflates the concerns of *executing* tests (a `CONSTRUCT`-like activity) with *validating the results of execution* (a `VALIDATE` activity). Separating them is cleaner.