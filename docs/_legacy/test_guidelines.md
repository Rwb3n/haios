# Project Guideline: Comprehensive Testing Strategy

*   **Artifact ID:** (to be assigned upon registration, e.g., `guideline_testing_v1_gX`)
*   **Version:** 1.0
*   **Status:** Ratified
*   **ADR References:** ADR-OS-007, ADR-OS-013, ADR-OS-014, ADR-023, ADR-024, ADR-025, ADR-026, ADR-027, ADR-028, ADR-029

## 1. Core Philosophy: Evidence over Declaration

The guiding principle for all testing in this project is **verifiability through evidence**. An agent's claim that "the tests pass" is insufficient. All testing activities must produce durable, machine-parsable `Test Results Artifacts`. The `VALIDATE` phase does not trust claims; it audits the evidence. This principle is non-negotiable.

## 2. The Anatomy of a Good Unit Test

Every unit test written by any agent **MUST** adhere to the following structure and principles. The goal is clarity, isolation, and maintainability.

### 2.1. The AAA Pattern (Arrange, Act, Assert)

All tests must be structured into three distinct, clear sections.

*   **Arrange (Given):** Prepare everything the code needs to run. This includes:
    *   Instantiating the System Under Test (SUT).
    *   Creating necessary test data (e.g., input objects).
    *   Setting up test doubles (mocks, stubs, spies) for all external dependencies.
    *   The Arrange section should be limited to only what is essential for the specific behavior being tested.

*   **Act (When):** Trigger the single behavior being tested.
    *   This should be a single method call or function invocation on the SUT.
    *   Do not include assertions or complex logic in this section.

*   **Assert (Then):** Verify the outcome.
    *   Check the return value of the action.
    *   Check for any expected state changes in the SUT.
    *   Check that interactions with mocked dependencies occurred as expected (e.g., a logger was called with a specific message).
    *   While a single behavior is tested, multiple assertions related to that one outcome are acceptable and encouraged.

### 2.2. Naming Convention

Test names must be descriptive sentences that clearly state the behavior being tested.
*   **Convention:** `it('should [do X] when [condition Y]')` or `it('throws [ErrorType] when [condition Z]')`.
*   **Avoid:** Vague names like "test function" or "error case." The test name itself should serve as a specification.

### 2.3. Test Isolation and Determinism

*   **Isolation:** Tests **MUST NOT** depend on each other or on a shared, mutable state. They must be able to run in any order, or in parallel, and still produce the same result. Clean up any side effects (e.g., created files, database entries) in a `teardown` or `afterEach` block.
*   **Determinism:** Tests **MUST NOT** rely on unpredictable factors like `Date.now()`, `Math.random()`, or network latency. Use test doubles to control time (time-traveling fakes) and randomness (seeded PRNGs). All external network calls must be stubbed.

## 3. The Bias Prevention Checklist

This checklist **MUST** be applied by any `Validation Agent` or `Critique Agent` when reviewing test results or test scripts. It serves to combat "declaration-based confidence" and suspiciously perfect results.

### Design Validation (Reviewing Test Scripts)
- [ ] **Clarity of Intent:** Does the test name clearly describe a single, specific behavior?
- [ ] **Isolation:** Does the test clean up after itself and avoid relying on shared state?
- [ ] **Determinism:** Are all sources of randomness and external factors (time, network) controlled with test doubles?
- [ ] **Correctness of Assertions:** Do the assertions meaningfully validate the desired outcome, or are they trivial (e.g., `assert(true)`)?

### Execution & Result Interpretation (Reviewing `Test Results Artifacts`)
- [ ] **Anomalous Metrics:** Are performance metrics (e.g., latency) suspiciously low (e.g., <5ms), potentially indicating that the test failed before execution and measured a "fast failure"?
- [ ] **Error vs. Failure:** Are error rates (e.g., 100% HTTP failures) being misinterpreted as test logic failures? The root cause must be identified.
- [ ] **"Perfect" Results:** Are 100% success rates on complex integration tests backed by evidence of realistic workloads, or are they running against "too clean" data or an overly simplistic setup?
- [ ] **Scale & Duration:** Is the test scale (e.g., number of virtual users) and duration sufficient to reveal real-world performance issues or race conditions?

## 4. Unit-Testing Glossary

All agents must use this standard terminology when discussing or logging information about tests.

*   **AAA (Arrange, Act, Assert):** The canonical three-step structure of a unit test.
*   **Assertion:** An executable claim that must be true for the test to pass.
*   **Code Coverage:** Percentage of source code executed by the test suite. A useful metric, but high coverage does not guarantee high-quality tests.
*   **Fake:** A lightweight, working implementation of a dependency (e.g., an in-memory database).
*   **Fixture:** Reusable setup/teardown code or a pre-configured set of objects used for a test.
*   **Flaky Test:** A test that passes and fails intermittently without code changes, typically due to issues with asynchronicity, shared state, or uncontrolled external factors. Flaky tests MUST be quarantined or fixed immediately as they erode trust in the entire test suite.
*   **Integration Test:** A test that verifies the interaction between multiple components.
*   **Mock:** A test double that can be configured with expectations and can verify that specific methods were called with specific arguments.
*   **Spy:** A test double that wraps a real object, allowing the test to observe (or "spy on") interactions without altering the object's behavior.
*   **Stub:** A test double that provides canned answers to calls made during the test. It does not verify interactions.
*   **System Under Test (SUT):** The specific function, method, or class being exercised by the test.
*   **Test Double:** The generic term for any object or function that stands in for a real dependency in a test (includes mocks, stubs, fakes, spies, dummies).
*   **Unit Test:** A test that verifies a single "unit" of code (e.g., a function or method) in complete isolation from its dependencies.

## 5. Distributed Systems Compliance for Testing (ADR-023 to ADR-029)

- **Idempotency:** All test runners and result artifacts must include an `idempotency_key` unique to each run. Retries must not overwrite results unless explicitly allowed by policy.
- **Async/Consistency:** Distributed/integration tests must flag if results are only eventually consistent, and propagate this in artifacts.
- **Zero-Trust:** Test runner identity (`agent_id` and `archetype`) must be logged and included in artifacts; only authorized agents may mutate test results.
- **Topology & Failure:** Partitioned, incomplete, or retried tests must record the failure topology, escalation path, and fallback agent.
- **Event Ordering:** All logs and results must include a `g` counter and `trace_id` (and vector clock if required).
- **Partition Tolerance:** Mark test results that are incomplete due to infra/network partition, and require reconciliation if later healed.
- **Observability:** Trace IDs must be propagated from every test run into all logs, reports, and dashboards.

All test validation and critique agents must enforce and audit for these invariants in every review.