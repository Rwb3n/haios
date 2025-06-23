# ADR Clarification Record: ADR-OS-003

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- The `EmbeddedAnnotationBlock` JSON structure will remain backward-compatible across future schema iterations.
- All text-editable file formats in the repository can safely embed comment-wrapped JSON without breaking primary runtime semantics.
- Agents executing CONSTRUCT and VALIDATE phases possess deterministic parsers that preserve exact annotation formatting (idempotent write-back).
- Parsing and serializing these annotation blocks adds negligible latency (<5 ms per artifact) to standard CI/CD workflows.
- The global registry (`os_root/global_registry_map.txt`) is considered the single authoritative index; any temporary divergence must be self-healing within one execution cycle.

## Dependencies & Risks
- **Upstream ADRs:** Depends on ADR-OS-023 (Idempotency), ADR-OS-029 (Observability & Tracing), ADR-OS-032 (Canonical Models Registry).
- **Toolchain:** Relies on custom linters and CI hooks described in Appendix H to validate annotation integrity—failure or mis-configuration may allow malformed blocks to merge.
- **Distributed Coordination:** Concurrent agents updating the same artifact risk write conflicts; without optimistic-locking, last-writer-wins could corrupt JSON.
- **Schema Drift:** Rapid evolution of the annotation schema could strand legacy artifacts; mitigation includes version gating and automated migrations.
- **Human Error:** Manual edits to annotation blocks may introduce syntax errors that break parsing pipelines.

## Summary
ADR-OS-003 mandates embedding a structured JSON metadata block—`EmbeddedAnnotationBlock`—at the top of every text-editable project artifact. This block captures purpose, authorship, dependencies, and traceability, enabling fully self-describing artifacts that support automated governance, distributed tracing, and architectural enforcement. The decision favors in-file annotations over external databases or sidecar files to maintain a single source of truth closely coupled with version control history.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What recovery process is defined if an `EmbeddedAnnotationBlock` becomes corrupted or partially deleted? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Automatic CI linter detects corruption, rolls back to last-known-good commit, then re-hydrates the block from authoritative data in `global_registry_map.txt`; manual patch only if auto-recovery fails. |
| 2 | How will concurrent annotation updates be orchestrated to avoid race conditions across distributed agents? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Agents perform optimistic-locking using the `v_file_instance` counter; conflicting writes are rejected and retried with a back-off strategy; CRDT-style merge applied for non-conflicting fields. |
| 3 | What strategy will be employed for non-text artifacts (e.g., binaries) that cannot embed JSON blocks? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Store the annotation in a sibling `.meta.json` file following the same schema and register it in the registry; alternatively embed as OCI labels for container images. |
| 4 | How will schema version migrations be automated to guarantee backward compatibility? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | CI runs migration scripts whenever `schema_version` changes; artifacts carry a `version_tag_of_host_at_annotation` field allowing selective upgrades; linter blocks merges if migration missing. |
| 5 | What audit trail fields (e.g., `trace_id`, `vector_clock`) are mandatory within each annotation update event? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Minimum required: `trace_id`, `g_annotation_created`, `vector_clock`, `author_identifier`, and `operation_type`; optional `change_summary` for human readability. |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-27 | 1 | See automated recovery workflow leveraging CI lint + registry restore; manual patch as fallback. |
| 2 | architect-1 | 2025-06-27 | 2 | Conflicts resolved via optimistic-locking and CRDT merge; retries with exponential back-off. |
| 3 | architect-1 | 2025-06-27 | 3 | Use `.meta.json` companions or OCI labels for binaries; registry tracks linkage. |
| 4 | architect-1 | 2025-06-27 | 4 | Versioned migrations executed in CI; linter ensures completeness before merge. |
| 5 | architect-1 | 2025-06-27 | 5 | Mandatory audit fields: `trace_id`, `vector_clock`, `g_annotation_created`, `author_identifier`, `operation_type`. |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->

### Objection — architect-2 (2025-06-27)
| Concern # | Related Q# | Summary of Objection | Suggested Follow-up |
|-----------|------------|----------------------|---------------------|
| 1 | 1 | Automatic rollback to last-known-good commit risks discarding concurrent valid changes; propose selective JSON patch strategy leveraging diff-aware recovery tool. | Prototype diff-aware linter extension and add integration test. |
| 2 | 2 | Optimistic-locking with CRDT merge may not scale under high-frequency updates; latency spikes observed in DR drill. | Evaluate append-only journal + transactional outbox pattern for multi-agent coordination. |
| 3 | 3 | `.meta.json` sidecars undermine "single-file source of truth" principle and increase file management overhead. | Investigate embedding annotations in Git LFS pointer comments or storing hash-linked registry entries instead. |
| 4 | 4 | Migration workflow lacks rollback mechanism if migration script itself fails mid-way. | Require two-phase migration with staging and verification gates before commit. |
| 5 | 5 | Mandatory audit fields omit `commit_sha` and `pipeline_id`, hindering forensic traceability across CI runs. | Amend audit schema to include `commit_sha`, `pipeline_id`, and `job_attempt`. |

_Resolution pending further discussion among architecture council; objections entered into record for visibility._

## Additional Notes
- Appendix A provides general assumption-surfacing guidelines applied here.
- Refer to Appendix H for CI/CD linter enforcement details ensuring presence and validity of annotation blocks. Failure cases discovered during internal DR drills should be back-ported to this clarification record.
- Future iterations should include a diagram (see ADR-OS-003 self-critique) illustrating annotation placement across representative file formats.

## Traceability
- adr_source: ADR-OS-003
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:2

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached

### Response — architect-1 (2025-06-27)
| Concern # | Disposition | Mitigation / Next Action |
|-----------|-------------|--------------------------|
| 1 | ACCEPT PARTIAL | Adopt diff-aware JSON patch workflow as primary recovery step; retain rollback as last-resort. Action: create linter PoC + integration test (tracked in issue `issue_diff_aware_recovery`). |
| 2 | ACCEPT | Initiate performance benchmark of CRDT merge vs. append-only journal pattern; if latency >50 ms at P95, switch to journal + outbox. Action: open spike task in next sprint. |
| 3 | ACCEPT PARTIAL | Maintain `.meta.json` as interim solution; commission feasibility study on Git LFS pointer annotations and registry-hash linkage. Outcome to inform ADR update. |
| 4 | ACCEPT | Enhance migration pipeline with two-phase commit (staging ➜ verify ➜ promote). Rollback mechanics to restore pre-staging snapshot upon verification failure. |
| 5 | ACCEPT | Extend mandatory audit schema to include `commit_sha`, `pipeline_id`, and `job_attempt`. Update linter rules and documentation accordingly. |

_Architect-1 concurs with all raised concerns and has scheduled corresponding mitigation items; detailed tasks will be logged in the forthcoming execution plan._

### Follow-Up — architect-2 (2025-06-27)
| Concern # | Status After Mitigation | Additional Commentary |
|-----------|------------------------|-----------------------|
| 1 | SATISFIED WITH ACTION | Ensure PoC includes chaos-engineering test that introduces conflicting valid edits during recovery to validate non-destructive behavior. |
| 2 | PENDING RESULTS | Await benchmark report; request inclusion of concurrent 8-agent workload and P99 latency in metrics. |
| 3 | PARTIAL ACCEPTANCE | Sidecar interim acceptable for binaries; request six-week deadline to finalize alternative embedding approach. |
| 4 | SATISFIED | Two-phase commit solves integrity concerns; request explicit rollback playbook in docs/appendices/Appendix_B. |
| 5 | SATISFIED | Audit schema additions address traceability; ensure pipeline enforcement updated across all repos. |

_Follow-up entered; no further blocking objections from architect-2 at this time._ 