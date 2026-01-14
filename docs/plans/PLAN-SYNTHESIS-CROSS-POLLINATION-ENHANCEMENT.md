---
template: implementation_plan
status: complete
date: 2025-12-07
backlog_id: PLAN-SYNTHESIS-CROSS-POLLINATION-ENHANCEMENT
title: "Synthesis Cross-Pollination Enhancement"
author: Hephaestus
lifecycle_phase: execute
version: "1.1"
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-09 18:48:58
# Implementation Plan: Synthesis Cross-Pollination Enhancement

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Enable comprehensive, idempotent cross-pollination runs with configurable parameters for unattended execution (1.5+ hours).

---

## Problem Statement

Current cross-pollination has critical limitations:
1. **No idempotency** - Running twice creates duplicate bridge insights
2. **Hardcoded limits** - 500 concepts, 200 traces, 10 bridges max
3. **No cross-only mode** - Must run full synthesis pipeline
4. **No visibility** - Long runs have no progress reporting

**Memory Reference:** Concept 62597 (techne) contains full analysis.

---

## Proposed Changes

### 1. Idempotency Guard (CRITICAL)
- [x] Add `_bridge_exists(concept_id, trace_id)` method in synthesis.py
- [x] Query synthesis_provenance for existing pairs before LLM call
- [x] Skip bridge creation if pair already exists

### 2. CLI Arguments (cli.py:425-434)
- [x] Add `--cross-only` flag (skip stages 1-3)
- [x] Add `--concept-sample N` (default 0 = ALL, ~60k)
- [x] Add `--trace-sample N` (default 0 = ALL, ~450)
- [x] Add `--max-bridges N` (default 100)

### 3. Synthesis Pipeline Updates (synthesis.py)
- [x] Update `find_cross_type_overlaps()` to accept sample size params
- [x] Update `run_synthesis_pipeline()` to accept cross_only flag
- [x] Remove hardcoded LIMIT 500/200 in SQL queries
- [x] Add progress logging every 100 bridges

---

## Technical Details

**Bottleneck Analysis:**
- Comparisons: 27M pairs at 100k/sec = ~5 minutes
- LLM calls: 1.5s per bridge (real bottleneck)
- 1% match rate = ~268k potential matches
- Full run without limit = 112 hours (impractical)

**Cost Model:**
- ~$0.001 per bridge LLM call
- 1000 bridges = $1, 2000 bridges = $2

**Example Usage:**
```bash
# 1.5 hour unattended run
python -m haios_etl.cli synthesis run --cross-only --max-bridges 2000
```

---

## Verification

- [x] Tests pass (162 total, 161 passed, 1 pre-existing failure)
- [x] Add test for `_bridge_exists()` idempotency (2 tests)
- [x] Test --cross-only skips stages 1-3
- [x] Test --max-bridges limits output
- [x] Test idempotency skips existing bridges
- [x] Documentation updated (this plan)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Duplicate bridges (pre-fix) | High | Idempotency check FIRST |
| API rate limiting | Medium | Progress logging shows issues |
| Long run crash | Medium | Deferred: resume capability |
| API cost overrun | Low | --max-bridges default 100 |

---

## References

- Memory: Concept 62597 (cross-pollination analysis)
- Code: haios_etl/synthesis.py:507-585 (cross-pollination functions)
- Code: haios_etl/cli.py:425-430 (synthesis CLI args)
- Schema: docs/specs/memory_db_schema_v3.sql (synthesis_provenance table)

---


<!-- VALIDATION ERRORS (2025-12-07 15:25:18):
  - ERROR: Invalid status 'complete' for implementation_plan template. Allowed: draft, approved, rejected
-->
