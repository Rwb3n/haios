---
template: implementation_plan
status: complete
date: 2026-01-08
backlog_id: E2-279
title: WorkEngine Decomposition
author: Hephaestus
lifecycle_phase: plan
session: 185
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-09T22:13:38'
---
# Implementation Plan: WorkEngine Decomposition

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

Decompose the 1197-line WorkEngine module into 5 atomic modules (each ≤300 lines), satisfying ADR-041 svelte governance criteria while maintaining backward compatibility for all existing consumers.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 6 | work_engine.py, cli.py, __init__.py, post_tool_use.py, context_loader.py, cycle_runner.py |
| Lines of code affected | 1197 | `wc -l .claude/haios/modules/work_engine.py` |
| New files to create | 4 | cascade_engine.py, portal_manager.py, spawn_tree.py, backfill_engine.py |
| Tests to write | 4 | One per new module (imports + basic function) |
| Dependencies | 5 | cli.py, __init__.py, post_tool_use.py, context_loader.py, test_work_engine.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | 5 consumers need import updates |
| Risk of regression | Low | Existing test_work_engine.py covers core functionality |
| External dependencies | Low | No external APIs, pure Python refactor |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Extract CascadeEngine | 30 min | High |
| Extract PortalManager | 30 min | High |
| Extract SpawnTree | 20 min | High |
| Extract BackfillEngine | 20 min | High |
| Update consumers + __init__.py | 20 min | High |
| Write tests + verify | 30 min | High |
| **Total** | ~2.5 hrs | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/work_engine.py - 1197 lines, 5 responsibility clusters
class WorkEngine:
    # Core CRUD: get_work, create_work, transition, get_ready, close, archive (lines 99-335)
    # Portal System: _create_portal, _update_portal, link_spawned_items (lines 405-567)
    # Cascade: cascade, _get_unblocked_items, _get_related_items, etc. (lines 626-913)
    # Spawn Tree: spawn_tree, _find_children, format_tree (lines 914-1031)
    # Backfill: backfill, backfill_all, _parse_backlog_entry, etc. (lines 1032-1197)
```

**Behavior:** Single monolithic class owns 5 distinct responsibility areas.

**Result:** Violates ADR-041 svelte criteria (max 300 lines, max 1 responsibility).

### Desired State

```python
# .claude/haios/modules/ - 5 atomic modules

# work_engine.py (~300 lines) - Core CRUD only
class WorkEngine:
    def get_work, create_work, transition, get_ready, close, archive
    # Delegates to CascadeEngine, PortalManager for specialized operations

# cascade_engine.py (~290 lines) - Completion cascade
class CascadeEngine:
    def cascade, _get_unblocked_items, _get_related_items, _get_milestone_delta, etc.

# portal_manager.py (~200 lines) - Portal CRUD
class PortalManager:
    def create_portal, update_portal, link_spawned_items, add_memory_refs_to_portal

# spawn_tree.py (~100 lines) - Tree traversal
class SpawnTree:
    def spawn_tree, _find_children, format_tree

# backfill_engine.py (~160 lines) - Backlog parsing
class BackfillEngine:
    def backfill, backfill_all, _parse_backlog_entry, _update_work_file_content
```

**Behavior:** Each module owns exactly one responsibility, under 300 lines.

**Result:** Satisfies ADR-041 svelte governance criteria.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: CascadeEngine Import and Basic Function
```python
def test_cascade_engine_imports():
    """CascadeEngine can be imported from modules package."""
    from .claude.haios.modules import CascadeEngine
    assert CascadeEngine is not None

def test_cascade_engine_cascade_returns_result():
    """CascadeEngine.cascade returns CascadeResult."""
    engine = CascadeEngine(work_engine=mock_work_engine, base_path=tmp_path)
    result = engine.cascade("E2-001", "complete")
    assert isinstance(result, CascadeResult)
```

### Test 2: PortalManager Import and Basic Function
```python
def test_portal_manager_imports():
    """PortalManager can be imported from modules package."""
    from .claude.haios.modules import PortalManager
    assert PortalManager is not None

def test_portal_manager_creates_portal():
    """PortalManager.create_portal creates REFS.md."""
    manager = PortalManager(base_path=tmp_path)
    manager.create_portal("E2-001", refs_path)
    assert refs_path.exists()
```

### Test 3: SpawnTree Import and Basic Function
```python
def test_spawn_tree_imports():
    """SpawnTree can be imported from modules package."""
    from .claude.haios.modules import SpawnTree
    assert SpawnTree is not None

def test_spawn_tree_returns_tree():
    """SpawnTree.spawn_tree returns nested dict."""
    tree = SpawnTree(base_path=tmp_path)
    result = tree.spawn_tree("E2-001")
    assert "E2-001" in result
```

### Test 4: BackfillEngine Import and Basic Function
```python
def test_backfill_engine_imports():
    """BackfillEngine can be imported from modules package."""
    from .claude.haios.modules import BackfillEngine
    assert BackfillEngine is not None

def test_backfill_engine_backfill_updates_file():
    """BackfillEngine.backfill updates work file from backlog."""
    engine = BackfillEngine(work_engine=mock_work_engine, base_path=tmp_path)
    result = engine.backfill("E2-001")
    assert isinstance(result, bool)
```

### Test 5: Backward Compatibility - Existing Tests Pass
```python
def test_existing_work_engine_tests_pass():
    """All existing tests in test_work_engine.py still pass."""
    # Run: pytest tests/test_work_engine.py -v
    # Expected: All ~40 tests pass
    # This ensures decomposition doesn't break existing functionality
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Pattern Verification (E2-255)

**Sibling Module Pattern (from cycle_runner.py lines 38-52):**
```python
# Import sibling modules
# Use conditional import to support both package and standalone usage (E2-255 pattern)
try:
    from .governance_layer import GovernanceLayer, GateResult
except ImportError:
    from governance_layer import GovernanceLayer, GateResult

# Import event logging from lib
import sys
_lib_path = Path(__file__).parent.parent.parent / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))
```

**All new modules MUST use this pattern.**

### Module 1: CascadeEngine

**File:** `.claude/haios/modules/cascade_engine.py` (NEW)
**Lines extracted from:** work_engine.py lines 626-913

```python
"""
CascadeEngine Module (E2-279)

Stateless cascade manager for work item completion effects. Provides:
- cascade(id, status): Run cascade for completed item
- Unblock dependents, notify related, track milestone

L4 Invariants:
- MUST NOT modify work files directly (uses WorkEngine)
- MUST emit cascade events to haios-events.jsonl
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Import sibling modules (E2-255 pattern)
try:
    from .work_engine import WorkEngine, WorkState, TRIGGER_STATUSES
except ImportError:
    from work_engine import WorkEngine, WorkState, TRIGGER_STATUSES

@dataclass
class CascadeResult:
    """Result of cascade operation."""
    unblocked: List[str] = field(default_factory=list)
    still_blocked: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    milestone_delta: Optional[int] = None
    substantive_refs: List[str] = field(default_factory=list)
    message: str = ""

class CascadeEngine:
    def __init__(self, work_engine: WorkEngine, base_path: Optional[Path] = None):
        self._work_engine = work_engine
        self._base_path = base_path or Path(".")

    def cascade(self, id: str, new_status: str, dry_run: bool = False) -> CascadeResult:
        # Extract lines 630-676 from work_engine.py
        ...

    def _get_unblocked_items(self, completed_id: str) -> tuple[List[str], List[str]]:
        # Extract lines 678-721
        ...

    # Additional methods: _is_item_complete, _get_related_items,
    # _get_milestone_delta, _get_substantive_refs, _format_cascade_message,
    # _write_cascade_event
```

### Module 2: PortalManager

**File:** `.claude/haios/modules/portal_manager.py` (NEW)
**Lines extracted from:** work_engine.py lines 405-567

```python
"""
PortalManager Module (E2-279)

Portal (references/REFS.md) management for work items. Provides:
- create_portal(id): Create REFS.md for new work item
- update_portal(id, updates): Add spawned_from, memory_refs, ADRs
- link_spawned_items(parent, children): Link multiple items

L4 Invariants:
- Owns REFS.md files (single writer)
- Works with WorkEngine for work item metadata
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

ACTIVE_DIR = Path("docs/work/active")

class PortalManager:
    def __init__(self, base_path: Optional[Path] = None):
        self._base_path = base_path or Path(".")

    @property
    def active_dir(self) -> Path:
        return self._base_path / ACTIVE_DIR

    def create_portal(self, id: str, refs_path: Path) -> None:
        # Extract lines 409-441 from work_engine.py
        ...

    def update_portal(self, id: str, updates: Dict[str, Any]) -> None:
        # Extract lines 443-517
        ...

    def link_spawned_items(self, spawned_by: str, ids: List[str],
                          milestone: Optional[str] = None) -> Dict[str, List[str]]:
        # Extract lines 519-566
        ...
```

### Module 3: SpawnTree

**File:** `.claude/haios/modules/spawn_tree.py` (NEW)
**Lines extracted from:** work_engine.py lines 914-1031

```python
"""
SpawnTree Module (E2-279)

Spawn tree traversal and formatting. Provides:
- spawn_tree(root_id): Build nested spawn tree
- format_tree(tree): Format as ASCII art

Stateless utility - no persistent state.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

ACTIVE_DIR = Path("docs/work/active")
ARCHIVE_DIR = Path("docs/work/archive")

class SpawnTree:
    def __init__(self, base_path: Optional[Path] = None):
        self._base_path = base_path or Path(".")

    def spawn_tree(self, root_id: str, max_depth: int = 5) -> Dict[str, Any]:
        # Extract lines 918-941 from work_engine.py
        ...

    def _find_children(self, parent_id: str) -> List[str]:
        # Extract lines 943-992
        ...

    @staticmethod
    def format_tree(tree: Dict[str, Any], use_ascii: bool = False) -> str:
        # Extract lines 994-1030
        ...
```

### Module 4: BackfillEngine

**File:** `.claude/haios/modules/backfill_engine.py` (NEW)
**Lines extracted from:** work_engine.py lines 1032-1197

```python
"""
BackfillEngine Module (E2-279)

Backlog content backfill for work items. Provides:
- backfill(id): Backfill single work item from backlog.md
- backfill_all(): Backfill all active work items

L4 Invariants:
- MUST NOT create new work items (uses WorkEngine.get_work to find)
- MUST write updates via WorkEngine pattern (direct file write ok since no state)
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import yaml

# Import sibling modules (E2-255 pattern)
try:
    from .work_engine import WorkEngine
except ImportError:
    from work_engine import WorkEngine

class BackfillEngine:
    def __init__(self, work_engine: WorkEngine, base_path: Optional[Path] = None):
        self._work_engine = work_engine
        self._base_path = base_path or Path(".")

    def backfill(self, id: str, force: bool = False) -> bool:
        # Extract lines 1036-1074 from work_engine.py
        ...

    def backfill_all(self, force: bool = False) -> Dict[str, List[str]]:
        # Extract lines 1076-1108
        ...

    def _parse_backlog_entry(self, backlog_id: str, content: str) -> Optional[Dict[str, Any]]:
        # Extract lines 1110-1157
        ...

    def _update_work_file_content(self, content: str, parsed: Dict[str, Any],
                                  force: bool) -> str:
        # Extract lines 1159-1197
        ...
```

### Module 5: WorkEngine (Refactored)

**File:** `.claude/haios/modules/work_engine.py` (MODIFIED)
**Target:** ~300 lines (down from 1197)

**Changes:**
1. Remove cascade methods (lines 626-913) → delegate to CascadeEngine
2. Remove portal methods (lines 405-567) → delegate to PortalManager
3. Remove spawn tree methods (lines 914-1031) → delegate to SpawnTree
4. Remove backfill methods (lines 1032-1197) → delegate to BackfillEngine
5. Keep: Core CRUD, transition, get_ready, close, archive
6. Add: Optional injected dependencies for backward compatibility

```python
class WorkEngine:
    def __init__(
        self,
        governance: GovernanceLayer,
        memory: Optional[Any] = None,
        base_path: Optional[Path] = None,
        # NEW: Optional injected dependencies for backward compat
        cascade_engine: Optional["CascadeEngine"] = None,
        portal_manager: Optional["PortalManager"] = None,
        spawn_tree: Optional["SpawnTree"] = None,
        backfill_engine: Optional["BackfillEngine"] = None,
    ):
        self._governance = governance
        self._memory = memory
        self._base_path = base_path or Path(".")
        # Lazy instantiation for backward compatibility
        self._cascade = cascade_engine
        self._portal = portal_manager
        self._spawn = spawn_tree
        self._backfill = backfill_engine

    # Delegation methods for backward compatibility
    def cascade(self, id: str, new_status: str, dry_run: bool = False) -> "CascadeResult":
        """Delegate to CascadeEngine."""
        if self._cascade is None:
            from .cascade_engine import CascadeEngine
            self._cascade = CascadeEngine(work_engine=self, base_path=self._base_path)
        return self._cascade.cascade(id, new_status, dry_run)

    # Similar delegation for portal_manager, spawn_tree, backfill_engine
```

### Call Chain Context

```
cli.py / post_tool_use.py / context_loader.py
    |
    +-> WorkEngine (refactored core)
            |
            +-> cascade() --> CascadeEngine
            |
            +-> _create_portal() --> PortalManager
            |
            +-> spawn_tree() --> SpawnTree
            |
            +-> backfill() --> BackfillEngine
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Lazy instantiation | Modules created on first use | Backward compatibility: `WorkEngine.cascade()` still works |
| CascadeResult stays in cascade_engine | Moved with cascade logic | Keeps related code together |
| TRIGGER_STATUSES stays in work_engine | Core constant | Used by both WorkEngine.close() and CascadeEngine |
| No circular imports | CascadeEngine imports WorkEngine, not vice versa | WorkEngine is the hub, others are satellites |
| PortalManager is standalone | No WorkEngine dependency | Only needs base_path for file operations |

### Consumer Updates

**__init__.py changes:**
```python
from .work_engine import WorkEngine, WorkState, InvalidTransitionError, WorkNotFoundError
from .cascade_engine import CascadeEngine, CascadeResult  # NEW
from .portal_manager import PortalManager  # NEW
from .spawn_tree import SpawnTree  # NEW
from .backfill_engine import BackfillEngine  # NEW

__all__ = [
    "WorkEngine", "WorkState", "InvalidTransitionError", "WorkNotFoundError",
    "CascadeEngine", "CascadeResult",  # NEW
    "PortalManager",  # NEW
    "SpawnTree",  # NEW
    "BackfillEngine",  # NEW
    ...
]
```

**cli.py changes (if needed):**
```python
# SpawnTree direct import for `just spawns` command
from spawn_tree import SpawnTree
# Line 137: WorkEngine.format_tree → SpawnTree.format_tree
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Old code calls WorkEngine.cascade() | Lazy delegation to CascadeEngine | Test 5 backward compat |
| CascadeEngine.cascade() with non-existent ID | Returns empty CascadeResult | Test 1 |
| PortalManager.create_portal() on existing | Overwrites (idempotent) | Test 2 |

### Open Questions

**Q: Should CascadeResult move to its own file or stay with CascadeEngine?**

Keep with CascadeEngine - it's only used by cascade operations. Moving would add unnecessary import complexity.

**Q: Should TRIGGER_STATUSES be duplicated or imported?**

Keep in work_engine.py and import into cascade_engine.py. Single source of truth.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No operator_decisions in work item frontmatter |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_decomposition.py` with tests from Tests First section
- [ ] Verify import tests fail (modules don't exist yet)

### Step 2: Extract CascadeEngine
- [ ] Create `.claude/haios/modules/cascade_engine.py`
- [ ] Copy lines 626-913 from work_engine.py
- [ ] Move CascadeResult dataclass to cascade_engine.py
- [ ] Add E2-255 import pattern
- [ ] Test 1 passes (CascadeEngine import + cascade function)

### Step 3: Extract PortalManager
- [ ] Create `.claude/haios/modules/portal_manager.py`
- [ ] Extract _create_portal, _update_portal, link_spawned_items (lines 405-567)
- [ ] Test 2 passes (PortalManager import + create_portal)

### Step 4: Extract SpawnTree
- [ ] Create `.claude/haios/modules/spawn_tree.py`
- [ ] Extract spawn_tree, _find_children, format_tree (lines 914-1031)
- [ ] Test 3 passes (SpawnTree import + spawn_tree)

### Step 5: Extract BackfillEngine
- [ ] Create `.claude/haios/modules/backfill_engine.py`
- [ ] Extract backfill, backfill_all, _parse_backlog_entry, _update_work_file_content (lines 1032-1197)
- [ ] Test 4 passes (BackfillEngine import + backfill)

### Step 6: Refactor WorkEngine Core
- [ ] Remove extracted methods from work_engine.py
- [ ] Add lazy delegation methods for backward compatibility
- [ ] Add optional dependency injection parameters
- [ ] Verify work_engine.py is ~300 lines
- [ ] Run existing test_work_engine.py tests - all pass (Test 5)

### Step 7: Update __init__.py
- [ ] Add new module exports to `.claude/haios/modules/__init__.py`
- [ ] Verify all modules importable from package

### Step 8: Consumer Verification (MUST)
- [ ] **MUST:** `Grep(pattern="WorkEngine.cascade|WorkEngine.format_tree")` - verify delegation works
- [ ] **MUST:** Update cli.py line 137 if needed (format_tree)
- [ ] **MUST:** Verify post_tool_use.py still works (uses WorkEngine)

### Step 9: Full Test Suite
- [ ] Run `pytest tests/test_work_engine.py -v` - all ~40 tests pass
- [ ] Run `pytest tests/test_decomposition.py -v` - all 5 tests pass
- [ ] Run `pytest tests/ -v` - full suite passes

### Step 10: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new modules
- [ ] **MUST:** Verify module descriptions and line counts are accurate

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular import between CascadeEngine and WorkEngine | High | CascadeEngine imports WorkEngine; WorkEngine uses lazy import for CascadeEngine |
| Existing tests break due to moved methods | Medium | Keep WorkEngine delegation methods for backward compat |
| cli.py format_tree call breaks | Medium | Check cli.py line 137, update to use SpawnTree.format_tree |
| post_tool_use.py WorkEngine call breaks | Medium | Verify hook still works - only imports WorkEngine, uses cascade() |
| Module line counts exceed 300 | Low | Track during extraction; refactor further if needed |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cascade_engine.py` | CascadeEngine class, cascade() method | [ ] | |
| `.claude/haios/modules/portal_manager.py` | PortalManager class, create_portal() method | [ ] | |
| `.claude/haios/modules/spawn_tree.py` | SpawnTree class, spawn_tree() method | [ ] | |
| `.claude/haios/modules/backfill_engine.py` | BackfillEngine class, backfill() method | [ ] | |
| `.claude/haios/modules/work_engine.py` | ~300 lines, delegation methods present | [ ] | |
| `.claude/haios/modules/__init__.py` | All 4 new modules exported | [ ] | |
| `.claude/haios/modules/README.md` | Documents all 9 modules | [ ] | |
| `tests/test_decomposition.py` | Tests for new modules exist | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
wc -l .claude/haios/modules/work_engine.py
# Expected: ~300 lines

pytest tests/test_work_engine.py -v
# Expected: ~40 tests passed

pytest tests/test_decomposition.py -v
# Expected: 5 tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- **ADR-041:** Svelte Governance Criteria (defines targets: max 300 lines, single responsibility)
- **INV-061:** Svelte Governance Architecture investigation (source of decomposition design)
- **E2-255:** Sibling module import pattern (try/except conditional imports)
- **S17:** Modular Architecture (Chariot modules)
- **S20:** Pressure Dynamics (breath mapping for modules)

---
