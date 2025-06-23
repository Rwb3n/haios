# Changelog

All notable changes to this repository will be documented in this file. The
format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Root-level changelog** to provide a central, aggregated history distinct
  from the per-feature files in `docs/CHANGELOG/`.
- `scripts/update_schema_links.py`: utility to migrate references from the
  legacy schema directory to `docs/schema/`.
- `scripts/update_appendix_links.py`: utility to migrate old documentation
  paths to the new versioned appendices (A–H).

### Changed
- Renamed `docs/Document_2/` to `docs/schema/` and updated **all** repository
  references (README, code, workflows, tests, Makefile, plans, etc.).
- Updated README and onboarding docs to point to the new schema directory.
- Codebase now relies on `docs/schema/` for runtime validation (see
  `src/engine.py`).

### Removed / Archived
- Legacy documentation (`docs/Document_1`, `docs/Document_3/Scaffold Definition Specification.md`,
  `docs/guidelines/test_guidelines.md`, `docs/source/frameworks_registry.md`,
  `docs/CI_CD_SETUP.md`) moved under `docs/_legacy/`.

---

## 2025-06-27 – Appendix & Schema Retrofit

Refer to individual detailed change logs under `docs/CHANGELOG/` for the full
breakdown of the appendix-refactor and distributed-systems schema retrofit
(e.g., `2025-06-27_ci_and_testing_guidelines_retrofit.md`,
`2025-06-27_assumptions_surfacing_completion.md`, etc.). 