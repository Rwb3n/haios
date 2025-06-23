# ADR Clarification Record: ADR-OS-006

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- Every `Scaffold Definition` JSON validates against the schema in docs/Schema/scaffold_definition_schema.md.
- All boilerplate assets referenced exist within `project_templates/` at scaffold time.
- The OS has adequate write permissions for all target paths in `project_workspace/`.
- Scaffold execution is idempotent; running the same definition twice produces no unintended duplicates.
- Each scaffolded artifact automatically receives a complete `EmbeddedAnnotationBlock` based on template metadata.
- Template placeholder syntax remains stable to avoid breaking older Scaffold Definitions.

## Dependencies & Risks
- **Upstream ADRs:** ADR-OS-003 (Annotations) ensures metadata embedding; ADR-OS-032 (Canonical Models Registry) defines template compliance.
- **Template Drift:** Updates to shared templates can unintentionally alter existing code bases—CI diff checks required.
- **Partial Failures:** Mid-process interruption may leave inconsistent state; mitigation via transaction-like rollback or resume logic.
- **Complex Placeholder Logic:** Advanced replacement rules increase maintenance overhead and risk of mis-rendering files.
- **Versioning:** Lack of scaffold version pinning could break reproducibility; recommend semantic versioning of Scaffold Definitions.

## Summary
ADR-OS-006 introduces a schema-based scaffolding system driven by `Scaffold Definition` JSON files. It orchestrates the automated creation of new components using assets from `project_templates/`, injecting rich annotations so artifacts are self-describing from inception. This accelerates development, enforces best practices, and guarantees consistent structure across the project.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | How are Scaffold Definitions versioned and migrated without breaking existing components? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Each definition carries `scaffold_def_version` (semver) + `template_version`. CI requires migration script or backward-compat flag when major bump detected. |
| 2 | What rollback mechanism exists if scaffolding fails midway through artifact generation? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Scaffold executor writes to temp staging dir; commits atomically on success else auto-rolls back and logs failure event with trace_id. |
| 3 | How will placeholders and conditional logic within templates be validated to prevent runtime syntax errors? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Pre-execution static analysis & unit compile of rendered templates; CI breaks if placeholder unresolved or syntax lint fails. |
| 4 | Can end-users override default templates while still passing CI scaffold integrity checks? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Users may reference custom templates via `template_registry_path`; linter validates schema conformance and required annotation fields. |
| 5 | What metrics will be collected to monitor scaffold usage, success rate, and drift over time? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Telemetry captures `scaffold_id`, duration, success/fail, drift hash, agent_id; aggregated in metrics dashboard with weekly report. |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-27 | 1 | Semver + migration gating ensures safe evolution; minor/patch auto-compatible. |
| 2 | architect-1 | 2025-06-27 | 2 | Temp staging directory enables atomic commit/rollback. |
| 3 | architect-1 | 2025-06-27 | 3 | Static analysis + compile test catches placeholder issues pre-merge. |
| 4 | architect-1 | 2025-06-27 | 4 | Custom templates allowed but must pass same schema and annotation checks. |
| 5 | architect-1 | 2025-06-27 | 5 | Telemetry dashboard provides visibility on scaffold health & drift. |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->

### Objection — architect-2 (2025-06-27)
| Concern # | Related Q# | Summary of Objection | Suggested Follow-up |
|-----------|------------|----------------------|---------------------|
| 1 | 1 | Relying on separate `scaffold_def_version` and `template_version` fields could diverge; unclear which drives CI gating. | Adopt single authoritative `schema_version` embedded in both definition and template header; CI cross-check for match. |
| 2 | 2 | Temp staging dir rollback may leave residual orphan files if process killed mid-rename. | Use transactional FS library with journal + checksum verification; add cleanup sentinel job. |
| 3 | 3 | Static analysis compile test assumes language-specific compilers exist for all templates; slows pipeline. | Provide language-agnostic placeholder linter first, compile tests optional per template tag. |
| 4 | 4 | Allowing custom templates risks fragmentation and quality drift. | Require central registry approval + semantic diff review before custom template allowed in CI. |
| 5 | 5 | Telemetry fields omit `template_version` and do not track failed placeholder resolutions count. | Extend metrics to include `template_version`, `placeholder_error_count`, and `rollback_flag`. |

### Response — architect-1 (2025-06-27)
| Concern # | Disposition | Mitigation / Next Action |
|-----------|-------------|--------------------------|
| 1 | ACCEPT | Replace dual fields with single `schema_version` embedded in both Scaffold Definition and template header; CI diff check enforces equality. Provide migration script to auto-converge legacy records. |
| 2 | ACCEPT | Integrate transactional FS lib with journaling & checksum; add watchdog cleanup job to purge residual staging artefacts on startup. |
| 3 | ACCEPT PARTIAL | Placeholder linter mandatory for all templates; compile tests gated by optional `requiresCompileTest` flag in template metadata to keep pipeline lean. Cache compiled artifacts to reduce overhead. |
| 4 | ACCEPT PARTIAL | Custom templates allowed only after central registry review & semantic diff approval; interim experimentation permitted behind `experimentalTemplate` flag not deployable to production. |
| 5 | ACCEPT | Extend telemetry to capture `template_version`, `placeholder_error_count`, `rollback_flag`, and emit to metrics pipeline. |

_Architect-1 has incorporated feedback; implementation tasks will be tracked under forthcoming execution plan tickets._

### Follow-Up — architect-2 (2025-06-27)
| Concern # | Status After Mitigation | Additional Commentary |
|-----------|------------------------|-----------------------|
| 1 | SATISFIED | Confirm migration script includes dry-run diff mode and adds `schema_version` to template header generator. |
| 2 | PENDING IMPLEMENTATION | Await integration of transactional FS library; please deliver design doc outlining journal format and cleanup sentinel logic. |
| 3 | SATISFIED | Placeholder linter fallback acceptable; request compile-test coverage metric to monitor opt-in adoption. |
| 4 | PARTIAL ACCEPTANCE | Experimental flag strategy valid; require sunset date review every 2 sprints to prevent perpetual experimental status. |
| 5 | SATISFIED | Telemetry additions suffice; ensure dashboard includes trend line on placeholder errors over last 30 days.

_No further blocking objections; monitor pending items._

## Additional Notes
- Appendix C details Scaffold Definition Template guidelines referenced here.
- Appendix F outlines testing guidelines; scaffold-generated tests should conform automatically.
- Future diagram needed to illustrate scaffold workflow and rollback paths.

## Traceability
- adr_source: ADR-OS-006
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:5

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 