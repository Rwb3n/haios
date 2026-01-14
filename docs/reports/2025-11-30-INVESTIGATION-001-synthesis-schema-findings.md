---
template: implementation_report
status: complete
date: 2025-11-30
title: "Investigation Report: Synthesis Schema Bug & Process Audit"
directive_id: PLAN-INVESTIGATION-001
author: Hephaestus
project_phase: Phase 9 Enhancement
version: "1.0"
---
# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 16:58:34
# Investigation Report: Synthesis Schema Bug & Process Audit

> **Navigation:** [Quick Reference](#quick-reference) | [Findings](#findings) | [Root Cause](#root-cause-analysis) | [Recommendations](#process-improvement-recommendations)

---

## Quick Reference

### TL;DR

**Original Hypothesis:** CHECK constraint in `synthesis_provenance` rejects 'cross' value.

**Actual Finding:** **No CHECK constraints exist in production.** The bug we were looking for doesn't exist because the constraints were never applied.

**Real Problem:** Schema source-of-truth fragmentation - three conflicting schema definitions with no sync mechanism.

### Investigation Status

| Item | Status |
|------|--------|
| Plan | @docs/plans/PLAN-INVESTIGATION-001-synthesis-schema-bug.md |
| Part A (Technical) | COMPLETE |
| Part B (Process) | COMPLETE |
| Root Cause | IDENTIFIED |
| Recommendations | DOCUMENTED |

---

## Findings

### Part A: Technical Investigation

#### A.1 Bug Verification Results

| Test | Expected | Actual |
|------|----------|--------|
| CHECK constraint exists | Yes | **NO** |
| 'concept' INSERT | Success | Success |
| 'cross' INSERT | Fail | **Success** |
| Existing data | 0 | 0 |

**Conclusion:** The hypothesized bug does not exist because the CHECK constraints were never applied to the production database.

#### A.2 Schema Drift Discovery

**Live database synthesis_provenance:**
```sql
CREATE TABLE synthesis_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synthesized_concept_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,  -- NO CHECK!
    source_id INTEGER NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Migration 007 synthesis_provenance:**
```sql
CREATE TABLE IF NOT EXISTS synthesis_provenance (
    ...
    source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace')),
    ...
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);
```

**Differences:**
1. CHECK constraint missing
2. FOREIGN KEY constraint missing

#### A.3 Cross-Table Comparison

| Table | Migration Has CHECK | Live DB Has CHECK |
|-------|---------------------|-------------------|
| synthesis_clusters | Yes (2 constraints) | **NO** |
| synthesis_cluster_members | Yes (1 constraint) | **NO** |
| synthesis_provenance | Yes (1 constraint) | **NO** |

**All synthesis tables have schema drift.**

### Part B: Process Audit

#### B.1 Test Fixture Analysis

**File:** @tests/test_synthesis.py (lines 39-108)

**Finding:** The test fixture creates a HAND-WRITTEN schema that:
- Claims to be "Migration 007" in comments
- Does NOT include CHECK constraints
- Does NOT include FOREIGN KEY constraints
- Is a simplified/stripped version of the migration

**Impact:** Tests cannot catch constraint violations because constraints don't exist in test DB.

#### B.2 Code Path Analysis

| Path | Calls store_synthesis()? | Could catch bug? |
|------|--------------------------|------------------|
| Dry-run | No (returns early at line 716) | No |
| Real-run | Yes | Yes, if constraints existed |
| test_bridge_insight_created | No (only calls create_bridge_insight) | No |

**Finding:** No test actually INSERTs a 'cross' type to synthesis_provenance.

#### B.3 Validation Process Review

| Document | Claims validation? | Actually validates constraints? |
|----------|-------------------|--------------------------------|
| Session 15c Checkpoint | "Live Validation" via stats | Stats only, no INSERT test |
| Handoff Request | Requests evaluation | Evaluation was POST-implementation |
| PLAN-SYNTHESIS-001 | Success criteria list | No "verify schema constraints" item |

**Finding:** No validation step compared:
1. Test schema to migration file
2. Live DB schema to migration file
3. Code values to CHECK constraint values

---

## Root Cause Analysis

### Primary Root Cause: Schema Source-of-Truth Fragmentation

**Three conflicting schema sources exist:**

| Source | Purpose | Has Synthesis Tables? | Has Constraints? |
|--------|---------|----------------------|------------------|
| `docs/specs/memory_db_schema_v2.sql` | Main schema | NO | N/A |
| `migrations/007_add_synthesis_tables.sql` | Additive migration | YES | YES |
| `tests/test_synthesis.py` fixture | Test database | YES | NO |

**No mechanism ensures these stay synchronized.**

### Contributing Factors

1. **Manual schema copy in tests** - Developer copied CREATE statements by hand, omitting constraints
2. **No migration runner** - Migrations applied manually, no tracking table
3. **Implicit trust in tests** - "Tests pass" = "Implementation correct" assumption
4. **Dry-run-only validation** - CLI dry-run exercises clustering, not storage
5. **Self-validation** - Builder (Session 15c) marked work complete before external evaluation

### Hypothesis Confirmation Matrix

| ID | Hypothesis | Confirmed? | Evidence |
|----|------------|------------|----------|
| H1 | Tests use hand-written schema | **YES** | Lines 39-108 of test file |
| H2 | No test INSERTs 'cross' to provenance | **YES** | test_bridge_insight_created stops early |
| H3 | Dry-run doesn't exercise storage | **YES** | Returns at line 716 |
| H4 | Self-validation (no external review) | **YES** | Checkpoint marked complete before eval |
| H5 | Checklist gap | **YES** | No "verify constraints" step in plan |

---

## Process Improvement Recommendations

### Immediate Fixes (This Session)

1. **Update test fixture to match migration**
   - Copy exact SQL from migration 007
   - Include CHECK and FOREIGN KEY constraints

2. **Add schema validation test**
   ```python
   def test_schema_matches_migration():
       """Verify test DB schema matches migration file."""
       # Compare CREATE statements
   ```

3. **Update main schema file**
   - Add synthesis tables to `memory_db_schema_v2.sql`
   - Establish single source of truth

### Process Changes (Future Sessions)

1. **Test fixture generation rule**
   - NEVER hand-write schema in tests
   - Import from migration files or main schema

2. **Pre-completion checklist additions**
   - [ ] Compare test schema to migration/main schema
   - [ ] Run non-dry-run on test data
   - [ ] Verify all CHECK constraints with INSERT tests
   - [ ] External evaluation before marking complete

3. **Migration tracking**
   - Add `schema_migrations` table to track applied migrations
   - Or use single schema file as source of truth

4. **Constraint validation tests**
   ```python
   @pytest.mark.parametrize("invalid_value", ['invalid', 'cross', ''])
   def test_source_type_constraint(invalid_value):
       """Verify CHECK constraint rejects invalid values."""
       # Attempt INSERT with invalid value
       # Expect IntegrityError
   ```

### Architectural Recommendation

**Single Source of Truth Pattern:**

```
docs/specs/memory_db_schema_v2.sql  (AUTHORITATIVE)
    |
    +-- haios_etl/database.py init_schema()  (READS FROM)
    |
    +-- tests/conftest.py temp_db()          (READS FROM)
    |
    +-- migrations/007_*.sql                  (MERGED INTO main)
```

**Rule:** Never duplicate schema definitions. Always read from one source.

---

## Deliverables

| Deliverable | Status | Location |
|-------------|--------|----------|
| Investigation findings | COMPLETE | This document |
| Root cause identification | COMPLETE | Section: Root Cause Analysis |
| Process recommendations | COMPLETE | Section: Process Improvements |
| Technical fix | PENDING | See Immediate Fixes |

---

## Next Steps

1. **Operator Decision:** Which fix approach?
   - A: Update live DB to add constraints (risk if bad data exists)
   - B: Update migration file to match live DB (accept no constraints)
   - C: Fix test fixture AND update live DB (recommended)

2. **If C selected:**
   - Fix test fixture to include constraints
   - Create migration 008 to add missing constraints to live DB
   - Add constraint validation tests

---

## References

### This Document Links To

- @docs/plans/PLAN-INVESTIGATION-001-synthesis-schema-bug.md - Investigation plan
- @docs/reports/2025-11-30-EVALUATION-synthesis-pipeline.md - Original evaluation
- @haios_etl/synthesis.py - Code under investigation
- @haios_etl/migrations/007_add_synthesis_tables.sql - Migration with constraints
- @tests/test_synthesis.py - Test with missing constraints
- @docs/specs/memory_db_schema_v2.sql - Main schema (missing synthesis)

### Documents That Should Link Here

- @docs/epistemic_state.md - Findings reference
- @docs/plans/README.md - Investigation complete

---

**Investigation Status:** COMPLETE
**Author:** Hephaestus (Session 16)
**Date:** 2025-11-30
**Duration:** ~35 minutes
