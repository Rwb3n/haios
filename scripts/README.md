# generated: 2025-11-25
# System Auto: last updated on: 2025-12-23T19:07:48
# HAIOS Utility Scripts - Quick Reference

> **Navigation:** [Quick Reference](../docs/README.md) | [Strategic Overview](../docs/epistemic_state.md) | [Operations](../docs/OPERATIONS.md)

> **Progressive Disclosure:** Quick reference for common tasks -> [Detailed Diagnostics](#detailed-usage) -> [Operations Manual](../docs/OPERATIONS.md)

---

## Governance Scripts (Epoch 2)

Note: Most governance automation (scaffolding, validation) now lives in `.claude/hooks/` and is accessed via slash commands (`/validate`, `/new-plan`). See `.claude/hooks/README.md`.

### M6-WorkCycle Migration

- `migrate_backlog.py` - Migrate backlog.md entries to WORK-{id}.md files (E2-151)
  ```bash
  python scripts/migrate_backlog.py --dry-run  # Preview
  python scripts/migrate_backlog.py            # Execute
  ```

## At a Glance

**Production Utilities** (safe to use anytime):
- `query_progress.py` - Query ETL processing status and history
- `check_status.py` - Quick database status check
- `load_test.py` - Performance load testing (Phase 5)
- `apply_migration.py` - Apply schema migrations
- `verify_stats.py` - Verify database statistics
- `generate_embeddings.py` - Generate embeddings for concepts (Phase 7)
- `complete_concept_embeddings.py` - Complete embedding generation for all concepts (Phase 7)
- `register_agents.py` - Register agents in the marketplace (Phase 8)
- `validate_schema.py` - Validate database schema integrity
- `verify_sqlite_vec.py` - Verify sqlite-vec extension
- `verify_space_id.py` - Verify space_id handling
- `verify_llm_classification.py` - Verify LLM classification
- `verify_live_db_constraints.py` - Verify live database constraints
- `get_full_schema.py` - Export full database schema
- `check_artifact.py` - Check artifact processing status
- `debug_extraction.py` - Debug extraction issues
- `investigate_concepts.py` - Investigate concept relationships
- `investigation_a1.py` - PLAN-INVESTIGATION-001: Verify synthesis_provenance bug
- `investigation_a2.py` - PLAN-INVESTIGATION-001: Test synthesis_provenance fix
- `apply_migration_008.py` - Apply migration 008
- `apply_migration_009.py` - Apply migration 009 (synthesis member fix)
- `benchmark_toon.py` - Benchmark TOON algorithm
- `verify_data_quality.py` - Verify data quality (large files, anti-patterns)
- `investigate_cross_pollination.py` - Cross-pollination debug
- `test_embedding_compatibility.py` - Embedding compatibility tests

**Development Tools** (for debugging):
- `dev/` - Debugging and investigation scripts
  - `investigate_duplicates.py` - Duplicate occurrence investigation
  - `verify_duplicate_fix.py` - Duplicate fix verification
  - `test_clean_json.py` - JSON preprocessing validation
  - `clear_errors.py` - Clear error states
  - `check_error_files.py` - Check error files
  - `check_large_files.py` - Check large file processing
  - `debug_readme.py` - Debug README issues

**Verification Archives** (historical):
- `verification/` - One-off verification scripts from past sessions

---

## Quick Start

### Check Current ETL Progress
```bash
# Quick summary
python scripts/query_progress.py

# Detailed breakdown by date
python scripts/query_progress.py --by-date

# Show all current errors
python scripts/query_progress.py --errors

# Full timeline view
python scripts/query_progress.py --timeline
```

### Check Database Status
```bash
python scripts/check_status.py
```

### Generate Embeddings
```bash
# Generate embeddings for new concepts
python scripts/generate_embeddings.py

# Complete all missing embeddings
python scripts/complete_concept_embeddings.py
```

### Register Agents
```bash
python scripts/register_agents.py
```

---

## Detailed Usage

See original README for full details on each script.

---

## Development Tools

### dev/ Directory

Contains debugging and investigation scripts created during development sessions. These are:
- **Session-specific**: Created to investigate particular issues
- **Not production-ready**: May have hard-coded paths or assumptions
- **Archived for reference**: Kept for understanding past debugging approaches

**Files:**
- `investigate_duplicates.py` - Duplicate occurrence investigation (Session 10)
- `verify_duplicate_fix.py` - Duplicate fix verification (Session 10)
- `test_clean_json.py` - JSON preprocessing validation (Session 9)
- `clear_errors.py` - Clear error states from database
- `check_error_files.py` - Analyze error files
- `check_large_files.py` - Check large file processing
- `debug_readme.py` - Debug README generation issues

**When to use:** Refer to these when debugging similar issues or understanding past investigations.

---

## Navigation

- **← Back:** [Project README](../README.md) | [Documentation Map](../docs/README.md)
- **→ Next:** [Operations Manual](../docs/OPERATIONS.md) | [Diagnostic Guide](../docs/OPERATIONS.md#diagnostics)
- **↓ Related:** [ETL CLI Reference](../docs/OPERATIONS.md#cli-commands)

---

**Last Updated:** 2025-12-09 (Session 54)
**Status:** Phase 9 Complete - Memory Synthesis + MCP Schema Abstraction
**Maintainer:** Hephaestus (Builder)
