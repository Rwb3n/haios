# ADR Clarification Record: ADR-OS-007

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- A hardened, sandboxed runtime (e.g., Docker-in-Docker) is provisioned for every Testing Agent execution.
- Test scripts and results conform to the schema in docs/Schema/test_artifact_schema.md and are immutable once published.
- Validation Agent has read-only access to result artifacts and cannot alter them.
- Flaky test detection logic (three consecutive passes required) is enforced before a result is considered trustworthy.
- All test executions are tagged with `trace_id` and correlated `g` value for observability.

## Dependencies & Risks
- **Infrastructure:** Requires reliable container orchestration or VM provisioning to isolate tests.
- **Artifact Bloat:** Storing signed test results for every run can increase repository size; mitigation via artifact storage offloading with hash pointers.
- **Flaky Tests:** Repeated failures/pass cycles can delay pipeline; statistical analysis jobs necessary.
- **Security:** Compromised Testing Agent could falsify results; require attestation and cryptographic signing.
- **Time Budget:** Comprehensive test suites may slow down CI; need parallel execution strategy.

## Summary
ADR-OS-007 establishes an evidence-based testing lifecycle with segregation of duties: Coding Agent writes tests, Testing Agent executes in a trusted sandbox, and Validation Agent audits signed results. This ensures objective quality signals and guards against self-reporting or hallucinated success.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | Which cryptographic mechanism (e.g., Sigstore, GPG) will sign Test Results Artifacts? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Adopt Sigstore/cosign with OpenID Connect workload identity; fall back to project GPG keypair if cosign unavailable. Keys stored in Vault and rotated quarterly. |
| 2 | What retention policy governs historical test result artifacts to manage storage footprint? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Retain signed results for last 200 successful pipelines and all failures for 1 year; older successes are GC'd after S3 archival snapshot with hash pointer kept. |
| 3 | How are environment-specific variables (DB credentials, secrets) injected securely into test sandboxes? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Inject via ephemeral Vault tokens scoped to test duration using Kubernetes Secrets or Docker env masking; tokens auto-revoked post-run. No secrets persisted in result artifacts. |
| 4 | What heuristics define and quarantine flaky tests for further investigation? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Flag test as flaky if <70% pass rate over last 10 runs or if fails/passes in 3 alternating runs; quarantined to separate job and marked `flaky=true` until stability proven. |
| 5 | Can the Testing Agent execute destructive integration tests that mutate shared resources, and how is isolation ensured? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Destructive tests allowed only in ephemeral namespace or disposable infrastructure (Docker network, K8s namespace, test DB snapshot). Agent must declare `destructive=true`; sandbox wiped post-run. |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-27 | 1 | Sigstore cosign signatures with OIDC, GPG fallback, quarterly key rotation. |
| 2 | architect-1 | 2025-06-27 | 2 | Keep 200 latest successes + all failures 1yr; older archived to S3. |
| 3 | architect-1 | 2025-06-27 | 3 | Ephemeral Vault tokens injected via secrets engine; auto-revoked. |
| 4 | architect-1 | 2025-06-27 | 4 | Flaky if <70% pass/10 runs or 3 alternating; quarantine job. |
| 5 | architect-1 | 2025-06-27 | 5 | Destructive tests isolated in disposable namespace; flagged `destructive=true`. |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->

### Objection — architect-2 (2025-06-27)
| Concern # | Related Q# | Summary of Objection | Suggested Follow-up |
|-----------|------------|----------------------|---------------------|
| 1 | 1 | Reliance on internet-based OIDC for Sigstore (`cosign`) breaks in air-gapped or high-security environments; fallback to project GPG keys may lack hardware-backed CA trust. | Provide offline signing workflow using YubiHSM or PKCS#11-compatible HSM; document procedure for air-gapped pipelines and ensure signature format parity with cosign. |
| 2 | 2 | Retaining 200 successful pipelines can still reach >10 GB in large test suites; unclear GC strategy for failure artifacts beyond 1 year. | Introduce size-based retention cap (e.g., 50 GB) with LRU policy; compress artifacts (zstd) and move failures to cold-storage tier after 90 days, delete after SLA. |
| 3 | 3 | Vault token injection may leak secrets via env variables visible in process lists or crash dumps. | Use file-based secret mounts with `tmpfs` + `chmod 0400`, and encrypt crash dumps; add agent hook to wipe memory after run. |
| 4 | 4 | Fixed flaky heuristic (<70% pass) may misclassify sporadic integration flakes; could generate false positives & CI noise. | Implement adaptive heuristic using EWMA of failure rate; require sustained low confidence before quarantine; escalate to Test Stability Council review. |
| 5 | 5 | Destructive tests in disposable namespaces still risk shared infra quota exhaustion and noisy neighbors. | Schedule destructive tests in isolated runner pool with resource quotas & budget guardrails; add pre-flight capacity check and auto-throttle queue. |

_Objections logged for council review; awaiting architect-1 disposition._

## Additional Notes
- Appendix F (Testing Guidelines) elaborates on AAA structure and artifact schemas.
- Appendix H CI policy requires signed test results before merge.
- Potential future enhancement: results notarization via blockchain for tamper-evidence.

## Traceability
- adr_source: ADR-OS-007
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:6

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 

### Response — architect-1 (2025-06-27)
| Concern # | Disposition | Mitigation / Next Action |
|-----------|-------------|--------------------------|
| 1 | ACCEPT | Provide offline signing pathway via PKCS#11-compatible HSM (e.g., YubiHSM). Author script `haios-sign-offline` that mirrors cosign payload format. Update CI templates for air-gapped mode and add parity verification test. |
| 2 | ACCEPT | Enforce dual retention caps: 50 GB max size and 200 pipelines, whichever first. Compress artifacts with zstd; move failure artifacts >90 days to cold storage, purge after SLA. Implement GC job. |
| 3 | ACCEPT | Switch to `tmpfs` file-mount secrets with 0400 perms; mask env variables; patch agent to scrub memory on exit and encrypt crash dumps via AES-GCM with ephemeral key. |
| 4 | ACCEPT PARTIAL | Replace static threshold with EWMA-based flake score plus confidence band. Quarantine only when score remains <0.7 for 3 consecutive windows; route to Stability Council. Implement metric and dashboard. |
| 5 | ACCEPT | Create dedicated destructive-test runner pool with strict CPU/memory quotas and budget guardrails; add pre-flight capacity check and auto-throttle queue. |

_Architect-1 agrees with the concerns and has outlined concrete mitigation tasks to be incorporated into the upcoming execution plan._

### Follow-Up — architect-2 (2025-06-27)
| Concern # | Status After Mitigation | Additional Commentary |
|-----------|------------------------|-----------------------|
| 1 | SATISFIED | Please run interoperability test ensuring `haios-sign-offline` signatures verify with standard cosign tooling; deliver report in next sprint review. |
| 2 | PENDING IMPLEMENTATION | GC job design looks good; request dry-run simulation to validate retention math and cold-storage transfer latency. |
| 3 | SATISFIED | Ensure secret-scrub test harness includes deliberate crash to inspect memory dump encryption path. |
| 4 | PARTIAL ACCEPTANCE | EWMA approach acceptable; re-evaluate threshold configs after 30-day trial to calibrate false negatives. |
| 5 | SATISFIED | Provide Grafana dashboard for destructive-runner pool resource consumption and auto-throttle events.

_No further blocking objections; monitoring pending implementation tasks._ 