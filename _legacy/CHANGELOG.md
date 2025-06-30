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

### Critical Fixes
- **ADR Index Desynchronization Resolution** - Fixed critical desynchronization between `docs/ADR/README.md` index and actual ADR content that was breaking system navigability. Updated descriptions to match actual ADR content:
  - ADR-OS-001: Corrected from "Embedded Annotation Blocks" to "Core Operational Loop & Phasing"
  - ADR-OS-003: Corrected from "OS Control File Schemas" to "Artifact Annotation Strategy"  
  - ADR-OS-006: Corrected from "Phase-Based Operational Model" to "Scaffolding Process"
  - ADR-OS-018: Flagged title/content mismatch for review (title says "Persistence & Recovery" but content covers security controls)
  - Reorganized categories by system function rather than implementation order for better developer experience
- **Third-Party Evaluation Follow-up** - Created comprehensive tracking issue for remaining architectural validation items identified in comprehensive third-party review process

### New Proposed ADRs
- **ADR-OS-033: Cookbook & Recipe Management System** - Formal system for capturing, validating, and reusing proven implementation patterns across HAiOS projects. Enforces DRY principles through structured Recipe lifecycle with validation process. Includes comprehensive Recipe schema with evidence requirements and integration with HAiOS governance model.
- **ADR-OS-034: Orchestration Layer & Session Management** - Unified coordination system for multi-agent workflows with persistent session state management and Cockpit interface for human operators. Addresses session continuity, agent coordination gaps, and workflow fragmentation identified in architectural review. Integrates with existing agent roles from ADR-OS-030.
- **ADR-OS-035: The Crystallization Protocol & Gatekeeper Agent** - Establishes formal two-space system for safely isolating exploratory work from canonical system state. Implements quality ratchet mechanism ensuring only validated knowledge enters canonical state. Addresses critical gap between creative exploration and rigorous governance identified in third-party architectural review.

---

## 2025-06-27 – Appendix & Schema Retrofit

Refer to individual detailed change logs under `docs/CHANGELOG/` for the full
breakdown of the appendix-refactor and distributed-systems schema retrofit
(e.g., `2025-06-27_ci_and_testing_guidelines_retrofit.md`,
`2025-06-27_assumptions_surfacing_completion.md`, etc.). 