---
template: implementation_plan
status: complete
date: 2026-01-21
backlog_id: WORK-006
title: Migrate .claude/lib to portable plugin directory
author: Hephaestus
lifecycle_phase: plan
session: 220
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-21T20:36:21'
---
# Implementation Plan: Migrate .claude/lib to portable plugin directory

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

All Python modules in `.claude/lib/` (23 files, ~8854 lines) will be moved to `.claude/haios/lib/`, with import paths updated across 6 consumer files, enabling the portable plugin directory to function independently.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to move | 23 | `Glob(".claude/lib/*.py")` - actual count: 23 Python files |
| Lines of code affected | ~8854 | `wc -l .claude/lib/*.py` |
| New files to create | 2 | `.claude/haios/lib/__init__.py`, `.claude/haios/lib/README.md` |
| Files to update imports | 6 | governance_layer.py, context_loader.py, cycle_runner.py, memory_bridge.py, pre_tool_use.py, post_tool_use.py |
| Tests to write | 3 | Import verification tests |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | 6 consumer files with sys.path manipulation |
| Risk of regression | Medium | Hooks and modules are runtime-critical |
| External dependencies | Low | No external APIs, pure file/import changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Move files + create __init__.py | 15 min | High |
| Update 6 consumer imports | 30 min | High |
| Create compatibility shims | 15 min | High |
| Write/run import tests | 20 min | High |
| README updates | 10 min | High |
| **Total** | ~90 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/governance_layer.py:34-40
import sys

_lib_path = Path(__file__).parent.parent.parent / "lib"  # Goes OUTSIDE haios/
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_validation_outcome  # External dependency
```

**Behavior:** Modules use sys.path manipulation to reach `.claude/lib/` which is outside the portable plugin directory.

**Result:** Plugin is not portable - dropping `.claude/haios/` into another project fails because it depends on external `.claude/lib/`.

### Desired State

```python
# .claude/haios/modules/governance_layer.py:34-40 (after migration)
# No sys.path manipulation needed - lib is inside haios/
try:
    from ..lib.governance_events import log_validation_outcome  # Relative import
except ImportError:
    from lib.governance_events import log_validation_outcome  # Fallback for direct execution
```

**Behavior:** Modules use relative imports from `.claude/haios/lib/` (inside portable plugin).

**Result:** Plugin is portable - `.claude/haios/` is self-contained with no external dependencies.

---

## Tests First (TDD)

### Test 1: All lib modules importable from new location
```python
def test_lib_modules_importable():
    """Verify all 23 modules can be imported from .claude/haios/lib/."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios"))

    modules = [
        "lib.database", "lib.scaffold", "lib.work_item", "lib.config",
        "lib.status", "lib.validate", "lib.observations", "lib.cascade",
        "lib.spawn", "lib.backfill", "lib.node_cycle", "lib.governance_events",
        "lib.routing", "lib.dependencies", "lib.retrieval", "lib.synthesis",
        "lib.extraction", "lib.error_capture", "lib.audit", "lib.errors",
        "lib.cli", "lib.mcp_server"
    ]
    for mod in modules:
        __import__(mod)  # Should not raise
```

### Test 2: Compatibility shims work
```python
def test_compatibility_shims():
    """Verify old import paths still work via re-exports."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude"))

    # Old import path should still work
    from lib.database import get_database_path  # Re-exported from haios/lib
    assert callable(get_database_path)
```

### Test 3: Consumer modules still function
```python
def test_governance_layer_imports():
    """Verify governance_layer.py imports work after migration."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

    from governance_layer import GovernanceLayer, GateResult
    layer = GovernanceLayer()
    assert layer is not None
```

---

## Detailed Design

### Strategy: Strangler Fig Pattern (Memory 80530)

Move files incrementally with compatibility shims, rather than big-bang migration.

```
Phase 1: Copy files to new location (.claude/haios/lib/)
Phase 2: Update consumer imports to use new location
Phase 3: Create compatibility shims in old location (re-exports)
Phase 4: Verify all tests pass
Phase 5: Mark old location deprecated (don't delete yet)
```

### Exact Code Changes

**Change 1: governance_layer.py imports**

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Lines 34-40

**Current Code:**
```python
# .claude/haios/modules/governance_layer.py:34-40
import sys

_lib_path = Path(__file__).parent.parent.parent / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_validation_outcome
```

**Changed Code:**
```python
# .claude/haios/modules/governance_layer.py:34-40
# Lib is now inside haios/ - use relative import
try:
    from ..lib.governance_events import log_validation_outcome
except ImportError:
    # Fallback for direct script execution
    from lib.governance_events import log_validation_outcome
```

**Change 2: post_tool_use.py imports**

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Lines 388-391, 434-437, 859-862

**Current Code (example from line 388):**
```python
# .claude/hooks/hooks/post_tool_use.py:388-391
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

from validate import validate_file
```

**Changed Code:**
```python
# .claude/hooks/hooks/post_tool_use.py:388-391
# Import from portable plugin lib
haios_lib = Path(__file__).parent.parent.parent / "haios" / "lib"
if str(haios_lib) not in sys.path:
    sys.path.insert(0, str(haios_lib))

from validate import validate_file
```

### New File: `.claude/haios/lib/__init__.py`

```python
"""
HAIOS Library - Portable plugin utilities.

Migrated from .claude/lib/ (Session 220) for portability.
Contains: database, scaffold, work_item, config, status, validate,
          observations, cascade, spawn, backfill, node_cycle, etc.
"""
```

### Compatibility Shim: `.claude/lib/__init__.py`

```python
"""
DEPRECATED: This location is deprecated.
Use .claude/haios/lib/ instead.

Compatibility shims re-export from new location.
"""
import warnings
warnings.warn(
    ".claude/lib/ is deprecated. Import from .claude/haios/lib/ instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from ..haios.lib.database import *
from ..haios.lib.scaffold import *
# ... etc for all 23 modules
```

### Call Chain Context

```
Hook/Module invocation
    |
    +-> sys.path.insert(haios_lib)  # NEW: points to haios/lib/
    |
    +-> from validate import validate_file
            |
            +-> .claude/haios/lib/validate.py  # NEW location
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Strangler fig vs big-bang | Strangler fig | Memory 80530: incremental migration reduces risk |
| Keep sys.path manipulation | Yes (in hooks) | Hooks run standalone, can't use relative imports |
| Use relative imports | Yes (in modules) | Modules are inside package, relative is cleaner |
| Keep shims in old location | Yes | Backward compat for any external consumers |
| Deprecation warning | Yes | Alert consumers to migrate |
| Delete old files | No (mark deprecated) | Safe rollback if issues found |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Direct script execution | try/except fallback | Test 3 |
| Old import path used | Deprecation warning, re-export | Test 2 |
| Circular imports | None expected - lib has no internal cycles | Manual verify |
| Path with spaces | Path() handles properly | N/A |

### Files to Move (23 total)

```
.claude/lib/
├── __init__.py       → .claude/haios/lib/__init__.py
├── audit.py          → .claude/haios/lib/audit.py
├── backfill.py       → .claude/haios/lib/backfill.py
├── cascade.py        → .claude/haios/lib/cascade.py
├── cli.py            → .claude/haios/lib/cli.py
├── config.py         → .claude/haios/lib/config.py
├── database.py       → .claude/haios/lib/database.py
├── dependencies.py   → .claude/haios/lib/dependencies.py
├── error_capture.py  → .claude/haios/lib/error_capture.py
├── errors.py         → .claude/haios/lib/errors.py
├── extraction.py     → .claude/haios/lib/extraction.py
├── governance_events.py → .claude/haios/lib/governance_events.py
├── mcp_server.py     → .claude/haios/lib/mcp_server.py
├── node_cycle.py     → .claude/haios/lib/node_cycle.py
├── observations.py   → .claude/haios/lib/observations.py
├── retrieval.py      → .claude/haios/lib/retrieval.py
├── routing.py        → .claude/haios/lib/routing.py
├── scaffold.py       → .claude/haios/lib/scaffold.py
├── spawn.py          → .claude/haios/lib/spawn.py
├── status.py         → .claude/haios/lib/status.py
├── synthesis.py      → .claude/haios/lib/synthesis.py
├── validate.py       → .claude/haios/lib/validate.py
└── work_item.py      → .claude/haios/lib/work_item.py
```

### Consumer Files to Update (6 total)

1. `.claude/haios/modules/governance_layer.py` - imports governance_events
2. `.claude/haios/modules/context_loader.py` - imports from lib
3. `.claude/haios/modules/cycle_runner.py` - imports from lib
4. `.claude/haios/modules/memory_bridge.py` - imports from lib
5. `.claude/hooks/hooks/pre_tool_use.py` - imports node_cycle
6. `.claude/hooks/hooks/post_tool_use.py` - imports validate, status, node_cycle

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No operator decisions required - scope and approach are clear |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_lib_migration.py`
- [ ] Add Test 1: All lib modules importable from new location
- [ ] Add Test 2: Compatibility shims work
- [ ] Add Test 3: Consumer modules still function
- [ ] Verify all tests fail (red) - new location doesn't exist yet

### Step 2: Create Target Directory Structure
- [ ] Create `.claude/haios/lib/` directory
- [ ] Create `.claude/haios/lib/__init__.py` with docstring

### Step 3: Move 23 Python Files
- [ ] Move all `.claude/lib/*.py` files to `.claude/haios/lib/`
- [ ] Verify files exist in new location
- [ ] Test 1 should now pass (modules importable)

### Step 4: Update Consumer Imports (6 files)
- [ ] Update `.claude/haios/modules/governance_layer.py` (lines 34-40)
- [ ] Update `.claude/haios/modules/context_loader.py`
- [ ] Update `.claude/haios/modules/cycle_runner.py`
- [ ] Update `.claude/haios/modules/memory_bridge.py`
- [ ] Update `.claude/hooks/hooks/pre_tool_use.py`
- [ ] Update `.claude/hooks/hooks/post_tool_use.py`
- [ ] Test 3 should now pass (consumers function)

### Step 5: Create Compatibility Shims
- [ ] Create new `.claude/lib/__init__.py` with deprecation warning
- [ ] Add re-exports for all 23 modules
- [ ] Test 2 should now pass (shims work)

### Step 6: Full Test Suite Verification
- [ ] Run `pytest tests/` - all tests pass
- [ ] Run `pytest tests/test_lib_migration.py -v` - migration tests pass

### Step 7: README Sync (MUST)
- [ ] **MUST:** Create `.claude/haios/lib/README.md` documenting modules
- [ ] **MUST:** Update `.claude/lib/README.md` with deprecation notice
- [ ] **MUST:** Update `.claude/haios/modules/README.md` if import docs changed

### Step 8: Consumer Verification (MUST)
- [ ] **MUST:** `Grep(pattern="\.claude/lib", path=".")` - find references
- [ ] **MUST:** Update all references to use new path or explain shim
- [ ] **MUST:** Verify no stale references remain

**Consumer Discovery Pattern:**
```bash
# Find all references to old lib path
Grep(pattern="\\.claude/lib[^/]|\\.claude/lib/", path=".", output_mode="files_with_matches")
```

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import failures at runtime | High | Test hooks and modules immediately after migration; keep shims for rollback |
| Circular import introduced | Medium | Lib modules have no internal cycles; verify post-migration |
| Missed consumer reference | Medium | Comprehensive grep for `.claude/lib`; don't delete old location |
| Hooks fail during session | High | Test hooks in isolation before full test suite |
| External tool references old path | Low | Shims with deprecation warning; gradual migration |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-006/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Move 23 Python modules to `.claude/haios/lib/` | [ ] | `ls .claude/haios/lib/*.py \| wc -l` = 23 |
| Update imports in `.claude/haios/modules/` | [ ] | Grep shows no `.parent.parent.parent / "lib"` |
| Update imports in `.claude/hooks/hooks/` | [ ] | Grep shows haios/lib path |
| Create `__init__.py` in `.claude/haios/lib/` | [ ] | File exists |
| Remove sys.path manipulation from modules | [ ] | Or explain why kept |
| Leave compatibility shims in `.claude/lib/` | [ ] | Re-exports work |
| Verify all tests pass | [ ] | pytest output |
| Update `.claude/haios/lib/README.md` | [ ] | README exists |
| Mark old `.claude/lib/` deprecated | [ ] | Deprecation notice present |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/__init__.py` | Contains package docstring | [ ] | |
| `.claude/haios/lib/database.py` | Migrated, functions work | [ ] | |
| `tests/test_lib_migration.py` | 3 tests, all pass | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Documents 23 modules | [ ] | |
| `.claude/lib/README.md` | **MUST:** Deprecation notice | [ ] | |
| `Grep: .claude/lib[^/h]` | **MUST:** Zero stale refs (except shim mentions) | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_3/observations/obs-219-001.md (spawning observation)
- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (arc context)
- @.claude/haios/manifesto/L4-implementation.md (Module-First principle)
- Memory 80530: Strangler fig pattern for incremental migration
- Memory 80606: Module migration pattern - port logic wholesale
- Memory 80665: Sibling import pattern - try/except conditional imports
- Session 219 checkpoint (memory_refs: 82230-82242)

---
