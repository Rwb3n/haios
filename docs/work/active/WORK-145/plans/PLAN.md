---
template: implementation_plan
status: draft
date: 2026-02-15
backlog_id: WORK-145
title: "Legacy Duplication Cleanup"
author: Hephaestus
lifecycle_phase: plan
session: 377
version: "1.5"
generated: 2026-02-15
last_updated: 2026-02-15T22:05:00
---
# Implementation Plan: Legacy Duplication Cleanup

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Verify existing tests pass, then remove orphan tests alongside orphan code |
| Query prior work | SHOULD | S365 system audit is the source (no prior memory needed) |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | All counts verified via Glob/Grep |

---

## Goal

Remove 3 orphaned lib/ files, 3 orphaned test files, and 1 deprecated skill to eliminate duplication and confusion per REQ-CONFIG-003.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to delete | 7 | 3 lib/ orphans + 3 test files + 1 skill dir |
| Files to modify | 3 | lib/__init__.py (docstring), lib/README.md, test_lib_migration.py |
| New files to create | 0 | Pure deletion task |
| Tests to write | 0 | Deletion removes tests, no new behavior |
| Dependencies | 0 | Orphan files have zero runtime consumers |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Orphan files have no runtime consumers |
| Risk of regression | Low | Removing dead code; modules/ versions are the live code |
| External dependencies | Low | No APIs or config changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Verify orphan status | 5 min | High |
| Delete files | 5 min | High |
| Update consumers | 10 min | High |
| Verify no regressions | 5 min | High |
| **Total** | **25 min** | High |

---

## Current State vs Desired State

### Current State

**Duplicated lib/ files (orphans — zero runtime imports):**

| lib/ file (ORPHAN) | Lines | modules/ file (ACTIVE) | Lines | Consumer |
|--------------------|-------|------------------------|-------|----------|
| `lib/cascade.py` | 600 | `modules/cascade_engine.py` | 387 | work_engine.py:1080 |
| `lib/spawn.py` | 192 | `modules/spawn_tree.py` | 170 | work_engine.py:1094,1106 |
| `lib/backfill.py` | 276 | `modules/backfill_engine.py` | 228 | work_engine.py:1148,1162 |

**NOT an orphan (critique A1):**
- `lib/spawn_ceremonies.py` — active consumer: `spawn-work-ceremony` skill (SKILL.md:72). Created 2026-02-12 for WORK-137/CH-017. NOT in S365 orphan list. DO NOT DELETE.

**Orphan test files (test the orphan lib/ files):**

| Test file | Tests | Imports from |
|-----------|-------|-------------|
| `tests/test_lib_cascade.py` | ~10 | `from cascade import ...` (lib/) |
| `tests/test_lib_spawn.py` | ~5 | `from spawn import ...` (lib/) |
| `tests/test_backfill.py` | ~5 | `from backfill import ...` (lib/) |

**Deprecated skill:**
- `observation-capture-cycle` — frontmatter has `deprecated: true`, replaced by `retro-cycle` (WORK-142)

**Evidence of orphan status:**
- Grep for `from cascade import|import cascade` → only self-reference in lib/cascade.py docstring
- Grep for `from spawn import|import spawn` → only self-reference in lib/spawn.py docstring
- Grep for `from backfill import|import backfill` → only self-reference in lib/backfill.py docstring
- Justfile routes through `modules/cli.py` for cascade, spawn-tree, backfill commands
- `work_engine.py` imports from `cascade_engine`, `spawn_tree`, `backfill_engine` (modules/)

### Desired State

- lib/cascade.py, lib/spawn.py, lib/backfill.py: **DELETED** (lib/spawn_ceremonies.py KEPT — active consumer)
- tests/test_lib_cascade.py, tests/test_lib_spawn.py, tests/test_backfill.py: **DELETED**
- observation-capture-cycle skill directory: **DELETED**
- lib/ README (if exists): updated to remove references
- modules/README.md: no changes needed (already references modules/ versions)
- test_lib_migration.py: updated to remove cascade/backfill from expected lib files list

---

## Tests First (TDD)

**SKIPPED:** This is a pure deletion task. No new behavior is being created. Verification is:
1. Existing modules/ tests still pass (test_decomposition.py, test_work_engine.py)
2. Full test suite has no regressions (minus the deleted orphan test files)
3. Zero stale import references remain

---

## Detailed Design

### Exact Changes

**Phase 1: Delete orphan lib/ files**
```
DELETE: .claude/haios/lib/cascade.py (600 lines)
DELETE: .claude/haios/lib/spawn.py (192 lines)
DELETE: .claude/haios/lib/backfill.py (276 lines)
```
Note: `lib/spawn_ceremonies.py` is NOT an orphan (critique A1 — used by spawn-work-ceremony skill). DO NOT DELETE.

**Phase 2: Delete orphan test files**
```
DELETE: tests/test_lib_cascade.py
DELETE: tests/test_lib_spawn.py
DELETE: tests/test_backfill.py
```

**Phase 3: Delete deprecated skill**
```
DELETE: .claude/skills/observation-capture-cycle/ (entire directory)
```

**Phase 4: Update consumers**

File: `tests/test_lib_migration.py` (critique A3)
- Remove `cascade` (line 53), `spawn` (line 54), `backfill` (line 55) from `core_modules` list
- List goes from 16 entries to 13 entries
- Update assertion on line 81: `assert len(imported) >= 17` → `assert len(imported) >= 13`
- Also update test docstring if it mentions module count

File: `.claude/haios/lib/__init__.py` (critique A4)
- Remove from docstring "Contains:" list: cascade, spawn, backfill
- Also remove stale WORK-029 entries: retrieval, synthesis, extraction, mcp_server (lines 23-24, 30)

File: `.claude/haios/lib/README.md`
- Remove table rows: cascade.py (line 88), spawn.py (line 89), backfill.py (line 90)
- Also remove stale WORK-029 rows: retrieval.py (line 96), synthesis.py (line 97), extraction.py (line 98), mcp_server.py (line 104)
- Update Notes section (lines 134-137) to remove reference to retrieval, synthesis, extraction, mcp_server

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delete lib/ files vs consolidate | Delete | modules/ versions are the active code; lib/ versions are dead (zero imports) |
| Delete orphan tests vs migrate | Delete | test_decomposition.py already covers modules/ versions; orphan tests test dead code |
| Delete observation-capture-cycle vs keep | Delete | Already marked `deprecated: true`, fully replaced by retro-cycle (WORK-142) |
| Keep spawn_ceremonies.py | Keep | Active consumer: spawn-work-ceremony skill (critique A1). NOT a duplicate. |
| Keep _legacy/implementation_plan.md | Keep | Still used as fallback by load_template() (WORK-099). Not in scope. |
| Keep ceremony/SKILL.md template | Keep | Wrong var syntax is a separate fix (template rationalization). Not in scope. |
| Clean stale WORK-029 doc entries | Include | retrieval/synthesis/extraction/mcp_server in __init__.py and README.md — trivially safe doc-only fix (critique A5) |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| lib/__init__.py docstring lists deleted modules | Remove cascade/spawn/backfill + stale WORK-029 entries from docstring | Manual verification |
| Skill references in docs/skills | Grep for observation-capture references | Consumer verification step |
| conftest.py sys.path includes lib/ | No change needed — other lib/ files still exist | Existing tests |

---

## Open Decisions (MUST resolve before implementation)

No operator decisions needed. All targets are confirmed orphans with zero runtime consumers.

---

## Implementation Steps

### Step 1: Pre-deletion verification
- [ ] Run full test suite to establish baseline
- [ ] Verify modules/ tests pass independently (test_decomposition.py, test_work_engine.py)

### Step 2: Delete orphan lib/ files
- [ ] Delete lib/cascade.py, lib/spawn.py, lib/backfill.py (NOT spawn_ceremonies.py — active consumer)
- [ ] Update lib/__init__.py docstring: remove cascade, spawn, backfill + stale WORK-029 entries (retrieval, synthesis, extraction, mcp_server)

### Step 3: Delete orphan test files
- [ ] Delete tests/test_lib_cascade.py, tests/test_lib_spawn.py, tests/test_backfill.py

### Step 4: Delete deprecated skill
- [ ] Delete .claude/skills/observation-capture-cycle/ directory

### Step 5: Update consumers
- [ ] Update tests/test_lib_migration.py: remove cascade (line 53), spawn (line 54), backfill (line 55) from core_modules list
- [ ] Update tests/test_lib_migration.py: change assertion `>= 17` to `>= 13` (line 81)
- [ ] Update lib/README.md: remove cascade.py, spawn.py, backfill.py rows + stale WORK-029 rows (retrieval, synthesis, extraction, mcp_server)
- [ ] Update lib/README.md: remove Notes section reference to retrieval/synthesis/extraction/mcp_server
- [ ] Grep ALL **/*.py files for remaining references to deleted files (WORK-093 retro lesson: grep all, not just known files)

### Step 6: Verify no regressions
- [ ] Run full test suite
- [ ] Verify test count decreased by expected amount (orphan tests removed)
- [ ] Zero stale references in grep

### Step 7: README Sync (MUST)
- [ ] Update .claude/haios/lib/ README
- [ ] Verify modules/README.md needs no changes

---

## Verification

- [ ] Full test suite passes (minus deleted orphan tests)
- [ ] Zero grep hits for `from cascade import|from spawn import|from backfill import` in lib/
- [ ] Zero grep hits for `observation-capture-cycle` in skills/
- [ ] test_lib_migration.py passes with updated expected file list

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hidden consumer of lib/ files | Medium | Grep ALL .py files (lesson from WORK-093 retro) |
| test_lib_migration.py breaks | Low | Update expected file list |
| Skill reference in hooks/docs | Low | Grep for observation-capture references |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Identify all duplicated lib/ files (audit report) | [ ] | This plan section documents all 4 |
| Remove duplicates, update imports | [ ] | Files deleted, imports cleaned |
| Remove or mark deprecated skill(s) | [ ] | observation-capture-cycle deleted |
| Remove stale templates | [ ] | Assessed: _legacy/implementation_plan.md still in use (WORK-099 fallback); ceremony/SKILL.md has separate syntax issue. No templates eligible for removal — documented in Key Design Decisions (critique A7) |
| Tests still pass after cleanup | [ ] | pytest output |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `lib/cascade.py` | DELETED | [ ] | |
| `lib/spawn.py` | DELETED | [ ] | |
| `lib/backfill.py` | DELETED | [ ] | |
| `lib/spawn_ceremonies.py` | KEPT (active consumer) | [ ] | Critique A1 |
| `tests/test_lib_cascade.py` | DELETED | [ ] | |
| `tests/test_lib_spawn.py` | DELETED | [ ] | |
| `tests/test_backfill.py` | DELETED | [ ] | |
| `observation-capture-cycle/` | DELETED | [ ] | |
| `test_lib_migration.py` | Updated (no cascade/spawn/backfill, assert >= 13) | [ ] | Critique A3 |
| `lib/__init__.py` | Docstring cleaned (7 stale entries removed) | [ ] | Critique A4 |
| `lib/README.md` | Table cleaned (7 stale rows removed, Notes updated) | [ ] | Critique A5 |
| `Grep: from cascade import\|from spawn import\|from backfill import` | Zero hits outside deleted files | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (full suite minus deleted orphan tests)
- [ ] All WORK.md deliverables verified complete
- [ ] Runtime consumer exists (N/A — deletion task, no new code)
- [ ] WHY captured (reasoning stored to memory)
- [ ] READMEs updated
- [ ] Consumer verification complete (zero stale references)

---

## References

- @.claude/haios/epochs/E2_6/system-audit-S365.md (source findings)
- @docs/work/active/WORK-145/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CONFIG-003)

---
