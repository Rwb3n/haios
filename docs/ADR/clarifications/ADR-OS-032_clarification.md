# ADR Clarification Record: ADR-OS-032

## Initial Clarification Draft (TBD)
+This clarification aligns with ADR-OS-032 (Canonical Models and Frameworks Registry & Enforcement) to surface assumptions, track open questions, and ensure downstream artifacts conform to the registry mandate.

## Assumptions & Constraints
- Best-practice models/frameworks must be explicitly cataloged and referenced, not implicit.
- Registry is versioned, agent-readable (YAML or JSON front-matter), stored at `docs/frameworks_registry.md`.
- CI job `framework_compliance_check` blocks merges if required frameworks are missing or compliance unproven.
- Governance board owns registry updates; changes require semantic version bump.
- Enforcement mode tiers (Required, Recommended, Optional) map to severity levels in lint output.

## Dependencies & Risks
- **Registry Drift:** Without ownership and review cadence, models may become outdated.
- **Over-Enforcement:** Rigid checks could stifle experimentation; override process needed.
- **Complex Onboarding:** New contributors must learn registry semantics; documentation/training essential.
- **Tooling Maintenance:** Linter and VS Code plugin must evolve with schema changes.
- **Cross-ADR Alignment:** Must stay synced with ADR-OS-021 (runtime metadata) for enforcement hooks.

## Summary
ADR-OS-032 establishes a central, versioned registry of canonical models and frameworks and mandates that every major artifact declare compliance, exceptions, and proof against that registry. It enables automated enforcement via CI/lint and provides legible standards for humans and agents.

## Clarification Questions
| # | Question | Asked By | Date | Status | Response Summary |
|---|----------|----------|------|--------|------------------|
| 1 | Which frameworks are **system mandatory** vs **recommended** at launch? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 2 | What governance process approves new registry entries or deprecations? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 3 | How will exceptions be tracked (e.g., annotation vs issue label)? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 4 | Where does the linter output compliance proof artifacts (reports)? | Hybrid_AI_OS | 2025-06-27 | OPEN | |
| 5 | Can registry entries reference external standards bodies (e.g., ISO) by link? | Hybrid_AI_OS | 2025-06-27 | OPEN | |

## Responses
| # | Response By | Date | Related Q# | Summary |
|---|-------------|------|------------|---------|
| 1 | _placeholder_ | | | |

## Formal Reviews & Dissents
- Pending approval from Architecture Governance Board.

## Additional Notes
- Appendix G (`Frameworks_Registry`) details current registry content.
- Long-term plan: GraphQL endpoint exposing registry for IDE plugins.

## Traceability
- adr_source: ADR-OS-032
- trace_id: {{TRACE-ID}}
- vector_clock: {{VECTOR-CLOCK}}

## Distributed-Systems Protocol Compliance Checklist
- [x] Idempotent updates supported (registry updates are version-controlled)
- [x] Message-driven integration points documented (CI linter emits events)
- [x] Immutable audit-trail hooks attached (Git history + signed commits) 