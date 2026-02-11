---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-117
title: "Unify test module loading via shared conftest.py"
author: Hephaestus
lifecycle_phase: plan
session: 351
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T23:15:49
---
# Implementation Plan: Unify test module loading via shared conftest.py

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Existing 119 tests are the regression suite — no new TDD tests needed (refactor, not new feature) |
| Query prior work | SHOULD | Memory from S338 WORK-116 documents the root cause |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | All metrics from actual file analysis |

---

## Goal

A single `tests/conftest.py` provides session-scoped fixtures for `governance_layer`, `work_engine`, and `queue_ceremonies` modules, eliminating per-file `_load_module` / `_ensure_module` / `sys.path.insert` boilerplate and the ContextVar divergence bug.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | `tests/conftest.py`, `test_work_engine.py`, `test_queue_ceremonies.py`, `test_ceremony_context.py` |
| Lines of code affected | ~120 | Module loading boilerplate in each file |
| New files to create | 0 | Modifying existing `tests/conftest.py` |
| Tests to write | 0 | Existing 119 tests are the regression suite |
| Dependencies | 3 | governance_layer, work_engine, queue_ceremonies modules |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | 3 modules with import dependencies |
| Risk of regression | Med | 119 existing tests must pass; ContextVar sensitivity |
| External dependencies | Low | No external APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| conftest.py fixtures | 15 min | High |
| test_work_engine.py cleanup | 10 min | High |
| test_queue_ceremonies.py cleanup | 10 min | High |
| test_ceremony_context.py cleanup | 15 min | Med (most complex workarounds) |
| Regression verification | 10 min | High |
| **Total** | ~60 min | |

---

## Current State vs Desired State

### Current State

Each of the 3 test files loads modules independently:

**test_work_engine.py:34-50** — Uses `_load_module()` which unconditionally creates new module + overwrites `sys.modules`:
```python
def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # Overwrites existing!
    spec.loader.exec_module(module)
    return module

governance_layer = _load_module("governance_layer", _gov_path)
work_engine = _load_module("work_engine", _work_path)
```

**test_queue_ceremonies.py:27-54** — Same `_load_module()` with a conditional guard on governance_layer:
```python
if "governance_layer" not in sys.modules:
    governance_layer = _load_module("governance_layer", _gov_path)
else:
    governance_layer = sys.modules["governance_layer"]
```

**test_ceremony_context.py:19-20, 269-298** — Uses `sys.path.insert` + `from governance_layer import`, plus `_ensure_module()` and `_get_gov_mod()` workarounds for the ContextVar bug:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
# ... later ...
def _ensure_module(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    # ...
def _get_gov_mod():
    return sys.modules["governance_layer"]
```

**Behavior:** When test_work_engine.py is collected first, its `_load_module("governance_layer", ...)` creates module instance A with ContextVar A. When test_ceremony_context.py is collected next, `from governance_layer import ceremony_context` may reference a stale module if `_load_module` already overwrote `sys.modules`. This causes `ceremony_context` to set ContextVar A but `check_ceremony_required` to read ContextVar B.

**Result:** Tests pass individually but fail intermittently in suite due to ContextVar divergence.

### Desired State

**tests/conftest.py** — Module-level loading (NOT fixtures — module-level code runs before test collection):
```python
import importlib.util
import sys
from pathlib import Path

import pytest

_root = Path(__file__).parent.parent

# Add module paths once
sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(_root / ".claude" / "haios" / "lib"))

def _load_module_once(name: str, path: Path):
    """Load module once into sys.modules. Reuse if already loaded."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load in dependency order at MODULE LEVEL (before test collection)
_load_module_once("governance_layer",
    _root / ".claude" / "haios" / "modules" / "governance_layer.py")
_load_module_once("work_engine",
    _root / ".claude" / "haios" / "modules" / "work_engine.py")
_load_module_once("queue_ceremonies",
    _root / ".claude" / "haios" / "lib" / "queue_ceremonies.py")
_load_module_once("cycle_runner",
    _root / ".claude" / "haios" / "modules" / "cycle_runner.py")
```

**NOTE:** Fixture-based approach was rejected. Module-level loading is required because test files use `from governance_layer import X` at module scope (during collection), which must find modules already in `sys.modules`. Fixtures run too late.

**Behavior:** Modules loaded exactly once per test session at conftest module level. All test files share the same module instances and ContextVars.

**Result:** No ContextVar divergence. No per-file boilerplate. Tests pass in any collection order.

---

## Tests First (TDD)

**SKIPPED:** This is a pure refactoring task. The existing 119 tests across the 3 files ARE the test suite. No new tests needed — all 119 must pass after the refactoring with zero regressions.

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Loading approach | Module-level (NOT fixtures) | Fixtures run too late — test files do `from X import Y` at collection time, which requires modules already in `sys.modules`. Module-level conftest code runs before collection. |
| Module loading strategy | `_load_module_once()` with `sys.modules` guard | Prevents the unconditional overwrite that caused ContextVar divergence (S338 root cause) |
| Import style in test files | `import governance_layer` + `from governance_layer import X` | Need both: `from` for convenient name access, bare `import` for module object (required by `monkeypatch.setattr(module, attr, ...)`) |
| w116 ContextVar rebind | KEEP as defensive code | The `monkeypatch.setattr(work_engine_mod, "check_ceremony_required", ...)` rebind prevents silent ContextVar divergence if module loading changes in future. Remove only after verified stable. |
| Regression scope | Full test suite, not just 3 files | conftest module-level loading affects all 17 test files that import governance modules. Must verify no breakage in untouched files. |
| `prior_session` fix | Already done | `get_prev_session()` in scaffold.py:365-390 already reads `.claude/session`. Verify at closure. |

### Architecture

The key insight is that conftest.py module-level code runs before test collection. We can load modules at module level in conftest.py (not as fixtures) so that `from governance_layer import X` in test files finds the correct module in `sys.modules`.

**conftest.py module-level loading:**
```python
# Ensure modules are in sys.modules BEFORE test files import them
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(_root / ".claude" / "haios" / "lib"))

# Load in dependency order (governance_layer first)
_load_module_once("governance_layer",
    _root / ".claude" / "haios" / "modules" / "governance_layer.py")
_load_module_once("work_engine",
    _root / ".claude" / "haios" / "modules" / "work_engine.py")
_load_module_once("queue_ceremonies",
    _root / ".claude" / "haios" / "lib" / "queue_ceremonies.py")
```

Then each test file simply does:
```python
from governance_layer import GovernanceLayer, ceremony_context, ...
from work_engine import WorkEngine, WorkState, ...
from queue_ceremonies import execute_queue_transition, ...
```

No `_load_module`, no `_ensure_module`, no `_get_gov_mod()`, no per-file `sys.path.insert`.

### Changes Per File

**1. tests/conftest.py** — Add module loading infrastructure:
- Add `_load_module_once()` function
- Add `sys.path.insert` for modules and lib dirs
- Load governance_layer, work_engine, queue_ceremonies at module level
- Keep existing (empty) fixtures

**2. tests/test_work_engine.py** — Remove boilerplate:
- Remove lines 24-50: `sys.path.insert`, `_load_module` function, module loading calls
- Replace with: `from governance_layer import GovernanceLayer` and `from work_engine import WorkEngine, WorkState, ...`
- Remove the `_load_module` call inside `test_batch_design_three_items_integration` (line 1574-1575) for cycle_runner — add cycle_runner to conftest loading
- Keep all 57+ tests unchanged

**3. tests/test_queue_ceremonies.py** — Remove boilerplate:
- Remove lines 17-54: `sys.path.insert`, `_load_module` function, conditional loading
- Replace with: `from governance_layer import GovernanceLayer` and `from work_engine import WorkEngine` and `from queue_ceremonies import ...`
- Keep all 12 tests unchanged

**4. tests/test_ceremony_context.py** — Remove boilerplate and workarounds:
- Remove lines 18-20: `sys.path.insert`
- Remove lines 262-298: `_ensure_module`, `_root` redefinition, redundant module loading
- Remove `_get_gov_mod()` function entirely
- **MUST** add `import governance_layer` (module reference) at top of file — needed for `monkeypatch.setattr(governance_layer, ...)` in Tests 6, 11-14. `from governance_layer import X` only brings names, not the module object.
- Add `import work_engine as work_engine_mod` for w116 fixtures
- Add `import queue_ceremonies` for w116 fixtures
- Replace all `_get_gov_mod()` references with `governance_layer` (the module from import)
- **w116_patch_events rebind strategy:** KEEP the `monkeypatch.setattr(work_engine_mod, "check_ceremony_required", governance_layer.check_ceremony_required)` line as defensive code with a comment: `# Defensive: ensures shared ContextVar even if module loading changes. Can remove after WORK-117 verified stable.` This prevents silent ContextVar divergence reintroduction.
- Update `w116_engine` fixture: replace `work_engine_mod.WorkEngine(governance=_get_gov_mod().GovernanceLayer(), ...)` with `work_engine.WorkEngine(governance=governance_layer.GovernanceLayer(), ...)`
- Keep all 18 tests unchanged

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| conftest.py already has content | Extend existing file, preserve `import pytest` and TODOs | Manual verification |
| Test collection order varies | Module-level loading in conftest runs before all test files | Full suite run |
| cycle_runner module (used in 1 test) | Add to conftest loading | test_batch_design_three_items_integration |
| `_get_gov_mod()` runtime resolution | Replace with direct `governance_layer` module reference since conftest guarantees single instance | w116 tests |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | All decisions resolved in design phase |

---

## Implementation Steps

### Step 1: Update tests/conftest.py with module loading infrastructure
- [ ] Add `_load_module_once()` function
- [ ] Add `sys.path.insert` for modules and lib directories
- [ ] Load governance_layer, work_engine, queue_ceremonies, cycle_runner at module level
- [ ] Verify conftest.py loads without error

### Step 2: Update test_work_engine.py — remove per-file loading
- [ ] Remove `_load_module` function and module-level loading (lines 24-50)
- [ ] Replace with `from` imports
- [ ] Remove inline `_load_module` in integration test (line 1574-1575)
- [ ] Verify all 57+ tests still pass

### Step 3: Update test_queue_ceremonies.py — remove per-file loading
- [ ] Remove `_load_module` function and module-level loading (lines 17-54)
- [ ] Replace with `from` imports
- [ ] Verify all 12 tests still pass

### Step 4: Update test_ceremony_context.py — remove workarounds
- [ ] Remove `sys.path.insert` (lines 18-20)
- [ ] Remove `_ensure_module`, `_get_gov_mod()`, redundant `_root` (lines 262-298)
- [ ] Replace `_get_gov_mod()` calls with `governance_layer` module reference
- [ ] Update `w116_engine` and `w116_patch_events` fixtures
- [ ] Verify all 18 tests still pass

### Step 5: Full regression verification
- [ ] Run all 3 target files together: `pytest tests/test_work_engine.py tests/test_queue_ceremonies.py tests/test_ceremony_context.py -v`
- [ ] Verify all tests in target files pass
- [ ] Run full test suite: `pytest tests/ -v` to verify no breakage in the 14+ other files that also import governance modules (conftest module-level loading changes their runtime behavior)
- [ ] Record actual test counts at implementation time (do not hardcode 119)

### Step 6: Consumer Verification
- [ ] Grep for `_load_module` in tests/ — should only remain in files NOT targeted by this work
- [ ] Grep for `_ensure_module` — should be zero
- [ ] Grep for `_get_gov_mod` — should be zero

---

## Verification

- [ ] 119 tests pass across all 3 target files
- [ ] No `_load_module` in the 3 target files
- [ ] No `_ensure_module` anywhere
- [ ] No `_get_gov_mod` anywhere
- [ ] conftest.py has module loading infrastructure

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Module loading order in conftest vs test file `from` imports | High — could break all tests | conftest module-level code runs before test collection |
| Other test files using `_load_module` break | Med | Only modifying 3 target files; other files untouched |
| `monkeypatch.setattr` targets change with module refactoring | Med | Verify all `monkeypatch.setattr("governance_layer.X", ...)` still works |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-117/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Create `tests/conftest.py` with session-scoped fixtures | [ ] | Read conftest.py, verify module loading |
| Update `test_work_engine.py` to use conftest | [ ] | No `_load_module` in file |
| Update `test_queue_ceremonies.py` to use conftest | [ ] | No `_load_module` in file |
| Update `test_ceremony_context.py`, remove workarounds | [ ] | No `_ensure_module` / `_get_gov_mod()` |
| All existing tests pass with no regressions | [ ] | pytest output: 119 passed |
| Fix checkpoint scaffold `prior_session` auto-detection | [ ] | Already done in scaffold.py:365-390 |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `tests/conftest.py` | `_load_module_once()` + module-level loading | [ ] | |
| `tests/test_work_engine.py` | No `_load_module`, uses `from` imports | [ ] | |
| `tests/test_queue_ceremonies.py` | No `_load_module`, uses `from` imports | [ ] | |
| `tests/test_ceremony_context.py` | No `_ensure_module`/`_get_gov_mod`, uses `from` imports | [ ] | |

**Verification Commands:**
```bash
# Target files regression
pytest tests/test_work_engine.py tests/test_queue_ceremonies.py tests/test_ceremony_context.py -v
# Full suite regression (other files affected by conftest module loading)
pytest tests/ -v --tb=short
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (119/119)
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (conftest.py is consumed by pytest automatically)
- [ ] WHY captured (reasoning stored to memory)
- [ ] No READMEs needed (no directory structure change)
- [ ] Consumer verification: zero stale `_load_module` / `_ensure_module` / `_get_gov_mod` in target files

---

## References

- @docs/work/active/WORK-116/observations.md (root cause analysis)
- @docs/work/active/WORK-117/WORK.md (work item)
- S338 WORK-116 learnings in MEMORY.md (test module loading patterns)
