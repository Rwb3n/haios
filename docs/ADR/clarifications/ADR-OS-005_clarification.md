# ADR Clarification Record: ADR-OS-005

## Initial Clarification Draft (TBD)


## Assumptions & Constraints
- A valid `haios.config.json` file is guaranteed at repo root and loaded before any OS action.
- All paths declared in the config remain within repository boundaries to preserve portability.
- The filesystem supports nesting and naming conventions defined (case-sensitive where required).
- Config schema evolution is strictly backward-compatible or accompanied by an auto-migration script.
- The OS operates with least-privilege FS permissions; missing write access to configured paths is treated as fatal.

## Dependencies & Risks
- **Upstream ADRs:** ADR-OS-032 (Canonical Models Registry) governs naming conventions; ADR-OS-029 (Observability) ensures config load is traced.
- **Single Point of Failure:** Corrupted or missing `haios.config.json` prevents startup; mitigated via schema validation and fallback wizard.
- **User Misconfiguration:** Incorrect path mappings could leak OS control files into versioned app code—CI linter halts merge.
- **Cross-Platform Variance:** Path separators and case sensitivity differ between OSes; mitigated via runtime normalization utilities.
- **Config Drift:** Manual edits may diverge from actual directory layout; scheduled VALIDATE jobs reconcile and raise issues.

## Summary
ADR-OS-005 adopts a configuration-driven directory structure, centralizing all operational paths in `haios.config.json`. This makes Hybrid_AI_OS portable, predictable, and easy to integrate into diverse project layouts while retaining clear separation between OS internals and project artifacts.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | What versioning strategy is defined for `haios.config.json` to support breaking schema changes? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Embed a top-level `config_schema_version` (semver) field; CI blocks if version bump lacks migration script. |
| 2 | How should the OS react to extra, unrecognized keys in the config file—ignore or fail fast? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Linter issues WARN for unknown keys in minor versions; MAJOR versions may elevate to ERROR per strict mode. |
| 3 | Is there a CLI bootstrap command to regenerate a default directory scaffold if the config is missing? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | `haios init --scaffold` generates default paths idempotently and writes validated config file. |
| 4 | What guardrails prevent user-supplied paths from escaping the repository root (path traversal)? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Loader canonicalizes paths and verifies they reside under repo root using `Path.resolve().is_relative_to(root)`; CI blocks traversal attempts. |
| 5 | How will multi-repository or mono-repo setups override or extend the single config paradigm? | Hybrid_AI_OS | 2025-06-27 | ANSWERED | Support layered override files (`haios.config.local.json`, workspace-level config) merged via deep-merge with precedence; union validated against master schema. |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | architect-1 | 2025-06-27 | 1 | Use semver field plus migration script gating. |
| 2 | architect-1 | 2025-06-27 | 2 | Unknown keys trigger warnings unless strict mode; future-proofing configs. |
| 3 | architect-1 | 2025-06-27 | 3 | Introduced `haios init --scaffold`; safe rerun. |
| 4 | architect-1 | 2025-06-27 | 4 | Path canonicalization prevents escapes; linter guards. |
| 5 | architect-1 | 2025-06-27 | 5 | Layered configs enable multi-repo; deep-merge with precedence. |

## Formal Reviews & Dissents
<!-- Capture formal approvals, objections, and alternative viewpoints here. -->

### Objection — architect-2 (2025-06-27)
| Concern # | Related Q# | Summary of Objection | Suggested Follow-up |
|-----------|------------|----------------------|---------------------|
| 1 | 1 | Sole reliance on a semver field is fragile; without explicit JSON Schema `$id` and `$schema` references, tooling may mis-interpret breaking changes. | Augment config with `$schema` URL pointing at tagged schema version; update CI to fetch and validate against that exact revision. |
| 2 | 2 | Treating unknown keys as warnings allows silent drift; strict mode should be default to prevent typo-driven misconfig. | Flip default to strict validation; allow opt-in `allowUnknownKeys` in config for extension points, guarded by feature flag. |
| 3 | 3 | `haios init --scaffold` may overwrite existing customized paths, risking data loss. | Add `--dry-run` and interactive diff output; require explicit `--force` to modify existing config. |
| 4 | 4 | Path canonicalization misses symlink traversal edge-cases; malicious symlinks could bypass root check. | Resolve symlinks and verify inode ancestry; optionally block symlink usage in control-file directories. |
| 5 | 5 | Layered override approach may yield nondeterministic results in mono-repo with nested workspaces; precedence rules unclear. | Document deterministic precedence order (workspace > repo > default) and add linter to detect override cycles. |

_Objections logged for council review; awaiting architect-1 disposition._

## Additional Notes
- Appendix C (Scaffold Definition Template) outlines default directory layout used by the bootstrap command.
- Appendix A's assumption-surfacing checklist guided the expanded assumption block above.
- Future work: provide a visual directory tree diagram in docs/source to complement textual spec.

## Traceability
- adr_source: ADR-OS-005
- trace_id: trace://auto-g69/resolve_placeholders
- vector_clock: vc://auto@69:4

## Distributed-Systems Protocol Compliance Checklist
- [ ] Idempotent updates supported
- [ ] Message-driven integration points documented
- [ ] Immutable audit-trail hooks attached 

### Response — architect-1 (2025-06-27)
| Concern # | Disposition | Mitigation / Next Action |
|-----------|-------------|--------------------------|
| 1 | ACCEPT | Embed `$schema` URL referencing semver-tagged schema revision; CI validator locked to that URL. Update config generator accordingly. |
| 2 | ACCEPT PARTIAL | Default to strict validation; introduce optional `allowUnknownKeys` flag behind feature gate for extension points. Add drift-detection unit tests. |
| 3 | ACCEPT | Enhance `haios init --scaffold` with `--dry-run`, interactive diff, and `--force` flags to safeguard customized paths. |
| 4 | ACCEPT | Resolver will follow symlinks and assert final inode under repo root; block symlinks in OS control directories. Add security test harness. |
| 5 | ACCEPT | Document precedence order (workspace > repo > default) and implement linter rule to detect override cycles. |

_Architect-1 concurs with recommendations and schedules tasks for next sprint to implement and document the mitigations._ 