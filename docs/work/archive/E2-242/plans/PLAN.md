---
template: implementation_plan
status: complete
date: 2026-01-03
backlog_id: E2-242
title: Implement WorkEngine Module
author: Hephaestus
lifecycle_phase: plan
session: 161
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-03T18:09:16'
---
# Implementation Plan: Implement WorkEngine Module

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

Create a stateless WorkEngine module that owns WORK.md files with typed interfaces for get/create/transition/ready/archive operations, integrating GovernanceLayer for transition validation and MemoryBridge for auto-linking.

**L4 Requirements (from L4-implementation.md):**
| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_work(id)` | Work ID | WorkState object | Returns parsed WORK.md |
| `create_work(id, title, ...)` | Work item data | Created file path | Creates directory + WORK.md |
| `transition(id, to_node)` | Work ID + target node | Updated WorkState | Updates current_node, appends node_history |
| `get_ready()` | None | List of unblocked items | Returns items where blocked_by is empty |
| `archive(id)` | Work ID | Archived path | Moves to docs/work/archive/ |

**L4 Invariants:**
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | New module (strangler fig) |
| Lines of code affected | ~0 | New code only |
| New files to create | 2 | `.claude/haios/modules/work_engine.py`, `tests/test_work_engine.py` |
| Tests to write | 12 | 5 functions x 2-3 tests + edge cases |
| Dependencies | 3 | GovernanceLayer, MemoryBridge, existing work_item.py logic |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | High | GovernanceLayer (transition validation), MemoryBridge (auto-link callback) |
| Risk of regression | Low | Strangler fig - new module, existing consumers untouched |
| External dependencies | Low | File system only, no external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests (RED) | 25 min | High |
| Implementation (GREEN) | 45 min | High |
| Integration verification | 15 min | High |
| Docs & README | 10 min | High |
| **Total** | ~1.5 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/work_item.py - Current implementation
def find_work_file(backlog_id: str) -> Optional[Path]:
    """Find work file for a backlog ID."""
    dir_path = ACTIVE_DIR / backlog_id / "WORK.md"
    if dir_path.exists():
        return dir_path
    # Fall back to flat file pattern
    pattern = f"WORK-{backlog_id}-*.md"
    matches = list(ACTIVE_DIR.glob(pattern))
    return matches[0] if matches else None

def update_node(path: Path, new_node: str) -> None:
    """Update work file to new DAG node with history tracking."""
    # Direct file manipulation without validation
    ...

def move_work_file_to_archive(path: Path) -> Path:
    """Move work file from active/ to archive/."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    new_path = ARCHIVE_DIR / path.name
    path.rename(new_path)
    return new_path
```

**Behavior:** Functions scattered across work_item.py with no:
- GovernanceLayer validation for transitions
- Typed return objects (uses Path/None)
- MemoryBridge integration for auto-linking
- Central ownership of WORK.md writes

**Result:** No module boundary, no integration with other Chariot modules, direct file access without validation.

### Desired State

```python
# .claude/haios/modules/work_engine.py - Target implementation
@dataclass
class WorkState:
    """Typed work item state."""
    id: str
    title: str
    status: str
    current_node: str
    blocked_by: List[str]
    node_history: List[Dict]
    memory_refs: List[int]
    path: Path

class WorkEngine:
    def __init__(self, governance: GovernanceLayer, memory: Optional[MemoryBridge] = None):
        self._governance = governance
        self._memory = memory

    def get_work(self, id: str) -> Optional[WorkState]:
        """Returns parsed WORK.md as typed object."""
        ...

    def transition(self, id: str, to_node: str) -> WorkState:
        """Validates via GovernanceLayer, updates node_history with timestamp."""
        if not self._governance.validate_transition(current_node, to_node):
            raise InvalidTransitionError(...)
        ...

    def get_ready(self) -> List[WorkState]:
        """Returns items where blocked_by is empty."""
        ...
```

**Behavior:** Central module that:
- Owns all WORK.md writes
- Validates transitions via GovernanceLayer
- Returns typed WorkState objects
- Integrates MemoryBridge for auto-linking

**Result:** Clean module boundary, typed interfaces, integrated validation.

---

## Tests First (TDD)

### Test 1: get_work returns WorkState for existing item
```python
def test_get_work_returns_work_state(tmp_path, engine):
    # Setup: Create WORK.md in docs/work/active/E2-TEST/
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_MD)

    # Action
    result = engine.get_work("E2-TEST")

    # Assert
    assert result is not None
    assert result.id == "E2-TEST"
    assert result.current_node == "backlog"
    assert isinstance(result.blocked_by, list)
```

### Test 2: get_work returns None for missing item
```python
def test_get_work_returns_none_for_missing(engine):
    result = engine.get_work("NONEXISTENT-123")
    assert result is None
```

### Test 3: transition validates via GovernanceLayer
```python
def test_transition_validates_via_governance(tmp_path, mock_governance):
    mock_governance.validate_transition.return_value = False
    engine = WorkEngine(governance=mock_governance)

    with pytest.raises(InvalidTransitionError):
        engine.transition("E2-TEST", "complete")

    mock_governance.validate_transition.assert_called_once()
```

### Test 4: transition updates node_history with timestamp
```python
def test_transition_updates_node_history(tmp_path, engine):
    # Setup: Create work item at 'backlog' node
    ...
    # Action
    result = engine.transition("E2-TEST", "plan")

    # Assert
    assert result.current_node == "plan"
    assert len(result.node_history) == 2  # backlog + plan
    assert result.node_history[-1]["node"] == "plan"
    assert result.node_history[-1]["entered"] is not None
    assert result.node_history[-2]["exited"] is not None
```

### Test 5: get_ready returns unblocked items only
```python
def test_get_ready_returns_unblocked_only(tmp_path, engine):
    # Setup: Create 3 items - 2 blocked, 1 unblocked
    ...
    result = engine.get_ready()

    assert len(result) == 1
    assert result[0].id == "E2-UNBLOCKED"
    assert result[0].blocked_by == []
```

### Test 6: create_work creates directory and WORK.md
```python
def test_create_work_creates_directory_structure(tmp_path, engine):
    result = engine.create_work(
        id="E2-NEW",
        title="New Work Item",
        milestone="M7b-WorkInfra"
    )

    assert result.exists()
    assert result.name == "WORK.md"
    assert result.parent.name == "E2-NEW"
```

### Test 7: archive moves to archive directory
```python
def test_archive_moves_to_archive_dir(tmp_path, engine):
    # Setup: Create active work item
    ...
    result = engine.archive("E2-TEST")

    assert "archive" in str(result)
    assert not (tmp_path / "docs/work/active/E2-TEST").exists()
    assert (tmp_path / "docs/work/archive/E2-TEST/WORK.md").exists()
```

### Test 8: add_memory_refs calls MemoryBridge auto_link
```python
def test_add_memory_refs_calls_memory_bridge(tmp_path, mock_memory):
    engine = WorkEngine(governance=GovernanceLayer(), memory=mock_memory)
    engine.add_memory_refs("E2-TEST", [80534, 80535])

    mock_memory.auto_link.assert_called_once_with("E2-TEST", [80534, 80535])
```

### Test 9: L4 Invariant - only writer to WORK.md
```python
def test_work_engine_is_only_writer(tmp_path, engine):
    """Verify WorkEngine owns WORK.md writes (no direct file access)."""
    work = engine.get_work("E2-TEST")
    original_content = work.path.read_text()

    # Transition should modify file
    engine.transition("E2-TEST", "plan")
    new_content = work.path.read_text()

    assert original_content != new_content
    assert "plan" in new_content
```

### Test 10: transition blocks invalid DAG transitions
```python
def test_transition_blocks_invalid_dag_path(tmp_path, engine):
    # Setup: Work item at 'backlog' node
    # Try to skip to 'complete' (invalid: backlog -> complete)
    with pytest.raises(InvalidTransitionError, match="Invalid transition"):
        engine.transition("E2-TEST", "complete")
```

### Test 11: archive preserves directory structure
```python
def test_archive_preserves_subdirectories(tmp_path, engine):
    # Setup: Create work item with plans/ subdirectory
    ...
    engine.archive("E2-TEST")

    archive_path = tmp_path / "docs/work/archive/E2-TEST"
    assert (archive_path / "WORK.md").exists()
    assert (archive_path / "plans").exists()
```

### Test 12: get_ready excludes archived items
```python
def test_get_ready_excludes_archived(tmp_path, engine):
    # Setup: 1 active unblocked, 1 archived unblocked
    ...
    result = engine.get_ready()

    assert len(result) == 1
    assert all("archive" not in str(w.path) for w in result)
```

---

## Detailed Design

### New File: `.claude/haios/modules/work_engine.py`

**File:** `.claude/haios/modules/work_engine.py` (NEW)

```python
"""
WorkEngine Module (E2-242)

Stateless owner of WORK.md files. Provides:
- get_work(id): Parse WORK.md into WorkState
- create_work(id, title, ...): Create new work item directory
- transition(id, to_node): Validate and execute DAG transition
- get_ready(): List unblocked work items
- archive(id): Move to archive directory
- add_memory_refs(id, refs): Link concepts to work item

L4 Invariants:
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import shutil
import yaml

# Import sibling modules
from .governance_layer import GovernanceLayer

WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


class InvalidTransitionError(Exception):
    """Raised when a DAG transition is invalid."""
    pass


class WorkNotFoundError(Exception):
    """Raised when work item doesn't exist."""
    pass


@dataclass
class WorkState:
    """Typed work item state."""
    id: str
    title: str
    status: str
    current_node: str
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    path: Optional[Path] = None


class WorkEngine:
    """
    Stateless work item management module.

    Owns all WORK.md file operations, validates transitions via
    GovernanceLayer, and integrates with MemoryBridge for auto-linking.
    """

    def __init__(
        self,
        governance: GovernanceLayer,
        memory: Optional[Any] = None,  # MemoryBridge
        base_path: Optional[Path] = None,
    ):
        self._governance = governance
        self._memory = memory
        self._base_path = base_path or Path(".")

    @property
    def active_dir(self) -> Path:
        return self._base_path / ACTIVE_DIR

    @property
    def archive_dir(self) -> Path:
        return self._base_path / ARCHIVE_DIR

    def get_work(self, id: str) -> Optional[WorkState]:
        """
        Get work item by ID.

        Args:
            id: Work item ID (e.g., "E2-242")

        Returns:
            WorkState if found, None otherwise
        """
        path = self._find_work_file(id)
        if path is None:
            return None
        return self._parse_work_file(path)

    def create_work(
        self,
        id: str,
        title: str,
        milestone: Optional[str] = None,
        priority: str = "medium",
        category: str = "implementation",
    ) -> Path:
        """
        Create new work item with directory structure.

        Args:
            id: Work item ID
            title: Work item title
            milestone: Optional milestone assignment
            priority: Priority level (low, medium, high)
            category: Category (implementation, investigation, etc.)

        Returns:
            Path to created WORK.md
        """
        work_dir = self.active_dir / id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (work_dir / "plans").mkdir(exist_ok=True)

        # Generate WORK.md
        work_path = work_dir / "WORK.md"
        now = datetime.now()
        frontmatter = {
            "template": "work_item",
            "id": id,
            "title": title,
            "status": "active",
            "owner": "Hephaestus",
            "created": now.strftime("%Y-%m-%d"),
            "closed": None,
            "milestone": milestone,
            "priority": priority,
            "category": category,
            "blocked_by": [],
            "blocks": [],
            "current_node": "backlog",
            "node_history": [
                {"node": "backlog", "entered": now.isoformat(), "exited": None}
            ],
            "memory_refs": [],
            "documents": {"plans": [], "investigations": [], "checkpoints": []},
        }
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n# WORK-{id}: {title}\n"
        work_path.write_text(content, encoding="utf-8")
        return work_path

    def transition(self, id: str, to_node: str) -> WorkState:
        """
        Transition work item to new DAG node.

        Validates via GovernanceLayer, updates node_history with timestamps.

        Args:
            id: Work item ID
            to_node: Target node

        Returns:
            Updated WorkState

        Raises:
            WorkNotFoundError: If work item doesn't exist
            InvalidTransitionError: If transition is invalid
        """
        work = self.get_work(id)
        if work is None:
            raise WorkNotFoundError(f"Work item {id} not found")

        from_node = work.current_node

        # L4 Invariant: Validate transitions via GovernanceLayer
        if not self._governance.validate_transition(from_node, to_node):
            raise InvalidTransitionError(
                f"Invalid transition: {from_node} -> {to_node}"
            )

        # Update node_history
        now = datetime.now().isoformat()
        if work.node_history:
            work.node_history[-1]["exited"] = now
        work.node_history.append({"node": to_node, "entered": now, "exited": None})
        work.current_node = to_node

        # Write changes
        self._write_work_file(work)
        return work

    def get_ready(self) -> List[WorkState]:
        """
        Get all unblocked work items from active directory.

        Returns:
            List of WorkState with empty blocked_by
        """
        ready = []
        if not self.active_dir.exists():
            return ready

        for subdir in self.active_dir.iterdir():
            if subdir.is_dir():
                work_md = subdir / "WORK.md"
                if work_md.exists():
                    work = self._parse_work_file(work_md)
                    if work and not work.blocked_by:
                        ready.append(work)
        return ready

    def archive(self, id: str) -> Path:
        """
        Move work item to archive directory.

        Preserves entire directory structure (plans/, observations.md, etc.).

        Args:
            id: Work item ID

        Returns:
            Path to archived WORK.md

        Raises:
            WorkNotFoundError: If work item doesn't exist
        """
        source_dir = self.active_dir / id
        if not source_dir.exists():
            raise WorkNotFoundError(f"Work item {id} not found in active/")

        dest_dir = self.archive_dir / id
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Move entire directory (preserves plans/, etc.)
        shutil.move(str(source_dir), str(dest_dir))
        return dest_dir / "WORK.md"

    def add_memory_refs(self, id: str, concept_ids: List[int]) -> None:
        """
        Add memory references to work item.

        L4 Invariant: Calls MemoryBridge.auto_link after memory operations.

        Args:
            id: Work item ID
            concept_ids: List of concept IDs to link
        """
        work = self.get_work(id)
        if work is None:
            return

        # Extend memory_refs (dedup)
        existing = set(work.memory_refs)
        for cid in concept_ids:
            if cid not in existing:
                work.memory_refs.append(cid)

        self._write_work_file(work)

        # Call MemoryBridge if available
        if self._memory:
            self._memory.auto_link(id, concept_ids)

    def _find_work_file(self, id: str) -> Optional[Path]:
        """Find WORK.md for given ID."""
        # Directory structure (primary)
        dir_path = self.active_dir / id / "WORK.md"
        if dir_path.exists():
            return dir_path

        # Check archive
        archive_path = self.archive_dir / id / "WORK.md"
        if archive_path.exists():
            return archive_path

        return None

    def _parse_work_file(self, path: Path) -> Optional[WorkState]:
        """Parse WORK.md into WorkState."""
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        fm = yaml.safe_load(parts[1]) or {}
        return WorkState(
            id=fm.get("id", ""),
            title=fm.get("title", ""),
            status=fm.get("status", ""),
            current_node=fm.get("current_node", "backlog"),
            blocked_by=fm.get("blocked_by", []) or [],
            node_history=fm.get("node_history", []),
            memory_refs=fm.get("memory_refs", []) or [],
            path=path,
        )

    def _write_work_file(self, work: WorkState) -> None:
        """Write WorkState back to WORK.md."""
        if work.path is None:
            return

        content = work.path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        fm = yaml.safe_load(parts[1]) or {}
        fm["current_node"] = work.current_node
        fm["node_history"] = work.node_history
        fm["memory_refs"] = work.memory_refs
        fm["status"] = work.status

        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        work.path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")
```

### Call Chain Context

```
Consumers (node_cycle.py, close command, plan_tree.py)
    │
    ├──► WorkEngine.get_work(id)     # Read work item
    │        Returns: WorkState
    │
    ├──► WorkEngine.transition(id, node)  # DAG transition
    │        │
    │        └──► GovernanceLayer.validate_transition()
    │                 Returns: bool
    │
    ├──► WorkEngine.get_ready()      # Routing decisions
    │        Returns: List[WorkState]
    │
    └──► WorkEngine.add_memory_refs(id, refs)  # Auto-linking
             │
             └──► MemoryBridge.auto_link()
```

### Function/Component Signatures

```python
@dataclass
class WorkState:
    """Typed work item state from parsed WORK.md."""
    id: str
    title: str
    status: str
    current_node: str
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    path: Optional[Path] = None


class WorkEngine:
    def __init__(
        self,
        governance: GovernanceLayer,
        memory: Optional[MemoryBridge] = None,
        base_path: Optional[Path] = None,
    ): ...

    def get_work(self, id: str) -> Optional[WorkState]: ...
    def create_work(self, id: str, title: str, ...) -> Path: ...
    def transition(self, id: str, to_node: str) -> WorkState: ...
    def get_ready(self) -> List[WorkState]: ...
    def archive(self, id: str) -> Path: ...
    def add_memory_refs(self, id: str, concept_ids: List[int]) -> None: ...
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Stateless module | No internal state between calls | Matches GovernanceLayer/MemoryBridge pattern; any Claude can call WorkEngine |
| base_path injection | Allow custom paths | Enables tmp_path fixtures in tests without monkeypatching |
| Preserve directory on archive | shutil.move entire directory | Keeps plans/, observations.md intact during archival |
| Return WorkState from transition | Typed object after write | Consumers get fresh state without re-reading |
| Optional MemoryBridge | None-check before auto_link | Graceful degradation if memory unavailable |
| Strangler fig pattern | New module alongside work_item.py | No breaking changes; consumers migrate incrementally |

### Input/Output Examples

**get_work("E2-242"):**
```python
# Input: Work item ID
result = engine.get_work("E2-242")

# Output: WorkState object
WorkState(
    id="E2-242",
    title="Implement WorkEngine Module",
    status="active",
    current_node="backlog",
    blocked_by=["E2-240", "E2-241"],
    node_history=[{"node": "backlog", "entered": "2026-01-03T13:07:57", "exited": None}],
    memory_refs=[],
    path=Path("docs/work/active/E2-242/WORK.md")
)
```

**transition("E2-242", "plan"):**
```python
# Before: current_node="backlog"
result = engine.transition("E2-242", "plan")

# After: current_node="plan", node_history extended
result.current_node  # "plan"
result.node_history[-1]  # {"node": "plan", "entered": "2026-01-03T17:45:00", "exited": None}
result.node_history[-2]["exited"]  # "2026-01-03T17:45:00" (previous node marked exited)
```

**get_ready():**
```python
# Returns only unblocked items
ready = engine.get_ready()
# [WorkState(id="E2-017", blocked_by=[]), WorkState(id="E2-018", blocked_by=[]), ...]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item not found | Return None / raise WorkNotFoundError | Test 2, Test 10 |
| Invalid DAG transition | Raise InvalidTransitionError | Test 3, Test 10 |
| Empty blocked_by list in YAML (null) | Coerce to empty list | Test 1 |
| Archive with subdirectories | shutil.move preserves structure | Test 11 |
| Memory not configured | Skip auto_link call | Test 8 |
| Work item in archive (not active) | _find_work_file checks both | Test 12 |

### Open Questions

**Q: Should WorkEngine handle legacy flat file pattern (WORK-{id}-*.md)?**

A: No. The flat file pattern is legacy and should not be supported by the new module. Existing work_item.py handles it for backward compatibility. New WorkEngine focuses on directory structure only.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_work_engine.py` with all 12 tests
- [ ] Create test fixtures (sample WORK.md, tmp_path setup)
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create WorkEngine Module Core
- [ ] Create `.claude/haios/modules/work_engine.py`
- [ ] Implement WorkState dataclass
- [ ] Implement InvalidTransitionError, WorkNotFoundError
- [ ] Implement WorkEngine.__init__ with governance/memory/base_path
- [ ] Tests 1, 2 pass (get_work returns WorkState / None)

### Step 3: Implement Transition and DAG Validation
- [ ] Implement WorkEngine.transition()
- [ ] Integrate GovernanceLayer.validate_transition()
- [ ] Tests 3, 4, 10 pass (governance validation, node_history, invalid blocked)

### Step 4: Implement get_ready and Filtering
- [ ] Implement WorkEngine.get_ready()
- [ ] Filter by empty blocked_by
- [ ] Tests 5, 12 pass (unblocked only, excludes archived)

### Step 5: Implement create_work and archive
- [ ] Implement WorkEngine.create_work()
- [ ] Implement WorkEngine.archive() with shutil.move
- [ ] Tests 6, 7, 11 pass (create structure, archive moves, preserves subdirs)

### Step 6: Implement add_memory_refs
- [ ] Implement WorkEngine.add_memory_refs()
- [ ] Integrate MemoryBridge.auto_link callback
- [ ] Tests 8, 9 pass (calls memory bridge, owns writes)

### Step 7: Integration Verification
- [ ] All 12 tests pass
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify no regressions in governance_layer tests

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with WorkEngine
- [ ] **MUST:** Verify README content matches actual file state

### Step 9: Consumer Verification (N/A)
- Strangler fig pattern: No consumers to migrate yet
- Existing work_item.py remains for current consumers
- Future items will create consumer migration tasks

---

## Verification

- [ ] Tests pass (`pytest tests/test_work_engine.py -v`)
- [ ] Full test suite passes (`pytest tests/ -v`)
- [ ] **MUST:** `.claude/haios/modules/README.md` updated
- [ ] Code follows existing module patterns (GovernanceLayer, MemoryBridge)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GovernanceLayer transition validation too strict | Medium | Use same VALID_TRANSITIONS from existing module |
| Archive moves break relative paths | Low | shutil.move preserves structure; test with subdirs |
| Memory auto-link creates circular dependency | Low | Optional MemoryBridge; None-check before calls |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 161 | 2026-01-03 | - | In Progress | Plan filled, starting implementation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | WorkEngine class with 5 L4 functions | [ ] | |
| `tests/test_work_engine.py` | 12 tests covering all functions | [ ] | |
| `.claude/haios/modules/README.md` | Lists WorkEngine with description | [ ] | |
| `.claude/haios/modules/__init__.py` | Exports WorkEngine | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_work_engine.py -v
# Expected: 12 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (12/12)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated (modules/README.md)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- L4-implementation.md: WorkEngine functional requirements
- E2-240: GovernanceLayer (dependency)
- E2-241: MemoryBridge (dependency)
- INV-052: HAIOS Architecture Reference (section 17)
- INV-053: Modular Architecture Review

---
